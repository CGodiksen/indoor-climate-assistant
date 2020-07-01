import datetime
import json
import os.path

import matplotlib
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QThreadPool


class MainWindow(QtWidgets.QMainWindow):
    """
    Main window that represents the visible window the application runs in.
    """
    def __init__(self, database, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.aqt_assistant_db = database

        # Load the UI Page
        uic.loadUi("resources/mainwindow.ui", self)

        # Loading the GUI settings from the persistent json file if it exists.
        if os.path.isfile("resources/settings.json"):
            self.load_settings()

        self.x = []
        self.y = []
        self.initialize_plot()

        # Initializing a new plot if any of the plot changing settings are changed.
        self.dataComboBox.currentIndexChanged.connect(self.initialize_plot)
        self.timeFrameComboBox.currentIndexChanged.connect(self.initialize_plot)
        self.aqMinSpinBox.valueChanged.connect(self.initialize_plot)
        self.tMinSpinBox.valueChanged.connect(self.initialize_plot)
        self.tMaxSpinBox.valueChanged.connect(self.initialize_plot)

        # Saving the settings if non plot changing settings are changed.
        self.aqWarningCheckBox.toggled.connect(self.save_settings)
        self.tWarningCheckBox.toggled.connect(self.save_settings)

        # Setup a timer to trigger the redraw every minute by calling update_plot.
        self.update_plot_timer = QtCore.QTimer()
        self.update_plot_timer.setInterval(60000)
        self.update_plot_timer.timeout.connect(self.update_plot)
        self.update_plot_timer.start()

    def save_settings(self):
        """Saving the settings from the GUI in a persistent json file."""
        settings = {
            "data": self.dataComboBox.currentText(),
            "time frame": self.timeFrameComboBox.currentText(),
            "air quality warning": self.aqWarningCheckBox.isChecked(),
            "air quality min threshold": self.aqMinSpinBox.value(),
            "temperature warning": self.tWarningCheckBox.isChecked(),
            "temperature min threshold": self.tMinSpinBox.value(),
            "temperature max threshold": self.tMaxSpinBox.value()
        }

        with open("resources/settings.json", "w+") as file:
            json.dump(settings, file)

    def load_settings(self):
        """Loading the settings from the persistent json file and using it to initialize the GUI."""
        with open("resources/settings.json", "r+") as file:
            settings = json.load(file)

        self.dataComboBox.setCurrentIndex(self.dataComboBox.findText(settings["data"]))
        self.timeFrameComboBox.setCurrentIndex(self.timeFrameComboBox.findText(settings["time frame"]))
        self.aqWarningCheckBox.setChecked(settings["air quality warning"])
        self.aqMinSpinBox.setValue(settings["air quality min threshold"])
        self.tWarningCheckBox.setChecked(settings["temperature warning"])
        self.tMinSpinBox.setValue(settings["temperature min threshold"])
        self.tMaxSpinBox.setValue(settings["temperature max threshold"])

    def initialize_plot(self):
        """Initialize a plot according to the settings set in the GUI. This is called every time the settings change."""
        # Getting the settings from the GUI and converting them into interval values that can be used for querying.
        number_rows = self.convert_time_frame(self.timeFrameComboBox.currentText())
        data_name = self.convert_data_name(self.dataComboBox.currentText())

        # Getting the last n rows from the database as a list of tuples with the format (time, data) and reversing
        # the list so they in the correct order.
        rows = self.aqt_assistant_db.get_sensor_data("time, " + data_name, number_rows)[::-1]

        # Extracting the time from every row and adding two hours to get the correct local time.
        self.x = [row[0] + datetime.timedelta(hours=2) for row in rows]

        # Extracting the data from every row and casting from Decimal to float.
        self.y = [float(row[1]) for row in rows]

        # Clear the canvas.
        self.graphWidget.canvas.ax.cla()

        # Drawing the canvas with all the plot configurations.
        self.draw_plot()

        # Since this is called when the settings change we save the updated settings to the persistent json file.
        self.save_settings()

    def update_plot(self):
        """Updating the plot with the latest row in the database."""
        data_name = self.convert_data_name(self.dataComboBox.currentText())

        # Getting a tuple with the format (time, temperature).
        latest = self.aqt_assistant_db.get_sensor_data("time, " + data_name, 1)[0]

        # Removing the oldest element and adding the latest for both time and temperature.
        self.x = self.x[1:] + [latest[0] + datetime.timedelta(hours=2)]
        self.y = self.y[1:] + [float(latest[1])]

        # Clear the canvas.
        self.graphWidget.canvas.ax.cla()

        # Redrawing the canvas with all the plot configurations.
        self.draw_plot()

    def draw_plot(self):
        """Drawing the plot completely by plotting the data and drawing the canvas specific stuff like labels."""
        # Plotting the data by converting the datetime objects from the database into numbers that matplotlib can plot.
        self.graphWidget.canvas.ax.plot_date(matplotlib.dates.date2num(self.x), self.y, 'r', color="#0088DE")

        data_name = self.dataComboBox.currentText()

        if data_name == "Air quality" or data_name == "Temperature":
            lines = []
            # If we are plotting air quality we draw the min air quality threshold.
            if data_name == "Air quality":
                lines.append(self.graphWidget.canvas.ax.axhline(y=self.aqMinSpinBox.value(), label="Min threshold",
                                                                color="#225DCF"))
            # If not, we are plotting temperature so we draw the min and max temperature thresholds.
            else:
                lines.append(self.graphWidget.canvas.ax.axhline(y=self.tMinSpinBox.value(), label="Min threshold",
                                                                color="#225DCF"))
                lines.append(self.graphWidget.canvas.ax.axhline(y=self.tMaxSpinBox.value(), label="Max threshold",
                                                                color="red"))

            # Setting the legend, including the background and edge color.
            legend = self.graphWidget.canvas.ax.legend(handles=lines, facecolor="#19232d", edgecolor="#19232d", loc=1)

            # Setting the font color of the labels in the legend.
            for text in legend.get_texts():
                text.set_color("white")

        # Setting the x and y label.
        self.graphWidget.canvas.ax.set_xlabel("Time", color="white", fontsize=12)
        self.graphWidget.canvas.ax.set_ylabel(self.dataComboBox.currentText(), color="white", fontsize=12)

        # Setting the color if the axis ticks.
        self.graphWidget.canvas.ax.tick_params(axis="x", colors="white")
        self.graphWidget.canvas.ax.tick_params(axis="y", colors="white")

        # Setting the background color of the plot itself.
        self.graphWidget.canvas.ax.set_facecolor("#19232d")

        self.graphWidget.canvas.draw()

    @staticmethod
    def convert_time_frame(time_frame):
        """
        Converts the time frame from the combobox into an internal value that can be used to query the corresponding
        amount of rows from the database. The value corresponds to the number of minutes in the time frame.

        :param time_frame: The time frame that we convert into a value.
        :return: The value that corresponds to the time_frame argument.
        """
        return {
            "Now": 60,
            "Today": 1440,
            "This week": 10080,
            "This month": 43829,
            "This year": 525949,
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
