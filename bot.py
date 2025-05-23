# bot.py
import discord
from discord.ext import commands

from commands.liga.votacao import register_votacao_command
from config import DISCORD_TOKEN
from commands.standings import register_standings_command
from commands.next_race import register_next_command
from commands.constructor_standings import register_constructor_standings
from utils.keep_alive import keep_alive

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"🤖 Bot ligado como {bot.user} (ID: {bot.user.id})")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Comandos slash sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")


#TODO: Exemplo de comando direto no bot.py (temporário)
@bot.tree.command(name="ping", description="Verifica se o bot está online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

register_next_command(bot)
register_standings_command(bot)
register_constructor_standings(bot)
register_votacao_command(bot)

keep_alive()
bot.run(DISCORD_TOKEN)
