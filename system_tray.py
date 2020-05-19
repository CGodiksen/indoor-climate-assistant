from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *


class SystemTray:
    """
    Class for creating the icon in the system tray icon.
    """
    def __init__(self):
        # Setting up the system tray icon itself.
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("resources/graph_icon.ico"))
        self.tray.setVisible(True)

        # Creating the menu.
        self.menu = QMenu()

        # Add the menu to the tray.
        self.tray.setContextMenu(self.menu)

    def show_warning(self, title, message):
        self.tray.showMessage(title, message, QIcon("resources/graph_icon.ico"))
