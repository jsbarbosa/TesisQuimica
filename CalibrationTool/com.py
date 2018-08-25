from serial import Serial
import serial.tools.list_ports as find_ports

START = 0x02
SET_CHANNEL_0 0x03
SET_CHANNEL_1 0x04
SET_CHANNEL_2 0x05
SET_CHANNEL_3 0x06
NAME 0x0f

BAUDRATE = 9600
TIMEOUT = 0.2

def testName(serial):
    serial.write([NAME])
    ans = serial.readline()
    if "Rutherford" in ans:
        return True
    return False

def findDevices():
    ports_objects = list(find_ports.comports())
    devs = []
    for port in ports:
        port = port.device
        ser = Serial(port = port, baudrate = BAUDRATE, timeout = TIMEOUT)
        if testName(ser):
            devs.append(port)
        ser.close()
    return devs

devs = findDevices()
print(devs)
#
# DTS = []
#
# def reader():
#     last = time.time()
#     while True:
#         try:
#             bytes = serial.read(2)
#             now = time.time()
#             dt = now - last
#             last = now
#             if len(bytes):
#                 print("\n>>>", bytes)
#                 DTS.append(dt)
#                 if (len(bytes) == 2):
#                     value = (bytes[0] << 8)
#                     value |= bytes[1]
#                     print(value)
#         except KeyboardInterrupt:
#             break

#
#
# baudrate = 9600
# serial = serial.Serial(port = port, baudrate = baudrate, timeout = 0.2)
#
# thread = Thread(target = reader, daemon = True)
# thread.start()
#
# while True:
#     try:
#         command = int(input("Command: "), 16)
#         serial.write([command])
#     except KeyboardInterrupt:
#         break
#
# mean_dt = sum(DTS) / len(DTS)
# print("Mean dt: %.1e, Frequency: %.1e"%(mean_dt, 1/mean_dt))
#
# for i in range(15):
#     sleep(1e-2)
#     serial.write([STOP])
#
# serial.close()
