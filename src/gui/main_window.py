from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_view()

    def init_view(self):
        self.setWindowTitle("RentalAPP - Widok Interfejsu")
        self.resize(800, 600)

        self.__central_widget = QWidget()
        self.setCentralWidget(self.__central_widget)
        self.__layout = QVBoxLayout(self.__central_widget)

        self.__tabs = QTabWidget()

        self.__tabs.addTab(self.__create_temp_tab("Tu będzie lista klientów"), "Klienci")
        self.__tabs.addTab(self.__create_temp_tab("Tu będzie flota pojazdów"), "Pojazdy")
        self.__tabs.addTab(self.__create_temp_tab("Tu będą aktywne wypożyczenia"), "Wypożyczalnia")

        self.__layout.addWidget(self.__tabs)

    def __create_temp_tab(self, text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel(text))
        return widget
