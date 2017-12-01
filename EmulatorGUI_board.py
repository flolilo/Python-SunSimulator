#!/usr/bin/python3
# EmulatorGUI_board  v1.0 - 2017-09-05
''' (Start of CREDIT:)

Modified version of vellarod's Pi GPIO Emulator: https://sourceforge.net/projects/pi-gpio-emulator/
The project has been marked under Creative Commons Attribution License:
https://creativecommons.org/licenses/by/4.0/

Changes to the original that I (flolilo) made:
- Packed everything inside this one python file,
- Changed the layout from horizontal to vertical,
- Made it work with PIN-Numbers (so BCM won't work any more).

(End of CREDIT:) '''
# TODO: Closing it via Ctrl+C in sunsimulator.py doesn't work.
#
import tkinter as tk
from inspect import signature
from functools import wraps
import threading
import time

# http://www.tutorialspoint.com/python/tk_button.htm

dictionaryPins = {}
dictionaryPinsTkinter = {}

GPIONames = ["8", "10", "12", "16", "18", "22", "24", "26", "32", "36", "38", "40", "3", "5", "7", "11", "13", "15",
             "19", "21", "23", "29", "31", "33", "35", "37"]


class PIN():
    SetMode = "None"  # IN/OUT/NONE
    Out = "0"
    pull_up_down = "PUD_OFF"  # PUD_UP/PUD_DOWN/PUD_OFF
    In = "1"

    def __init__(self, SetMode):
        self.SetMode = SetMode
        self.Out = "0"


def typeassert(*ty_args, **ty_kwargs):
    def decorate(func):
        # If in optimized mode, disable type checking
        if not __debug__:
            return func

        # Map function argument names to supplied types
        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            # Enforce type assertions across supplied arguments
            '''for name, value in list(bound_values.arguments.items()):
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError('Argument {} must be {}'.format(name, bound_types[name]))'''
            return func(*args, **kwargs)

        return wrapper

    return decorate


class App(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.wm_title("GPIO Emulator - Board Edition")
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        # Pin 1 - 3V3
        pin1label = tk.Label(text="Pin 1\n3V3", fg="dark orange")
        pin1label.grid(row=0, column=0, padx=(10, 10), pady=(5, 5))
        # Pin 2 - 5V
        pin2label = tk.Label(text="Pin 2\n5V", fg="red")
        pin2label.grid(row=0, column=1, padx=(10, 10))
        # Pin 3 - GPIO 02
        pin03btn = tk.Button(text="Pin 3\nOUT=0", command="2", padx="1px", pady="1px", bd="0px", fg="purple",
                          relief="sunken", activeforeground="blue")
        pin03btn.grid(row=1, column=0, padx=(10, 10), pady=(5, 5))
        dictionaryPinsTkinter["3"] = pin03btn
        # Pin 4 - 5V
        pin4label = tk.Label(text="Pin 4\n5V", fg="red")
        pin4label.grid(row=1, column=1, padx=(10, 10))
        # Pin 5 - GPIO 03
        pin05btn = tk.Button(text="Pin 5\nOUT=0", command="3", padx="1px", pady="1px", bd="0px", fg="purple",
                          relief="sunken", activeforeground="blue")
        pin05btn.grid(row=2, column=0, padx=(10, 10))
        dictionaryPinsTkinter["5"] = pin05btn
        # Pin 6 - GND
        pin6label = tk.Label(text="Pin 6\nGND", fg="black")
        pin6label.grid(row=2, column=1, padx=(10, 10))
        # Pin 7 - GPIO 04
        pin07btn = tk.Button(text="Pin 7\nOUT=0", command="4", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin07btn.grid(row=3, column=0, padx=(10, 10))
        dictionaryPinsTkinter["7"] = pin07btn
        # Pin 8 - GPIO 14
        pin8btn = tk.Button(text="Pin 8\nOUT=0", command="8", padx="1px", pady="1px", bd="0px", fg="purple",
                         relief="sunken", activeforeground="blue")
        pin8btn.grid(row=3, column=1, padx=(10, 10), pady=(5, 5))
        dictionaryPinsTkinter["8"] = pin8btn
        # Pin 9  - GND
        pin09label = tk.Label(text="Pin 9\nGND", fg="black")
        pin09label.grid(row=4, column=0, padx=(10, 10))
        # Pin 10 - GPIO 15
        pin10btn = tk.Button(text="Pin 10\nOUT=0", command="10", padx="1px", pady="1px", bd="0px", fg="purple",
                          relief="sunken", activeforeground="blue")
        pin10btn.grid(row=4, column=1, padx=(10, 10))
        dictionaryPinsTkinter["10"] = pin10btn
        # Pin 11 - GPIO 17
        pin11btn = tk.Button(text="Pin 11\nOUT=0", command="17", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin11btn.grid(row=5, column=0, padx=(10, 10))
        dictionaryPinsTkinter["11"] = pin11btn
        # Pin 12 - GPIO 18
        pin12btn = tk.Button(text="Pin 12\nOUT=0", command="12", padx="1px", pady="1px", bd="0px", fg="purple",
                          relief="sunken", activeforeground="blue")
        pin12btn.grid(row=5, column=1, padx=(10, 10))
        dictionaryPinsTkinter["12"] = pin12btn
        # Pin 13 - GPIO 27
        pin13btn = tk.Button(text="Pin 13\nOUT=0", command="27", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin13btn.grid(row=6, column=0, padx=(10, 10))
        dictionaryPinsTkinter["13"] = pin13btn
        # Pin 14 - GND
        pin14label = tk.Label(text="Pin 14\nGND", fg="black")
        pin14label.grid(row=6, column=1, padx=(10, 10))
        # Pin 15 - GPIO 22
        pin15btn = tk.Button(text="Pin 15\nOUT=0", command="22", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin15btn.grid(row=7, column=0, padx=(10, 10))
        dictionaryPinsTkinter["15"] = pin15btn
        # Pin 16 - GPIO 23
        pin16btn = tk.Button(text="Pin 16\nOUT=0", command="16", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin16btn.grid(row=7, column=1, padx=(10, 10))
        dictionaryPinsTkinter["16"] = pin16btn
        # Pin 17 - 3V3
        pin17label = tk.Label(text="Pin 17\n3V3", fg="dark orange")
        pin17label.grid(row=8, column=0, padx=(10, 10))
        # Pin 18 - GPIO 24
        pin18btn = tk.Button(text="Pin 18\nOUT=0", command="18", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin18btn.grid(row=8, column=1, padx=(10, 10))
        dictionaryPinsTkinter["18"] = pin18btn
        # Pin 19 - GPIO 10
        pin19btn = tk.Button(text="Pin 19\nOUT=0", command="10", padx="1px", pady="1px", bd="0px", fg="purple",
                          relief="sunken", activeforeground="blue")
        pin19btn.grid(row=9, column=0, padx=(10, 10))
        dictionaryPinsTkinter["19"] = pin19btn
        # Pin 20 - GND
        pin20label = tk.Label(text="Pin 20\nGND", fg="black")
        pin20label.grid(row=9, column=1, padx=(10, 10))
        # Pin 21 - GPIO 09
        pin21btn = tk.Button(text="Pin 21\nOUT=0", command="9", padx="1px", pady="1px", bd="0px", fg="purple",
                          relief="sunken", activeforeground="blue")
        pin21btn.grid(row=10, column=0, padx=(10, 10))
        dictionaryPinsTkinter["21"] = pin21btn
        # Pin 22 - GPIO 25
        pin22btn = tk.Button(text="Pin 22\nOUT=0", command="22", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin22btn.grid(row=10, column=1, padx=(10, 10))
        dictionaryPinsTkinter["22"] = pin22btn
        # Pin 23 - GPIO 11
        pin23btn = tk.Button(text="Pin 23\nOUT=0", command="11", padx="1px", pady="1px", bd="0px", fg="purple",
                          relief="sunken", activeforeground="blue")
        pin23btn.grid(row=11, column=0, padx=(10, 10))
        dictionaryPinsTkinter["23"] = pin23btn
        # Pin 24 - GPIO 08
        pin24btn = tk.Button(text="Pin 24\nOUT=0", command="24", padx="1px", pady="1px", bd="0px", fg="purple",
                          relief="sunken", activeforeground="blue")
        pin24btn.grid(row=11, column=1, padx=(10, 10))
        dictionaryPinsTkinter["24"] = pin24btn
        # Pin 25 - GND
        pin25label = tk.Label(text="Pin 25\nGND", fg="black")
        pin25label.grid(row=12, column=0, padx=(10, 10))
        # Pin 26 - GPIO 07
        pin26btn = tk.Button(text="Pin 26\nOUT=0", command="26", padx="1px", pady="1px", bd="0px", fg="purple",
                          relief="sunken", activeforeground="blue")
        pin26btn.grid(row=12, column=1, padx=(10, 10))
        dictionaryPinsTkinter["26"] = pin26btn
        # Pin 27 - ID_SD
        pin27label = tk.Label(text="Pin 27\nID_SD", fg="black")
        pin27label.grid(row=13, column=0, padx=(10, 10))
        # Pin 28 - ID_SC
        pin28label = tk.Label(text="Pin 28\nID_SC", fg="black")
        pin28label.grid(row=13, column=1, padx=(10, 10))
        # Pin 29 - GPIO 05
        pin29btn = tk.Button(text="Pin29\nOUT=0", command="5", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin29btn.grid(row=14, column=0, padx=(10, 10))
        dictionaryPinsTkinter["29"] = pin29btn
        # Pin 30 - GND
        pin30label = tk.Label(text="Pin 30\nGND", fg="black")
        pin30label.grid(row=14, column=1, padx=(10, 10))
        # Pin 31 - GPIO 06
        pin31btn = tk.Button(text="Pin 31\nOUT=0", command="6", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin31btn.grid(row=15, column=0, padx=(10, 10))
        dictionaryPinsTkinter["31"] = pin31btn
        # Pin 32 - GPIO 12
        pin32btn = tk.Button(text="Pin 32\nOUT=0", command="32", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin32btn.grid(row=15, column=1, padx=(10, 10))
        dictionaryPinsTkinter["32"] = pin32btn
        # Pin 33 - GPIO 13
        pin33btn = tk.Button(text="Pin 33\nOUT=0", command="13", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin33btn.grid(row=16, column=0, padx=(10, 10))
        dictionaryPinsTkinter["33"] = pin33btn
        # Pin 34 - GND
        pin34label = tk.Label(text="Pin 34\nGND", fg="black")
        pin34label.grid(row=16, column=1, padx=(10, 10))
        # Pin 35 - GPIO 19
        pin35btn = tk.Button(text="Pin 35\nOUT=0", command="19", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin35btn.grid(row=17, column=0, padx=(10, 10))
        dictionaryPinsTkinter["35"] = pin35btn
        # Pin 36 - GPIO 16
        pin36btn = tk.Button(text="Pin 36\nOUT=0", command="36", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin36btn.grid(row=17, column=1, padx=(10, 10))
        dictionaryPinsTkinter["36"] = pin36btn
        # Pin 37 - GPIO 26
        pin37btn = tk.Button(text="Pin 37\nOUT=0", command="26", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin37btn.grid(row=18, column=0, padx=(10, 10))
        dictionaryPinsTkinter["37"] = pin37btn
        # Pin 38 - GPIO 20
        pin38btn = tk.Button(text="Pin 38\nOUT=0", command="38", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin38btn.grid(row=18, column=1, padx=(10, 10))
        dictionaryPinsTkinter["38"] = pin38btn
        # Pin 39 - GND
        pin39label = tk.Label(text="Pin 39\nGND", fg="black")
        pin39label.grid(row=19, column=0, padx=(10, 10))
        # Pin 40 - GPIO 21
        pin40btn = tk.Button(text="Pin 40\nOUT=0", command="40", padx="1px", pady="1px", bd="0px", fg="blue",
                          relief="sunken", activeforeground="blue")
        pin40btn.grid(row=19, column=1, padx=(10, 10))
        dictionaryPinsTkinter["40"] = pin40btn
        self.root.geometry('%dx%d+%d+%d' % (140, 720, 0, 0))
        self.root.mainloop()
        # tk.Button1.unbind("<Button-1>")


app = App()


def toggleButton(gpioID):
    # print(gpioID)
    objBtn = dictionaryPinsTkinter[str(gpioID)]
    objPin = dictionaryPins[str(gpioID)]

    if (objPin.In == "1"):
        objPin.In = "0"
    elif (objPin.In == "0"):
        objPin.In = "1"

    objBtn["text"] = "Pin" + str(gpioID) + "\nIN=" + str(objPin.In)


def ButtonClick(self):
    # print("clicked")
    gpioID = (self.widget.config('command')[-1])
    toggleButton(gpioID)


def ButtonClickRelease(self):
    # print("released")
    gpioID = (self.widget.config('command')[-1])
    toggleButton(gpioID)


def drawGPIOOut(gpioID):
    global dictionaryPins
    global dictionaryPinsTkinter

    gpioID = str(gpioID)
    objPin = dictionaryPins[gpioID]
    objBtn = dictionaryPinsTkinter[gpioID]

    if (objPin.SetMode == "OUT"):
        objBtn["text"] = "Pin" + str(gpioID) + "\nOUT=" + str(objPin.Out)
        if (str(objPin.Out) == "1"):
            objBtn.configure(background='tan2')
            objBtn.configure(activebackground='tan2')
        else:
            objBtn.configure(background='DarkOliveGreen3')
            objBtn.configure(activebackground='DarkOliveGreen3')


def drawBindUpdateButtonIn(gpioID, In):
    objBtn = dictionaryPinsTkinter[gpioID]
    objBtn.configure(background='gainsboro')
    objBtn.configure(activebackground='gainsboro')
    objBtn.configure(relief='raised')
    objBtn.configure(bd="1px")
    objBtn["text"] = "Pin" + str(gpioID) + "\nIN=" + str(In)
    objBtn.bind("<Button-1>", ButtonClick)
    objBtn.bind("<ButtonRelease-1>", ButtonClickRelease)


class GPIO:
    # constants
    LOW = 0
    HIGH = 1
    OUT = 2
    IN = 3
    PUD_OFF = 4
    PUD_DOWN = 5
    PUD_UP = 6
    BOARD = 7

    # flags
    setModeDone = False

    # Extra functions
    def checkModeValidator():
        if (GPIO.setModeDone is False):
            raise Exception('Setup your GPIO mode. Must be set to BOARD')

    # GPIO LIBRARY Functions
    @typeassert(int)
    def setmode(mode):
        time.sleep(1)
        if (mode == GPIO.BOARD):
            GPIO.setModeDone = True
        else:
            GPIO.setModeDone = False

    @typeassert(bool)
    def setwarnings(flag):
        pass

    @typeassert(int, int, int, int)
    def setup(channel, state: object, initial: object = -1, pull_up_down: object = -1) -> object:
        global dictionaryPins
        GPIO.checkModeValidator()
        if str(channel) not in GPIONames:
            raise Exception('Pin ' + str(channel) + ' does not exist')

        # check if channel is already setup
        '''if (str(channel) in dictionaryPins):
            raise Exception('GPIO is already setup')'''

        if (state == GPIO.OUT):
            # GPIO is set as output, default OUT 0
            objTemp = PIN("OUT")
            if (initial == GPIO.HIGH):
                objTemp.Out = "1"

            dictionaryPins[str(channel)] = objTemp
            drawGPIOOut(channel)
        elif (state == GPIO.IN):
            # set input
            objTemp = PIN("IN")
            if (pull_up_down == -1):
                objTemp.pull_up_down = "PUD_DOWN"  # by default pud_down
                objTemp.In = "0"
            elif (pull_up_down == GPIO.PUD_DOWN):
                objTemp.pull_up_down = "PUD_DOWN"
                objTemp.In = "0"
            elif (pull_up_down == GPIO.PUD_UP):
                objTemp.pull_up_down = "PUD_UP"
                objTemp.In = "1"

            drawBindUpdateButtonIn(str(channel), objTemp.In)
            dictionaryPins[str(channel)] = objTemp

    @typeassert(int, int)
    def output(channel, outmode):
        global dictionaryPins
        channel = str(channel)

        GPIO.checkModeValidator()

        if (channel not in dictionaryPins):
            # if channel is not setup
            raise Exception('GPIO must be setup before used')
        else:
            objPin = dictionaryPins[channel]
            if (objPin.SetMode == "IN"):
                # if channel is setup as IN and used as an OUTPUT
                raise Exception('GPIO must be setup as OUT')

        if (outmode != GPIO.LOW and outmode != GPIO.HIGH):
            raise Exception('Output must be set to HIGH/LOW')

        objPin = dictionaryPins[channel]
        if (outmode == GPIO.LOW):
            objPin.Out = "0"
        elif (outmode == GPIO.HIGH):
            objPin.Out = "1"

        drawGPIOOut(channel)

    @typeassert(int)
    def input(channel):
        global dictionaryPins
        channel = str(channel)

        GPIO.checkModeValidator()

        '''if (channel not in dictionaryPins):
            # if channel is not setup
            raise Exception('GPIO must be setup before used')
        else:
            objPin = dictionaryPins[channel]
            if (objPin.SetMode == "OUT"):
                # if channel is setup as OUTPUT and used as an INPUT
                raise Exception('GPIO must be setup as IN')'''

        objPin = dictionaryPins[channel]
        if (objPin.In == "1"):
            return True
        elif (objPin.Out == "0"):
            return False

    def cleanup(self):
        pass
