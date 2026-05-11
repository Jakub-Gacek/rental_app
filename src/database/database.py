from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def load_all(self):
        pass

    @abstractmethod
    def save_one(self, clients, vehicles, rentals):
        pass

    @abstractmethod
    def update_one(self, obj_id, new_data):
        pass

    @abstractmethod
    def delete_one(self, obj_id):
        pass