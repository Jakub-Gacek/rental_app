import uuid

class Vehicle:
    def __init__(self, brand, model, year, vin, vehicle_id=None):
        self.__brand = brand
        self.__model = model
        self.__year = year
        self.__vin = vin
        self.__id = vehicle_id if vehicle_id is not None else str(uuid.uuid4())[:8]

    def get_id(self): return self.__id
    def get_brand(self): return self.__brand
    def get_model(self): return self.__model
    def get_year(self): return self.__year
    def get_vin(self): return self.__vin

    def to_json(self):
        return {
            "brand": self.__brand,
            "model": self.__model,
            "year": self.__year,
            "vin": self.__vin,
            "id": self.__id
        }