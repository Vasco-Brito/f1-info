# monitor.py (reformulado com parser2024)

import asyncio
import discord
from datetime import datetime
from pathlib import Path
import json
from telemetry.utils.parser2024 import Listener

output_folder = Path("corridas")
output_folder.mkdir(exist_ok=True)

participants = {}
last_laps = {}
final_result = []
penalties = []
finished = False


async def monitor_telemetry(bot):
    global finished
    listener = Listener()
    print("📶 A escutar F1 24 UDP (formato 2024)...")

    canal_id = 1364658111687692360
    channel = bot.get_channel(canal_id)
    if channel:
        await channel.send("📶 Telemetria ligada! À espera de dados do F1 24...")

    while True:
        try:
            result = listener.get()
            if result is None:
                await asyncio.sleep(0.01)
                continue

            header, packet = result
            packet_type = type(packet).__name__

            if packet_type == "PacketParticipantsData":
                for i, p in enumerate(packet.m_participants):
                    name = p.m_name.decode('utf-8', errors='ignore').split("\x00")[0].strip()
                    if not name:
                        name = f"Carro {i}"
                    participants[i] = {"nome": name, "ia": bool(p.m_ai_controlled)}
                print(f"👥 Participantes: {[p['nome'] for p in participants.values()]}")

            elif packet_type == "PacketLapData":
                for i, lap in enumerate(packet.m_lap_data):
                    lap_number = lap.m_current_lap_num
                    car_position = lap.m_car_position
                    if not (1 <= car_position <= 22) or not (0 < lap_number < 100):
                        continue
                    if i in participants:
                        nome = participants[i]["nome"]
                        ia = participants[i]["ia"]
                        ultima_volta = last_laps.get(i, -1)
                        if lap_number > ultima_volta:
                            print(f"🚩 O {'bot' if ia else 'jogador'} {nome} terminou a volta {lap_number} na posição {car_position}")
                            last_laps[i] = lap_number

            elif packet_type == "PacketEventData":
                try:
                    code = packet.m_event_string.decode('ascii')
                    if code == "SEND":
                        print("🏁 Corrida ou qualificação terminada!")
                except:
                    pass

            elif packet_type == "PacketFinalClassificationData" and not finished:
                for i, data in enumerate(packet.m_classification_data):
                    nome = participants.get(i, {}).get("nome", f"Carro {i}")
                    ia = participants.get(i, {}).get("ia", True)
                    final_result.append({
                        "posicao": data.m_position,
                        "nome": nome,
                        "ia": ia,
                        "voltas": data.m_num_laps,
                        "grid": data.m_grid_position,
                        "pontos": data.m_points,
                        "melhor_volta": round(data.m_best_lap_time_in_ms / 1000.0, 3),
                        "tempo_total": round(data.m_total_race_time, 3)
                    })

                now = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
                filename = output_folder / f"corrida_{now}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump({
                        "corrida": {
                            "data": now,
                            "tipo": "Corrida ou Qualificação",
                            "resultado": final_result,
                            "penalizacoes": penalties
                        }
                    }, f, indent=2, ensure_ascii=False)

                finished = True
                if channel:
                    await channel.send(
                        f"🏁 Corrida terminada! Resultados salvos em `corrida_{now}.json`",
                        file=discord.File(str(filename))
                    )

        except Exception as e:
            print(f"Erro no loop de telemetria: {e}")
