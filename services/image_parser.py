import io
from discord import File
from PIL import Image
from services.image_utils import cortar_campos_linha_1440, cortar_campos_linha_1080
from services.ocr import ocr_imagem
from services.vision_usage import registar_pedido


async def processar_1440(image_bytes, total_linhas, offset_y, linha_inicial_visual, debug=False):
    print("[DEBUG] processar_1440 chamado.")

    try:
        img = Image.open(io.BytesIO(image_bytes))
        print("[DEBUG] imagem original aberta.")

        # Corte da tabela
        x, y = 1393, 491
        largura, altura = 1447, 729
        corte = img.crop((x, y, x + largura, y + altura))
        print(f"[DEBUG] corte principal feito em ({x},{y}) → {largura}x{altura}")

        if debug:
            print(f"[DEBUG] Modo DEBUG → linha inicial visual: {linha_inicial_visual}")
            arquivos = []

            # Enviar a imagem da tabela
            buffer_corte = io.BytesIO()
            corte.save(buffer_corte, format="PNG")
            buffer_corte.seek(0)
            arquivos.append(File(buffer_corte, filename="tabela_corte.png"))

            # Cortar e enviar 2 linhas
            linhas_debug = cortar_campos_linha_1440(
                corte, total_linhas=2,
                offset_y=offset_y,
                linha_inicial_visual=linha_inicial_visual
            )

            for linha in linhas_debug:
                for campo in ["nome", "equipa", "tempo", "gap"]:
                    buffer = io.BytesIO()
                    linha[campo].save(buffer, format="PNG")
                    buffer.seek(0)
                    arquivos.append(File(buffer, filename=f"linha{linha['index']}_{campo}.png"))

            return f"Modo DEBUG — Linhas {linha_inicial_visual}-{linha_inicial_visual + 1}", arquivos

        if total_linhas == 0:
            print("[DEBUG] total_linhas = 0 → OCR desativado.")
            return "OCR desativado (total_linhas = 0)", None

        # OCR real
        linhas = cortar_campos_linha_1440(
            corte,
            total_linhas=total_linhas,
            offset_y=offset_y,
            linha_inicial_visual=linha_inicial_visual
        )

        print(f"[DEBUG] {len(linhas)} linhas cortadas (iniciando OCR)")

        texto_final = []

        for linha in linhas:
            print(f"[DEBUG] OCR linha {linha['index']}")
            nome = ocr_imagem(linha["nome"])
            equipa = ocr_imagem(linha["equipa"])
            tempo = ocr_imagem(linha["tempo"])
            gap = ocr_imagem(linha["gap"])

            texto_final.append(f"{linha['index']:<2} {nome:<15} {equipa:<22} {tempo:<8} {gap}")

        registar_pedido(len(linhas*4))
        mensagem = "OCR completo:\n```markdown\n" + "\n".join(texto_final) + "\n```"
        return mensagem, None

    except Exception as e:
        print(f"[ERROR] Erro em processar_1440: {e}")
        return "❌ Erro ao processar imagem 1440p", None

async def processar_1080(image_bytes, total_linhas, offset_y, linha_inicial_visual, debug=False):
    print("[DEBUG] processar_1080 chamado.")

    try:
        img = Image.open(io.BytesIO(image_bytes))
        print("[DEBUG] imagem original aberta.")

        # Corte da tabela
        x, y = 714, 366
        largura, altura = 1086, 550
        corte = img.crop((x, y, x + largura, y + altura))
        print(f"[DEBUG] corte principal feito em ({x},{y}) → {largura}x{altura}")

        if debug:
            print(f"[DEBUG] Modo DEBUG → linha inicial visual: {linha_inicial_visual}")
            arquivos = []

            # Enviar a imagem da tabela
            buffer_corte = io.BytesIO()
            corte.save(buffer_corte, format="PNG")
            buffer_corte.seek(0)
            arquivos.append(File(buffer_corte, filename="tabela_corte.png"))

            # Cortar e enviar 2 linhas
            linhas_debug = cortar_campos_linha_1080(
                corte, total_linhas=2,
                offset_y=offset_y,
                linha_inicial_visual=linha_inicial_visual
            )

            for linha in linhas_debug:
                for campo in ["nome", "equipa", "tempo", "gap"]:
                    buffer = io.BytesIO()
                    linha[campo].save(buffer, format="PNG")
                    buffer.seek(0)
                    arquivos.append(File(buffer, filename=f"linha{linha['index']}_{campo}.png"))

            return f"Modo DEBUG — Linhas {linha_inicial_visual}-{linha_inicial_visual + 1}", arquivos

        if total_linhas == 0:
            print("[DEBUG] total_linhas = 0 → OCR desativado.")
            return "OCR desativado (total_linhas = 0)", None

        # OCR real
        linhas = cortar_campos_linha_1080(
            corte,
            total_linhas=total_linhas,
            offset_y=offset_y,
            linha_inicial_visual=linha_inicial_visual
        )

        print(f"[DEBUG] {len(linhas)} linhas cortadas (iniciando OCR)")

        texto_final = []

        for linha in linhas:
            print(f"[DEBUG] OCR linha {linha['index']}")
            nome = ocr_imagem(linha["nome"])
            equipa = ocr_imagem(linha["equipa"])
            tempo = ocr_imagem(linha["tempo"])
            gap = ocr_imagem(linha["gap"])

            texto_final.append(f"{linha['index']:<2} {nome:<15} {equipa:<22} {tempo:<8} {gap}")

        registar_pedido(len(linhas*4))
        mensagem = "OCR completo:\n```markdown\n" + "\n".join(texto_final) + "\n```"
        return mensagem, None

    except Exception as e:
        print(f"[ERROR] Erro em processar_1440: {e}")
        return "❌ Erro ao processar imagem 1440p", None

async def analisar_imagem(attachment, total_linhas, offset_y, linha_inicial_visual, debug=False):
    image_bytes = await attachment.read()
    img = Image.open(io.BytesIO(image_bytes))
    largura, altura = img.size

    if (largura, altura) == (3440, 1440):
        return await processar_1440(image_bytes, total_linhas, offset_y, linha_inicial_visual, debug)
    if (largura, altura) == (1920, 1080):
        return await processar_1080(image_bytes, total_linhas, offset_y, linha_inicial_visual, debug)

    return "❌ Resolução inválida ou não suportada", []
