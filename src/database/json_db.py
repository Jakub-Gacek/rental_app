import json
from src.database.database import Database
from src.models.client import Client
from src.models.vehicle import Vehicle
from src.models.rental import Rental


class JSONDatabase(Database):
    def __init__(self, file_path):
        super().__init__()
        self.__file_path = file_path

    def load_all(self):
        with open(self.__file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        clients = [Client(**c) for c in data.get("clients", [])]
        vehicles = [Vehicle(**v) for v in data.get("vehicles", [])]
        rentals = [Rental(**r) for r in data.get("rentals", [])]

        return clients, vehicles, rentals

    def save_one(self, clients, vehicles, rentals):
        data = {
            "clients": [c.to_json() for c in clients],
            "vehicles": [v.to_json() for v in vehicles],
            "rentals": [r.to_json() for r in rentals]
        }
        with open(self.__file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def update_one(self, obj_id, new_data):
        pass

    def delete_one(self, obj_id):
        pass