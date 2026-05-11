import json
import os
from src.database.database import Database
from src.models.client import Client


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

        return clients, [], []

    def save_one(self, clients, vehicles, rentals):
        self.__data_cache = {
            "clients": [c.to_json() for c in clients],
            "vehicles": [],
            "rentals": []
        }
        with open(self.__file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__data_cache, f, indent=4)

    def add_client(self, client):
        clients, v, r = self.load_all()
        clients.append(client)
        self.save_one(clients, v, r)

    def update_one(self, obj_id, new_data):
        pass

    def delete_one(self, obj_id):
        pass