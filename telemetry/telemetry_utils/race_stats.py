# telemetry_utils/race_stats.py

from collections import defaultdict

# Armazenamento interno
_stats = {
    "max_speed": defaultdict(float),
    "compostos": defaultdict(set),
    "pitstops": defaultdict(list),
    "ultima_volta_vista": {},
    "pit_status": {},
}


def start_stats_tracking():
    global _stats
    _stats = {
        "max_speed": defaultdict(float),
        "compostos": defaultdict(set),
        "pitstops": defaultdict(list),
        "ultima_volta_vista": {},
        "pit_status": {},
    }


def process_speedtrap(packet):
    idx = packet.m_vehicle_idx
    velocidade = packet.m_speed
    if velocidade > _stats["max_speed"][idx]:
        _stats["max_speed"][idx] = round(velocidade, 2)


def process_lap_and_status_data(lap_data, status_data):
    for idx in range(22):
        lap = lap_data[idx]
        status = status_data[idx]

        composto = status.m_actual_tyre_compound
        _stats["compostos"][idx].add(composto)

        volta_atual = lap.m_current_lap_num
        estado_pit = lap.m_pit_status  # 0=none, 1=pitting, 2=em pit lane
        ultima_volta = _stats["ultima_volta_vista"].get(idx, -1)
        em_pit_antes = _stats["pit_status"].get(idx, 0)

        # Registo do pitstop só quando transita de "pitting/pitlane" para "none"
        if em_pit_antes in (1, 2) and estado_pit == 0:
            tempo_total = round(lap.m_pit_lane_time_in_lane_in_ms / 1000.0, 3)
            tempo_parado = round(lap.m_pit_stop_timer_in_ms / 1000.0, 3)

            _stats["pitstops"][idx].append({
                "volta": volta_atual,
                "tempo_total": tempo_total,
                "tempo_parado": tempo_parado,
                "composto_saida": status.m_actual_tyre_compound
            })

        _stats["ultima_volta_vista"][idx] = volta_atual
        _stats["pit_status"][idx] = estado_pit


def anexar_stats_a_resultado(resultado):
    final = []
    for piloto in resultado:
        idx = piloto.get("idx", -1)

        final.append({
            **piloto,
            "velocidade_maxima": _stats["max_speed"].get(idx, 0.0),
            "compostos_usados": list(sorted(_stats["compostos"].get(idx, []))),
            "pitstops": _stats["pitstops"].get(idx, [])
        })

    return final



# # Esta função deve ser adaptada ao teu sistema de nomes
# def _encontrar_idx_por_nome(nome):
#     from telemetry.telemetry_utils.packet_management import LISTE_JOUEURS
#     for i, j in enumerate(LISTE_JOUEURS):
#         if j.name == nome:
#             return i
#     return -1
