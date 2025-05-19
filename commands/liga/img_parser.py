from discord import app_commands, Interaction
import discord
from services.image_parser import analisar_imagem
from services.vision_usage import registar_pedido


@app_commands.command(name="img", description="Analisa 2 imagens de qualificação")
@app_commands.describe(
    imagem1="Imagem principal (linhas 1-14)",
    imagem2="Imagem complementar (linhas 15-20)",
    debug="Ativa modo DEBUG para enviar os cortes como imagens"
)
async def img_command(
    interaction: Interaction,
    imagem1: discord.Attachment,
    imagem2: discord.Attachment,
    debug: bool = False
):
    await interaction.response.defer()

    mensagens = []

    offset_y2 = 0
    if imagem2.width == 3440:
        offset_y2 = 424
    else:
        offset_y2 = 320

    # 📄 Imagem 1 → linhas 1 a 14 (começa em cima)
    resultado1, ficheiros1 = await analisar_imagem(
        imagem1,
        total_linhas=14,
        offset_y=0,
        linha_inicial_visual=1,
        debug=debug
    )
    mensagens.append((resultado1, ficheiros1))

    # 📄 Imagem 2 → linhas 15 a 20 (começa na 9ª linha visível → offset 8 * 53 = 424px)
    resultado2, ficheiros2 = await analisar_imagem(
        imagem2,
        total_linhas=6,
        offset_y=offset_y2,
        linha_inicial_visual=15,
        debug=debug
    )
    mensagens.append((resultado2, ficheiros2))

    # Enviar respostas para o Discord
    # Ver se estamos em modo debug (ficheiros presentes) ou modo OCR (só texto)
    if any(f for _, f in mensagens if f):  # pelo menos uma imagem foi gerada
        for texto, ficheiros in mensagens:
            if ficheiros:
                await interaction.followup.send(content=texto, files=ficheiros)
            else:
                await interaction.followup.send(content=texto)
    else:
        # Junta todos os textos numa só mensagem
        texto_final = "\n".join(t for t, _ in mensagens)
        await interaction.followup.send(content=texto_final)

