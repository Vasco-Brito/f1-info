from discord import app_commands, Interaction, Embed
from typing import Optional
import requests

team_colors = {
    "Red Bull": 0x1E41FF,
    "Mercedes": 0x00D2BE,
    "Ferrari": 0xDC0000,
    "McLaren": 0xFF8700,
    "Aston Martin": 0x006F62,
    "Alpine": 0x0090FF,
    "AlphaTauri": 0x2B4562,
    "Williams": 0x005AFF,
    "Alfa Romeo": 0x900000,
    "Haas": 0xFFFFFF,
}


def register_standings_command(bot):
    @bot.tree.command(name="standings", description="Mostra a classificação atual dos pilotos")
    @app_commands.describe(top="Número de pilotos a mostrar (default: 10)")
    async def standings(interaction: Interaction, top: Optional[int] = 10):
        try:
            top = max(1, min(top, 20))  # Limita entre 1 e 20

            url = "https://api.jolpi.ca/ergast/f1/current/driverStandings.json"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
            season = data["MRData"]["StandingsTable"]["season"]

            emojis = ["🥇", "🥈", "🥉"]

            table_lines = [
                f"{'Pos':<4} {'Driver':<22} {'Team':<20} {'Pts':>4}"
            ]

            leader_team = standings[0]["Constructors"][0]["name"]
            embed_color = team_colors.get(leader_team, 0xAAAAAA)  # fallback cinza

            for i, driver in enumerate(standings[:top]):
                pos = i + 1
                name = f"{driver['Driver']['givenName']} {driver['Driver']['familyName']}"
                team = driver["Constructors"][0]["name"]
                points = driver["points"]

                # Truncar nome se for longo demais
                name = (name[:19] + "...") if len(name) > 22 else name

                table_lines.append(
                    f"{str(pos):<4} {name:<22} {team:<20} {points:>4}"
                )

            embed = Embed(
                title=f"🏎️ Classificação de Pilotos 2025 [{leader_team}]",
                description="```markdown\n" + "\n".join(table_lines) + "\n```",
                color=embed_color
            )
            embed.set_footer(text="Fonte: Jolpi (Ergast)")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao buscar classificação: {e}")
