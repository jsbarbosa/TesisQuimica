import os
from time import sleep, gmtime, strftime
from com import initPort, findDevices, setChannel, getVoltage, setGlobalSerial, close

TIME = 10 # seconds
ADJUST_TIME = 0.4 # seconds

FILE_ROOT = "TemperatureData"
EXTENSION = ".txt"

FILE_NAME = FILE_ROOT + EXTENSION

if os.path.exists(FILE_NAME):
    i = 0
    FILE_NAME = "%s_%d%s"%(FILE_ROOT, i, EXTENSION)
    while os.path.exists(FILE_NAME):
        FILE_NAME = "%s_%d%s"%(FILE_ROOT, i, EXTENSION)
        i += 1

with open(FILE_NAME, "w") as file:
    file.write("Date\tChannel1\tChannel2\tChannel3\r\n")
    pass

print("File name:", FILE_NAME)

while True:
    devs = findDevices()
    if len(devs) == 1:
        try:
            setGlobalSerial(initPort(devs[0]))
            break
        except Exception as e:
            print(e)
            setGlobalSerial(None)
            sleep(1)
    else:
        print(len(devs), devs)
        setGlobalSerial(None)
        sleep(1)

print(devs[0])

while True:
    adjust = TIME / 3 - ADJUST_TIME
    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    if adjust < 0: adjust = 0
    try:
        values = [now]
        for i in range(1, 4):
            setChannel(i)
            values.append("%.5f" % getVoltage())
            sleep(adjust)
        with open(FILE_NAME, "a") as file:
            line = "\t".join(values) + "\r\n"
            file.write(line)

    except Exception as e:
        print(e)
