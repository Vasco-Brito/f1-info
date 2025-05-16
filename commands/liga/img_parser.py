from discord import app_commands, Interaction, File
import discord
from PIL import Image, ImageDraw, ImageFilter
import pytesseract
import io
import re

PILOTOS_REAIS = [
    "Max VERSTAPPEN", "Sergio PEREZ", "Charles LECLERC", "Carlos SAINZ",
    "Lewis HAMILTON", "George RUSSELL", "Lando NORRIS", "Oscar PIASTRI",
    "Fernando ALONSO", "Lance STROLL", "Pierre GASLY", "Esteban OCON",
    "Yuki TSUNODA", "Daniel RICCIARDO", "Valtteri BOTTAS", "ZHOU Guanyu",
    "Kevin MAGNUSSEN", "Nico HULKENBERG", "Alexander ALBON", "Logan SARGEANT"
]

async def perguntar_jogadores_faltantes() -> str:
    return

async def processar_imagem_16_9(image: Image.Image, interaction: Interaction):
    return "🖈 Imagem é 16:9 (1920x1080)"

async def processar_imagem_21_9(image: Image.Image, interaction: Interaction, debug: bool = False):
    # Coordenadas
    x_titulo, y_titulo = 566, 351
    largura_titulo, altura_titulo = 1022, 40
    box_titulo = (x_titulo, y_titulo, x_titulo + largura_titulo, y_titulo + altura_titulo)

    x_tab, y_tab = 1393, 489
    w_tab, h_tab = 1449, 732
    box_tab = (x_tab, y_tab, x_tab + w_tab, y_tab + h_tab)

    # OCR título
    cropped_titulo = image.crop(box_titulo)
    texto_titulo = pytesseract.image_to_string(cropped_titulo, config='--psm 6').strip()

    # Tipo sessão
    tipo_formatado = "❓ Desconhecido"
    texto_maiusculas = texto_titulo.upper()
    if "RACE" in texto_maiusculas:
        tipo_formatado = "🏎 Race"
    elif "SPRINT" in texto_maiusculas:
        tipo_formatado = "⚡ Sprint"
    elif "QUALIFYING" in texto_maiusculas:
        tipo_formatado = "⏱️ Qualifying"

    # Mensagem principal
    mensagem = f"🏎 **Título**: {texto_titulo}\n🧱 **Tipo**: {tipo_formatado}"
    await interaction.followup.send(content=mensagem)

    # Imagem ampliada da tabela
    tabela_crop = image.crop(box_tab)
    tabela_resize = tabela_crop.resize((w_tab * 2, h_tab * 2))
    resized_width, resized_height = tabela_resize.size

    draw_linhas = ImageDraw.Draw(tabela_resize)
    linha_altura = 95
    espaco = 11
    resultados = []

    for i in range(14):
        top = i * (linha_altura + espaco)
        cor = "blue" if i % 2 == 0 else "red"
        draw_linhas.rectangle([(0, top), (resized_width, top + linha_altura)], outline=cor, width=2)

        nome_box = (0, top, 677, top + linha_altura)
        equipa_box = (689, top, 689 + 762, top + linha_altura)
        best_box = (1868, top, 1868 + 342, top + linha_altura)
        time_box = (2211, top, 2211 + 582, top + linha_altura)

        draw_linhas.rectangle(nome_box, outline="yellow", width=1)
        draw_linhas.rectangle(equipa_box, outline="green", width=1)
        draw_linhas.rectangle(best_box, outline="purple", width=1)
        draw_linhas.rectangle(time_box, outline="orange", width=1)

        nome_img = tabela_resize.crop(nome_box)
        equipa_img = tabela_resize.crop(equipa_box).filter(ImageFilter.MedianFilter()).convert("L").point(lambda x: 0 if x < 160 else 255, mode='1')
        best_img = tabela_resize.crop(best_box)
        time_img = tabela_resize.crop(time_box)

        nome = pytesseract.image_to_string(nome_img, config="--psm 7").strip()
        equipa = pytesseract.image_to_string(equipa_img, config="--psm 7").strip()
        best = pytesseract.image_to_string(best_img, config="--psm 7").strip()
        time = pytesseract.image_to_string(time_img, config="--psm 7").strip()

        # Limpeza e correções
        nome = re.sub(r'^[^a-zA-Z0-9]*', '', nome)

        equipa = re.sub(r'f?AA', 'M', equipa, flags=re.IGNORECASE)
        equipa = re.sub(r'[^a-zA-Z0-9\- ]+', '', equipa)

        best = best.replace('L', '1').replace('£', '1').replace(',', '.').replace('°', '.')
        best = best.replace('S', '5').replace('I', '1').replace('|', '1')
        best = re.sub(r'[^0-9:.]', '', best)
        best = re.sub(r'\.{2,}', '.', best)
        if not ':' in best and len(best) >= 5:
            best = f"{best[0]}:{best[1:3]}.{best[3:]}"

        time = time.replace('S', '5').replace('I', '1')
        time = re.sub(r'\s+', ' ', time).strip()
        time = time.replace('++', '+').replace(' +', '+').replace('+ ', '+')
        time = re.sub(r'[^0-9+:.a-zA-Z ]', '', time).strip()
        if re.fullmatch(r'[0-9]{6}', time):
            time = f"+{time[0]}:{time[1:3]}.{time[3:]}"
        elif re.fullmatch(r'[0-9]{5}', time):
            time = f"+0:{time[0:2]}.{time[2:]}"

        resultados.append(f"{i+1:>2}. {nome} | {equipa} | Best: {best} | Time: {time}")

    texto_resultados = "\n".join(resultados)
    await interaction.followup.send(content=f"```\n{texto_resultados}\n```")

@app_commands.command(name="img", description="Recebe até 2 imagens e marca zonas por colunas")
@app_commands.describe(
    imagem1="Imagem com o topo da qualificação (1 a 14)",
    imagem2="Imagem com o fundo da qualificação (15 a 20)",
    debug="Ativa modo debug para mostrar imagens com boxes marcados"
)
async def img_command(interaction: Interaction, imagem1: discord.Attachment, imagem2: discord.Attachment = None, debug: bool = False):
    await interaction.response.defer()

    image_bytes = await imagem1.read()
    image = Image.open(io.BytesIO(image_bytes))

    largura, altura = image.size
    texto = f"🖈 Resolução: **{largura}x{altura}**\n"

    if largura == 1920 and altura == 1080:
        resultado = await processar_imagem_16_9(image, interaction)
    elif largura == 3440 and altura == 1440:
        resultado = await processar_imagem_21_9(image, interaction, debug)
    else:
        resultado = "❌ Resolução desconhecida ou não suportada."

    if resultado:
        await interaction.followup.send(content=texto + resultado)
