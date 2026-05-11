from PyQt6.QtWidgets import (QWidget, QGridLayout, QTableWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit,
                             QHeaderView, QTableWidgetItem)

from src.database.json_db import JSONDatabase
from src.models.client import Client

class ClientsTab(QWidget):
    def __init__(self, db_manager: JSONDatabase):
        super().__init__()
        self.__db = db_manager
        self.init_view()
        self.odswiez_tabele()

    def init_view(self):
        # Układ Siatki
        self.__grid_layout = QGridLayout(self)

        # Formularz
        self.__form_container = QWidget()
        self.__form_layout = QVBoxLayout(self.__form_container)

        self.__form_layout.addWidget(QLabel("DODAJ NOWEGO KLIENTA"))
        self.__input_name = QLineEdit()
        self.__input_name.setPlaceholderText("Imię")
        self.__input_surname = QLineEdit()
        self.__input_surname.setPlaceholderText("Nazwisko")
        self.__input_pesel = QLineEdit()
        self.__input_pesel.setPlaceholderText("PESEL")
        self.__input_country = QLineEdit()
        self.__input_country.setPlaceholderText("Kraj pochodzenia")
        self.__form_layout.addWidget(self.__input_country)

        self.__form_layout.addWidget(self.__input_name)
        self.__form_layout.addWidget(self.__input_surname)
        self.__form_layout.addWidget(self.__input_pesel)
        self.__form_layout.addWidget(self.__input_country)
        self.__form_layout.addStretch()  # Spycha pola do góry kafla

        # Przyciski
        self.__action_container = QWidget()
        self.__action_layout = QVBoxLayout(self.__action_container)
        self.__btn_save = QPushButton("Zapisz do bazy")
        self.__btn_save.clicked.connect(self.dodaj_klienta_do_bazy)
        self.__btn_clear = QPushButton("Wyczyść pola")
        self.__action_layout.addWidget(self.__btn_save)
        self.__action_layout.addWidget(self.__btn_clear)

        # Tabela
        self.__table = QTableWidget()
        self.__table.setColumnCount(3)
        self.__table.setHorizontalHeaderLabels(["Imię", "Nazwisko", "PESEL"])
        self.__table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.__table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.__table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.__table.itemClicked.connect(self.dodaj_klienta_do_bazy)

        # 2. Rozmieszczamy kafle w siatce
        self.__grid_layout.addWidget(self.__form_container, 0, 0)
        self.__grid_layout.addWidget(self.__action_container, 1, 0)
        self.__grid_layout.addWidget(self.__table, 0, 1, 2, 1)

        # Ustawiamy proporcje, żeby lewa strona była węższa (1) a prawa szersza (2)
        self.__grid_layout.setColumnStretch(0, 1)
        self.__grid_layout.setColumnStretch(1, 2)

    def dodaj_klienta_do_bazy(self):
        imie = self.__input_name.text()
        nazwisko = self.__input_surname.text()
        pesel = self.__input_pesel.text()
        country = self.__input_country.text()

        if imie and nazwisko and pesel and country:
            nowy_klient = Client(imie, nazwisko, pesel, country, None)

            self.__db.add_client(nowy_klient)

            self.odswiez_tabele()

            self.__input_name.clear()
            self.__input_surname.clear()
            self.__input_pesel.clear()
            self.__input_country.clear()

    def odswiez_tabele(self):
        self.__table.setRowCount(0)
        clients, _, _ = self.__db.load_all()

        for client in clients:
            row = self.__table.rowCount()
            self.__table.insertRow(row)
            self.__table.setItem(row, 0, QTableWidgetItem(client.get_name()))
            self.__table.setItem(row, 1, QTableWidgetItem(client.get_surname()))
            self.__table.setItem(row, 2, QTableWidgetItem(client.get_pesel()))

    def zaladuj_dane_do_formularza(self):
        current_row = self.__table.currentRow()
        if current_row < 0:
            return

        self.__input_name.setText(self.__table.item(current_row, 0).text())
        self.__input_surname.setText(self.__table.item(current_row, 1).text())
        self.__input_pesel.setText(self.__table.item(current_row, 2).text())

        self.__btn_save.setText("Edytuj dane")

        self.__btn_save.clicked.disconnect()
        self.__btn_save.clicked.connect(self.edytuj_klienta_w_bazie)

