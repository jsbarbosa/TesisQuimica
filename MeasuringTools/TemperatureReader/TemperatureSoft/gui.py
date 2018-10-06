import sys
import time

import __images__
from com import initPort, findDevices, setChannel, getTemperatures, setGlobalSerial, close, isSerialNone

import pyqtgraph as pg
try:
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QLabel, QWidget, QMainWindow, QHBoxLayout,\
            QGroupBox, QFormLayout, QSystemTrayIcon, QApplication, QMenu, QStyleFactory
except ImportError:
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QLabel, QWidget, QMainWindow, QHBoxLayout, \
            QGroupBox, QFormLayout, QSystemTrayIcon, QApplication, QMenu, QStyleFactory

import numpy as np

START_TIME = 0
KERNEL_FILTER = 3

MAX_HOLDER = 1e8

# https://gist.github.com/iverasp/9349dffa42aeffb32e48a0868edfa32d

class RingBuffer(object):
    def __init__(self, size_max):
        self.max = size_max
        self.data = []

    class __Full:
        """ class that implements a full buffer """
        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur+1) % self.max

        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:]+self.data[:self.cur]

    def append(self, x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            self.__class__ = self.__Full # Permanently change self's class from non-full to full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data

class DataHolder(object):
    def __init__(self):
        self.x = RingBuffer(MAX_HOLDER)
        self.y = [RingBuffer(MAX_HOLDER), RingBuffer(MAX_HOLDER), RingBuffer(MAX_HOLDER)]

    def addValues(self, temperatures):
        now = time.localtime()
        self.x.append(now)
        for i in range(3):
            self.y[i].append(temperatures[i])
        self.save()
        # if (len(self.y) > KERNEL_FILTER) and (KERNEL_FILTER > 0):
        #     temp = sorted(self.y[-KERNEL_FILTER:])[(KERNEL_FILTER - 1) // 2]
        #     self.y[-(KERNEL_FILTER - 1)] = temp

    def save(self):
        with open("TemperatureData.txt", "a") as file:
            now = time.strftime(strftime("%Y-%m-%d %H:%M:%S", self.getX()[-1]))
            data = ["%.2f"%self.getY(i)[-1] for i in range(3)]
            line = [now] + data
            file.write("\t".join(line) + "\r\n")

    def getX(self):
        return self.x.get()

    def getY(self, i):
        return self.y[i].get()

    def clear(self):
        self.x = []
        self.y = []

    def __len__(self):
        return len(self.x.get())

class FindDevicesThread(QtCore.QThread):
    def __init__(self):
        super(QtCore.QThread, self).__init__()

    def run(self):
        while True:
            if isSerialNone():
                devs = findDevices()
                if len(devs) == 1:
                    try:
                        setGlobalSerial(initPort(devs[0]))
                    except:
                        setGlobalSerial(None)
                else:
                    setGlobalSerial(None)
            else:
                time.sleep(10)

class RequestDataThread(QtCore.QThread):
    def __init__(self, holder):
        super(QtCore.QThread, self).__init__()
        self.holder = holder
        self.exception = None

    def run(self):
        global START_TIME
        while True:
            if not isSerialNone:
                try:
                    holder.addValues(getTemperatures())
                except Exception as e:
                    self.stop()
                    self.exception = e
            else:
                time.sleep(10)

    def stop(self):
        close()

class MainWindow(QMainWindow):
    SAMPLING_DEFAULT = 1 # seconds
    MINIMUM_PLOT_UPDATE = 2000

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle("Lector de temperatura")
        widget = QWidget()
        self.setCentralWidget(widget)

        self.main_layout = QHBoxLayout(widget)
        self.main_layout.setContentsMargins(11, 11, 11, 11)
        self.main_layout.setSpacing(6)

        self.settings_frame = QGroupBox()
        self.settings_layout = QFormLayout(self.settings_frame)

        self.label_0 = QLabel("00.00")
        self.label_1 = QLabel("00.00")
        self.label_2 = QLabel("00.00")
        self.settings_layout.addRow(self.label_0, QLabel("\tInterno (°C)"))
        self.settings_layout.addRow(self.label_1, QLabel("\tExterno (°C)"))
        self.settings_layout.addRow(self.label_2, QLabel("\tAmbiente (°C)"))

        self.main_layout.addWidget(self.settings_frame)
        ### pyqtgraph
        pg.setConfigOptions(foreground = 'k', background = None, antialias = True)
        self.temperature_plot_widget = pg.GraphicsWindow()
        self.main_layout.addWidget(self.temperature_plot_widget)

        self.temperature_plot = self.temperature_plot_widget.addPlot()
        self.temperature_plot.addLegend()

        self.temperature_plot.setLabel('left', "Temperature", units = '°C')
        self.temperature_plot.setLabel('bottom', "Time", units = 's')

        symbol = None #
        symbolSize = 3
        self.data0_line = self.temperature_plot.plot(pen = "b", symbol = symbol, symbolPen = "b", symbolBrush="b", symbolSize=symbolSize, name="Interno")
        self.data1_line = self.temperature_plot.plot(pen = "m", symbol = symbol, symbolPen = "m", symbolBrush="m", symbolSize=symbolSize, name="Externo")
        self.data2_line = self.temperature_plot.plot(pen = "g", symbol = symbol, symbolPen = "g", symbolBrush="g", symbolSize=symbolSize, name="Ambiente")

        #### signals
        self.update_plots_timer = QtCore.QTimer()
        self.update_plots_timer.setInterval(self.MINIMUM_PLOT_UPDATE)
        self.update_plots_timer.timeout.connect(self.updatePlots)

        self.find_thread = FindDevicesThread()
        self.find_thread.start()

        self.data = DataHolder()
        self.data_thread = RequestDataThread(self.data)
        self.data_thread.start()
        self.update_plots_timer.start()

    def updatePlots(self):
        if self.data_thread.exception != None:
            self.errorWindow(self.data_thread.exception)
        else:
            try:
                x = self.data.getX()
                for i in range(3):
                    label = getattr(self, "label_%d" % i)
                    plot = getattr(self, "data%d_line" % i)
                    data = self.data.getY(i)
                    plot.setData(x, data)
                    label.setText("%.2f"%data[-1])
            except Exception as e:
                print(e)

    def deviceConnection(self):
        if self.find_thread.success:
            self.deviceExists()
        else:
            self.noDevice()

    def noDevice(self):
        self.data_thread.stop()
        self.update_plots_timer.stop()

    def warning(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText('Warning.\n%s' % text)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def errorWindow(self, exception):
        self.noDevice()
        text = str(exception)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText('An error ocurred.\n%s' % text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent = None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)
        openAction = menu.addAction("Open")
        exitAction = menu.addAction("Exit")
        self.setContextMenu(menu)

        openAction.triggered.connect(self.openMain)
        exitAction.triggered.connect(self.exit)
        self.activated.connect(self.systemIcon)

        self.main_window = MainWindow()
        self.openMain()

    def exit(self):
        QtCore.QCoreApplication.exit()

    def systemIcon(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.openMain()

    def openMain(self):
        self.main_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion')) # <- Choose the style

    icon = QtGui.QIcon(':/icon.ico')
    app.setWindowIcon(icon)
    app.processEvents()

    w = QWidget()
    trayIcon = SystemTrayIcon(icon, w)

    trayIcon.show()
    app.exec_()

    close()
