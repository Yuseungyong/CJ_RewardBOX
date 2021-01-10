import sys, os
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
from threading import Timer

file_off = open("STEP_offset.txt", 'w')
file_off.write("0")
file_off.close()

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111, xlim=(0, 100), ylim=(0, 200))

        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def compute_initial_figure(self):
        pass


class AnimationWidget(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        vbox = QVBoxLayout()
        self.canvas = MyMplCanvas(self, width=10, height=8, dpi=100)
        # self.stepNumber = QLCDNumber(self)
        vbox.addWidget(self.canvas)
        # vbox.addWidget(self.stepNumber)
        hbox = QHBoxLayout()
        self.start_button = QPushButton("start", self)
        self.stop_button = QPushButton("stop", self)
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.stop_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.x = np.arange(100)
        self.y = np.ones(100, dtype=np.float) * np.nan
        self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, lw=2)


    def update_line(self, i):
        file = open("BPM_output.txt", 'r')
        data = file.read()
        try:
            y = float(data)
            old_y = self.line.get_ydata()
            new_y = np.r_[old_y[1:], y]
            self.line.set_ydata(new_y)

        except:
            pass

        return [self.line]
        # self.line.set_ydata(y)

    def on_start(self):
        self.ani = animation.FuncAnimation(self.canvas.figure, self.update_line, blit=True, interval=25)

    def on_stop(self):
        self.ani._stop()


class StepMonitor(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        vbox = QVBoxLayout()
        self.stepNumber = QLCDNumber(self)
        self.stepNumber.setDigitCount(4)
        vbox.addWidget(self.stepNumber)
        hbox = QHBoxLayout()
        self.reset_button = QPushButton("reset", self)
        self.stop_button = QPushButton("stop", self)
        # self.reset_button.resize(150, 300)
        self.reset_button.clicked.connect(self.on_reset)
        self.stop_button.clicked.connect(self.on_stop)
        hbox.addWidget(self.reset_button)
        hbox.addWidget(self.stop_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.showStepNum()

    def on_reset(self):
        file = open("STEP_output.txt", 'r')
        data = file.read()
        file_off = open("STEP_offset.txt", 'w')
        file_off.write(data)
        file_off.close()

    def on_stop(self):
        self.ani._stop()


    def showStepNum(self):
        file = open("STEP_output.txt", 'r')
        file_off = open("STEP_offset.txt", 'r')
        data = file.read()
        offset = file_off.read()
        offset_int = int(offset)
        print(data)
        try:
            step = int(data)
            step = step - offset_int
            self.stepNumber.display(step)
        except:
            pass
        timer = Timer(1, self.showStepNum)
        timer.start()

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setGeometry(100, 100, 350, 250)

        self.tab_widget = RewardBox(self)
        self.setCentralWidget(self.tab_widget)

        self.show()

class RewardBox(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout()

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        # Add tabs
        self.tabs.addTab(self.tab1, "BPM")
        self.tabs.addTab(self.tab2, "STEP")

        # Create first tab
        self.BPM_plot = AnimationWidget()

        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addWidget(self.BPM_plot)
        self.tab1.setLayout(self.tab1.layout)

        # Create second tab
        self.STEP_monitor = StepMonitor()
        self.tab2.layout = QVBoxLayout(self)
        self.tab2.layout.addWidget(self.STEP_monitor)
        self.tab2.setLayout(self.tab2.layout)



        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    aw = App()
    aw.show()
    sys.exit(qApp.exec_())