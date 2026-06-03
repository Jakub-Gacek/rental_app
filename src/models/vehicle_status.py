from enum import Enum

class VehicleStatus(Enum):
    AVAILABLE = "Dostępny"
    UNAVAILABLE = "Wypożyczony"
    SERVICE = "Serwis"