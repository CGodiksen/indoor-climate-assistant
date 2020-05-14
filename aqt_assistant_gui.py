import random

from PyQt5 import QtWidgets, uic, QtCore
import sys

from PyQt5.QtCore import QThreadPool

from database import Database
from worker import Worker
import matplotlib
import datetime


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('mainwindow.ui', self)

        # Setting up the thread pool that will handle the threads that are created when initializing a new plot
        # and updating the existing plot.
        self.threadpool = QThreadPool()

        self.aqtassistant_db = Database()

        self.graphWidget.canvas.fig.suptitle("Living room", fontsize=16)

        self.x = []
        self.y = []
        self.initialize_plot()

        # Initializing an new plot if the data setting is changed.
        self.dataComboBox.currentIndexChanged.connect(self.initialize_plot)

        # Initializing a new plot if the time frame setting is changed.
        self.timeFrameComboBox.currentIndexChanged.connect(self.initialize_plot)

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def initialize_plot(self):
        """Initialize a plot according to the settings set in the GUI. This is called every time the settings change."""
        # Getting the settings from the GUI and converting them into interval values that can be used for querying.
        number_rows = self.convert_time_frame(self.timeFrameComboBox.currentText())
        data_name = self.convert_data_name(self.dataComboBox.currentText())

        # Getting the last n rows from the database as a list of tuples with the format (time, temperature)
        # and reversing the list so they in the correct order.
        rows = self.aqtassistant_db.get_sensor_data("time, " + data_name, number_rows)[::-1]

        # Extracting the time from every row and adding two hours to get the correct local time.
        self.x = [row[0] + datetime.timedelta(hours=2) for row in rows]

        # Extracting the temperature from every row and casting from Decimal to float.
        self.y = [float(row[1]) for row in rows]

        # Plotting the data by converting the datetime objects from the database into numbers that matplotlib can plot.
        self.graphWidget.canvas.ax.plot_date(matplotlib.dates.date2num(self.x), self.y, 'r')

        # Drawing the canvas with all the plot configurations.
        self.draw_plot()

    def update_plot(self):
        """Updating the plot with the latest row in the database."""
        data_name = self.convert_data_name(self.dataComboBox.currentText())

        # Getting a tuple with the format (time, temperature).
        latest = self.aqtassistant_db.get_sensor_data("time, " + data_name, 1)[0]

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
        self.graphWidget.canvas.ax.set_ylabel(self.dataComboBox.currentText())
        self.graphWidget.canvas.draw()

    @staticmethod
    def convert_time_frame(time_frame):
        """
        Converts the time frame from the combobox into an internal value that can be used to query the corresponding
        amount of rows from the database. The value corresponds to the number of seconds in the time frame.

        :param time_frame: The time frame that we convert into a value.
        :return: The value that corresponds to the time_frame argument.
        """
        return {
            "Now": 3600,
            "Today": 86400,
            "This week": 604800,
            "This month": 2629744,
            "This year": 31556926,
            # Using a number that is large enough to ensure that all rows are queried.
            "All time": 946707779
        }[time_frame]

    @staticmethod
    def convert_data_name(data_name):
        """
        Converts the data name from the combobox into an internal value that can be used to query the corresponding
        columns from the database.

        :param data_name: The data name from the combobox that we convert into a column name.
        :return: The column name that corresponds to the data_name argument.
        """
        return {
            "Air quality": "airquality",
            "Temperature": "temperature",
            "Air pressure": "airpressure",
            "Gas resistance": "gasresistance",
            "Humidity": "humidity",
        }[data_name]


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':         
    main()
