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

session_dictionary = {
    5: "Q1",
    6: "Q2",
    7: "Q3",
    8: "Short qualy",
    15: "Race"

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