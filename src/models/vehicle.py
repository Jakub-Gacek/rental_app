class Vehicle:
    def __init__(self, brand, model, plate, vin, mileage, status, vehicle_id):
        self.__brand = brand
        self.__model = model
        self.__plate = plate
        self.__vin = vin
        self.__mileage = mileage
        self.__status = status
        self.__vehicle_id = vehicle_id

    def get_info(self):
        return f"{self.__brand} {self.__model} [{self.__plate}]"

    def to_json(self):
        return {
            "brand": self.__brand,
            "model": self.__model,
            "plate": self.__plate,
            "vin": self.__vin,
            "mileage": self.__mileage,
            "status": self.__status,
            "vehicle_id": self.__vehicle_id
        }
