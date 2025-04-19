from discord import app_commands, Interaction, Embed
from typing import Optional
from collections import defaultdict
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
    "RB F1 Team": 0x5E8B7E,
    "RB": 0x5E8B7E,
    "Sauber": 0xFF0000
}

def register_constructor_standings(bot):

    async def handle_constructors(interaction: Interaction, top: Optional[int]):
        try:
            top = max(1, min(top or 5, 10))

            url = "https://api.jolpi.ca/ergast/f1/current/driverStandings.json"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
            season = data["MRData"]["StandingsTable"]["season"]

            team_points = defaultdict(float)
            for driver in standings:
                team = driver["Constructors"][0]["name"]
                points = float(driver["points"])
                team_points[team] += points

            sorted_teams = sorted(team_points.items(), key=lambda x: x[1], reverse=True)

            table_lines = [f"{'Pos':<4} {'Team':<22} {'Pts':>5}"]
            for i, (team, points) in enumerate(sorted_teams[:top]):
                team_display = team[:22] if len(team) <= 22 else team[:19] + "..."
                table_lines.append(f"{i+1:<4} {team_display:<22} {int(points):>5}")

            table = "```markdown\n" + "\n".join(table_lines) + "\n```"

            leader_team = sorted_teams[0][0]
            embed_color = team_colors.get(leader_team, 0xAAAAAA)

            embed = Embed(
                title=f"🏆 Classificação de Construtores {season} [{leader_team}]",
                description=f"Top {top} equipas da temporada atual",
                color=embed_color
            )
            embed.add_field(name="📋 Tabela", value=table, inline=False)
            embed.set_footer(text="Fonte: Jolpi / Ergast API")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao buscar dados: {e}")

    @bot.tree.command(name="teams", description="Mostra a classificação atual das equipas (construtores)")
    @app_commands.describe(top="Número de equipas a mostrar (default: 5, máximo: 10)")
    async def teams_command(interaction: Interaction, top: Optional[int] = 5):
        await handle_constructors(interaction, top)

    @bot.tree.command(name="constructors", description="Alias para /teams")
    @app_commands.describe(top="Número de equipas a mostrar (default: 5, máximo: 10)")
    async def constructors_command(interaction: Interaction, top: Optional[int] = 5):
        await handle_constructors(interaction, top)