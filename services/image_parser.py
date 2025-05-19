import io
import os
from discord import File
from PIL import Image
from google.cloud import vision

# Definir a chave da Google Vision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "f1-liga-ai-59347f3d41aa.json"

client = vision.ImageAnnotatorClient()

async def processar_1080(image_bytes):
    print("[DEBUG] processar_1080 chamado.")
    return "Imagem no formato 1920x1080 (Full HD)", None


async def processar_1440(image_bytes):
    print("[DEBUG] processar_1440 chamado.")

    try:
        img = Image.open(io.BytesIO(image_bytes))
        print("[DEBUG] imagem original aberta.")

        x, y = 1393, 491
        largura, altura = 1447, 729
        corte = img.crop((x, y, x + largura, y + altura))
        print(f"[DEBUG] corte principal feito em ({x},{y}) → {largura}x{altura}")

        total_linhas = 14
        linhas = cortar_campos_linha_1440(corte, total_linhas)
        print(f"[DEBUG] {len(linhas)} linhas cortadas com sucesso.")

        texto_final = []

        for linha in linhas:
            print(f"[DEBUG] OCR para linha {linha['index']}")

            nome = ocr_imagem(linha["nome"])
            equipa = ocr_imagem(linha["equipa"])
            tempo = ocr_imagem(linha["tempo"])
            gap = ocr_imagem(linha["gap"])

            print(f"[DEBUG] → {nome} | {equipa} | {tempo} | {gap}")

            texto_final.append(f"{linha['index']:<2} {nome:<15} {equipa:<22} {tempo:<8} {gap}")

        mensagem = "Corte 1440p concluído com OCR:\n```markdown\n" + "\n".join(texto_final) + "\n```"
        print("[DEBUG] OCR finalizado com sucesso.")
        return mensagem, None

    except Exception as e:
        print(f"[ERROR] Erro em processar_1440: {e}")
        return "❌ Erro ao processar imagem 1440p", None


# Decide o que fazer conforme resolução
async def analisar_imagem(attachment):
    image_bytes = await attachment.read()
    img = Image.open(io.BytesIO(image_bytes))
    largura, altura = img.size

    if (largura, altura) == (3440, 1440):
        texto, ficheiro = await processar_1440(image_bytes)
        ficheiro = [ficheiro] if ficheiro else []
        return texto, ficheiro
    elif (largura, altura) == (1920, 1080):
        texto, ficheiro = await processar_1080(image_bytes)
    else:
        texto = f"Imagem num formato inesperado: {largura}x{altura}"
        ficheiro = File(io.BytesIO(image_bytes), filename=attachment.filename)

    return f"🖼️ **{attachment.filename}** → {texto}", [ficheiro]

def ocr_imagem(img: Image.Image) -> str:
    try:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        image = vision.Image(content=buffer.read())
        response = client.text_detection(image=image)

        if response.error.message:
            print(f"[ERROR] Vision API: {response.error.message}")
            return ""

        if response.text_annotations:
            texto = response.text_annotations[0].description.strip()
            print(f"[DEBUG] OCR → '{texto}'")
            return texto

        print("[DEBUG] OCR → nenhum texto detectado")
        return ""

    except Exception as e:
        print(f"[ERROR] Erro em ocr_imagem: {e}")
        return ""


# Corta os campos nome/equipa/tempo/gap por linha
def cortar_campos_linha_1440(imagem: Image.Image, total_linhas: int = 2) -> list[dict]:
    linhas = []
    altura_linha = 45
    espacamento = 8

    for i in range(total_linhas):
        y = i * (altura_linha + espacamento)

        linha = {
            "index": i + 1,
            "nome": imagem.crop((0, y, 0 + 332, y + altura_linha)),
            "equipa": imagem.crop((350, y, 350 + 421, y + altura_linha)),  # já ajustado!
            "tempo": imagem.crop((1034, y, 1034 + 239, y + altura_linha)),
            "gap": imagem.crop((1334, y, 1334 + 113, y + altura_linha)),
        }

        linhas.append(linha)

    return linhas