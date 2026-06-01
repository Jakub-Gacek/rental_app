import json
import os
from src.database.database import Database
from src.models.client import Client
from src.models.vehicle import Vehicle
from src.models.rental import Rental


class JSONDatabase(Database):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, file_path="data/database.json"):
        if not hasattr(self, '_initialized'):
            self.__file_path = file_path
            self._data_cache = None

            os.makedirs(os.path.dirname(self.__file_path), exist_ok=True)

            self.load_all()

            self._initialized = True

    def load_all(self):
        if not os.path.exists(self.__file_path):
            self.__data_cache = {"clients": [], "vehicles": [], "rentals": []}
        else:
            try:
                with open(self.__file_path, 'r', encoding='utf-8') as f:
                    self.__data_cache = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.__data_cache = {"clients": [], "vehicles": [], "rentals": []}

        clients = [Client(
            c.get("name"),
            c.get("surname"),
            c.get("pesel"),
            c.get("country"),
            c.get("id"))
            for c in self.__data_cache.get("clients", [])]

        vehicles = [Vehicle(
            v.get("brand"),
            v.get("model"),
            v.get("plate"),
            v.get("mileage"),
            v.get("vin"),
            v.get("id"),
            v.get("status"))
            for v in self.__data_cache.get("vehicles", [])]

        rentals = [Rental(
            r.get("client_id"),
            r.get("vehicle_id"),
            r.get("location_area"),
            r.get("id"),
            r.get("end_date"),
            r.get("range_area"))
            for r in self.__data_cache.get("rentals", [])]

        return clients, vehicles, rentals

    def save_one(self, clients, vehicles, rentals):
        self.__data_cache = {
            "clients": [c.to_json() for c in clients],
            "vehicles": [v.to_json() for v in vehicles],
            "rentals": [r.to_json() for r in rentals]
        }
        with open(self.__file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__data_cache, f, indent=4, ensure_ascii=False)

    def update_one(self, obj_id, updated_obj):
        clients, vehicles, rentals = self.load_all()

        for i, c in enumerate(clients):
            if c.get_id() == obj_id:
                clients[i] = updated_obj
                self.save_one(clients, vehicles, rentals)
                return

        for i, v in enumerate(vehicles):
            if v.get_id() == obj_id:
                vehicles[i] = updated_obj
                self.save_one(clients, vehicles, rentals)
                return

        for i, r in enumerate(rentals):
            if r.get_id() == obj_id:
                rentals[i] = updated_obj
                self.save_one(clients, vehicles, rentals)
                return

    def delete_one(self, obj_id):
        try:
            clients, vehicles, rentals = self.load_all()

            for v in vehicles:
                if v.get_id() == obj_id:
                    vehicles.remove(v)
                    self.save_one(clients, vehicles, rentals)
                    return True

            for c in clients:
                if c.get_id() == obj_id:
                    clients.remove(c)
                    self.save_one(clients, vehicles, rentals)
                    return True

            for r in rentals:
                if r.get_id() == obj_id:
                    rentals.remove(r)
                    self.save_one(clients, vehicles, rentals)
                    return True

            return False
        except Exception as e:
            print(f"Błąd podczas usuwania: {e}")
            return False
