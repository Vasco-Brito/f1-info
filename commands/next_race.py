from discord import app_commands, Interaction, Embed
from datetime import datetime, timezone, timedelta
import requests

API_URL = "https://api.formula1.com/v1/event-tracker"
API_KEY = "BQ1SiSmLUOsp460VzXBlLrh689kGgYEZ"

HEADERS = {
    "User-Agent": "f1-discord-bot",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "apikey": API_KEY,
    "locale": "en"
}

def register_next_command(bot):
    @bot.tree.command(name="next", description="Mostra quanto falta para a próxima corrida")
    async def next_race(interaction: Interaction):
        try:
            response = requests.get(API_URL, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            race_name = data["race"]["meetingOfficialName"]
            location = f'{data["race"]["meetingLocation"]}, {data["race"]["meetingCountryName"]}'
            year = data["seasonContext"]["seasonYear"]
            color_hex = data.get("brandColourHexadecimal", "ee0000")

            session_labels = {
                "p1": "Practice 1",
                "p2": "Practice 2",
                "p3": "Practice 3",
                "q": "Qualifying",
                "r": "Race",
                "sprint": "Sprint",
                "ss": "Sprint Shootout"
            }

            sessions_text = ""
            race_datetime = None
            now = datetime.now(timezone.utc)

            for session in data["seasonContext"]["timetables"]:
                code = session["session"]
                label = session_labels.get(code, code.upper())

                start_str = session["startTime"]
                offset_str = session.get("gmtOffset", "+00:00")
                offset_hours, offset_minutes = map(int, offset_str.split(":"))
                offset = timedelta(hours=offset_hours, minutes=offset_minutes)

                local_dt = datetime.fromisoformat(start_str)
                utc_dt = (local_dt - offset).replace(tzinfo=timezone.utc)
                timestamp = int(utc_dt.timestamp())

                sessions_text += f"**{label}** — <t:{timestamp}:f> • <t:{timestamp}:R>\n"

                if code == "r":
                    race_datetime = utc_dt

            if not race_datetime:
                await interaction.response.send_message("❌ Não encontrei a data da corrida.")
                return

            diff = race_datetime - now
            dias = diff.days
            horas, resto = divmod(diff.seconds, 3600)
            minutos = resto // 60
            countdown = f"{dias} dias, {horas} horas, {minutos} minutos"

            embed = Embed(
                title=f"🏁 {race_name}",
                description=f"📍 {location}\n📆 Temporada {year}",
                color=int(color_hex, 16)
            )

            embed.add_field(name="🗓️ Sessões do fim de semana", value=sessions_text, inline=False)
            embed.add_field(
                name="🕓 Inicio da corrida",
                value=f"<t:{int(race_datetime.timestamp())}:f> • <t:{int(race_datetime.timestamp())}:R>",
                inline=False
            )

            circuit_img = data.get("circuitSmallImage", {}).get("url")
            if circuit_img:
                embed.set_thumbnail(url=circuit_img)

            embed.set_footer(text="Powered by F1 Official")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao buscar dados da corrida: {e}")
