import GPUtil
import psutil
import serial
import serial.tools.list_ports
from threading import Thread
import time
import sys, warnings

graphSize = 16
blank = "░"
filled = "▓"


class Monitor(Thread):
    def __init__(self, delay):
        super(Monitor, self).__init__()
        self.stopped = False
        self.delay = delay # Time between calls to GPUtil
        self.start()

    def run(self):
        while not self.stopped:
            startTime = time.time()
            DoUpdate()
            elapsedTime = time.time()-startTime
            time.sleep(max(self.delay-elapsedTime,0.01))

    def stop(self):
        self.stopped = True

def repeatCharacter(Char,reps):
    returnString = ""
    for _ in range(reps):
        returnString += Char
    return returnString

def GetFirstArduino():
    print("Finding Arduino...")
    arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'Arduino' in p.description  # may need tweaking to match new arduinos
    ]
    if not arduino_ports:
        warnings.warn("No Arduino found")
        return 0
    if len(arduino_ports) > 1:
        warnings.warn('Multiple Arduinos found - using the first')
    print("Using Arduino on "+str(arduino_ports[0]))
    return arduino_ports[0]

def DoUpdate():
    CPU = round(psutil.cpu_percent(),2)
    RAM = round(dict(psutil.virtual_memory()._asdict()).get('percent'),2)
    GPUmem = GPUtil.getGPUs()[0].memoryUsed/GPUtil.getGPUs()[0].memoryTotal
    GPUmem = round(GPUmem * 100,2)
    GPULoad = GPUtil.getGPUs()[0].load
    GPULoad = round(GPULoad * 100,2)

    print()
    print()
    print("CPU Avrg:   "+str(CPU)+"%")
    print("RAM Usage:  "+str(RAM)+"%")
    print("GPU0 Usage: "+str(GPULoad)+"%")
    print("GPU0 mem:   "+str(GPUmem)+"%")
    #print("GPU0 Usage: "+"{:.2%}".format(GPULoad))
    #print("GPU0 Mem:   "+"{:.2%}".format(GPUmem))


    workString = ""
    filledNumber = 0
    #CPU graph
    filledNumber = int(round(CPU/100*graphSize,0))
    workString = repeatCharacter(filled,filledNumber)
    workString += repeatCharacter(blank,graphSize-filledNumber)
    print("CPU Load: "+workString)
    filledNumber = int(round(RAM/100*graphSize,0))
    workString = repeatCharacter(filled,filledNumber)
    workString += repeatCharacter(blank,graphSize-filledNumber)
    print("RAM Usage:"+workString)

    #GPU Graph
    filledNumber = int(round(GPULoad/100*graphSize,0))
    workString = repeatCharacter(filled,filledNumber)
    workString += repeatCharacter(blank,graphSize-filledNumber)
    print("GPU Load: "+workString)
    filledNumber = int(round(GPUmem/100*graphSize,0))
    workString = repeatCharacter(filled,filledNumber)
    workString += repeatCharacter(blank,graphSize-filledNumber)
    print("GPU Mem:  "+workString)

    if ser.is_open:
        ExportString = str(delay) + "," + str(CPU) + "," + str(RAM) + "," + str(GPULoad) + "," + str(GPUmem)
        ser.write(ExportString.encode())
        print(ser.readline().strip().decode())
    else:
        print("Serial Unavailable.")
        #ser = OpenComPort(ser)

def OpenComPort(ser):
    #open serial comms
    try:
        #ser = serial.Serial()
        COMPort = sys.argv[2]
        if COMPort == "None":
            return ser
    except:
        COMPort = GetFirstArduino()
        #COMPort = "COM5"

    if COMPort != 0:
        ser = serial.Serial(COMPort, 9600, bytesize = 8, parity = 'O', stopbits = 2, timeout = 0)
        #ser.baudrate = 9600
        #ser.open()
        while ser.is_open == False:
            print("Waiting For Serial...")
            #waste time
        print("Serial Open")
        #Exchange pleasantries
        print(ser.readline().strip().decode())

    #wait a second for it to settle
    time.sleep(2.5)
    return ser









#ACTUAL CODE STARTS HERE
#First argument is time between updates in seconds
try:
    delay = float(sys.argv[1])
except:
    delay = 1

#open serial comms
ser = serial.Serial()
ser = OpenComPort(ser)

#open the resource monitor class
monitor = Monitor(delay)

while True:
    i = input("Press enter to quit.")
    if not i:
        break
    #DoUpdate()
    #time.sleep(delay)

#time.sleep(10)
# Close monitor
monitor.stop()

if ser.is_open:
    ser.close()