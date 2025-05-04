from discord import app_commands, Interaction, File
import discord
from PIL import Image, ImageDraw
import pytesseract
import io
import re

PILOTOS_REAIS = [
    "Max VERSTAPPEN", "Sergio PEREZ", "Charles LECLERC", "Carlos SAINZ",
    "Lewis HAMILTON", "George RUSSELL", "Lando NORRIS", "Oscar PIASTRI",
    "Fernando ALONSO", "Lance STROLL", "Pierre GASLY", "Esteban OCON",
    "Yuki TSUNODA", "Daniel RICCIARDO", "Valtteri BOTTAS", "Zhou GUANYU",
    "Kevin MAGNUSSEN", "Nico HULKENBERG", "Alexander ALBON", "Logan SARGEANT"
]

def extract_text_from_box(image: Image.Image, box: tuple[int, int, int, int]) -> str:
    cropped = image.crop(box)
    return pytesseract.image_to_string(cropped, config='--psm 6').strip()

def extract_race_title(image: Image.Image) -> str:
    box = (315, 265, 880, 290)
    return extract_text_from_box(image, box)

def corrigir_tempo_ou_gap(raw: str) -> str:
    raw = raw.replace(';', ':').replace(',', '.').replace(' ', '').strip()

    if re.match(r'^1\d{2}\.\d{3}$', raw):
        return f"{raw[0]}:{raw[1:]}"

    if re.match(r'^1\d{5}$', raw):
        return f"{raw[0]}:{raw[1:3]}.{raw[3:]}"

    if re.match(r'^\+\d{4}$', raw):
        return f"+{raw[1]}.{raw[2:]}"

    return raw

def extract_column_data(image: Image.Image, base_y: int, linhas: int, x1: int, x2: int, corrigir: bool = False) -> list[str]:
    dados = []
    text_height = 22
    line_height = 40

    for i in range(linhas):
        y1 = base_y + i * line_height - 2
        y2 = y1 + text_height
        box = (x1, y1, x2, y2)
        texto = extract_text_from_box(image, box)
        if corrigir:
            texto = corrigir_tempo_ou_gap(texto)
        dados.append(texto if texto else "")

    return dados

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
            for _, (x1, x2) in colunas.items():
                draw.rectangle([(x1, y1), (x2, y2)], outline="green", width=2)

        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        return img, output

    if not imagem1.content_type.startswith("image/") or not imagem2.content_type.startswith("image/"):
        await interaction.followup.send("❌ Ambas as imagens devem ser válidas.")
        return

    imagem1_bytes = await imagem1.read()
    imagem2_bytes = await imagem2.read()

    img1, img1_editada = preparar_imagem(imagem1_bytes, incluir_titulo=True, linhas=14, base_y=375)
    img2, img2_editada = preparar_imagem(imagem2_bytes, incluir_titulo=False, linhas=6, base_y=690)

    titulo = extract_race_title(img1)

    nomes1 = extract_column_data(img1, 375, 14, 776, 964)
    teams1 = extract_column_data(img1, 375, 14, 972, 1173)
    bests1 = extract_column_data(img1, 375, 14, 1356, 1483, corrigir=True)
    gaps1  = extract_column_data(img1, 375, 14, 1488, 1578, corrigir=True)

    nomes2 = extract_column_data(img2, 690, 6, 776, 964)
    teams2 = extract_column_data(img2, 690, 6, 972, 1173)
    bests2 = extract_column_data(img2, 690, 6, 1356, 1483, corrigir=True)
    gaps2  = extract_column_data(img2, 690, 6, 1488, 1578, corrigir=True)

    nomes = nomes1 + nomes2
    teams = teams1 + teams2
    bests = bests1 + bests2
    gaps  = gaps1 + gaps2

    file1 = File(fp=img1_editada, filename="imagem_topo_marcada.png")
    file2 = File(fp=img2_editada, filename="imagem_fundo_marcada.png")

    # Conteúdo de resposta como texto simples para evitar limites de embed
    linhas_formatadas = [
        f"{i+1:>2}. {nomes[i]:<18} | {teams[i]:<16} | {bests[i]:<9} | {gaps[i]}"
        for i in range(len(nomes))
    ]

    texto = f"\U0001f3c1 **{titulo if titulo else 'Corrida não identificada'}**\n\n" + "\n".join(linhas_formatadas)

    await interaction.followup.send(
        content=texto,
        files=[file1, file2]
    )
