from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget

from src.gui.tabs.clients_tab import ClientsTab
from src.database.json_db import JSONDatabase
from src.gui.tabs.fleet_tab import FleetTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = JSONDatabase("data/database.json")
        self.init_view()

    def init_view(self):
        self.setWindowTitle("RentalAPP - Widok Interfejsu")
        self.resize(800, 600)

        self.__central_widget = QWidget()
        self.setCentralWidget(self.__central_widget)

        self.__main_layout = QVBoxLayout(self.__central_widget)

        self.__tabs = QTabWidget()

        self.__tabs.addTab(ClientsTab(self.db), "Klienci")
        self.__tabs.addTab(FleetTab(self.db), "Pojazdy")
        self.__tabs.addTab(QWidget(), "Wypożyczenia")
        self.__tabs.addTab(QWidget(), "Mapa")

        self.__main_layout.addWidget(self.__tabs)
