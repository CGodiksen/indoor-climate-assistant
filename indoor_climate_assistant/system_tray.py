from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5 import QtCore


class SystemTray:
    """
    System tray icon that is used to access the application when it is closed.
    """
    def __init__(self, main_window, database, app):
        self.main_window = main_window
        self.aqt_assistant_db = database
        self.app = app

        # Setting up the system tray icon itself.
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("../resources/graph_icon.ico"))
        self.tray.setVisible(True)

        # Opening the main window when the tray icon is double clicked. We only want to call show() if the activation
        # reason is 2, meaning that the icon was double clicked.
        self.tray.activated.connect(
            lambda activation_reason: self.main_window.show() if activation_reason == 2 else None)

        # Creating the menu.
        self.menu = QMenu()

        # Creating an action that opens the main window.
        self.open_window_action = QAction("Open")
        self.open_window_action.triggered.connect(self.main_window.show)
        self.menu.addAction(self.open_window_action)

        # Creating an action that exits the application
        self.exit_app_action = QAction("Exit")
        self.exit_app_action.triggered.connect(self.app.exit)
        self.menu.addAction(self.exit_app_action)

        # Separating the default actions and the application specific actions.
        self.menu.addSeparator()

        # Creating an action that toggles the air quality warning.
        self.aq_warning_action = QAction("Air quality warning")
        self.aq_warning_action.setCheckable(True)
        self.aq_warning_action.setChecked(self.main_window.aqWarningCheckBox.isChecked())
        self.aq_warning_action.toggled.connect(self.main_window.aqWarningCheckBox.setChecked)
        self.menu.addAction(self.aq_warning_action)

        # Creating an action that toggles the temperature warning.
        self.t_warning_action = QAction("Temperature warning")
        self.t_warning_action.setCheckable(True)
        self.t_warning_action.setChecked(self.main_window.tWarningCheckBox.isChecked())
        self.t_warning_action.toggled.connect(self.main_window.tWarningCheckBox.setChecked)
        self.menu.addAction(self.t_warning_action)

        # Add the menu to the tray.
        self.tray.setContextMenu(self.menu)

        # Setup a timer to trigger the warning check every 10 minutes.
        self.warning_check_timer = QtCore.QTimer()
        self.warning_check_timer.setInterval(600000)
        self.warning_check_timer.timeout.connect(self.check_warnings)
        self.warning_check_timer.start()

    def check_warnings(self):
        """Checks if the warning thresholds have been crossed. If so we send a warning to the user."""
        # Getting the latest air quality and temperature from the database.
        air_quality, temperature = self.aqt_assistant_db.get_sensor_data("airquality, temperature", 1)[0]

        title = ""
        message = ""

        # If the user wants air quality warnings we check it.
        if self.main_window.aqWarningCheckBox.isChecked():
            # If the air quality is below the min threshold we add it to the warning.
            if air_quality < self.main_window.aqMinSpinBox.value():
                title += " Low air quality "
                message += "Air quality is too low: " + str(air_quality) + "%\n"

        # If the user wants temperature warnings we check it.
        if self.main_window.tWarningCheckBox.isChecked():
            # If the temperature is below the min threshold we add it to the warning.
            if temperature < self.main_window.tMinSpinBox.value():
                title += " Low temperature "
                message += "Temperature is too low: " + str(temperature) + "°C\n"

            # If the temperature is above the max threshold we add it to the warning.
            if temperature > self.main_window.tMaxSpinBox.value():
                title += " High temperature "
                message += "Temperature is too high: " + str(temperature) + "°C\n"

        if title != "" and message != "":
            self.tray.showMessage(title, message, QIcon("../resources/graph_icon.ico"))
