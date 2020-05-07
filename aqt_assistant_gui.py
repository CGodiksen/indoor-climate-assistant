from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTime, QTimer
from random import randint
import pyqtgraph as pg
import sys
from database import Database


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('mainwindow.ui', self)

        self.aqtassistant_db = Database()

        self.x = [i for i in range(100)]
        self.y = [float(row[0]) for row in self.aqtassistant_db.get_sensor_data("temperature", 100)]

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0), width=2)
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        # Remove the first x element.
        self.x = self.x[1:]

        # Add a new value 1 higher than the last.
        self.x.append(self.x[-1] + 1)

        # Remove the first y element.
        self.y = self.y[1:]
        self.y.append(float(self.aqtassistant_db.get_sensor_data("temperature", 1)[0][0]))

        # Update the data.
        self.data_line.setData(self.x, self.y)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':         
    main()
