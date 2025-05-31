class Player:
    def __init__(self):
        self.position: int = 0
        self.tyre_wear = []
        self.tyres = 0
        self.warnings = 0
        self.ERS_mode = -1
        self.ERS_pourcentage = 0
        self.fuelRemainingLaps = 0
        self.fuelMix = 0
        self.numero = 0
        self.teamId = -1
        self.pit: int = 0
        self.FrontLeftWingDamage = 0
        self.FrontRightWingDamage = 0
        self.tyres_temp_inner = [0, 0, 0, 0]
        self.tyres_temp_surface = [0, 0, 0, 0]
        self.tyresAgeLaps = 0
        self.lastLapTime: float = 0
        self.currentSectors = [0] * 3
        self.lastLapSectors = [0] * 3
        self.bestLapSectors = [0] * 3
        self.worldPositionX = 0
        self.worldPositionZ = 0
        self.penalties = 0
        self.driverStatus = 0
        self.bestLapTime = 0
        self.drs: int = 0
        self.yourTelemetry: int = 0
        self.speed: int = 0
        self.rearWingDamage = 0
        self.floorDamage = 0
        self.diffuserDamage = 0
        self.sidepodDamage = 0
        self.name = " "
        self.currentLap = 0
        self.S200_reached = True
        self.currentLapTime = 0
        self.setup_array = []
        self.oval = None
        self.Xmove = 0
        self.Zmove = 0
        self.etiquette = ""
        self.aiControlled = -1
        self.hasRetired = False
        self.speed_trap = 0
        self.delta_to_leader = 0
        self.currentLapInvalid = 1


    def __str__(self):
        return self.name + str(self.position)

    def is_not_on_lap(self):
        return self.currentLapTime == 0 or (self.yourTelemetry==1 and self.ERS_mode == 0) or \
               (self.currentSectors[0] + 1 > self.bestLapSectors[0] != 0) or \
               (self.currentSectors[1] + 1 > self.bestLapSectors[1] != 0)

    def gestion_qualif(self, MnT_team):
        if MnT_team is None:
            return "black"
        else:
            if self.teamId == MnT_team:
                return "blue"
            else:
                return "green" if self.is_not_on_lap() else "red"


