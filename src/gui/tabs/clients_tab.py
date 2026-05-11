from PyQt6.QtWidgets import (QWidget, QGridLayout, QTableWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit,
                             QHeaderView)


class ClientsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_view()

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

        self.__form_layout.addWidget(self.__input_name)
        self.__form_layout.addWidget(self.__input_surname)
        self.__form_layout.addWidget(self.__input_pesel)
        self.__form_layout.addStretch()  # Spycha pola do góry kafla

        # Przyciski
        self.__action_container = QWidget()
        self.__action_layout = QVBoxLayout(self.__action_container)
        self.__btn_save = QPushButton("Zapisz do bazy")
        self.__btn_save.clicked.connect(self.dodaj_klienta_do_tabeli)
        self.__btn_clear = QPushButton("Wyczyść pola")
        self.__action_layout.addWidget(self.__btn_save)
        self.__action_layout.addWidget(self.__btn_clear)

        # Tabela
        self.__table = QTableWidget()
        self.__table.setColumnCount(3)
        self.__table.setHorizontalHeaderLabels(["Imię", "Nazwisko", "PESEL"])
        self.__table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # 2. Rozmieszczamy kafle w siatce
        self.__grid_layout.addWidget(self.__form_container, 0, 0)
        self.__grid_layout.addWidget(self.__action_container, 1, 0)
        self.__grid_layout.addWidget(self.__table, 0, 1, 2, 1)

        # Ustawiamy proporcje, żeby lewa strona była węższa (1) a prawa szersza (2)
        self.__grid_layout.setColumnStretch(0, 1)
        self.__grid_layout.setColumnStretch(1, 2)
