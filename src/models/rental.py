class Rental:
    def __init__(self, client_id, vehicle_id, location_area, rental_id):
        self.__id = rental_id
        self.__client_id = client_id
        self.__vehicle_id = vehicle_id
        self.__location_area = location_area

    def to_json(self):
        return {
            "id": self.__id,
            "client_id": self.__client_id,
            "vehicle_id": self.__vehicle_id,
            "location_area": self.__location_area,
        }
