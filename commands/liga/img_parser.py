from discord import app_commands, Interaction
import discord
from services.image_parser import analisar_imagem

@app_commands.command(name="img", description="Analisa até 2 imagens de qualificação")
@app_commands.describe(
    imagem1="Imagem principal",
    imagem2="(Opcional) Segunda imagem"
)
async def img_command(
    interaction: Interaction,
    imagem1: discord.Attachment,
    imagem2: discord.Attachment = None
):
    await interaction.response.defer()

    mensagens = []

    resultado1, ficheiros1 = await analisar_imagem(imagem1)
    mensagens.append((resultado1, ficheiros1))

    if imagem2:
        resultado2, ficheiros2 = await analisar_imagem(imagem2)
        mensagens.append((resultado2, ficheiros2))

    for texto, ficheiros in mensagens:
        if ficheiros:
            await interaction.followup.send(content=texto, files=ficheiros)
        else:
            await interaction.followup.send(content=texto)
