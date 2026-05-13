import json
import os
from src.database.database import Database
from src.models.client import Client
from src.models.vehicle import Vehicle  # Musisz zaimportować model Vehicle


class JSONDatabase(Database):
    def __init__(self, file_path="data/database.json"):
        self.__file_path = file_path
        self.__data_cache = {}

        os.makedirs(os.path.dirname(self.__file_path), exist_ok=True)
        self.load_all()

    def load_all(self):
        if not os.path.exists(self.__file_path):
            self.__data_cache = {"clients": [], "vehicles": [], "rentals": []}
        else:
            try:
                with open(self.__file_path, 'r', encoding='utf-8') as f:
                    self.__data_cache = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.__data_cache = {"clients": [], "vehicles": [], "rentals": []}

        clients = [Client(c.get("name"), c.get("surname"), c.get("pesel"), c.get("country"), c.get("id"))
                   for c in self.__data_cache.get("clients", [])]

        vehicles = [Vehicle(v.get("brand"), v.get("model"), v.get("year"), v.get("vin"), v.get("id"))
                    for v in self.__data_cache.get("vehicles", [])]

        return clients, vehicles, []

    def save_one(self, clients, vehicles, rentals):
        self.__data_cache = {
            "clients": [c.to_json() for c in clients],
            "vehicles": [v.to_json() for v in vehicles],
            "rentals": []
        }
        with open(self.__file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__data_cache, f, indent=4)

    def add_client(self, client):
        clients, v, r = self.load_all()
        clients.append(client)
        self.save_one(clients, v, r)

    def add_vehicle(self, vehicle):
        clients, vehicles, rentals = self.load_all()
        vehicles.append(vehicle)
        self.save_one(clients, vehicles, rentals)

    def update_one(self, obj_id, updated_obj):
        clients, vehicles, rentals = self.load_all()

        # Szukamy w klientach
        for i, c in enumerate(clients):
            if c.get_id() == obj_id:
                clients[i] = updated_obj
                self.save_one(clients, vehicles, rentals)
                return

        # Szukamy w pojazdach
        for i, v in enumerate(vehicles):
            if v.get_id() == obj_id:
                vehicles[i] = updated_obj
                self.save_one(clients, vehicles, rentals)
                return

    def delete_one(self, obj_id):
        clients, vehicles, rentals = self.load_all()

        clients = [c for c in clients if c.get_id() != obj_id]
        vehicles = [v for v in vehicles if v.get_id() != obj_id]

        self.save_one(clients, vehicles, rentals)