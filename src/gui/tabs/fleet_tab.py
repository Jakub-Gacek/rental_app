from PyQt6.QtWidgets import (QWidget, QGridLayout, QTableWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit,
                             QHeaderView, QTableWidgetItem, QMessageBox)

from src.database.json_db import JSONDatabase
from src.models.vehicle import Vehicle


class FleetTab(QWidget):
    def __init__(self, db_manager: JSONDatabase):
        super().__init__()
        self.__db = db_manager
        self.vehicles = []
        self.init_view()
        self.refresh_tab()

    def init_view(self):
        self.__grid_layout = QGridLayout(self)

        self.__form_container = QWidget()
        self.__form_layout = QVBoxLayout(self.__form_container)

        self.__form_layout.addWidget(QLabel("DODAJ NOWY POJAZD"))
        self.__input_brand = QLineEdit()
        self.__input_brand.setPlaceholderText("Marka")
        self.__input_model = QLineEdit()
        self.__input_model.setPlaceholderText("Model")
        self.__input_plate = QLineEdit()
        self.__input_plate.setPlaceholderText("Tablice")
        self.__input_vin = QLineEdit()
        self.__input_vin.setPlaceholderText("Numer VIN")
        self.__input_mileage = QLineEdit()
        self.__input_mileage.setPlaceholderText("Przebieg")

        self.__form_layout.addWidget(self.__input_brand)
        self.__form_layout.addWidget(self.__input_model)
        self.__form_layout.addWidget(self.__input_plate)
        self.__form_layout.addWidget(self.__input_vin)
        self.__form_layout.addWidget(self.__input_mileage)

        self.__label_id = QLabel("Unique ID: ---")
        self.__label_id.setStyleSheet("color: gray; font-size: 11px; margin-top: 10px;")
        self.__label_id.setVisible(False)
        self.__form_layout.addWidget(self.__label_id)

        self.__label_status = QLabel("Status: ---")
        self.__label_status.setStyleSheet("color: gray; font-size: 11px; margin-top: 5px;")
        self.__label_status.setVisible(False)
        self.__form_layout.addWidget(self.__label_status)

        self.__form_layout.addStretch()

        self.__action_container = QWidget()
        self.__action_layout = QVBoxLayout(self.__action_container)
        self.__btn_save = QPushButton("Zapisz do bazy")
        self.__btn_delete = QPushButton("Skasuj Pojazd")

        self.__btn_save.clicked.connect(self.add_vehicle_to_db)
        self.__btn_delete.clicked.connect(self.delete_vehicle_in_db)

        self.__action_layout.addWidget(self.__btn_save)
        self.__action_layout.addWidget(self.__btn_delete)

        self.__search_input = QLineEdit()
        self.__search_input.setPlaceholderText("Szukaj pojazdu (Marka, Model lub Tablice)...")
        self.__search_input.textChanged.connect(self.filter_table)

        self.__table = QTableWidget()
        self.__table.setColumnCount(3)
        self.__table.setHorizontalHeaderLabels(["Marka", "Model", "Tablice"])
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

    def add_vehicle_to_db(self):
        brand = self.__input_brand.text()
        model = self.__input_model.text()
        plate = self.__input_plate.text()
        vin = self.__input_vin.text()
        mileage = self.__input_mileage.text()

        # Podstawowa obsluga bledow
        if not (brand and model and plate and vin and mileage):
            self.show_warning("Błąd formularza", "Wszystkie pola muszą być uzupełnione!")
            return

        if not (vin.isalnum() and len(vin) == 17):
            self.show_warning("Błędny VIN", "Numer VIN musi składać się z dokładnie 17 znaków (cyfry i litery)!")
            return

        if not (mileage.isdigit() and int(mileage) >= 0):
            self.show_warning("Błędny przebieg", "Przebieg pojazdu musi być liczba odatnią!")
            return

        new_vehicle = Vehicle(brand, model, plate, mileage, vin, None, "Dostępny")
        clients, vehicles, rentals = self.__db.load_all()
        vehicles.append(new_vehicle)
        self.__db.save_one(clients, vehicles, rentals)
        self.refresh_tab()
        self.reset_to_add_mode()

    def delete_vehicle_in_db(self):
        selected_row = self.__table.currentRow()
        if selected_row >= 0:
            vehicle = self.vehicles[selected_row]
            if self.__db.delete_one(vehicle.get_id()):
                self.refresh_tab()
                self.reset_to_add_mode()

    def edit_vehicle_db(self):
        brand = self.__input_brand.text()
        model = self.__input_model.text()
        plate = self.__input_plate.text()
        vin = self.__input_vin.text()
        mileage = self.__input_mileage.text()

        vehicle_id = self.__label_id.text().replace("Unique ID: ", "")
        status = self.__label_status.text().replace("Status: ", "")

        if not (brand and model and plate and vin and mileage and vehicle_id):
            self.show_warning("Błąd formularza", "Wszystkie pola muszą być uzupełnione!")
            return

        if not (vin.isalnum() and len(vin) == 17):
            self.show_warning("Błędny VIN", "Numer VIN musi składać się z dokładnie 17 znaków (cyfry i litery)!")
            return

        if not (mileage.isdigit() and int(mileage) >= 0):
            self.show_warning("Błędny przebieg", "Przebieg pojazdu musi być liczbą dodatnią!")
            return

        selected_row = self.__table.currentRow()
        if selected_row >= 0:
            old_vehicle = self.vehicles[selected_row]
            if int(mileage) < int(old_vehicle.get_mileage()):
                self.show_warning(
                    "Błędny przebieg",
                    f"Nowy przebieg ({mileage} km) nie może być mniejszy niż dotychczasowy ({old_vehicle.get_mileage()} km)!"
                )
                return

        updated_vehicle = Vehicle(brand, model, plate, mileage, vin, vehicle_id, status)
        self.__db.update_one(vehicle_id, updated_vehicle)
        self.refresh_tab()
        self.reset_to_add_mode()

    def refresh_tab(self):
        self.__table.setRowCount(0)
        _, vehicles, _ = self.__db.load_all()
        self.vehicles = vehicles

        for vehicle in vehicles:
            row = self.__table.rowCount()
            self.__table.insertRow(row)
            self.__table.setItem(row, 0, QTableWidgetItem(vehicle.get_brand()))
            self.__table.setItem(row, 1, QTableWidgetItem(vehicle.get_model()))
            self.__table.setItem(row, 2, QTableWidgetItem(vehicle.get_plate()))

    def load_data_to_form(self, item):
        if item is None: return
        row = item.row()
        _, vehicles, _ = self.__db.load_all()

        if row < len(vehicles):
            selected = vehicles[row]
            self.__input_brand.setText(selected.get_brand())
            self.__input_model.setText(selected.get_model())
            self.__input_plate.setText(selected.get_plate())
            self.__input_vin.setText(selected.get_vin())
            self.__input_mileage.setText(selected.get_mileage())

            self.__label_id.setText(f"Unique ID: {selected.get_id()}")
            self.__label_id.setVisible(True)
            self.__label_status.setText(f"Status: {selected.get_status()}")
            self.__label_status.setVisible(True)

            self.__btn_save.setText("Edytuj dane")
            try:
                self.__btn_save.clicked.disconnect()
            except TypeError:
                pass
            self.__btn_save.clicked.connect(self.edit_vehicle_db)

    def reset_to_add_mode(self):
        self.__input_brand.clear()
        self.__input_model.clear()
        self.__input_plate.clear()
        self.__input_vin.clear()
        self.__input_mileage.clear()
        self.__label_id.setVisible(False)
        self.__label_status.setVisible(False)
        self.__btn_save.setText("Zapisz do bazy")
        try:
            self.__btn_save.clicked.disconnect()
        except TypeError:
            pass
        self.__btn_save.clicked.connect(self.add_vehicle_to_db)

    def filter_table(self):
        search_text = self.__search_input.text().lower()
        for row in range(self.__table.rowCount()):
            item_brand = self.__table.item(row, 0).text().lower()
            item_model = self.__table.item(row, 1).text().lower()
            item_plate = self.__table.item(row, 2).text().lower()
            self.__table.setRowHidden(row,
                                      search_text not in item_brand and search_text not in item_model and search_text not in item_plate)

    def show_warning(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
