from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget

from src.gui.tabs.clients_tab import ClientsTab
from src.database.json_db import JSONDatabase
from src.gui.tabs.fleet_tab import FleetTab
from src.gui.tabs.map_tab import MapTab
from src.gui.tabs.rentals_tab import RentalsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = JSONDatabase("data/database.json")
        self.init_view()

    def init_view(self):
        self.setWindowTitle("RentalAPP")
        self.resize(800, 600)

        self.__central_widget = QWidget()
        self.setCentralWidget(self.__central_widget)

        self.__main_layout = QVBoxLayout(self.__central_widget)

        self.__tabs = QTabWidget()

        self.__tabs.addTab(ClientsTab(self.db), "Klienci")
        self.__tabs.addTab(FleetTab(self.db), "Pojazdy")

        self.__rental_tab = RentalsTab(self.db)
        self.__tabs.addTab(self.__rental_tab, "Wypożyczenia")

        self.__map_tab = MapTab(self.db)
        self.__tabs.addTab(self.__map_tab, "Mapa")

        self.__tabs.currentChanged.connect(self.__on_tab_changed)

        self.__main_layout.addWidget(self.__tabs)

    def __on_tab_changed(self, index):
        if index == 3:
            self.__map_tab.refresh_tab()
        elif index == 2:
            self.__rental_tab.refresh_tab()
