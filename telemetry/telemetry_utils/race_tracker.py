"""
race_tracker.py

Responsável por registar os dados completos de cada corrida da liga, incluindo:
- Resultados finais
- Penalizações e avisos
- Voltas lideradas
- Detalhes por volta (quem liderou qual)

Usado em conjunto com os dados captados via UDP no parser2024.py.
"""

import json
import os
from datetime import datetime
from collections import defaultdict

class RaceTracker:
    def __init__(self, nome_corrida: str):
        self.nome_corrida = nome_corrida
        self.data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.resultado_final = []
        self.voltas_lideradas = defaultdict(int)
        self.detalhes_voltas = []
        self._lider_volta_atual = None
        self._volta_atual = 1

    def registrar_lider_volta(self, piloto: str, volta: int):
        if volta != self._volta_atual:
            # Nova volta começou, regista o líder da anterior
            self.detalhes_voltas.append({
                "volta": self._volta_atual,
                "lider": self._lider_volta_atual
            })
            self._volta_atual = volta
        self._lider_volta_atual = piloto
        self.voltas_lideradas[piloto] += 1

    def registrar_resultados_finais(self, lista_resultados: list):
        """
        lista_resultados: lista de dicionários com:
        { "nick": str, "pos": int, "penalizacao": int, "avisos": int }
        """
        self.resultado_final = lista_resultados

    def end_race_tracking(self):
        # Registar a última volta
        if self._lider_volta_atual:
            self.detalhes_voltas.append({
                "volta": self._volta_atual,
                "lider": self._lider_volta_atual
            })

        dados = {
            "data": self.data,
            "nome_corrida": self.nome_corrida,
            "resultado_final": self.resultado_final,
            "voltas_lideradas": dict(self.voltas_lideradas),
            "detalhes_voltas": self.detalhes_voltas
        }

        nome_ficheiro = f"corrida_{self.data.replace(':', '-').replace(' ', '_')}.json"
        path = os.path.join("corridas", nome_ficheiro)
        os.makedirs("corridas", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        print(f"Corrida guardada em {path}")
