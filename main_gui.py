from PyQt5 import QtWidgets
from main_window import MainWindow
import sys
import qdarkstyle


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()

    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    main_window.show()

    sys.exit(app.exec_())
