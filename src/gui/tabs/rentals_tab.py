import uuid
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (QWidget, QGridLayout, QTableWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QHeaderView, QTableWidgetItem, QFileDialog, QDateEdit, QMessageBox)

from src.database.json_db import JSONDatabase
from src.models.rental import Rental
from src.models.vehicle import Vehicle
from src.models.vehicle_status import VehicleStatus
from src.utils.rentals_cords import geo_coords


class RentalsTab(QWidget):
    def __init__(self, db_manager: JSONDatabase):
        super().__init__()
        self.__db = db_manager
        self.__selected_client_id = None
        self.__selected_vehicle_id = None
        self.init_view()
        self.refresh_tab()

    def init_view(self):
        self.__grid_layout = QGridLayout(self)

        self.__form_container = QWidget()
        self.__form_layout = QVBoxLayout(self.__form_container)

        self.__form_layout.addWidget(QLabel("NOWE WYPOŻYCZENIE"))

        self.__input_location = QLineEdit()
        self.__input_location.setPlaceholderText("Miejsce zwrotu")
        self.__form_layout.addWidget(self.__input_location)

        self.__input_range = QLineEdit()
        self.__input_range.setPlaceholderText("Promień wypożyczenia (km)")
        self.__form_layout.addWidget(self.__input_range)

        self.__form_layout.addWidget(QLabel("Data końca wynajmu:"))
        self.__input_date = QDateEdit()
        self.__input_date.setCalendarPopup(True)
        self.__input_date.setDate(QDate.currentDate().addDays(7))
        self.__form_layout.addWidget(self.__input_date)

        self.__label_selected_client = QLabel("Wybrany klient: BRAK")
        self.__label_selected_client.setStyleSheet("color: #0078d7; font-weight: bold;")
        self.__label_selected_vehicle = QLabel("Wybrany pojazd: BRAK")
        self.__label_selected_vehicle.setStyleSheet("color: #0078d7; font-weight: bold;")

        self.__form_layout.addWidget(self.__label_selected_client)
        self.__form_layout.addWidget(self.__label_selected_vehicle)
        self.__form_layout.addStretch()

        self.__btn_rent = QPushButton("Wypożycz")
        self.__btn_rent.clicked.connect(self.add_rental_to_db)
        self.__form_layout.addWidget(self.__btn_rent)

        self.__btn_export_pdf = QPushButton("Wyeksportuj do PDF")
        self.__btn_export_pdf.setStyleSheet("background-color: #2b6cb0; color: white; font-weight: bold; padding: 6px;")
        self.__btn_export_pdf.clicked.connect(self.export_rentals_to_pdf)
        self.__form_layout.addWidget(self.__btn_export_pdf)

        self.__tables_container = QWidget()
        self.__tables_layout = QHBoxLayout(self.__tables_container)

        self.__client_sec = QWidget()
        self.__client_sec_layout = QVBoxLayout(self.__client_sec)
        self.__search_client = QLineEdit()
        self.__search_client.setPlaceholderText("Szukaj klienta...")
        self.__search_client.textChanged.connect(self.filter_clients)

        self.__table_clients = QTableWidget()
        self.__table_clients.setColumnCount(2)
        self.__table_clients.setHorizontalHeaderLabels(["Imię", "Nazwisko"])
        self.__table_clients.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.__table_clients.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.__table_clients.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.__table_clients.itemClicked.connect(self.select_client)

        self.__client_sec_layout.addWidget(self.__search_client)
        self.__client_sec_layout.addWidget(self.__table_clients)

        self.__vehicle_sec = QWidget()
        self.__vehicle_sec_layout = QVBoxLayout(self.__vehicle_sec)
        self.__search_vehicle = QLineEdit()
        self.__search_vehicle.setPlaceholderText("Szukaj pojazdu...")
        self.__search_vehicle.textChanged.connect(self.filter_vehicles)

        self.__table_vehicles = QTableWidget()
        self.__table_vehicles.setColumnCount(2)
        self.__table_vehicles.setHorizontalHeaderLabels(["Marka", "Model"])
        self.__table_vehicles.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.__table_vehicles.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.__table_vehicles.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.__table_vehicles.itemClicked.connect(self.select_vehicle)

        self.__vehicle_sec_layout.addWidget(self.__search_vehicle)
        self.__vehicle_sec_layout.addWidget(self.__table_vehicles)

        self.__tables_layout.addWidget(self.__client_sec)
        self.__tables_layout.addWidget(self.__vehicle_sec)

        self.__grid_layout.addWidget(self.__form_container, 0, 0)
        self.__grid_layout.addWidget(self.__tables_container, 0, 1)
        self.__grid_layout.setColumnStretch(0, 1)
        self.__grid_layout.setColumnStretch(1, 3)

    def refresh_tab(self):
        self.__table_clients.setRowCount(0)
        self.__table_vehicles.setRowCount(0)
        clients, vehicles, _ = self.__db.load_all()

        for c in clients:
            row = self.__table_clients.rowCount()
            self.__table_clients.insertRow(row)
            item_name = QTableWidgetItem(c.get_name())
            item_name.setData(Qt.ItemDataRole.UserRole, c.get_id())
            item_name.setData(Qt.ItemDataRole.UserRole + 1, c.get_pesel())
            self.__table_clients.setItem(row, 0, item_name)
            self.__table_clients.setItem(row, 1, QTableWidgetItem(c.get_surname()))

        for v in vehicles:
            if v.get_status() == VehicleStatus.AVAILABLE.value:
                row = self.__table_vehicles.rowCount()
                self.__table_vehicles.insertRow(row)
                item_brand = QTableWidgetItem(v.get_brand())
                item_brand.setData(Qt.ItemDataRole.UserRole, v.get_id())
                item_brand.setData(Qt.ItemDataRole.UserRole + 1, v.get_plate())
                self.__table_vehicles.setItem(row, 0, item_brand)
                self.__table_vehicles.setItem(row, 1, QTableWidgetItem(v.get_model()))

    def select_client(self, item):
        if item is None:
            return
        row = item.row()
        name_item = self.__table_clients.item(row, 0)
        surname_item = self.__table_clients.item(row, 1)
        self.__selected_client_id = name_item.data(Qt.ItemDataRole.UserRole)
        pesel = name_item.data(Qt.ItemDataRole.UserRole + 1)
        self.__label_selected_client.setText(f"Wybrany: {name_item.text()} {surname_item.text()} (PESEL: {pesel})")

    def select_vehicle(self, item):
        if item is None:
            return
        row = item.row()
        brand_item = self.__table_vehicles.item(row, 0)
        model_item = self.__table_vehicles.item(row, 1)
        self.__selected_vehicle_id = brand_item.data(Qt.ItemDataRole.UserRole)
        plate = brand_item.data(Qt.ItemDataRole.UserRole + 1)
        self.__label_selected_vehicle.setText(f"Wybrany: {brand_item.text()} {model_item.text()} ({plate})")

    def add_rental_to_db(self):
        location = self.__input_location.text().strip()
        range_area = self.__input_range.text().strip()
        end_date_str = self.__input_date.date().toString("yyyy-MM-dd")

        if not (range_area.isdigit() and float(range_area) > 0):
            self.show_warning("Błędny promień", "Promień strefy musi być liczbą większą od 0!")
            return

        if location.lower() not in geo_coords:
            self.show_warning(
                "Nieobsługiwana lokalizacja",
                f"Miasto '{location}' nie znajduje się w bazie danych! Wybierz jedno z obsługiwanych miast."
            )
            return

        if self.__selected_client_id and self.__selected_vehicle_id:
            clients, vehicles, rentals = self.__db.load_all()
            rental_id = str(uuid.uuid4())[:8]

            new_rental = Rental(
                client_id=str(self.__selected_client_id),
                vehicle_id=str(self.__selected_vehicle_id),
                location_area=str(location),
                rental_id=str(rental_id),
                end_date=str(end_date_str),
                range_area=str(range_area),
            )
            rentals.append(new_rental)

            for i, v in enumerate(vehicles):
                if str(v.get_id()) == str(self.__selected_vehicle_id):
                    vehicles[i] = Vehicle(
                        v.get_brand(), v.get_model(), v.get_plate(),
                        v.get_mileage(), v.get_vin(), v.get_id(), VehicleStatus.UNAVAILABLE
                    )
                    break

            cleaned_rentals = []
            for r in rentals:
                if isinstance(r, Rental):
                    cleaned_rentals.append(r)
                elif isinstance(r, dict):
                    restored_rental = Rental(
                        client_id=r.get("client_id"),
                        vehicle_id=r.get("vehicle_id"),
                        location_area=r.get("location_area"),
                        rental_id=r.get("id"),
                        end_date=r.get("end_date"),
                        range_area=r.get("range_area")
                    )
                    cleaned_rentals.append(restored_rental)

            self.__db.save_one(clients, vehicles, cleaned_rentals)

            self.reset_to_add_mode()
            self.clear_table_selections()
            self.refresh_tab()

    def clear_table_selections(self):
        self.__table_clients.clearSelection()
        self.__table_vehicles.clearSelection()
        self.__table_clients.setCurrentCell(-1, -1)
        self.__table_vehicles.setCurrentCell(-1, -1)

    def filter_clients(self):
        search_text = self.__search_client.text().lower()
        for row in range(self.__table_clients.rowCount()):
            name = self.__table_clients.item(row, 0).text().lower()
            surname = self.__table_clients.item(row, 1).text().lower()

            if search_text in name or search_text in surname:
                self.__table_clients.setRowHidden(row, False)
            else:
                self.__table_clients.setRowHidden(row, True)

    def filter_vehicles(self):
        search_text = self.__search_vehicle.text().lower()
        for row in range(self.__table_vehicles.rowCount()):
            brand = self.__table_vehicles.item(row, 0).text().lower()
            model = self.__table_vehicles.item(row, 1).text().lower()

            if search_text in brand or search_text in model:
                self.__table_vehicles.setRowHidden(row, False)
            else:
                self.__table_vehicles.setRowHidden(row, True)

    def reset_to_add_mode(self):
        self.__input_location.clear()
        self.__input_range.clear()
        self.__label_selected_client.setText("Wybrany klient: BRAK")
        self.__label_selected_vehicle.setText("Wybrany pojazd: BRAK")
        self.__selected_client_id = None
        self.__selected_vehicle_id = None
        self.__input_date.setDate(QDate.currentDate().addDays(7))

    def export_rentals_to_pdf(self):
        from src.models.pdf_generator import PDFGenerator

        clients, vehicles, rentals = self.__db.load_all()
        if not rentals: return

        file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz PDF", "", "Pliki PDF (*.pdf)")
        if not file_path: return

        try:
            PDFGenerator.create_rental_report(file_path, rentals, clients, vehicles)
        except Exception as e:
            print(f"Błąd zapisu raportu: {e}")

    def show_warning(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()