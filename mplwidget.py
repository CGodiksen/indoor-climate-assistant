"""Defining the matplotlib widget that is used in the gui to display a matplotlib graph."""
from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib

# Ensure using PyQt5 backend.
matplotlib.use('QT5Agg')


# Matplotlib canvas class to create figure.
class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure(facecolor="#19232d")
        self.ax = self.fig.add_subplot(111)
        self.fig.set_tight_layout(True)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)


# Matplotlib widget.
class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.vbl = QtWidgets.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
