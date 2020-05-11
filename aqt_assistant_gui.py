import random

from PyQt5 import QtWidgets, uic, QtCore
import sys
from database import Database
import matplotlib
import datetime


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('mainwindow.ui', self)

        self.aqtassistant_db = Database()

        self.graphWidget.canvas.fig.suptitle("Living room", fontsize=16)

        n_data = 200

        # Getting the last n rows from the database as a list of tuples with the format (time, temperature)
        # and reversing the list so they in the correct order.
        rows = self.aqtassistant_db.get_sensor_data("time, temperature", n_data)[::-1]

        # Extracting the time from every row and adding two hours to get the correct local time.
        self.x = [row[0] + datetime.timedelta(hours=2) for row in rows]

        # Extracting the temperature from every row and casting from Decimal to float.
        self.y = [float(row[1]) for row in rows]

        # Plotting the data by converting the datetime objects from the database into numbers that matplotlib can plot.
        self.graphWidget.canvas.ax.plot_date(matplotlib.dates.date2num(self.x), self.y, 'r')

        # Drawing the canvas with all the plot configurations.
        self.draw_plot()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        """Updating the plot with the latest row in the database."""
        # Getting a tuple with the format (time, temperature).
        latest = self.aqtassistant_db.get_sensor_data("time, temperature", 1)[0]

        # Removing the oldest element and adding the latest for both time and temperature.
        self.x = self.x[1:] + [latest[0] + datetime.timedelta(hours=2)]
        self.y = self.y[1:] + [float(latest[1])]

        # Clear the canvas.
        self.graphWidget.canvas.ax.cla()

        # Plotting the data by converting the datetime objects from the database into numbers that matplotlib can plot.
        self.graphWidget.canvas.ax.plot_date(matplotlib.dates.date2num(self.x), self.y, 'r')

        # Redrawing the canvas with all the plot configurations.
        self.draw_plot()

    def draw_plot(self):
        """Drawing the canvas completely with all canvas specific configurations."""
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
