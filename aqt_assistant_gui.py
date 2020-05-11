import random

from PyQt5 import QtWidgets, uic, QtCore
import sys
from database import Database


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('mainwindow.ui', self)

        self.aqtassistant_db = Database()

        self.graphWidget.canvas.fig.suptitle("Living room", fontsize=16)
        n_data = 50
        self.x = list(range(n_data))
        self.y = [float(temperature[0]) for temperature in self.aqtassistant_db.get_sensor_data("temperature", n_data)]
        self.graphWidget.canvas.ax.plot(self.x, self.y, 'r')
        self.graphWidget.canvas.draw()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        self.x = self.x[1:] + [self.x[-1] + 1]
        self.y = self.y[1:] + [random.randint(0, 10)]
        self.graphWidget.canvas.ax.cla()  # Clear the canvas.
        self.graphWidget.canvas.ax.plot(self.x, self.y, 'r')

        # Trigger the canvas to update and redraw.
        self.draw_plot()

    def draw_plot(self):
        # Since the plot is cleared completely when we clear the canvas we draw the plot with all plot configurations.
        self.graphWidget.canvas.ax.set_xlabel("Time")
        self.graphWidget.canvas.ax.set_ylabel("Temperature")
        self.graphWidget.canvas.draw()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':         
    main()
