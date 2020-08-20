from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWinExtras import QtWin

from main_window import MainWindow
from system_tray import SystemTray
from database import Database

import sys
import qdarkstyle
import mplwidget


def main():
    """
    Main function for the GUI that sets up the application, main window, database and system tray and starts the
    even loop. General settings regarding the application is also handled here.
    """
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("resources/graph_icon.ico"))

    # Changing the app id so our custom window icon is shown on the toolbar.
    QtWin.setCurrentProcessExplicitAppUserModelID("aqt_assistant.v1.0")

    # Ensuring that we do not stop the application when the main window is closed.
    app.setQuitOnLastWindowClosed(False)

    # Setting up the database object that can be used to query from the livingroom database.
    aqt_assistant_db = Database()

    # Setting up the main GUI window.
    main_window = MainWindow(aqt_assistant_db)

    # Setting up the system tray icon.
    system_tray = SystemTray(main_window, aqt_assistant_db, app)

    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
