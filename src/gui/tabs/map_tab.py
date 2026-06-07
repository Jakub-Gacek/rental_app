import folium
import os
from PyQt6.QtCore import Qt, QDate, QCoreApplication
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QSizePolicy, QPushButton, QFileDialog, QLineEdit)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from src.database.json_db import JSONDatabase
from src.models.vehicle_status import VehicleStatus
from src.utils.rentals_cords import geo_coords


class MapTab(QWidget):
    def __init__(self, db_manager: JSONDatabase):
        super().__init__()
        self.__db = db_manager
        self.init_view()

    def init_view(self):
        self.__main_layout = QHBoxLayout(self)
        self.__main_layout.setContentsMargins(0, 0, 0, 0)
        self.__main_layout.setSpacing(10)

        self.__left_layout = QVBoxLayout()
        self.__left_layout.setContentsMargins(10, 10, 0, 10)

        self.__web_view = QWebEngineView()
        self.__web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.__web_view.setStyleSheet("background-color: #2b2b2b; border: none;")

        self.__btn_export_pdf = QPushButton("Wyeksportuj mapę do PDF")
        self.__btn_export_pdf.setStyleSheet("background-color: #2b6cb0; color: white; font-weight: bold; padding: 6px;")
        self.__btn_export_pdf.clicked.connect(self.export_map_data_to_pdf)

        self.__left_layout.addWidget(QLabel("LOKALIZACJA POJAZDÓW FLOTY (EUROPA):"))
        self.__left_layout.addWidget(self.__web_view)
        self.__left_layout.addWidget(self.__btn_export_pdf)

        self.__right_container = QWidget()
        self.__right_layout = QVBoxLayout(self.__right_container)
        self.__right_layout.setContentsMargins(0, 10, 10, 10)

        self.__search_rental = QLineEdit()
        self.__search_rental.setPlaceholderText("Wyszukaj Wypożyczenie...")
        self.__search_rental.textChanged.connect(self.filter_rentals)

        self.__table_history = QTableWidget()
        self.__table_history.setColumnCount(4)
        self.__table_history.setHorizontalHeaderLabels(["Klient", "Pojazd", "Miejsce Zwrotu", "Termin"])
        self.__table_history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.__table_history.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.__table_history.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.__btn_end_rental = QPushButton("Zakończ wynajem")
        self.__btn_end_rental.setStyleSheet("padding: 6px; font-weight: bold;")
        self.__btn_end_rental.clicked.connect(self.end_rental)

        self.__right_layout.addWidget(QLabel("AKTUALNE WYPOŻYCZENIA:"))
        self.__right_layout.addWidget(self.__search_rental)
        self.__right_layout.addWidget(self.__table_history)
        self.__right_layout.addWidget(self.__btn_end_rental)

        self.__main_layout.addLayout(self.__left_layout, stretch=3)
        self.__main_layout.addWidget(self.__right_container, stretch=2)

        self.refresh_tab()

    def refresh_tab(self):
        self.__table_history.blockSignals(True)
        self.__table_history.setRowCount(0)
        clients, vehicles, rentals = self.__db.load_all()

        client_map = {str(c.get_id()): c for c in clients}
        vehicle_map = {str(v.get_id()): v for v in vehicles}

        folium_map = folium.Map(location=[50.5, 15.0], zoom_start=4, control_scale=True)
        city_counters = {}
        current_date = QDate.currentDate()

        for r in rentals:
            c_id = str(r.get_client_id())
            v_id = str(r.get_vehicle_id())
            location = r.get_location_area()
            end_date_str = r.get_end_date()
            range_area = r.get_range_area()

            client_obj = client_map.get(c_id)
            client_text = f"{client_obj.get_name()} {client_obj.get_surname()}" if client_obj else f"Nieznany ({c_id})"

            vehicle_obj = vehicle_map.get(v_id)
            vehicle_text = f"{vehicle_obj.get_brand()} {vehicle_obj.get_model()}" if vehicle_obj else f"Nieznany ({v_id})"

            location_key = str(location).strip().lower()
            coords = geo_coords.get(location_key)

            if coords:
                row = self.__table_history.rowCount()
                self.__table_history.insertRow(row)

                item_c = QTableWidgetItem(client_text)
                item_v = QTableWidgetItem(vehicle_text)
                item_l = QTableWidgetItem(str(location))
                item_d = QTableWidgetItem(str(end_date_str))

                if QDate.fromString(end_date_str, "yyyy-MM-dd") < current_date:
                    past_date_color = QColor("#ffcccc")
                    for item in (item_c, item_v, item_l, item_d):
                        item.setBackground(past_date_color)
                        item.setForeground(QColor("black"))

                self.__table_history.setItem(row, 0, item_c)
                self.__table_history.setItem(row, 1, item_v)
                self.__table_history.setItem(row, 2, item_l)
                self.__table_history.setItem(row, 3, item_d)

                city_counters[location_key] = city_counters.get(location_key, -1) + 1
                shift = city_counters[location_key] * 0.015
                adjusted_coords = [coords[0] + shift, coords[1] + shift]
                adjusted_range = float(range_area) * 1000 if range_area else 0.0

                popup_content = f"<b>Klient:</b> {client_text}<br><b>Pojazd:</b> {vehicle_text}<br><b>Miejsce:</b> {location}<br><b>Termin:</b> {end_date_str}"

                folium.Circle(
                    location=adjusted_coords,
                    radius=adjusted_range,
                    color="#2b6cb0",
                    fill=True,
                    fill_color="#2b6cb0",
                    fill_opacity=0.15,
                    tooltip=f"Pojazd: {vehicle_text} | Zasięg: {range_area}km"
                ).add_to(folium_map)

                folium.Marker(
                    location=adjusted_coords,
                    popup=folium.Popup(popup_content, max_width=250),
                    tooltip=f"{vehicle_text} -> {client_text}",
                    icon=folium.Icon(color="blue", icon="car", prefix="fa")
                ).add_to(folium_map)

        try:
            fig = folium.Figure(height="100%")
            folium_map.add_to(fig)

            html_data = fig._repr_html_()

            custom_style = """
                    <style>
                        html, body { 
                            margin: 0 !important; 
                            padding: 0 !important; 
                            height: 100% !important; 
                            width: 100% !important; 
                            overflow: hidden !important; 
                            background-color: #2b2b2b !important; 
                        }
                        iframe {
                            width: 100% !important;
                            height: 100% !important;
                            border: none !important;
                        }
                    </style>
                    """
            self.__web_view.setHtml(custom_style + html_data)
        except Exception as e:
            print(f"Błąd generowania mapy: {e}")

        self.__table_history.blockSignals(False)

    def filter_rentals(self):
        search_text = self.__search_rental.text().lower()
        for row in range(self.__table_history.rowCount()):
            client = self.__table_history.item(row, 0).text().lower()
            vehicle = self.__table_history.item(row, 1).text().lower()
            self.__table_history.setRowHidden(row, search_text not in client and search_text not in vehicle)

    def end_rental(self):
        row = self.__table_history.currentRow()
        if row < 0: return

        client_text = self.__table_history.item(row, 0).text()
        vehicle_text = self.__table_history.item(row, 1).text()
        clients, vehicles, rentals = self.__db.load_all()

        for r in rentals:
            c_obj = next((c for c in clients if str(c.get_id()) == r.get_client_id()), None)
            v_obj = next((v for v in vehicles if str(v.get_id()) == r.get_vehicle_id()), None)

            if c_obj and v_obj:
                if f"{c_obj.get_name()} {c_obj.get_surname()}" == client_text and f"{v_obj.get_brand()} {v_obj.get_model()}" == vehicle_text:
                    rentals.remove(r)
                    for i, v in enumerate(vehicles):
                        if v.get_id() == v_obj.get_id():
                            from src.models.vehicle import Vehicle
                            vehicles[i] = Vehicle(v.get_brand(), v.get_model(), v.get_plate(), v.get_mileage(),
                                                  v.get_vin(), v.get_id(), VehicleStatus.AVAILABLE)
                            break
                    break

        self.__db.save_one(clients, vehicles, rentals)
        self.refresh_tab()

    def export_map_data_to_pdf(self):
        from src.models.pdf_generator import PDFGenerator
        clients, vehicles, rentals = self.__db.load_all()
        if not rentals: return

        file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz PDF", "", "Pliki PDF (*.pdf)")
        if not file_path: return

        QCoreApplication.processEvents()
        temp_img_path = "data_temp_map.png"

        try:
            screenshot = self.__web_view.grab()
            screenshot.save(temp_img_path, "PNG")
            PDFGenerator.create_map_report(file_path, rentals, clients, vehicles, temp_img_path)
        except Exception as e:
            print(f"Błąd zapisu raportu mapy PDF: {e}")
        finally:
            if temp_img_path and os.path.exists(temp_img_path):
                try:
                    os.remove(temp_img_path)
                except Exception:
                    pass