from PyQt6.QtWidgets import (QWidget, QGridLayout, QTableWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit,
                             QHeaderView, QTableWidgetItem)

from src.database.json_db import JSONDatabase
from src.models.client import Client


class ClientsTab(QWidget):
    def __init__(self, db_manager: JSONDatabase):
        super().__init__()
        self.__db = db_manager
        self.init_view()
        self.refresh_tab()

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

        self.__label_id = QLabel("Unique ID: ---")
        self.__label_id.setStyleSheet("color: gray; font-size: 11px; margin-top: 10px;")
        self.__label_id.setVisible(False)
        self.__form_layout.addWidget(self.__label_id)

        self.__form_layout.addStretch()  # Spycha pola do góry kafla

        # Przyciski
        self.__action_container = QWidget()
        self.__action_layout = QVBoxLayout(self.__action_container)
        self.__btn_save = QPushButton("Zapisz do bazy")
        self.__btn_save.clicked.connect(self.add_client_to_db)
        self.__action_layout.addWidget(self.__btn_save)

        # Tabela
        self.__table = QTableWidget()
        self.__table.setColumnCount(3)
        self.__table.setHorizontalHeaderLabels(["Imię", "Nazwisko", "PESEL"])
        self.__table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Blokada Tabeli
        self.__table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.__table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.__table.itemClicked.connect(self.load_data_to_form)

        # 2. Rozmieszczamy kafle w siatce
        self.__grid_layout.addWidget(self.__form_container, 0, 0)
        self.__grid_layout.addWidget(self.__action_container, 1, 0)
        self.__grid_layout.addWidget(self.__table, 0, 1, 2, 1)

        # Ustawiamy proporcje, żeby lewa strona była węższa (1) a prawa szersza (2)
        self.__grid_layout.setColumnStretch(0, 1)
        self.__grid_layout.setColumnStretch(1, 2)

    def add_client_to_db(self):
        imie = self.__input_name.text()
        nazwisko = self.__input_surname.text()
        pesel = self.__input_pesel.text()
        country = self.__input_country.text()

        if imie and nazwisko and pesel and country:
            nowy_klient = Client(imie, nazwisko, pesel, country, None)

            self.__db.add_client(nowy_klient)

            self.refresh_tab()

            self.__input_name.clear()
            self.__input_surname.clear()
            self.__input_pesel.clear()
            self.__input_country.clear()

    def edit_client_db(self):
        name = self.__input_name.text()
        surname = self.__input_surname.text()
        pesel = self.__input_pesel.text()
        country = self.__input_country.text()

        full_id_text = self.__label_id.text()
        client_id = full_id_text.replace("Unique ID: ", "")

        if name and surname and pesel and client_id:
            updated_client = Client(name, surname, pesel, country, client_id)

            self.__db.update_one(client_id, updated_client)

            self.refresh_tab()
            self.reset_to_add_mode()

    def refresh_tab(self):
        self.__table.setRowCount(0)
        clients, _, _ = self.__db.load_all()

        for client in clients:
            row = self.__table.rowCount()
            self.__table.insertRow(row)
            self.__table.setItem(row, 0, QTableWidgetItem(client.get_name()))
            self.__table.setItem(row, 1, QTableWidgetItem(client.get_surname()))
            self.__table.setItem(row, 2, QTableWidgetItem(client.get_pesel()))

    def load_data_to_form(self, item):

        row = item.row()

        clients, _, _ = self.__db.load_all()

        if row < len(clients):
            selected_client = clients[row]

            self.__label_id.setText(selected_client.get_id())
            self.__input_name.setText(selected_client.get_name())
            self.__input_surname.setText(selected_client.get_surname())
            self.__input_pesel.setText(selected_client.get_pesel())
            self.__input_country.setText(selected_client.get_country())

            self.__label_id.setText(f"Unique ID: {selected_client.get_id()}")
            self.__label_id.setVisible(True)
            self.__btn_save.setText("Edytuj dane")
            try:
                self.__btn_save.clicked.disconnect()
            except TypeError:
                pass
            self.__btn_save.clicked.connect(self.edit_client_db)

    def reset_to_add_mode(self):
        self.__input_name.clear()
        self.__input_surname.clear()
        self.__input_pesel.clear()
        self.__input_country.clear()

        self.__label_id.setVisible(False)
        self.__btn_save.setText("Zapisz do bazy")

        try:
            self.__btn_save.clicked.disconnect()
        except TypeError:
            pass
        self.__btn_save.clicked.connect(self.add_client_to_db)