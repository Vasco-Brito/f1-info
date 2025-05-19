import io
import os
from google.cloud import vision

from services.vision_usage import pode_usar_vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "f1-liga-ai-59347f3d41aa.json"
client = vision.ImageAnnotatorClient()

def ocr_imagem(img) -> str:
    try:
        if not pode_usar_vision():
            print("[BLOQUEADO] Limite de uso da API Vision atingido.")
            return "[LIMITADO]"
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
