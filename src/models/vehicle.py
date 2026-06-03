import uuid

from src.models.vehicle_status import VehicleStatus


class Vehicle:
    def __init__(self, brand, model, plate, mileage, vin, vehicle_id=None, status=VehicleStatus.AVAILABLE):
        self.__brand = brand
        self.__model = model
        self.__plate = plate
        self.__mileage = mileage
        self.__vin = vin
        self.__id = vehicle_id if vehicle_id else str(uuid.uuid4())[:8]
        self.__status = status

    def get_id(self): return self.__id

    def get_brand(self): return self.__brand

    def get_model(self): return self.__model

    def get_plate(self): return self.__plate

    def get_vin(self): return self.__vin

    def get_status(self): return self.__status.value

    def get_mileage(self): return self.__mileage

    def to_json(self):
        return {
            "brand": self.__brand,
            "model": self.__model,
            "plate": self.__plate,
            "status": self.__status.value,
            "mileage": self.__mileage,
            "vin": self.__vin,
            "id": self.__id
        }
