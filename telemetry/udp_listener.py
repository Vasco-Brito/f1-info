import asyncio
import json
from datetime import datetime as dt, timezone
from pathlib import Path

import discord

from telemetry.telemetry_utils.parser2024 import (
    Listener,
    PacketFinalClassificationData,
    processar_pacote  # 👈 Importa o processador que regista voltas/penalizações
)
from telemetry.telemetry_utils.packet_management import (
    update_lap_data,
    update_participants,
    warnings,
    LISTE_JOUEURS,
)
from telemetry.telemetry_utils.dictionnaries import *
from config import TELEMETRY_PORT

CHANNEL_ID = 1364658111687692360

# IP → Jogador
JOGADORES_POR_IP = {
    "176.78.118.245": "Y0orha",
    "127.0.0.1": "TazWanted",
}

output_folder = Path("corridas")
output_folder.mkdir(exist_ok=True)

last_laps = {}  # index -> última volta conhecida
voltas_concluidas = {}  # número da volta -> nome do jogador que a completou primeiro
tipo_corrida_atual = None
sent_final = False


async def monitor_telemetry(bot):
    global sent_final
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

            # 🧠 RaceTracker: regista liderança e penalizações
            processar_pacote(header, packet)

            # Participantes
            if packet_id == 4:
                update_participants(packet)
                print(f"👥 Participantes recebidos de {jogador_nome}.")

            elif packet_id == 1:
                tipo_corrida_atual = packet.m_session_type
                print(f"[DEBUG] Tipo de sessão atual: {tipo_corrida_atual}")

            # Voltas
            elif packet_id == 2:
                update_lap_data(packet)

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

            # Eventos
            elif packet_id == 3:
                warnings(packet)

            # Fim da corrida
            print(f"[DEBUG] sent_final = {sent_final}")
            if packet_id == 8 and not sent_final:
                print(packet_id)
                print(f"Tipo do pacote recebido: {type(packet)}")
                if isinstance(packet, PacketFinalClassificationData):
                    print("🎯 ENTROU no bloco de final da corrida!")
                    resultado = []
                    for i, data in enumerate(packet.m_classification_data):
                        nome = LISTE_JOUEURS[i].name or f"Carro {i}"
                        ia = LISTE_JOUEURS[i].aiControlled
                        resultado.append({
                            "posicao": data.m_position,
                            "nome": nome,
                            "ia": ia,
                            "voltas": data.m_num_laps,
                            "grid": data.m_grid_position,
                            "pontos": data.m_points,
                            "melhor_volta": round(data.m_best_lap_time_in_ms / 1000.0, 3),
                            "tempo_total": round(data.m_total_race_time, 3)
                        })

                    now = dt.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
                    filename = output_folder / f"corrida_{now}.json"
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump({
                            "corrida": {
                                "data": now,
                                "tipo": "Corrida",
                                "resultado": resultado,
                                "penalizacoes": [],
                                "voltas_concluidas": voltas_concluidas
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

        except Exception as e:
            print(f"❌ Erro no loop de telemetria: {e}")
