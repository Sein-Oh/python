import sys
from PyQt5.QtWidgets import QMainWindow, QApplication

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello PyQt5")
        self.setGeometry(300,300,800,600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()
