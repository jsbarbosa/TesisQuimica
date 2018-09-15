from time import sleep
from serial import Serial
import serial.tools.list_ports as find_ports

GET_ADC = 0x02
SET_CHANNEL_0 = 0x03
SET_CHANNEL_1 = 0x04
SET_CHANNEL_2 = 0x05
SET_CHANNEL_3 = 0x06
NAME = 0x0f

BAUDRATE = 115200
TIMEOUT = 0.2

SERIAL = None

V_REF = 1.1

LAST_CHANNEL = -1

class NoActiveSerialException(Exception):
    """
        There is no serial port active.
    """
    def __init__(self):
        super(Exception, self).__init__("There is no serial port active.")

class InvalidCalibrationPort(Exception):
    """
        Not a calibration port.
    """
    def __init__(self, port):
        super(Exception, self).__init__("%s is not a calibration port."%port)

class ADCException(Exception):
    """
        Critical error. It was not possible to retrieve a valid ADC value.
    """
    def __init__(self):
        super(Exception, self).__init__("Critical error. It was not possible to retrieve a valid ADC value.")

def testName(serial):
    serial.write([NAME])
    sleep(0.2)
    ans = serial.readline()
    try:
        ans = ans.decode()
    except:
        return False
    if "Rutherford" in ans:
        return True
    return False

def findDevices():
    ports = list(find_ports.comports())
    devs = []
    for port in ports:
        port = port.device
        try:
            ser = initPort(port)
            devs.append(port)
            ser.close()
        except Exception as e:
            print(e)
            # pass
    return devs

def initPort(port):
    ser = Serial(port = port, baudrate = BAUDRATE, timeout = TIMEOUT)
    if testName(ser):
        return ser
    else:
        ser.close()
        raise(InvalidCalibrationPort(port))

def setChannel(channel):
    global SERIAL, LAST_CHANNEL
    if LAST_CHANNEL != channel:
        LAST_CHANNEL = channel
        if (channel <= 3) and (channel >= 0):
            try:
                SERIAL.write([SET_CHANNEL_0 + channel])
            except AttributeError:
                raise(NoActiveSerialException())
        else:
            raise(Exception("%d is not a valid channel."%channel))

def getADC():
    for i in range(5):
        SERIAL.write([GET_ADC])
        try:
            high = SERIAL.read()[0]
            if high <= 3:
                low = SERIAL.read()[0]
                return (high << 8) | low
        except IndexError:
            pass
    raise(ADCException())

def getVoltage():
    global V_REF
    return V_REF * getADC() / 1023

def setGlobalSerial(serial):
    global SERIAL
    SERIAL = serial

def close():
    global SERIAL
    try: SERIAL.close()
    except: pass

if __name__ == '__main__':
    devs = findDevices()
    print(devs)
    if len(devs) == 1:
        SERIAL = initPort(devs[0])

        while True:
            try:
                text = []
                for i in range(4):
                    setChannel(i)
                    val = getADC()
                    text.append("C%d: %d"%(i, val))
                text = "\t".join(text)
                print(text)

                sleep(5e-2)
            except KeyboardInterrupt:
                break

        SERIAL.close()
