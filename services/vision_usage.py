import json
import os
from datetime import datetime

USO_PATH = "jsons/vision_usage.json"
LIMITE_MENSAL = 1000

def carregar_uso():
    os.makedirs(os.path.dirname(USO_PATH), exist_ok=True)
    if not os.path.exists(USO_PATH):
        return {}
    with open(USO_PATH, "r") as f:
        return json.load(f)


def guardar_uso(dados):
    with open(USO_PATH, "w") as f:
        json.dump(dados, f, indent=2)

def registar_pedido(qtd=1):
    hoje = datetime.now().strftime("%Y-%m")
    dados = carregar_uso()
    dados[hoje] = dados.get(hoje, 0) + qtd
    guardar_uso(dados)

def pode_usar_vision(qtd=1):
    hoje = datetime.now().strftime("%Y-%m")
    dados = carregar_uso()
    return dados.get(hoje, 0) + qtd <= LIMITE_MENSAL

def uso_atual():
    hoje = datetime.now().strftime("%Y-%m")
    dados = carregar_uso()
    return dados.get(hoje, 0)
