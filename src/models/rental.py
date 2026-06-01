class Rental:
    def __init__(self, client_id, vehicle_id, location_area, rental_id, end_date, range_area):
        self.__id = rental_id
        self.__client_id = client_id
        self.__vehicle_id = vehicle_id
        self.__location_area = location_area
        self.__end_date = end_date
        self.__range_area = range_area

    def get_id(self): return self.__id

    def get_client_id(self): return self.__client_id

    def get_vehicle_id(self): return self.__vehicle_id

    def get_location_area(self): return self.__location_area

    def get_end_date(self): return self.__end_date

    def get_range_area(self): return self.__range_area

    def to_json(self):
        return {
            "id": self.__id,
            "client_id": self.__client_id,
            "vehicle_id": self.__vehicle_id,
            "location_area": self.__location_area,
            "end_date": self.__end_date,
            "range_area": self.__range_area
        }
