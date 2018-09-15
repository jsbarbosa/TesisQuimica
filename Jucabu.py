from serial import Serial, PARITY_EVEN, SEVENBITS
from serial.tools import list_ports
import serial

ports = list(list_ports.comports())
for p in ports:
    print(p)

serial = Serial("/dev/ttyUSB0", baudrate = 9600, timeout = 1, bytesize = serial.SEVENBITS,  xonxoff = True)
#, parity = PARITY_EVEN, bytesize = SEVENBITS, rtscts = True,

def getMessage(command, value = ''):
	if value != '':
		command += " " + str(value)
	command += " \n"
	return [ord(c) for c in command]

command = getMessage("version")

while True:
	try:
		serial.write(command)
		l = serial.readline()
		print(l)
	except:
		break

serial.close()
