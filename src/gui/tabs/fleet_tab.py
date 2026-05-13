from PyQt6.QtWidgets import (QWidget, QGridLayout, QTableWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit,
                             QHeaderView, QTableWidgetItem)

from src.database.json_db import JSONDatabase
from src.models.vehicle import Vehicle


class FleetTab(QWidget):
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

        self.__form_layout.addWidget(QLabel("DODAJ NOWY POJAZD"))

        self.__input_brand = QLineEdit()
        self.__input_brand.setPlaceholderText("Marka")
        self.__input_model = QLineEdit()
        self.__input_model.setPlaceholderText("Model")
        self.__input_year = QLineEdit()
        self.__input_year.setPlaceholderText("Rok produkcji")
        self.__input_vin = QLineEdit()
        self.__input_vin.setPlaceholderText("Numer VIN")

        self.__form_layout.addWidget(self.__input_brand)
        self.__form_layout.addWidget(self.__input_model)
        self.__form_layout.addWidget(self.__input_year)
        self.__form_layout.addWidget(self.__input_vin)

        # Unikalne ID (widoczne tylko przy edycji)
        self.__label_id = QLabel("Unique ID: ---")
        self.__label_id.setStyleSheet("color: gray; font-size: 11px; margin-top: 10px;")
        self.__label_id.setVisible(False)
        self.__form_layout.addWidget(self.__label_id)

        self.__form_layout.addStretch()

        # Przyciski
        self.__action_container = QWidget()
        self.__action_layout = QVBoxLayout(self.__action_container)
        self.__btn_save = QPushButton("Zapisz do bazy")
        self.__btn_save.clicked.connect(self.add_vehicle_to_db)
        self.__btn_clear = QPushButton("Wyczyść pola")
        self.__btn_clear.clicked.connect(self.reset_to_add_mode)

        self.__action_layout.addWidget(self.__btn_save)
        self.__action_layout.addWidget(self.__btn_clear)

        # Tabela
        self.__table = QTableWidget()
        self.__table.setColumnCount(3)
        self.__table.setHorizontalHeaderLabels(["Marka", "Model", "Rok"])
        self.__table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.__table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.__table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.__table.itemClicked.connect(self.load_data_to_form)

        # Rozmieszczenie w siatce
        self.__grid_layout.addWidget(self.__form_container, 0, 0)
        self.__grid_layout.addWidget(self.__action_container, 1, 0)
        self.__grid_layout.addWidget(self.__table, 0, 1, 2, 1)

        self.__grid_layout.setColumnStretch(0, 1)
        self.__grid_layout.setColumnStretch(1, 2)

    def add_vehicle_to_db(self):
        brand = self.__input_brand.text()
        model = self.__input_model.text()
        year = self.__input_year.text()
        vin = self.__input_vin.text()

        if brand and model and year and vin:
            # Model Vehicle sam wylosuje ID w __init__
            nowy_pojazd = Vehicle(brand, model, year, vin, None)
            self.__db.add_vehicle(nowy_pojazd)
            self.refresh_tab()
            self.reset_to_add_mode()

    def refresh_tab(self):
        self.__table.setRowCount(0)
        _, vehicles, _ = self.__db.load_all()

        for v in vehicles:
            row = self.__table.rowCount()
            self.__table.insertRow(row)
            self.__table.setItem(row, 0, QTableWidgetItem(v.get_brand()))
            self.__table.setItem(row, 1, QTableWidgetItem(v.get_model()))
            self.__table.setItem(row, 2, QTableWidgetItem(str(v.get_year())))

    def load_data_to_form(self, item):
        if item is None:
            return

        row = item.row()
        _, vehicles, _ = self.__db.load_all()

        if row < len(vehicles):
            selected = vehicles[row]

            self.__input_brand.setText(selected.get_brand())
            self.__input_model.setText(selected.get_model())
            self.__input_year.setText(str(selected.get_year()))
            self.__input_vin.setText(selected.get_vin())

            self.__label_id.setText(f"Unique ID: {selected.get_id()}")
            self.__label_id.setVisible(True)

            self.__btn_save.setText("Edytuj dane")
            try:
                self.__btn_save.clicked.disconnect()
            except TypeError:
                pass
            self.__btn_save.clicked.connect(self.edit_vehicle_db)

    def edit_vehicle_db(self):
        brand = self.__input_brand.text()
        model = self.__input_model.text()
        year = self.__input_year.text()
        vin = self.__input_vin.text()

        full_id_text = self.__label_id.text()
        vehicle_id = full_id_text.replace("Unique ID: ", "")

        if brand and model and year and vehicle_id:
            updated_vehicle = Vehicle(brand, model, year, vin, vehicle_id)
            self.__db.update_one(vehicle_id, updated_vehicle)

            self.refresh_tab()
            self.reset_to_add_mode()

    def reset_to_add_mode(self):
        self.__input_brand.clear()
        self.__input_model.clear()
        self.__input_year.clear()
        self.__input_vin.clear()

        self.__label_id.setVisible(False)
        self.__btn_save.setText("Zapisz do bazy")

        try:
            self.__btn_save.clicked.disconnect()
        except TypeError:
            pass
        self.__btn_save.clicked.connect(self.add_vehicle_to_db)