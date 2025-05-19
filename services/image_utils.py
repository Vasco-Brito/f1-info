from PIL import Image

def cortar_campos_linha_1440(
    imagem: Image.Image,
    total_linhas: int,
    offset_y: int,
    linha_inicial_visual: int
) -> list[dict]:
    linhas = []
    altura_linha = 45
    espacamento = 8

    for i in range(total_linhas):
        y = offset_y + i * (altura_linha + espacamento)
        linha_real = linha_inicial_visual + i

        linha = {
            "index": linha_real,
            "nome": imagem.crop((0, y, 332, y + altura_linha)),
            "equipa": imagem.crop((350, y, 771, y + altura_linha)),
            "tempo": imagem.crop((1034, y, 1273, y + altura_linha)),
            "gap": imagem.crop((1334, y, 1447, y + altura_linha)),
        }

        linhas.append(linha)

    return linhas

def cortar_campos_linha_1080(
    imagem: Image.Image,
    total_linhas: int,
    offset_y: int,
    linha_inicial_visual: int
) -> list[dict]:
    linhas = []
    altura_linha = 36
    espacamento = 4

    for i in range(total_linhas):
        y = offset_y + i * (altura_linha + espacamento)
        linha_real = linha_inicial_visual + i

        linha = {
            "index": linha_real,
            "nome": imagem.crop((0, y, 0 + 251, y + altura_linha)),
            "equipa": imagem.crop((262, y, 262 + 313, y + altura_linha)),
            "tempo": imagem.crop((761, y, 761 + 156, y + altura_linha)),
            "gap": imagem.crop((980, y, 980 + 106, y + altura_linha)),
        }

        linhas.append(linha)

    return linhas
