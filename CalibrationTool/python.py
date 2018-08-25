import serial
from time import sleep
import serial.tools.list_ports as find_ports

ports_objects = list(find_ports.comports())
port = ports_objects[0].device

serial = serial.Serial(port = port, baudrate = 9600, timeout = 1)

while True:
    try:
        val = int(input("Val: "), 16)
        serial.write(val)
        byte = serial.read(2)
        print(byte)
    except KeyboardInterrupt:
        break

serial.close()
