from discord import app_commands, Interaction, File
import discord
from PIL import Image, ImageDraw
import io

@app_commands.command(name="img", description="Recebe até 2 imagens e marca zonas por colunas")
@app_commands.describe(
    imagem1="Imagem com o topo da qualificação (1 a 14)",
    imagem2="Imagem com o fundo da qualificação (15 a 20)"
)
async def img_command(interaction: Interaction, imagem1: discord.Attachment, imagem2: discord.Attachment):
    await interaction.response.defer()

    def preparar_imagem(img_bytes, incluir_titulo=False, linhas=0, base_y=0):
        img = Image.open(io.BytesIO(img_bytes))
        if img.width > 1920 or img.height > 1080:
            img = img.resize((1920, 1080))

        draw = ImageDraw.Draw(img)

        if incluir_titulo:
            draw.rectangle([(315, 265), (880, 290)], outline="red", width=2)

        # Colunas definidas
        colunas = {
            "Driver": (778, 966),
            "Team": (974, 1175),
            "Best": (1358, 1485),
            "Gap": (1490, 1580)
        }

        text_height = 22
        line_height = 40

        for i in range(linhas):
            y1 = base_y + i * line_height - 2
            y2 = y1 + text_height
            for nome, (x1, x2) in colunas.items():
                draw.rectangle([(x1, y1), (x2, y2)], outline="green", width=2)

        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        return output

    if not imagem1.content_type.startswith("image/") or not imagem2.content_type.startswith("image/"):
        await interaction.followup.send("❌ Ambas as imagens devem ser válidas.")
        return

    imagem1_bytes = await imagem1.read()
    imagem2_bytes = await imagem2.read()

    img1_editada = preparar_imagem(imagem1_bytes, incluir_titulo=True, linhas=14, base_y=375)
    img2_editada = preparar_imagem(imagem2_bytes, incluir_titulo=False, linhas=6, base_y=690)

    file1 = File(fp=img1_editada, filename="imagem_topo_marcada.png")
    file2 = File(fp=img2_editada, filename="imagem_fundo_marcada.png")

    await interaction.followup.send(
        content="📎 Zonas marcadas com colunas por linha.",
        files=[file1, file2]
    )
