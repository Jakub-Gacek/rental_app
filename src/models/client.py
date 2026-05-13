import uuid


class Client:
    def __init__(self, name, surname, pesel, country, client_id: None):
        self.__name = name
        self.__surname = surname
        self.__pesel = pesel
        self.__id = client_id
        self.__country = country
        self.__id = client_id if client_id else str(uuid.uuid4())[:8]

    def get_name(self): return self.__name

    def get_surname(self): return self.__surname

    def get_pesel(self): return self.__pesel

    def get_country(self): return self.__country

    def get_id(self): return self.__id

    def to_json(self):
        return {
            "name": self.__name,
            "surname": self.__surname,
            "pesel": self.__pesel,
            "country": self.__country,
            "id": self.__id
        }
