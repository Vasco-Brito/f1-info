import asyncio
import json
from datetime import datetime as dt, timezone
from pathlib import Path

import discord

from telemetry.telemetry_utils.parser2024 import (
    Listener,
    PacketFinalClassificationData,
    processar_pacote
)
from telemetry.telemetry_utils.packet_management import (
    update_lap_data,
    update_participants,
    warnings,
    LISTE_JOUEURS,
)
from telemetry.telemetry_utils.dictionnaries import *
from config import TELEMETRY_PORT
from telemetry.telemetry_utils.race_stats import (
    process_speedtrap,
    process_lap_and_status_data,
    anexar_stats_a_resultado
)

CHANNEL_ID = 1364658111687692360

JOGADORES_POR_IP = {
    "176.78.118.245": "Y0orha",
    "127.0.0.1": "TazWanted",
}

output_folder = Path("corridas")
output_folder.mkdir(exist_ok=True)

last_laps = {}
voltas_concluidas = {}
tipo_corrida_atual = -1
nome_sessao_atual = "Sessão Desconhecida"
car_status_data_atual = None
sent_final = False
session_uid_atual = None
jogadores_com_telemetria = set()
penalizacoes = []
colisoes = []
dnf_pilotos = set()
dsq_pilotos = set()
safety_car_ativo = False
red_flag_ativa = False
melhores_tempos_qualy = {}



async def monitor_telemetry(bot):
    global sent_final, session_uid_atual, tipo_corrida_atual, nome_sessao_atual, car_status_data_atual,\
        jogadores_com_telemetria, penalizacoes, colisoes, dnf_pilotos, dsq_pilotos, safety_car_ativo, red_flag_ativa, \
        melhores_tempos_qualy

    print(f"🟢 PORTA DE ESCUTA: {TELEMETRY_PORT}")
    listener = Listener(port=TELEMETRY_PORT)
    print("📶 A escutar F1 24 UDP...")

    while True:
        try:
            result = listener.get()
            if result is None:
                await asyncio.sleep(0.01)
                continue

            header, packet, addr = result
            ip = addr[0]
            jogador_nome = JOGADORES_POR_IP.get(ip, f"Desconhecido ({ip})")
            packet_id = header.m_packet_id

            processar_pacote(header, packet)

            if packet_id == 1:
                if tipo_corrida_atual != packet.m_session_type or session_uid_atual != header.m_session_uid:
                    sent_final = False
                    session_uid_atual = header.m_session_uid
                    penalizacoes = []
                    colisoes = []
                    dnf_pilotos = set()
                    dsq_pilotos = set()
                    safety_car_ativo = False
                    red_flag_ativa = False
                    last_laps.clear()
                    voltas_concluidas.clear()
                    # print("[DEBUG] Reset do estado por nova sessão")

                tipo_corrida_atual = packet.m_session_type
                nome_sessao_atual = get_nome_sessao(tipo_corrida_atual)
                # print(f"[DEBUG] Tipo de sessão atual: {tipo_corrida_atual} → {nome_sessao_atual}")
                # print(f"[DEBUG] UID da sessão: {session_uid_atual}")

            elif packet_id == 2:
                update_lap_data(packet)
                if car_status_data_atual and tipo_corrida_atual in [10, 11]:
                    process_lap_and_status_data(packet.m_lap_data, car_status_data_atual)

                for i, jogador in enumerate(LISTE_JOUEURS):
                    volta_atual = jogador.currentLap
                    ultima_volta_guardada = last_laps.get(i, -1)
                    if jogador.lastLapTime > 0 and jogador.name.strip() and volta_atual > ultima_volta_guardada:
                        last_laps[i] = volta_atual
                        if volta_atual not in voltas_concluidas:
                            voltas_concluidas[volta_atual] = jogador.name
                            canal = bot.get_channel(CHANNEL_ID)
                            if canal:
                                msg = (
                                    f"🏁 `{jogador.name}` foi o primeiro a terminar a volta {volta_atual - 1} "
                                    f"com {round(jogador.lastLapTime, 3)}s!"
                                )
                                print(f"[Volta {volta_atual}] {msg}")
                                await canal.send(msg)

                # Guarda melhores tempos de qualificação
                if tipo_corrida_atual in [5, 6, 7, 8, 9]:  # Q1–Q3, Short Q, OSQ
                    for jogador in LISTE_JOUEURS:
                        nome = jogador.name.strip()
                        if not nome or jogador.bestLapTime == 0:
                            continue
                        if nome not in melhores_tempos_qualy or jogador.bestLapTime < melhores_tempos_qualy[nome]:
                            melhores_tempos_qualy[nome] = jogador.bestLapTime


            elif packet_id == 3:
                try:
                    event_code = bytes(packet.m_event_string_code).decode(errors="ignore").strip()

                    if event_code == "SPTP":
                        print("[📡] Speed trap ativado")
                        process_speedtrap(packet.m_event_details.m_speed_trap)

                    elif event_code == "PENA":
                        detalhes = packet.m_event_details.m_penalty

                        penalizado_por_idx = detalhes.m_other_vehicle_idx
                        piloto_idx = detalhes.m_vehicle_idx

                        if not (LISTE_JOUEURS[piloto_idx].aiControlled and (
                                penalizado_por_idx == 255 or LISTE_JOUEURS[penalizado_por_idx].aiControlled
                        )):
                            tipo_penalizacao = detalhes.m_penalty_type
                            tipo_infracao = detalhes.m_infringement_type
                            tempo = detalhes.m_time
                            volta = detalhes.m_lap_num

                            nome_piloto = (
                                LISTE_JOUEURS[piloto_idx].name
                                if 0 <= piloto_idx < len(LISTE_JOUEURS)
                                else "Desconhecido"
                            )


                            penalizado_por = (
                                LISTE_JOUEURS[penalizado_por_idx].name
                                if penalizado_por_idx != 255 and penalizado_por_idx < len(LISTE_JOUEURS)
                                else None
                            )

                            # Se for DSQ
                            if tipo_penalizacao == 6:
                                dsq_pilotos.add(nome_piloto)
                                print(f"[🟥] {nome_piloto} foi desclassificado (DSQ)")

                            penalizacao = {
                                "piloto": nome_piloto,
                                "tipo_penalizacao": tipo_penalizacao,
                                "tipo_penalizacao_desc": PENALTY_TYPES.get(tipo_penalizacao,
                                                                           f"Desconhecida ({tipo_penalizacao})"),
                                "tipo_infracao": tipo_infracao,
                                "tipo_infracao_desc": INFRINGEMENT_TYPES.get(tipo_infracao,
                                                                             f"Desconhecida ({tipo_infracao})"),
                                "volta": volta,
                                "tempo": tempo,
                                "penalizado_por": penalizado_por
                            }

                            penalizacoes.append(penalizacao)
                            print(f"[⚠️] Penalização registada: {penalizacao}")


                    elif event_code == "COLL":
                        colisao = packet.m_event_details.m_collision
                        idx1 = getattr(colisao, "m_vehicle1Idx", 255)
                        idx2 = getattr(colisao, "m_vehicle2Idx", 255)

                        if not (LISTE_JOUEURS[idx1].aiControlled and LISTE_JOUEURS[idx2].aiControlled):
                            nome1 = LISTE_JOUEURS[idx1].name if idx1 < len(LISTE_JOUEURS) else "Desconhecido"
                            nome2 = LISTE_JOUEURS[idx2].name if idx2 < len(LISTE_JOUEURS) else "Desconhecido"
                            volta = LISTE_JOUEURS[idx1].currentLap if idx1 < len(LISTE_JOUEURS) else -1
                            setor = (LISTE_JOUEURS[idx1].sector + 1) if idx1 < len(LISTE_JOUEURS) and hasattr(
                                LISTE_JOUEURS[idx1], "sector") else -1

                            colisoes.append({
                                "volta": volta,
                                "setor": setor,
                                "piloto": nome1,
                                "contra": nome2 if idx2 != 255 else None
                            })

                            print(f"[💥] Colisão na volta {volta}, setor {setor}: {nome1} ⇄ {nome2}")



                    elif event_code == "RTMT":
                        piloto_idx = packet.m_event_details.m_retirement.m_vehicle_index
                        if piloto_idx < len(LISTE_JOUEURS):
                            nome = LISTE_JOUEURS[piloto_idx].name
                            dnf_pilotos.add(nome)
                            print(f"[❌] {nome} retirou-se (DNF)")

                    elif event_code == "RCWN":
                        canal = bot.get_channel(CHANNEL_ID)
                        if canal:
                            await canal.send("🏁 Corrida terminada! Um vencedor foi declarado! (via RCWN)")

                    elif event_code == "FTLP":
                        detalhes = packet.m_event_details.m_fastest_lap
                        idx = detalhes.m_vehicle_idx
                        tempo = convert_tempo(detalhes.m_lap_time)
                        nome = LISTE_JOUEURS[idx].name
                        canal = bot.get_channel(CHANNEL_ID)
                        if canal:
                            await canal.send(f"⚡ `{nome}` fez a volta mais rápida: `{tempo}`")

                    elif event_code == "SCAR":
                        print("[🚗] Safety car ativado")
                        safety_car_ativo = True

                    elif event_code == "RDFL":
                        print("[🟥] Bandeira vermelha ativada")
                        red_flag_ativa = True

                    #else:
                    #    print(f"[📦] Evento não tratado: {event_code}")

                except Exception as e:
                    print(f"[⚠️] Erro ao processar evento: {e}")

            elif packet_id == 4:
                update_participants(packet)
                print(f"👥 Participantes recebidos de {jogador_nome}.")

            elif packet_id == 7:
                car_status_data_atual = packet.m_car_status_data
                for idx, status in enumerate(car_status_data_atual):
                    if idx >= len(LISTE_JOUEURS):
                        continue
                    nome = LISTE_JOUEURS[idx].name
                    if nome and nome not in jogadores_com_telemetria:
                        jogadores_com_telemetria.add(nome)
                        print(f"[📡] A receber telemetria completa de: {', '.join(sorted(jogadores_com_telemetria))}")

            if packet_id == 8 and not sent_final:
                if tipo_corrida_atual in [10, 11, 12, 13, 14, 15, 16, 17]:
                    if isinstance(packet, PacketFinalClassificationData):
                        resultado = []
                        for i, data in enumerate(packet.m_classification_data):
                            nome = LISTE_JOUEURS[i].name or f"Carro {i}"
                            ia = LISTE_JOUEURS[i].aiControlled
                            melhor_volta_segundos = round(data.m_best_lap_time_in_ms / 1000.0, 3)
                            tempo_total_segundos = round(data.m_total_race_time, 3)
                            resultado.append({
                                "idx": i,
                                "posicao": data.m_position,
                                "nome": nome,
                                "ia": ia,
                                "voltas": data.m_num_laps,
                                "grid": data.m_grid_position,
                                "pontos": data.m_points,
                                "melhor_volta": melhor_volta_segundos,
                                "melhor_volta_str": convert_tempo(melhor_volta_segundos),
                                "tempo_total": tempo_total_segundos,
                                "tempo_total_str": convert_tempo(tempo_total_segundos)
                            })

                        for r in resultado:
                            r["DNF"] = 1 if r["nome"] in dnf_pilotos else 0
                            r["DSQ"] = 1 if r["nome"] in dsq_pilotos else 0

                        resultado = anexar_stats_a_resultado(resultado)

                        now = dt.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
                        session_uid = header.m_session_uid
                        filename = output_folder / f"corrida_{now}.json"
                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump({
                                "corrida": {
                                    "data": now,
                                    "tipo": nome_sessao_atual,
                                    "session_uid": session_uid,
                                    "resultado": resultado,
                                    "penalizacoes": penalizacoes,
                                    "voltas_concluidas": voltas_concluidas,
                                    "colisoes": colisoes,
                                    "safety_car": 1 if safety_car_ativo else 0,
                                    "red_flag": 1 if red_flag_ativa else 0
                                }
                            }, f, indent=2, ensure_ascii=False)

                        canal = bot.get_channel(CHANNEL_ID)
                        if canal:
                            embed = discord.Embed(
                                title="🏁 Corrida terminada!",
                                description=f"Resultados guardados em `{filename.name}`",
                                color=discord.Color.green()
                            )
                            embed.add_field(name="Top 3", value="\n".join(
                                [f"**#{r['posicao']}** {r['nome']} — {r['pontos']} pts"
                                 for r in sorted(resultado, key=lambda x: x['posicao'])[:3]]
                            ))
                            await canal.send(embed=embed)

                        print(f"🏁 Corrida terminada. Resultados guardados em {filename}")
                        sent_final = True
                    elif tipo_corrida_atual in [5, 6, 7, 8, 9] and melhores_tempos_qualy:
                        now = dt.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
                        session_uid = header.m_session_uid
                        filename = output_folder / f"qualificacao_{now}.json"

                        resultado_qualy = [
                            {
                                "nome": nome,
                                "melhor_volta": round(tempo, 3),
                                "melhor_volta_str": convert_tempo(tempo)
                            }
                            for nome, tempo in sorted(melhores_tempos_qualy.items(), key=lambda x: x[1])
                        ]

                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump({
                                "qualificacao": {
                                    "data": now,
                                    "tipo": nome_sessao_atual,
                                    "session_uid": session_uid,
                                    "resultados": resultado_qualy
                                }
                            }, f, indent=2, ensure_ascii=False)

                        canal = bot.get_channel(CHANNEL_ID)
                        if canal:
                            embed = discord.Embed(
                                title="⏱️ Qualificação concluída!",
                                description=f"Tempos guardados em `{filename.name}`",
                                color=discord.Color.blue()
                            )
                            embed.add_field(name="Top 3", value="\n".join(
                                [f"**#{i + 1}** {r['nome']} — {r['melhor_volta_str']}" for i, r in
                                 enumerate(resultado_qualy[:3])]
                            ))
                            await canal.send(embed=embed)

                        print(f"⏱️ Qualificação terminada. Resultados guardados em {filename}")
                        sent_final = True


        except Exception as e:
            print(f"❌ Erro no loop de telemetria: {e}")
