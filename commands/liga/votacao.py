from discord import app_commands, Interaction
import discord
from discord.http import Route
from datetime import datetime, timedelta
from typing import Optional
import pytz

dias_semana = {
    "segunda": 0,
    "terça": 1, "terca": 1,
    "quarta": 2,
    "quinta": 3,
    "sexta": 4,
    "sábado": 5, "sabado": 5,
    "domingo": 6
}

def calcular_duracao(dia_str):
    hoje = datetime.now(pytz.timezone("Europe/Lisbon"))
    alvo = dias_semana.get(dia_str.lower())

    if alvo is None:
        raise ValueError("Dia inválido. Usa: segunda, terça, quarta, etc.")

    dias_ate_alvo = (alvo - hoje.weekday() + 7) % 7
    data_corrida = hoje + timedelta(days=dias_ate_alvo)

    data_fim = datetime(
        year=data_corrida.year,
        month=data_corrida.month,
        day=data_corrida.day,
        hour=20, minute=0, second=0,
        tzinfo=pytz.timezone("Europe/Lisbon")
    ) - timedelta(days=1)

    duracao_horas = (data_fim - hoje).total_seconds() / 3600
    return max(int(duracao_horas), 1)

def register_votacao_command(bot):
    @bot.tree.command(name="votação", description="Cria uma votação com thread e horário")
    @app_commands.describe(
        titulo="Título da votação",
        dia="Dia da corrida (ex: domingo, sábado...)",
        role="Role a mencionar no fim (ex: @everyone)"
    )
    async def votacao(interaction: Interaction, titulo: str, dia: str, role: Optional[str] = None):
        await interaction.response.defer(thinking=True)

        try:
            duration = calcular_duracao(dia)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro ao calcular duração: {e}")
            return

        poll_payload = {
            "content": "",
            "poll": {
                "question": { "text": titulo },
                "answers": [
                    { "answer_text": "A", "poll_media": { "text": "✅ Sim" } },
                    { "answer_text": "B", "poll_media": { "text": "❌ Não" } },
                    { "answer_text": "C", "poll_media": { "text": "🤔 Talvez" } }
                ],
                "duration": duration
            }
        }

        try:
            create_msg_route = Route("POST", f"/channels/{interaction.channel_id}/messages")
            response = await bot.http.request(create_msg_route, json=poll_payload)
            message_id = int(response["id"])

            thread_route = Route(
                "POST",
                f"/channels/{interaction.channel_id}/messages/{message_id}/threads"
            )
            thread_payload = {
                "name": f"{titulo[:80]} - Horas",
                "auto_archive_duration": 1440,
                "type": 11
            }
            thread_response = await bot.http.request(thread_route, json=thread_payload)
            thread_id = int(thread_response["id"])

            horarios_payload = {
                "content": "",
                "poll": {
                    "question": { "text": "Qual o melhor horário?" },
                    "answers": [
                        { "answer_text": "A", "poll_media": { "text": "Antes das 21" } },
                        { "answer_text": "B", "poll_media": { "text": "21" } },
                        { "answer_text": "C", "poll_media": { "text": "21:30" } },
                        { "answer_text": "D", "poll_media": { "text": "22" } },
                        { "answer_text": "E", "poll_media": { "text": "22:30" } },
                        { "answer_text": "F", "poll_media": { "text": "23" } },
                        { "answer_text": "G", "poll_media": { "text": "23:30" } },
                        { "answer_text": "H", "poll_media": { "text": "Depois da 00:00" } }
                    ],
                    "duration": duration,
                    "allow_multiselect": True
                }
            }

            thread_msg_route = Route("POST", f"/channels/{thread_id}/messages")
            await bot.http.request(thread_msg_route, json=horarios_payload)

            if role:
                channel = await bot.fetch_channel(thread_id)
                ping = await channel.send(role)
                await ping.delete()

            await interaction.followup.send("✅ Votação, thread e horários criados com sucesso!")

        except Exception as e:
            await interaction.followup.send(f"❌ Erro ao criar votação ou thread: {e}")
