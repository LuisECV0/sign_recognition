import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
from PyQt5 import uic

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Cargar la interfaz desde el archivo .ui
        uic.loadUi("main_window.ui", self)

        # Conectar los botones a las funciones correspondientes
        self.btnClose.clicked.connect(self.close_program)
        self.btnShowMainProgram.clicked.connect(self.show_main_program)

    def close_program(self):
        # Cerrar la aplicación
        self.close()

    def show_main_program(self):
        # Mostrar la ejecución del programa principal
        from main_program import run_main_program
        run_main_program()

def run_interface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_interface()
