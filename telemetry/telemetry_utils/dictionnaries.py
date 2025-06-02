import datetime

def rgbtohex(r,g,b):
    return f'#{r:02x}{g:02x}{b:02x}'

def valid_ip_address(adress):
    s = adress.split(".")
    drapeau = len(s)==4
    for element in s:
        if not (element.isdigit() and 0<=int(element)<=255):
            drapeau = False
    return drapeau

black = "#000000"
white = "#FFFFFF"
green = "#00FF00"
blue = "#0000FF"
yellow = "#FFD700"
red = "#FF0000"
purple = "#880088"
gold = "#FFD700"
grey = "#4B4B4B"


tyres_dictionnary = {
    0:"S",
    16: "S",
    17: "M",
    18: "H",
    7: "I",
    8: "W"
}

tyres_color_dictionnary = {
    0:"#FF0000",
    16: "#FF0000",
    17: "#FFD700",
    18: "#FFFFFF",
    7: "#00FF00",
    8: "#0000FF"
}

track_dictionary = { #(track name, highNumber=Small on canvas, x_offset, y_offset)
    0: ("melbourne", 3.5, 300, 300),
    1: ("paul_ricard", 2.5, 500, 300),
    2: ("shanghai", 2, 300, 300),
    3: ("sakhir", 2, 600, 350),
    4: ("catalunya", 2.5, 400, 300),
    5: ("monaco", 2, 300, 300),
    6: ("montreal", 3, 300, 100),
    7: ("silverstone", 3.5, 400, 250),
    8: ("hockenheim", 2, 300, 300),
    9: ("hungaroring", 2.5, 400, 300),
    10: ("spa", 3.5, 500, 350),
    11: ("monza", 4, 400, 300),
    12: ("singapore", 2, 400, 300),
    13: ("suzuka", 2.5, 500, 300),
    14: ("abu_dhabi", 2, 500, 250),
    15: ("texas", 2, 400, 50),
    16: ("brazil", 2, 600, 250),
    17: ("austria", 2, 300, 300),
    18: ("sochi", 2, 300, 300),
    19: ("mexico", 2.5, 500, 500),
    20: ("baku", 3, 400,400),
    21: ("sakhir_short", 2, 300, 300),
    22: ("silverstone_short", 2, 300, 300),
    23: ("texas_short", 2, 300, 300),
    24: ("suzuka_short", 2, 300, 300),
    25: ("hanoi", 2, 300, 300),
    26: ("zandvoort", 2, 500, 300),
    27: ("imola", 2, 500, 300),
    28: ("portimao", 2, 300, 300),
    29: ("jeddah", 4,500, 350),
    30:("Miami", 2,400,300),
    31:("Las Vegas", 4,400, 300),
    32:("Losail", 2.5,400,300)
}

teams_color_dictionary = {
    -1: "#FFFFFF",
    0: "#00C7CD",
    1: "#FF0000",
    2: "#0000FF",
    3: "#5097FF",
    4: "#00902A",
    5: "#009BFF",
    6: "#00446F",
    7: "#95ACBB",
    8: "#FFAE00",
    9: "#980404",
    41:"#000000",
    104: "#670498",
    255: "#670498"
}

teams_name_dictionary = {
    -1: "Unknown",
    0: "Mercedes",
    1: "Ferrari",
    2: "Red Bull",
    3: "Williams",
    4: "Aston Martin",
    5: "Alpine",
    6: "Alpha Tauri",
    7: "Haas",
    8: "McLaren",
    9: "Alfa Romeo",
    41:"Multi"
}

weather_dictionary = {
    0: "Dégagé",
    1: "Légèrement nuageux",
    2: "Couvert",
    3: "Pluie fine",
    4: "Pluie forte",
    5: "Tempête"
}

fuel_dict = {
    0: "Lean",
    1: "Standard",
    2: "Rich",
    3: "Max"
}

pit_dictionary = {
    0: "",
    1: "PIT",
    2: "PIT"
}

ERS_dictionary = {
    0: "NONE",
    1: "MEDIUM",
    2: "HOTLAP",
    3: "OVERTAKE",
    -1: "PRIVÉE"
}

SESSION_TYPES = {
    0: {"nome": "Desconhecida", "abreviado": "?"},  # ou "" se preferires
    1: {"nome": "Prática 1", "abreviado": "FP1"},
    2: {"nome": "Prática 2", "abreviado": "FP2"},
    3: {"nome": "Prática 3", "abreviado": "FP3"},
    4: {"nome": "Prática curta", "abreviado": "FP"},
    5: {"nome": "Qualificação 1", "abreviado": "Q1"},
    6: {"nome": "Qualificação 2", "abreviado": "Q2"},
    7: {"nome": "Qualificação 3", "abreviado": "Q3"},
    8: {"nome": "Qualificação curta", "abreviado": "Short Qualy"},
    9: {"nome": "Qualificação One-Shot", "abreviado": "OSQ"},
    10: {"nome": "Sprint Shootout 1", "abreviado": "SSO1"},
    11: {"nome": "Sprint Shootout 2", "abreviado": "SSO2"},
    12: {"nome": "Sprint Shootout 3", "abreviado": "SSO3"},
    13: {"nome": "Sprint Shootout curta", "abreviado": "Short SSO"},
    14: {"nome": "Sprint Shootout One-Shot", "abreviado": "SSO OS"},
    15: {"nome": "Corrida principal", "abreviado": "Race"},
    16: {"nome": "Corrida 2", "abreviado": "Race 2"},
    17: {"nome": "Corrida 3", "abreviado": "Race 3"},
    18: {"nome": "Time Trial", "abreviado": "TT"},
}


color_flag_dict = {
    0: white, 1: green, 2: blue, 3: yellow, 4: red
}

DRS_dict = {0: "", 1: "DRS"}

WeatherForecastAccuracy = {
    -1: "Unknown",
    0: "Parfaite",
    1: "Approximative"
}

packetDictionnary = {
    0:"MotionPacket",
    1:"SessionPacket",
    2:"LapDataPacket",
    3:"EventPacket",
    4:"ParticipantsPacket",
    5:"CarSetupPacket",
    6:"CarTelemetryPacket",
    7:"CarStatusPacket",
    8:"FinalClassificationPacket",
    9:"LobbyInfoPacket",
    10:"CarDamagePacket",
    11:"SessionHistoryPacket",
    12:"TyreSets",
    13:"MotionEx",
    14:"Time Trial"

}

safetyCarStatusDict = {
    0:"",
    1:"SC",
    2:"VSC",
    3:"FL",
    4:""
}

PENALTY_TYPES = {
    0: "Drive through",
    1: "Stop Go",
    2: "Grid penalty",
    3: "Penalty reminder",
    4: "Time penalty",
    5: "Warning",
    6: "Disqualified",
    7: "Removed from formation lap",
    8: "Parked too long timer",
    9: "Tyre regulations",
    10: "This lap invalidated",
    11: "This and next lap invalidated",
    12: "This lap invalidated without reason",
    13: "This and next lap invalidated without reason",
    14: "This and previous lap invalidated",
    15: "This and previous lap invalidated without reason",
    16: "Retired",
    17: "Black flag timer"
}

INFRINGEMENT_TYPES = {
    0: "Blocking by slow driving",
    1: "Blocking by wrong way driving",
    2: "Reversing off the start line",
    3: "Big Collision",
    4: "Small Collision",
    5: "Collision failed to hand back position single",
    6: "Collision failed to hand back position multiple",
    7: "Corner cutting gained time",
    8: "Corner cutting overtake single",
    9: "Corner cutting overtake multiple",
    10: "Crossed pit exit lane",
    11: "Ignoring blue flags",
    12: "Ignoring yellow flags",
    13: "Ignoring drive through",
    14: "Too many drive throughs",
    15: "Drive through reminder serve within n laps",
    16: "Drive through reminder serve this lap",
    17: "Pit lane speeding",
    18: "Parked for too long",
    19: "Ignoring tyre regulations",
    20: "Too many penalties",
    21: "Multiple warnings",
    22: "Approaching disqualification",
    23: "Tyre regulations select single",
    24: "Tyre regulations select multiple",
    25: "Lap invalidated corner cutting",
    26: "Lap invalidated running wide",
    27: "Corner cutting ran wide gained time minor",
    28: "Corner cutting ran wide gained time significant",
    29: "Corner cutting ran wide gained time extreme",
    30: "Lap invalidated wall riding",
    31: "Lap invalidated flashback used",
    32: "Lap invalidated reset to track",
    33: "Blocking the pitlane",
    34: "Jump start",
    35: "Safety car to car collision",
    36: "Safety car illegal overtake",
    37: "Safety car exceeding allowed pace",
    38: "Virtual safety car exceeding allowed pace",
    39: "Formation lap below allowed speed",
    40: "Formation lap parking",
    41: "Retired mechanical failure",
    42: "Retired terminally damaged",
    43: "Safety car falling too far back",
    44: "Black flag timer",
    45: "Unserved stop go penalty",
    46: "Unserved drive through penalty",
    47: "Engine component change",
    48: "Gearbox change",
    49: "Parc Fermé change",
    50: "League grid penalty",
    51: "Retry penalty",
    52: "Illegal time gain",
    53: "Mandatory pitstop",
    54: "Attribute assigned"
}

event_code_dict = {
    "SSTA": "Sessão iniciada",
    "SEND": "Sessão terminada",
    "FTLP": "Fastest lap",
    "RTMT": "DNF",
    "DRSE": "DRS ativado",
    "DRSD": "DRS desativado",
    "TMPT": "Colega de equipa entrou na box",
    "CHQF": "Bandeira de xadrez",
    "RCWN": "Vencedor anunciado",
    "PENA": "Penalização",
    "SPTP": "Speed trap",
    "STLG": "Semáforo aceso",
    "LGOT": "Luzes apagadas",
    "DTSV": "Drive-through cumprido",
    "SGSV": "Stop-go cumprido",
    "FLBK": "Flashback",
    "BUTN": "Botão pressionado",
    "RDFL": "Bandeira vermelha",
    "OVTK": "Ultrapassagem",
    "SCAR": "Safety car",
    "COLL": "Colisão"
}


def conversion(millis, mode):  # mode 1 = titre, mode 2 = last lap
    if mode == 1:
        texte = str(datetime.timedelta(seconds=millis))
        liste = texte.split(":")
        return f"{liste[1]} min {liste[2]}s"
    elif mode == 2:
        seconds, millis = millis // 1000, millis%1000
        minutes, seconds = seconds // 60, seconds%60
        if (minutes!=0 or seconds!=0 or millis!=0) and (minutes>=0 and seconds<10):
            seconds = "0"+str(seconds)

        if millis//10 == 0:
            millis="00"+str(millis)
        elif millis//100 == 0:
            millis="0"+str(millis)
        
        if minutes != 0:
            return f"{minutes}:{seconds}.{millis}"
        else:
            return f"{seconds}.{millis}"



def file_len(fname):
    with open(fname) as file:
        for i, l in enumerate(file):
            pass
    return i + 1


def string_code(packet):
    string = ""
    for i in range(4):
        string += packet.m_event_string_code[i]
    return string

def get_nome_sessao(session_type: int) -> str:
    return SESSION_TYPES.get(session_type, {}).get("nome", f"Desconhecida ({session_type})")

def get_nome_abreviado(session_type: int) -> str:
    return SESSION_TYPES.get(session_type, {}).get("abreviado", f"? ({session_type})")

def convert_tempo(segundos: float) -> str:
    minutos = int(segundos // 60)
    resto_segundos = segundos % 60
    return f"{minutos}:{resto_segundos:06.3f}" if minutos > 0 else f"{resto_segundos:.3f}"