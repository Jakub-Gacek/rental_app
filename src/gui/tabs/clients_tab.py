from PyQt6.QtWidgets import (QWidget, QGridLayout, QTableWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit,
                             QHeaderView, QTableWidgetItem, QMessageBox)

from src.database.json_db import JSONDatabase
from src.models.client import Client


class ClientsTab(QWidget):
    def __init__(self, db_manager: JSONDatabase):
        super().__init__()
        self.__db = db_manager
        self.clients = []
        self.init_view()
        self.refresh_tab()

    def init_view(self):
        self.__grid_layout = QGridLayout(self)

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

        self.__form_layout.addWidget(self.__input_name)
        self.__form_layout.addWidget(self.__input_surname)
        self.__form_layout.addWidget(self.__input_pesel)
        self.__form_layout.addWidget(self.__input_country)

        self.__label_id = QLabel("Unique ID: ---")
        self.__label_id.setStyleSheet("color: gray; font-size: 11px; margin-top: 10px;")
        self.__label_id.setVisible(False)
        self.__form_layout.addWidget(self.__label_id)

        self.__form_layout.addStretch()

        self.__action_container = QWidget()
        self.__action_layout = QVBoxLayout(self.__action_container)
        self.__btn_save = QPushButton("Zapisz do bazy")
        self.__btn_delete = QPushButton("Skasuj Klienta")

        self.__btn_save.clicked.connect(self.add_client_to_db)
        self.__btn_delete.clicked.connect(self.delete_client_in_db)

        self.__action_layout.addWidget(self.__btn_save)
        self.__action_layout.addWidget(self.__btn_delete)

        self.__search_input = QLineEdit()
        self.__search_input.setPlaceholderText("Szukaj klienta (Imię, Nazwisko lub PESEL)...")
        self.__search_input.textChanged.connect(self.filter_table)

        self.__table = QTableWidget()
        self.__table.setColumnCount(3)
        self.__table.setHorizontalHeaderLabels(["Imię", "Nazwisko", "PESEL"])
        self.__table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.__table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.__table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.__table.itemClicked.connect(self.load_data_to_form)

        self.__grid_layout.addWidget(self.__form_container, 0, 0)
        self.__grid_layout.addWidget(self.__action_container, 1, 0)

        self.__right_container = QWidget()
        self.__right_layout = QVBoxLayout(self.__right_container)
        self.__right_layout.addWidget(self.__search_input)
        self.__right_layout.addWidget(self.__table)

        self.__grid_layout.addWidget(self.__right_container, 0, 1, 2, 1)

        self.__grid_layout.setColumnStretch(0, 1)
        self.__grid_layout.setColumnStretch(1, 2)

    def add_client_to_db(self):
        name = self.__input_name.text()
        surname = self.__input_surname.text()
        pesel = self.__input_pesel.text()
        country = self.__input_country.text()

        if not (name and surname and pesel and country):
            self.show_warning("Błąd formularza", "Wszystkie pola muszą być uzupełnione!")
            return

        if not (pesel.isdigit() and len(pesel) == 11):
            self.show_warning("Błędny PESEL", "PESEL musi składać się z dokładnie 11 cyfr!")
            return

        new_client = Client(name, surname, pesel, country, None)
        clients, vehicles, rentals = self.__db.load_all()
        clients.append(new_client)
        self.__db.save_one(clients, vehicles, rentals)
        self.refresh_tab()
        self.reset_to_add_mode()

    def delete_client_in_db(self):
        selected_row = self.__table.currentRow()
        if selected_row >= 0:
            client = self.clients[selected_row]
            if self.__db.delete_one(client.get_id()):
                self.refresh_tab()
                self.reset_to_add_mode()

    def edit_client_db(self):
        name = self.__input_name.text()
        surname = self.__input_surname.text()
        pesel = self.__input_pesel.text()
        country = self.__input_country.text()

        client_id = self.__label_id.text().replace("Unique ID: ", "")
        if not (name and surname and pesel and country):
            self.show_warning("Błąd formularza", "Wszystkie pola muszą być uzupełnione!")
            return

        if not (pesel.isdigit() and len(pesel) == 11):
            self.show_warning("Błędny PESEL", "PESEL musi składać się z dokładnie 11 cyfr!")
            return

        updated_client = Client(name, surname, pesel, country, client_id)
        self.__db.update_one(client_id, updated_client)
        self.refresh_tab()
        self.reset_to_add_mode()

    def refresh_tab(self):
        self.__table.setRowCount(0)
        clients, _, _ = self.__db.load_all()
        self.clients = clients

        for client in clients:
            row = self.__table.rowCount()
            self.__table.insertRow(row)
            self.__table.setItem(row, 0, QTableWidgetItem(client.get_name()))
            self.__table.setItem(row, 1, QTableWidgetItem(client.get_surname()))
            self.__table.setItem(row, 2, QTableWidgetItem(client.get_pesel()))

    def load_data_to_form(self, item):
        if item is None:
            return

        row = item.row()
        clients, _, _ = self.__db.load_all()

        if row < len(clients):
            selected = clients[row]

            self.__input_name.setText(selected.get_name())
            self.__input_surname.setText(selected.get_surname())
            self.__input_pesel.setText(selected.get_pesel())
            self.__input_country.setText(selected.get_country())

            self.__label_id.setText(f"Unique ID: {selected.get_id()}")
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

    def filter_table(self):
        search_text = self.__search_input.text().lower()
        for row in range(self.__table.rowCount()):
            item_name = self.__table.item(row, 0).text().lower()
            item_surname = self.__table.item(row, 1).text().lower()
            item_pesel = self.__table.item(row, 2).text().lower()

            if search_text in item_name or search_text in item_surname or search_text in item_pesel:
                self.__table.setRowHidden(row, False)
            else:
                self.__table.setRowHidden(row, True)

    def show_warning(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
