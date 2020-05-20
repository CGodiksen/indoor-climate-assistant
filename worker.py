from PyQt5.QtCore import *


class Worker(QRunnable):
    """
    Worker that can run a function in a separate thread. Inherits from QRunnable to handler worker thread setup.
    """
    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()

        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """"Running the runner function with passed args, kwargs."""
        self.function(*self.args, **self.kwargs)
