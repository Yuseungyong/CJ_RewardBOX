import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
from threading import Timer
import subprocess


file_off = open("STEP_offset.txt", 'w')
file_off.write("0")
file_off.close()

file = open("STEP_output.txt", 'w')
file.write("0")
file.close()


class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        
        self.axes = fig.add_subplot(111, xlim=(0, 100), ylim=(0, 200))
        self.axes.set_title("BPM", fontsize = 30)                                       # BPM font size
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
    def compute_initial_figure(self):
        pass

class AnimationWidget(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        vbox = QVBoxLayout()
        self.canvas = MyMplCanvas(self, width=10, height=8, dpi=100)
        self.BPM_button = QPushButton("BPM", self)
        self.STEP_button = QPushButton("STEP", self)
        self.LOCK_button = QPushButton("LOCK", self)

        # self.BPM_button.setMinimumWidth(2)
        # self.STEP_button.setMinimumWidth(2)
        # self.LOCK_button.setMinimumWidth(2)

        self.BPM_button.setMinimumSize( 1, 15)
        self.STEP_button.setMinimumSize( 1, 15)
        self.LOCK_button.setMinimumSize( 1, 15)

        self.BPM_button.clicked.connect(self.on_BPM)
        self.STEP_button.clicked.connect(self.on_STEP)
        self.LOCK_button.clicked.connect(self.on_LOCK)

        vbox3 = QHBoxLayout()
        vbox3.addStretch(10)
        vbox3.addWidget(self.BPM_button)
        vbox3.addWidget(self.STEP_button)
        vbox3.addWidget(self.LOCK_button)

        self.label2 = QLabel('REWARD BOX', self)
        self.label2.setAlignment(Qt.AlignCenter)
        font2 = self.label2.font()
        font2.setPointSize(15)                                                          # REWARDBOX font size
        self.label2.setFont(font2)

        self.label1 = QLabel('STEP:', self)
        self.label1.setAlignment(Qt.AlignRight)                                         #STEP font alignment
        font1 = self.label1.font()
        font1.setPointSize(30)                                                         #STEP font size
        self.label1.setFont(font1)

        self.stepNumber = QLCDNumber(self)
        self.stepNumber.setDigitCount(3)                                                #STEP number digit
        self.stepNumber.setMinimumHeight(40)                                            #STEP number

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.label2, Qt.AlignCenter)
        vbox.addLayout(hbox2)
        vbox.addLayout(vbox3)
        vbox.addWidget(self.canvas)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.label1)
        hbox1.addWidget(self.stepNumber, Qt.AlignCenter)                                #STEP digit alignment
        vbox.addLayout(hbox1)
        hbox = QHBoxLayout()
        self.start_button = QPushButton("start", self)
        self.reset_button = QPushButton("reset", self)
        self.stop_button = QPushButton("stop", self)

        self.start_button.setMinimumHeight(50)
        self.reset_button.setMinimumHeight(50)
        self.stop_button.setMinimumHeight(50)

        self.start_button.clicked.connect(self.on_start)
        self.reset_button.clicked.connect(self.on_reset)
        self.stop_button.clicked.connect(self.on_stop)
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.reset_button)
        hbox.addWidget(self.stop_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.x = np.arange(100)
        self.y = np.ones(100, dtype=np.float)*np.nan
        self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, lw=2)
        
        self.showStepNum()

        
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
        self.ani = animation.FuncAnimation(self.canvas.figure, self.update_line,blit=True, interval=25)

    def on_reset(self):
        file = open("STEP_output.txt", 'r')
        data = file.read()
        file_off = open("STEP_offset.txt", 'w')
        file_off.write(data)
        file_off.close()

    def on_stop(self):
        self.ani._stop()

    def on_BPM(self):
        subprocess.call(["python", "bpm_subscriber.py"])

    def on_STEP(self):
        subprocess.call(["python", "step_subscriber.py"])

    def on_LOCK(self):
        subprocess.call(["python", "LOCK.py"])

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

def main():
    qApp = QApplication(sys.argv)
    aw = AnimationWidget()
    aw.showFullScreen()
    sys.exit(qApp.exec_())