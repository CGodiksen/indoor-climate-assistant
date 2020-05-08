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
        self.xdata = list(range(n_data))
        self.ydata = [random.randint(0, 10) for i in range(n_data)]
        self.graphWidget.canvas.ax.plot(self.xdata, self.ydata, 'r')
        self.graphWidget.canvas.draw()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        # Drop off the first y element, append a new one.
        self.ydata = self.ydata[1:] + [random.randint(0, 10)]
        self.graphWidget.canvas.ax.cla()  # Clear the canvas.
        self.graphWidget.canvas.ax.plot(self.xdata, self.ydata, 'r')

        # Trigger the canvas to update and redraw.
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
