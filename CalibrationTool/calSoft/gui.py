import sys
import time
from com import initPort, findDevices, setChannel, getVoltage, setGlobalSerial

import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets

START_TIME = 0

class DataHolder(object):
    def __init__(self):
        self.x = []
        self.y = []

    def addValue(self, value):
        global START_TIME
        self.y.append(value)
        self.x.append(time.time() - START_TIME)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def clear(self):
        self.x = []
        self.y = []

    def __len__(self):
        return len(self.x)

    # def getXDiff(self):
    #     global START_TIME
    #     diff = [self.x[i] - START_TIME for i in range(len(self))]
    #     return diff

class FindDevicesThread(QtCore.QThread):
    def __init__(self, parent):
        super(QtCore.QThread, self).__init__()
        self.parent = parent
        self.success = False

    def run(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        devs = findDevices()
        if len(devs) == 1:
            try:
                setGlobalSerial(initPort(devs[0]))
                self.success = True
            except:
                setGlobalSerial(None)
        else:
            setGlobalSerial(None)
        QtWidgets.QApplication.restoreOverrideCursor()

class MainWindow(QtWidgets.QMainWindow):
    FIND_LABEL = "Find device"
    FOUND_LABEL = "Device found"

    START_LABEL = "Start"
    STOP_LABEL = "Stop"

    SAMPLING_LABEL = "Sampling time (ms)"
    SAMPLING_MIN = 10
    SAMPLING_MAX = 10000
    SAMPLING_DEFAULT = 250

    def __init__(self):
        super(QtWidgets.QMainWindow, self).__init__()
        self.setWindowTitle("Calibration Software")
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)

        self.main_layout = QtWidgets.QHBoxLayout(widget)
        self.main_layout.setContentsMargins(11, 11, 11, 11)
        self.main_layout.setSpacing(6)

        self.settings_frame = QtWidgets.QGroupBox()
        self.settings_layout = QtWidgets.QFormLayout(self.settings_frame)

        self.sampling_widget = QtWidgets.QSpinBox()
        self.sampling_widget.setMaximum(self.SAMPLING_MAX)
        self.sampling_widget.setMinimum(self.SAMPLING_MIN)
        self.sampling_widget.setValue(self.SAMPLING_DEFAULT)

        self.find_device_widget = QtWidgets.QPushButton(self.FIND_LABEL)
        self.start_widget = QtWidgets.QPushButton(self.START_LABEL)

        self.channel_0_widget = QtWidgets.QCheckBox("Channel 0")
        self.channel_1_widget = QtWidgets.QCheckBox("Channel 1")
        self.channel_2_widget = QtWidgets.QCheckBox("Channel 2")
        self.channel_3_widget = QtWidgets.QCheckBox("Channel 3")

        self.clear_widget = QtWidgets.QPushButton("Clear plot")

        self.settings_layout.addRow(QtWidgets.QLabel(self.SAMPLING_LABEL), self.sampling_widget)
        self.settings_layout.addWidget(self.channel_0_widget)
        self.settings_layout.addWidget(self.channel_1_widget)
        self.settings_layout.addWidget(self.channel_2_widget)
        self.settings_layout.addWidget(self.channel_3_widget)
        self.settings_layout.addRow(self.find_device_widget, self.start_widget)
        self.settings_layout.addRow(self.clear_widget)

        self.main_layout.addWidget(self.settings_frame)

        ### pyqtgraph
        pg.setConfigOptions(foreground = 'k', background = None, antialias = True)
        self.adc_plot_widget = pg.GraphicsWindow()
        self.main_layout.addWidget(self.adc_plot_widget)

        self.adc_plot = self.adc_plot_widget.addPlot()
        self.adc_plot.addLegend()

        self.adc_plot.setLabel('left', "Voltage", units = 'V')
        self.adc_plot.setLabel('bottom', "Time", units = 's')

        symbolSize = 5
        self.data0_line = self.adc_plot.plot(pen = "b", symbol='o', symbolPen = "b", symbolBrush="b", symbolSize=symbolSize, name="Channel 0")
        self.data1_line = self.adc_plot.plot(pen = "m", symbol='o', symbolPen = "m", symbolBrush="m", symbolSize=symbolSize, name="Channel 1")
        self.data2_line = self.adc_plot.plot(pen = "g", symbol='o', symbolPen = "g", symbolBrush="g", symbolSize=symbolSize, name="Channel 2")
        self.data3_line = self.adc_plot.plot(pen = "r", symbol='o', symbolPen = "r", symbolBrush="r", symbolSize=symbolSize, name="Channel 3")

        #### signals
        self.sampling_widget.valueChanged.connect(self.changeSampling)
        self.find_device_widget.clicked.connect(self.findDevicesPush)
        self.start_widget.clicked.connect(self.startPush)
        self.clear_widget.clicked.connect(self.clearPlot)

        self.sampling_timer = QtCore.QTimer()
        self.sampling_timer.setInterval(self.SAMPLING_DEFAULT)
        self.sampling_timer.timeout.connect(self.samplingTimerTimeout)

        self.enableOnDevice(False)

        self.data0 = DataHolder()
        self.data1 = DataHolder()
        self.data2 = DataHolder()
        self.data3 = DataHolder()

    def samplingTimerTimeout(self):
        channels = self.getChannels()
        try:
            for channel in channels:
                setChannel(channel)
                holder = getattr(self, "data%d" % channel)
                holder.addValue(getVoltage())
                line = getattr(self, "data%d_line" % channel)
                line.setData(holder.getX(), holder.getY())
        except Exception as e:
            self.errorWindow(e)

    def changeSampling(self, value):
        self.sampling_timer.setInterval(value)

    def findDevicesPush(self):
        self.find_thread = FindDevicesThread(self)
        self.find_thread.finished.connect(self.deviceConnection)
        self.find_thread.start()

    def startPush(self):
        global START_TIME
        if self.start_widget.text() == self.START_LABEL:
            self.enableOnStart(False)
            self.sampling_timer.start()
            self.start_widget.setText(self.STOP_LABEL)

            if START_TIME == 0:
                START_TIME = time.time()
        else:
            self.enableOnStart(True)
            self.sampling_timer.stop()
            self.start_widget.setText(self.START_LABEL)

    def enableOnDevice(self, enable):
        self.start_widget.setEnabled(enable)
        self.enableOnStart(enable)
        self.find_device_widget.setEnabled(not enable)

    def enableOnStart(self, enable):
        pass
        # self.sampling_widget.setEnabled(enable)
        # self.channel_0_widget.setEnabled(enable)
        # self.channel_1_widget.setEnabled(enable)
        # self.channel_2_widget.setEnabled(enable)
        # self.channel_3_widget.setEnabled(enable)

    def deviceConnection(self):
        if self.find_thread.success:
            self.deviceExists()
        else:
            self.noDevice()

    def deviceExists(self):
        self.find_device_widget.setText(self.FOUND_LABEL)
        self.enableOnDevice(True)

    def noDevice(self):
        self.sampling_timer.stop()
        self.find_device_widget.setText(self.FIND_LABEL)
        self.enableOnDevice(False)

    def clearPlot(self):
        global START_TIME
        START_TIME = time.time()
        for channel in range(4):
            holder = getattr(self, "data%d" % channel)
            line = getattr(self, "data%d_line" % channel)
            holder.clear()
            line.setData(holder.getX(), holder.getY())

    def getChannels(self):
        channels = []
        for i in range(4):
            attr = getattr(self, "channel_%d_widget"%i)
            if attr.checkState():
                channels.append(i)
        return channels

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


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion')) # <- Choose the style

    # splash_pix = QtGui.QPixmap(':/splash.png').scaledToWidth(600)
    # splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    # splash.show()

    # icon = QtGui.QIcon(':/abacus_small.ico')
    # app.setWindowIcon(icon)
    app.processEvents()

    # if abacus.CURRENT_OS == 'win32':
    #     import ctypes
    #     myappid = 'abacus.abacus.01' # arbitrary string
    #     ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # sleep(1)
    #
    # softwareUpdate(splash)
    # splash.close()

    main = MainWindow()
    main.show()
    app.exec_()
        # frame = QtWidgets.QFrame()
        # frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # frame.setFrameShadow(QtWidgets.QFrame.Raised)
        #
        # horizontalLayout =  QtWidgets.QHBoxLayout(frame)
        # label = QtWidgets.QLabel("Save as:")
        #
        # self.save_as_lineEdit = ClickableLineEdit()
        # self.save_as_lineEdit.clicked.connect(self.chooseFile)
        #
        # self.save_as_button = QtWidgets.QPushButton("Open")
        #
        # horizontalLayout.addWidget(label)
        # horizontalLayout.addWidget(self.save_as_lineEdit)
        # horizontalLayout.addWidget(self.save_as_button)
        #
        # layout.addWidget(frame)
        #
        # frame2 = QtWidgets.QFrame()
        # layout2 = QtWidgets.QHBoxLayout(frame2)