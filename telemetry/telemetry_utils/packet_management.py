from telemetry.telemetry_utils.Session import Session
from telemetry.telemetry_utils.Player import Player
from telemetry.telemetry_utils.dictionnaries import *
import time

LISTE_JOUEURS: list[Player] = [Player() for _ in range(22)]
session: Session = Session()


def update_lap_data(packet):  # Packet 2
    mega_array = packet.m_lap_data
    for index in range(22):
        element = mega_array[index]
        joueur = LISTE_JOUEURS[index]
        joueur.position = element.m_car_position
        joueur.lastLapTime = round(element.m_last_lap_time_in_ms, 3)
        joueur.pit = element.m_pit_status
        joueur.driverStatus = element.m_driver_status
        joueur.currentLap = element.m_current_lap_num
        joueur.penalties = element.m_penalties
        joueur.warnings = element.m_corner_cutting_warnings
        joueur.currentLap = element.m_current_lap_num
        joueur.speed_trap = round(element.m_speedTrapFastestSpeed, 2)
        joueur.currentLapTime = element.m_current_lap_time_in_ms
        joueur.delta_to_leader = element.m_deltaToCarInFrontMSPart
        joueur.currentLapInvalid = element.m_current_lap_invalid

        if element.m_sector1_time_in_ms == 0 and joueur.currentSectors[0] != 0:
            joueur.lastLapSectors = joueur.currentSectors[:]
            joueur.lastLapSectors[2] = joueur.lastLapTime / 1_000 - joueur.lastLapSectors[0] - joueur.lastLapSectors[1]

        joueur.currentSectors = [
            element.m_sector1_time_in_ms / 1000,
            element.m_sector2_time_in_ms / 1000,
            0
        ]

        if joueur.bestLapTime > element.m_last_lap_time_in_ms != 0 or joueur.bestLapTime == 0:
            joueur.bestLapTime = element.m_last_lap_time_in_ms
            joueur.bestSectors = joueur.lastLapSectors[:]

        if joueur.bestLapTime < session.bestLapTime and element.m_last_lap_time_in_ms != 0 or joueur.bestLapTime == 0:
            session.bestLapTime = joueur.bestLapTime
            session.idxBestLapTime = index

        if element.m_car_position == 1:
            session.currentLap = mega_array[index].m_current_lap_num
            session.tour_precedent = session.currentLap - 1


def warnings(packet):  # Packet 3
    if packet.m_event_string_code[3] == 71 and packet.m_event_details.m_start_lights.m_num_lights >= 2:
        session.formationLapDone = True
        print(f"{packet.m_event_details.m_start_lights.m_num_lights} red lights")
    elif packet.m_event_string_code[0] == 76 and session.formationLapDone:
        print("Lights out!")
        session.formationLapDone = False
        session.startTime = time.time()
        for joueur in LISTE_JOUEURS:
            joueur.S200_reached = False
            joueur.warnings = 0
            joueur.lastLapSectors = [0] * 3
            joueur.bestSectors = [0] * 3
            joueur.lastLapTime = 0
            joueur.currentSectors = [0] * 3
            joueur.bestLapTime = 0
    elif packet.m_event_string_code[2] == 82:
        LISTE_JOUEURS[packet.m_event_details.m_vehicle_idx].hasRetired = True


def update_participants(packet):  # Packet 4
    for index in range(22):
        element = packet.m_participants[index]
        joueur = LISTE_JOUEURS[index]
        joueur.numero = element.m_race_number
        joueur.teamId = element.m_team_id
        joueur.aiControlled = element.m_ai_controlled
        joueur.yourTelemetry = element.m_your_telemetry
        try:
            joueur.name = element.m_name.decode("utf-8")
        except:
            joueur.name = element.m_name
        session.nb_players = packet.m_num_active_cars
        if joueur.name in ['Player', 'Joueur']:
            joueur.name = teams_name_dictionary[joueur.teamId] + "#" + str(joueur.numero)


def update_car_telemetry(packet):  # Packet 6
    for index in range(22):
        element = packet.m_car_telemetry_data[index]
        joueur = LISTE_JOUEURS[index]
        joueur.drs = element.m_drs
        joueur.tyres_temp_inner = element.m_tyres_inner_temperature
        joueur.tyres_temp_surface = element.m_tyres_surface_temperature
        joueur.speed = element.m_speed
        if joueur.speed >= 200 and not joueur.S200_reached:
            print(f"{joueur.position} {joueur.name} = {time.time() - session.startTime}")
            joueur.S200_reached = True


def update_car_status(packet):  # Packet 7
    for index in range(22):
        element = packet.m_car_status_data[index]
        joueur = LISTE_JOUEURS[index]
        joueur.fuelMix = element.m_fuel_mix
        joueur.fuelRemainingLaps = element.m_fuel_remaining_laps
        joueur.tyresAgeLaps = element.m_tyres_age_laps
        if joueur.tyres != element.m_visual_tyre_compound:
            joueur.tyres = element.m_visual_tyre_compound
        joueur.ERS_mode = element.m_ers_deploy_mode
        joueur.ERS_pourcentage = round(element.m_ers_store_energy / 40_000)


def update_car_damage(packet):  # Packet 10
    for index in range(22):
        element = packet.m_car_damage_data[index]
        joueur = LISTE_JOUEURS[index]
        joueur.tyre_wear = '[' + ', '.join('%.2f' % w for w in element.m_tyres_wear) + ']'
        joueur.FrontLeftWingDamage = element.m_front_left_wing_damage
        joueur.FrontRightWingDamage = element.m_front_right_wing_damage
        joueur.rearWingDamage = element.m_rear_wing_damage
        joueur.floorDamage = element.m_floor_damage
        joueur.diffuserDamage = element.m_diffuser_damage
        joueur.sidepodDamage = element.m_sidepod_damage


def nothing(packet):  # Packet 8, 9, 11, 12, 13
    pass