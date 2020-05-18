import datetime
import json
import os.path
import sys

import matplotlib
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QThreadPool

from database import Database
from system_tray import SystemTray


# TODO: Maybe lock the position of the legend box.
# TODO: Dark mode?
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('mainwindow.ui', self)

        # Loading the GUI settings from the persistent json file if it exists.
        if os.path.isfile("settings.json"):
            self.load_settings()

        # Setting up the thread pool that will handle the threads that are created when initializing a new plot
        # and updating the existing plot.
        self.threadpool = QThreadPool()

        # Setting up the system tray icon.
        self.system_tray = SystemTray()

        # Setting up the database object that can be used to query from the livingroom database.
        self.aqtassistant_db = Database()

        self.graphWidget.canvas.fig.suptitle("Living room", fontsize=16)

        self.x = []
        self.y = []
        self.initialize_plot()

        # Initializing a new plot if any of the settings are changed.
        self.dataComboBox.currentIndexChanged.connect(self.initialize_plot)
        self.timeFrameComboBox.currentIndexChanged.connect(self.initialize_plot)
        self.aqMinSpinBox.valueChanged.connect(self.initialize_plot)
        self.tMinSpinBox.valueChanged.connect(self.initialize_plot)
        self.tMaxSpinBox.valueChanged.connect(self.initialize_plot)

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def save_settings(self):
        """Saving the settings from the GUI in a persistent json file."""
        settings = {
            "data": self.dataComboBox.currentText(),
            "time frame": self.timeFrameComboBox.currentText(),
            "AQ min threshold": self.aqMinSpinBox.value(),
            "T min threshold": self.tMinSpinBox.value(),
            "T max threshold": self.tMaxSpinBox.value()
        }

        with open("settings.json", "w+") as file:
            json.dump(settings, file)

    def load_settings(self):
        """Loading the settings from the persistent json file and using it to initialize the GUI."""
        with open("settings.json", "r+") as file:
            settings = json.load(file)

        self.dataComboBox.setCurrentIndex(self.dataComboBox.findText(settings["data"]))
        self.timeFrameComboBox.setCurrentIndex(self.timeFrameComboBox.findText(settings["time frame"]))
        self.aqMinSpinBox.setValue(settings["AQ min threshold"])
        self.tMinSpinBox.setValue(settings["T min threshold"])
        self.tMaxSpinBox.setValue(settings["T max threshold"])

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

        # Drawing the canvas with all the plot configurations.
        self.draw_plot()

        # Since this is called when the settings change we save the updated settings to the persistent json file.
        self.save_settings()

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

        # Redrawing the canvas with all the plot configurations.
        self.draw_plot()

        # Finally we check if the warning thresholds have been crossed and send out a warning if yes.
        self.check_warnings()

    def draw_plot(self):
        """Drawing the plot completely by plotting the data and drawing the canvas specific stuff like labels."""
        # Plotting the data by converting the datetime objects from the database into numbers that matplotlib can plot.
        self.graphWidget.canvas.ax.plot_date(matplotlib.dates.date2num(self.x), self.y, 'r')

        data_name = self.dataComboBox.currentText()

        # If we are plotting air quality we draw the min air quality threshold.
        if data_name == "Air quality":
            min_line = self.graphWidget.canvas.ax.axhline(y=self.aqMinSpinBox.value(), label="Min threshold")

            self.graphWidget.canvas.ax.legend(handles=[min_line])

        # If we are plotting temperature we draw the min and max temperature thresholds.
        if data_name == "Temperature":
            min_line = self.graphWidget.canvas.ax.axhline(y=self.tMinSpinBox.value(), label="Min threshold")
            max_line = self.graphWidget.canvas.ax.axhline(y=self.tMaxSpinBox.value(), label="Max threshold",
                                                          color="red")

            self.graphWidget.canvas.ax.legend(handles=[min_line, max_line])

        # Setting the x and y label.
        self.graphWidget.canvas.ax.set_xlabel("Time")
        self.graphWidget.canvas.ax.set_ylabel(self.dataComboBox.currentText())

        self.graphWidget.canvas.draw()

    def check_warnings(self):
        """Checks if the warning thresholds have been crossed. If so we send a warning to the user."""
        # Getting the latest air quality and temperature from the database.
        air_quality, temperature = self.aqtassistant_db.get_sensor_data("airquality, temperature", 1)[0]

        title = ""
        message = ""
        # If the air quality is below the min threshold we add it to the warning.
        if air_quality < self.aqMinSpinBox.value():
            title += " Low air quality "
            message += "Air quality is too low: " + str(air_quality) + "%\n"

        # If the temperature is below the min threshold we add it to the warning.
        if temperature < self.tMinSpinBox.value():
            title += " Low temperature "
            message += "Temperature is too low: " + str(temperature) + "°C\n"

        # If the temperature is above the max threshold we add it to the warning.
        if temperature > self.tMaxSpinBox.value():
            title += " High temperature "
            message += "Temperature is too high: " + str(temperature) + "°C\n"

        if title != "" and message != "":
            self.system_tray.show_warning(title, message)

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
