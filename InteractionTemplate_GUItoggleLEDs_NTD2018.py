from tkinter import *
from time import sleep
import datetime
from math import *
import sys
import serial
from matplotlib import pyplot as plotting
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

myWindow = Tk()
myWindow.title("this is myWindow")

# For plotting y against x, you need two arrays
x_array = []
y_array = []

# configuring the chart
style.use('ggplot')
fig = plotting.figure(figsize=(9, 3.0), dpi=100)
ax1 = fig.add_subplot(1, 1, 1) #(Row, column, position_of_this_figure. You could add more charts...)
ax1.set_ylim(20, 35) # fixed temperature interval on the y-axis
line, = ax1.plot(x_array, y_array, 'r', marker='o')

#-----finding the COM port the Arduino is connected to, on windows.
ComPorts=range(1,63)
ValidPorts=[]
for ComPort in ComPorts:
    namn='COM'+str(ComPort)
    try:
        testConn=serial.Serial(namn, 9600, timeout=1)
        if testConn:
            #print(namn)
            ValidPorts.append(namn)
            testConn.close()
    except (OSError, serial.SerialException):
            pass
# Connect to the first port you found, ValidPorts[0]
print("hooking up to COM port "+ValidPorts[0])
theConnection = serial.Serial(ValidPorts[0], 9600, timeout=1)
#theConnection = serial.Serial('COM33', 9600, timeout=1) # Hardcoded work-around
# serial ports on Linux are called some version of "/dev/ttyS0"

filename="Sensorlog_"+datetime.datetime.now().strftime("%H_%M_%S")+".txt"

def animate(i):
    dataStr = theConnection.readline().decode("ascii")         # THIS is where you get the data in !!!
    myFile = open(filename, 'a')
    myFile.write(datetime.datetime.now().strftime("%H:%M:%S") + " " + dataStr + "\n")  # +"\n"
    myFile.close()
    if(len( y_array) > 10): # keep the number of plottet values low, and the chart flowing
        y_array.pop(0)
        x_array.pop(0)
    try:
        data = float(dataStr)
        y_array.append(data)
        x_array.append(i)
        line.set_data(x_array, y_array)
        ax1.set_xlim(max(0,i-10), i + 1)
    except ValueError: # if there is spurious non-float formatted bytes on the serial port, ignore them
        pass

#--------------- Configuring the control section, with buttons ---------
class toggleArea:
    def tog(self):    # ---------   !!! Define new button-action functions like this
        if self.toggleFrame.cget('bg') == 'yellow':
            self.toggleFrame.configure(bg = 'gray')
            print("Switching to gray")
            theConnection.write("0".encode())  #------- !!! this is what you sent to the Arduino
            print("Turning off LED")
        else:
            self.toggleFrame.configure(bg='yellow')
            print("Switching to yellow")
            theConnection.write("1".encode())
            print("Turning on LED")

    # --- More button-action functions..
    def right(self):
        print("to the right...")
        theConnection.write("R".encode())

    def left(self):
        print("to the left...")
        theConnection.write("L".encode())

    def stop(self):
        print("stop moving...")
        theConnection.write("S".encode())

    def __init__(self, daddyWindow): # ---- !!! In this method you need to add TWO lines per new button:
        self.toggleFrame=Frame(daddyWindow)
        self.toggleFrame.pack()
        self.myBtnTog=Button(self.toggleFrame, text = "Switch now!", command = self.tog )   # !!! define myBtnTog
        self.myBtnEnd=Button(self.toggleFrame, text = "Close program in ToggleArea", command =        quit )
        self.myBtnRight=Button(self.toggleFrame, text = "Right now", command = self.right )
        self.myBtnLeft=Button(self.toggleFrame, text = "Left now", command = self.left )
        self.myBtnStop=Button(self.toggleFrame, text = "Stop the motor", command = self.stop )
        self.myBtnTog.pack(padx =10, pady=10)                                               # !!! and enter in Frame.
        self.myBtnRight.pack(padx =10, pady=10)
        self.myBtnLeft.pack(padx =10, pady=10)
        self.myBtnStop.pack(padx =10, pady=10)
        self.myBtnEnd.pack(padx =10, pady=10)

#-------------------------------------------------------------
class chartArea:
    def __init__(self, daddyWindow):
        self.chartFrame=Frame(daddyWindow)
        self.plotcanvas = FigureCanvasTkAgg(fig, daddyWindow)
        self.plotcanvas.get_tk_widget().pack() #grid(column=1, row=2)
        #  If you want to order buttons yourself you have to be consistent with not packing. Tricky. K.I.S.S. for me.
        self.ani = animation.FuncAnimation(fig, animate, interval=1000, blit=False)  # animate is called from here

#-----------------------------------------------------------------

# connect the defined areas to overall Window "myWindow"
ta = toggleArea(myWindow)
cha = chartArea(myWindow)
myWindow.mainloop()  # and start the thread. The program stays here until you close the mainloop nicely.
# ------- The following happens when/if the window is closed by a button press.
print("like this would ever happen!")
theConnection.close()
