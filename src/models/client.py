class Client:
    def __init__(self, name, surname, pesel, country, client_id):
        self.__name = name
        self.__surname = surname
        self.__pesel = pesel
        self.__id = client_id
        self.__country = country

    def get_info(self):
        return f"{self.__name} {self.__surname} ({self.__id})"

    def to_json(self):
        return {
            "name": self.__name,
            "surname": self.__surname,
            "pesel": self.__pesel,
            "id": self.__id,
            "country": self.__country
        }
