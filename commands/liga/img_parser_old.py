from discord import app_commands, Interaction
import discord
import os
import re
from google.cloud import vision
from collections import defaultdict

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "f1-liga-ai-59347f3d41aa.json"

@app_commands.command(name="img", description="Extrai texto de imagens com OCR estruturado (qualificacao)")
@app_commands.describe(
    imagem1="Imagem da qualificacao",
    imagem2="(Opcional) Outra imagem",
    debug="Mostrar texto agrupado por linha (modo debug)"
)
async def img_command(
    interaction: Interaction,
    imagem1: discord.Attachment,
    imagem2: discord.Attachment = None,
    debug: bool = False
):
    await interaction.response.defer()
    client = vision.ImageAnnotatorClient()

    async def processar_imagem(attachment: discord.Attachment):
        image_bytes = await attachment.read()
        image = vision.Image(content=image_bytes)
        response = client.document_text_detection(image=image)
        annotation = response.full_text_annotation

        linhas_y = defaultdict(list)
        y_list = []

        for page in annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        text = "".join([s.text for s in word.symbols])
                        y = word.bounding_box.vertices[0].y
                        x = word.bounding_box.vertices[0].x
                        y_key = round(y / 10)
                        linhas_y[y_key].append((x, text))
                        y_list.append(y)

        y_list = sorted(set(y_list))
        deltas = [y_list[i+1] - y_list[i] for i in range(len(y_list)-1)]
        media_dy = sum(deltas) / len(deltas) if deltas else 0

        linhas_reconstruidas = []
        for y_key in sorted(linhas_y):
            palavras_ordenadas = sorted(linhas_y[y_key], key=lambda p: p[0])
            linha = " ".join([p for _, p in palavras_ordenadas]).strip()
            linha = linha.replace("Al ", "AI ")
            linha = re.sub(r"(\d)\s*:\s*(\d+)", r"\1:\2", linha)
            linha = re.sub(r'\b[ISMWHE]\b', '', linha)
            lixo = ["ROLE", "米", "NM", "ATAR", "ROLEX", "LICENCE", "PROFILE"]
            if any(l in linha.upper() for l in lixo):
                continue
            linha = re.sub(r'\s{2,}', ' ', linha).strip()
            linhas_reconstruidas.append(linha)

        if debug:
            texto_debug = f"\U0001F4C4 **{attachment.filename} - DEBUG**\n"
            texto_debug += f"\U0001F4CF Espa\u00e7amento m\u00e9dio entre linhas (Y): `{media_dy:.2f}` px\n"
            texto_debug += "```text\n" + "\n".join(linhas_reconstruidas) + "\n```"
            return texto_debug

        # Lógica melhorada para juntar linhas quebradas com tempo e gap
        linhas_final = []
        i = 0

        while i < len(linhas_reconstruidas):
            atual = linhas_reconstruidas[i]
            prox = linhas_reconstruidas[i+1] if i+1 < len(linhas_reconstruidas) else ""
            prox2 = linhas_reconstruidas[i+2] if i+2 < len(linhas_reconstruidas) else ""

            tempo_regex = re.match(r"^(?:\d+:)?\d+\.\d+$", atual)
            gap_regex = re.match(r"^\+\d+\.\d+$", atual)
            tempo_gap_regex = re.match(r"^(?:\d+:)?\d+\.\d+\s+\+\d+\.\d+$", atual)

            # Ex: linha com nome, depois tempo, depois gap → junta tudo
            if tempo_regex and gap_regex and i >= 1:
                linhas_final[-1] += " " + atual + " " + prox
                i += 2
                continue

            # Ex: linha com nome, depois tempo+gap → junta
            if tempo_gap_regex and i >= 1:
                linhas_final[-1] += " " + atual
                i += 1
                continue

            # Ex: linha com tempo, gap vem depois (do Yuki)
            if tempo_regex and re.match(r"^\+\d+\.\d+$", prox):
                if i >= 1:
                    linhas_final[-1] += " " + atual + " " + prox
                    i += 2
                    continue

            # Ex: gap sozinho depois da linha certa (fallback)
            if gap_regex:
                if i+1 < len(linhas_reconstruidas):
                    linhas_reconstruidas[i+1] += " " + atual
                else:
                    linhas_final.append(atual)
                i += 1
                continue

            linhas_final.append(atual)
            i += 1

        regex = re.compile(
            r"(\d+)\s+([A-Z]?[A-Za-z0-9\-\. ]+?)\s+([A-Z][A-Za-z0-9\s\-\&\|]+?)\s+((?:\d+:)?\d+\.\d+|DNF)(?:\s+(\+\d+\.\d+))?"
        )
        tabela = [f"{'POS':<3} {'Piloto':<15} {'Equipa':<22} {'Tempo':<8} {'Gap'}"]

        for linha in linhas_final:
            match = regex.match(linha)
            if match:
                pos, nome, equipa, tempo, gap = match.groups()
                gap = gap or "-"
                tabela.append(f"{pos:<3} {nome:<15} {equipa:<22} {tempo:<8} {gap}")

        if len(tabela) == 1:
            return f"⚠️ Não consegui formatar `{attachment.filename}`\nTenta com `debug=True` para ver o texto cru."

        return f"🖼️ **{attachment.filename}**\n```markdown\n" + "\n".join(tabela) + "\n```"

    resultados = [await processar_imagem(imagem1)]
    if imagem2:
        resultados.append(await processar_imagem(imagem2))

    await interaction.followup.send("\n\n".join(resultados))
