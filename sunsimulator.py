#!/usr/bin/python3
# SunSimulator v3.0 (BETA) - By flolilo, 2018-04-05
#
try:
    import RPi.GPIO as GPIO  # For Raspberry Pi
except ImportError:
    from EmulatorGUI_board import GPIO  # For PC, import GPIO Emulator from EmulatorGUI_board.py
import time  # For timeouts
import datetime  # To get the current time
import ephem  # To get information about sunrise & sunset
from random import randint  # For random dimming of the light in --mode "aquarium"
import os  # For rebooting
import signal  # For keyboard interrupts
import sys  # For keyboard interrupts
import argparse  # Set variables via parameters
parser = argparse.ArgumentParser()
parser.add_argument("--Latitude", dest="Latitude",
                    help="in decimal degrees, e.g. Paris is 48.8567",
                    type=float, default="-180.0000")
parser.add_argument("--Longitude", dest="Longitude",
                    help="in decimal degrees, e.g. Paris is 2.3517",
                    type=float, default="-360.0000")
parser.add_argument("--Mode", dest="Mode",
                    help="aquarium, outside",
                    default="none")
parser.add_argument("--Log", dest="Log", help="0 = no debug-info, 1 = info in console, 2 = info in file.",
                    type=int, default=1)
parser.add_argument("--EnableOverride", dest="EnableOverride",
                    help="Ignore light sensor (if N/A or malfunctioning). Only with --mode outside.",
                    type=int, default=1)
parser.add_argument("--TestMode", dest="TestMode",
                    help="0 = test-mode disabled, 1 = enabled.",
                    type=int, default=0)
parser.add_argument("--Restart", dest="Restart",
                    help="Restart the device every 24 hours (noon).",
                    type=int, default=1)
parser.add_argument("--PollTime", dest="PollTime",
                    help="Polling interval (in seconds).",
                    type=int, default=10)
args = parser.parse_args()

# DEFINITION: Counting GPIO via Pins, deactivating warnings
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# DEFINITION: Set print location (none/terminal/file)
if (args.Log == 2):
    f = open("./LOG_sunsimulator.txt", mode='a')
elif (args.Log == 1):
    f = sys.stdout
else:
    f = open(os.devnull, 'w')
    sys.stdout = f

print("\nSunSimulator v3.0 (BETA) - By flolilo, 2018-04-05", file=f)

# ==================================================================================================
# ==============================================================================
#    Testing parameters, adding some variables:
# ==============================================================================
# ==================================================================================================

if (args.Latitude == -180.0000):
    print("--Latitude not specified - exiting!", file=f)
    f.close()
    sys.exit(0)

if (args.Longitude == -360.0000):
    print("--Longitude not specified - exiting!", file=f)
    f.close()
    sys.exit(0)

# DEFINITION: Specifying pinout for each application:
if (args.Mode == "outside"):
    print("Outside-mode was chosen for this execution.", file=f)
    ''' GPIO-PINOUT FOR OUTSIDE-MODE:
    PIN -   Name        -   True-State
    15  -   Sensor      -   Dark (Input)
    29  -   Light 1     -   Off
    31  -   Light 2     -   Off
    33  -   Light 3     -   Off
    35  -   Light 4     -   Off
    37  -   Light Well  -   On
    36  -   Pump Well   -   On
    38  -   Spare 1     -   /
    40  -   Spare 2     -   /
    NEVER FORGET: "True" = "deactivate" '''
    pins = [15, 29, 31, 33, 35, 37, 36, 38, 40]
    lighton = [True, False, False, False, False, True, True, True, True]
    lightoff = [True, True, True, True, True, False, True, True, True]

    for k in range(len(pins)):
        if(k == 0):
            # activating GPIO for the photoresistor
            GPIO.setup(pins[k], GPIO.IN)
        else:
            # activate GPIOs for relais
            GPIO.setup(pins[k], GPIO.OUT, initial=lightoff[k])
        time.sleep(0.1)
elif (args.Mode == "aquarium"):
    print("Aquarium-mode was chosen for this execution.", file=f)
    ''' GPIO-PINOUT FOR AQUARIUM-MODE:
    PIN -   Name        -   True-State
    13  -   Light       -   On
    15  -   Dimmer      -   Off
    NEVER FORGET: "True" = "deactivate" '''
    pins = [13, 15]
    lighton = [True, True]
    lightoff = [False, True]
    lightdim = [True, False]

    # activate GPIOs for relais
    for k in range(len(pins)):
        GPIO.setup(pins[k], GPIO.OUT, initial=lighton[k])
        time.sleep(0.1)
else:
    print("--Mode not specified - exiting!", file=f)
    f.close()
    sys.exit(0)

if(args.PollTime <= 0 or args.PollTime >= 3601):
    print("--PollTime not between 1 and 3600 - exiting!", file=f)
    f.close()
    sys.exit(0)

print("\nExplanation:", file=f)
print("           Local   |   UTC    | UTC total", file=f)

# ==================================================================================================
# ==============================================================================
#    Defining variables:
# ==============================================================================
# ==================================================================================================

if (args.Mode == "outside"):
    reboot_time_min = 65  # Min time to reboot
    sensed_darkness = 0  # --Mode outside. Increasing value shows that sensor reports light-intensity below threshold.
    override = "off"  # --Mode outside. If sensor does not work, this will decide light states via pyephem.
    bigben_done = 0  # --Mode outside. Specifies if lights_BigBen was already working.
else:
    reboot_time_min = 725  # Min time to reboot
    # DEFINITION: --Mode aquarium. Prepare values for random dimming:
    random_i = 0
    random_day = 0
    random_time_min = 9999
    random_time_max = random_time_min + 5


set_daytime = "none"  # specifies in which mode the script currently is to prevent re-doing the same thing.
regular_sleep_time = args.PollTime  # time (in seconds) that the script idles between two iterations
reboot_threshold = (86400 / 2) / regular_sleep_time  # restart after at least 12h
reboot_time_max = reboot_time_min + 5  # Max time to reboot
ephempoll_timer = (15 * 60) / regular_sleep_time  # poll ephem every 15min

# DEFINITION: Values for function time_GetSet:
now_utc = [0, 0, 0, 0]
now_local = [0, 0, 0, 0]

# DEFINITION: Values for function time_ephem:
suntimes = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
# get ephem objects
ephem_sunrise = ephem.Observer()
ephem_sunset = ephem.Observer()
ephem_dusk = ephem.Observer()
ephem_sun = ephem.Sun()
# set elevation of polled place (default: 0)
# sun_rise.elev = 0
# set longitude and latitude according to args
ephem_sunrise.lat = "{:.4f}".format(args.Latitude)
ephem_sunrise.lon = "{:.4f}".format(args.Longitude)
ephem_sunset.lat = "{:.4f}".format(args.Latitude)
ephem_sunset.lon = "{:.4f}".format(args.Longitude)
# set definition of horizon (nautic/civil/...)
if (args.Mode == "outside"):
    ephem_sunrise.horizon = '-9'
    ephem_sunset.horizon = '-0.5'
else:
    ephem_sunrise.horizon = '18'
    ephem_sunset.horizon = '-3'
    ephem_dusk.lat = "{:.4f}".format(args.Latitude)
    ephem_dusk.lon = "{:.4f}".format(args.Longitude)
    ephem_dusk.horizon = '-12'
ephem_objects = [ephem_sun, ephem_sunrise, ephem_sunset, ephem_dusk]
del ephem_sun
del ephem_sunrise
del ephem_sunset
del ephem_dusk

# ==================================================================================================
# ==============================================================================
#    Defining functions:
# ==============================================================================
# ==================================================================================================


# DEFINITION: Print information about times and dates
def print_information():
    global now_utc
    global now_local
    global suntimes
    global f

    print("\nTime:     " + str(now_local[1]).zfill(2) + ":" + str(now_local[2]).zfill(2) + ":" +
          str(now_local[3]).zfill(2) + " | " + str(now_utc[1]).zfill(2) + ":" +
          str(now_utc[2]).zfill(2) + ":" + str(now_utc[3]).zfill(2) + " | " +
          str(now_utc[0]).zfill(5), file=f)
    print("Sunrise:           | " + str(suntimes[0][1]).zfill(2) + ":" + str(suntimes[0][2]).zfill(2) + ":" +
          str(suntimes[0][3]).zfill(2) + " | " + str(suntimes[0][0]).zfill(5), file=f)
    print("Sunset:            | " + str(suntimes[1][1]).zfill(2) + ":" + str(suntimes[1][2]).zfill(2) + ":" +
          str(suntimes[1][3]).zfill(2) + " | " + str(suntimes[1][0]).zfill(4), file=f)
    if (args.Mode == "aquarium"):
        print("Dusk:              | " + str(suntimes[2][1]).zfill(2) + ":" + str(suntimes[2][2]).zfill(2) + ":" +
              str(suntimes[2][3]).zfill(2) + " | " + str(suntimes[2][0]).zfill(5), file=f)


# DEFINITION: Switching on the lights:
def lights_switchOn(pin_first, pin_last):
    global f
    global args
    global set_daytime
    global pins

    print_information()
    if (args.Mode == "outside"):
        for k in range(pin_first, pin_last + 1):
            GPIO.output(pins[k], lighton[k])
            time.sleep(0.3)
        print("It has been dark long enough - Lights ON (False).", file=f)
        set_daytime = "night"
    else:
        for k in range(len(pins)):
            GPIO.output(pins[k], lighton[k])
        print("It is day now - Light ON (True), Dimmer OFF (True).", file=f)
        set_daytime = "day"


# DEFINITION: Switching off the lights:
def lights_switchOff(pin_first, pin_last):
    global f
    global args
    global set_daytime
    global pins

    print_information()
    if (args.Mode == "outside"):
        for k in range(pin_first, pin_last + 1):
            GPIO.output(pins[k], lightoff[k])
            time.sleep(0.3)
        print("It has been bright long enough - Lights OFF (True).", file=f)
        set_daytime = "day"
    else:
        for k in range(len(pins)):
            GPIO.output(pins[k], lightoff[k])
        print("It is night now - Light OFF (False), Dimmer OFF (True).", file=f)
        set_daytime = "night"


# DEFINITION: Dimming the lights: (only --Mode "aquarium")
def lights_dimming(pin_first, pin_last):
    global f
    global set_daytime
    global pins

    print_information()
    print("The sun is setting - Light ON (True), Dimmer ON (False).", file=f)
    set_daytime = "evening"


# DEFINITION: Every quarter of the hour, show the time with flashing the lights: (only --Mode "outside")
def lights_BigBen(hour, minute):
    global f
    global pins
    lights_switchOff(1, 4)
    time.sleep(7)

    print_information()

    # DEFINITION: Use AM-style times & make midnight to 12:00
    if (hour == 0):
        hour = 12
    elif (hour >= 13):
        hour -= 12

    for x in range(0, hour, 1):
        print("Hour " + str(x).zfill(2), file=f)
        for k in range(1, 5):
            GPIO.output(pins[k], lighton[k])
        time.sleep(0.9)
        for k in range(1, 5):
            GPIO.output(pins[k], lightoff[k])
        time.sleep(0.3)
    time.sleep(1.8)
    y = 1
    for x in range(0, minute, 15):
        print("Minute " + str(x).zfill(2), file=f)
        for k in range(y):
            GPIO.output(pins[k + 1], lighton[k + 1])
        time.sleep(0.6)
        for j in range(1, 5):
            GPIO.output(pins[j], lightoff[j])
        time.sleep(0.2)
        y += 1
    time.sleep(7)
    lights_switchOn(1, 4)


# DEFINITION: Getting the sunrise & sunset, setting variables accordingly:
def time_Ephem():
    global args
    global ephem_objects
    global suntimes

    # set polled date
    now_ephem = datetime.datetime.now()

    # DEFINITION: Figure out sunrise, sunset, and dusk:
    ephem_objects[1].date = now_ephem
    suntimes[0][1] = ephem_objects[1].next_rising(ephem_objects[0], use_center=True).tuple()[3]
    suntimes[0][2] = ephem_objects[1].next_rising(ephem_objects[0], use_center=True).tuple()[4]
    suntimes[0][3] = int(round(ephem_objects[1].next_rising(ephem_objects[0], use_center=True).tuple()[5]))
    suntimes[0][0] = suntimes[0][1] * 3600 + suntimes[0][2] * 60 + suntimes[0][3]

    ephem_objects[2].date = now_ephem
    suntimes[1][1] = ephem_objects[2].next_setting(ephem_objects[0], use_center=True).tuple()[3]
    suntimes[1][2] = ephem_objects[2].next_setting(ephem_objects[0], use_center=True).tuple()[4]
    suntimes[1][3] = int(round(ephem_objects[2].next_setting(ephem_objects[0], use_center=True).tuple()[5]))
    suntimes[1][0] = suntimes[1][1] * 3600 + suntimes[1][2] * 60 + suntimes[1][3]
    if (args.Mode == "aquarium"):
        ephem_objects[3].date = now_ephem
        suntimes[2][1] = ephem_objects[3].next_setting(ephem_objects[0], use_center=True).tuple()[3]
        suntimes[2][2] = ephem_objects[3].next_setting(ephem_objects[0], use_center=True).tuple()[4]
        suntimes[2][3] = int(round(ephem_objects[3].next_setting(ephem_objects[0], use_center=True).tuple()[5]))
        suntimes[2][0] = suntimes[2][1] * 3600 + suntimes[2][2] * 60 + suntimes[2][3]


# DEFINITION: Getting the current time:
def time_GetSet():
    global f
    global args
    global now_utc
    global now_local

    now_utc[1] = time.gmtime(time.time())[3]
    now_utc[2] = time.gmtime(time.time())[4]
    now_utc[3] = int(round(time.gmtime(time.time())[5]))
    now_utc[0] = now_utc[1] * 3600 + now_utc[2] * 60 + now_utc[3]
    now_local[1] = time.localtime(time.time())[3]
    now_local[2] = time.localtime(time.time())[4]
    now_local[3] = int(round(time.localtime(time.time())[5]))
    now_local[0] = now_local[1] * 3600 + now_local[2] * 60 + now_local[3]


# DEFINITION: Getting the values of the sensor:
def sensor_readout():
    global f
    global sensed_darkness
    global pins

    # DEFINITION: Checking brightness, saving to variable:
    sens = GPIO.input(pins[0])
    if (sens == 1 and sensed_darkness <= 3):
        sensed_darkness += 1
        print("Darker. Light-Value is now: " + str(sensed_darkness), file=f)
    elif (sens == 0 and sensed_darkness >= 1):
        sensed_darkness -= 1
        print("Brighter. Light-Value is now: " + str(sensed_darkness), file=f)


# DEFINITION: Preparing restart by cleaning up and closing:
def prepare_restart():
    global f
    global pins

    print_information()

    print("Preparing restart...", file=f)
    time.sleep(1)
    f.close()
    time.sleep(1)
    GPIO.cleanup(pins)
    time.sleep(1)
    os.system("reboot")


# DEFINITION: For keyboard interrupts:
def signal_handler(signal, frame):
    global f
    global args
    global pins

    print("You pressed <Ctrl> + <C> -- Exiting SunSimulator!", file=f)
    time.sleep(1)
    f.close()
    time.sleep(1)
    GPIO.cleanup(pins)
    time.sleep(1)
    sys.exit(0)


# ==================================================================================================
# ==============================================================================
#    Start everything:
# ==============================================================================
# ==================================================================================================

signal.signal(signal.SIGINT, signal_handler)

i = 0
# DEFINITION: Loop for repetition of getting the current time:
while True:
    time_GetSet()
    if(i % ephempoll_timer == 0):
        time_Ephem()
        print_information()
        print("Daytime-Variable = " + str(set_daytime), file=f)

    if (args.Mode == "outside"):
        if(args.TestMode == 1):
            while(True):
                lights_switchOn(1, 5)
                time.sleep(5)
                lights_switchOff(1, 5)
                time.sleep(5)
        else:
            sensor_readout()

            # overrides for different times:
            if (args.EnableOverride == 1):
                if (9 <= now_local[1] <= 15):
                    if (override != "day"):
                        print_information()
                        print("It must be day by now - Setting override to 'day'.", file=f)
                        override = "day"
                elif (suntimes[1][0] <= now_utc[0] or now_utc[0] <= suntimes[0][0]):
                    if (override != "night"):
                        print_information()
                        print("It must be night by now - Setting override to 'night'.", file=f)
                        override = "night"
                else:
                    if (override != "off"):
                        print_information()
                        print("It could be dark by now - Setting override to 'off'.", file=f)
                        override = "off"

            # If dark enough or late enough: switch light on, else: switch it off
            if (sensed_darkness >= 4 and set_daytime != "night" and override == "off" and i >= 4):
                lights_switchOn(1, 5)
            elif (sensed_darkness <= 0 and set_daytime != "day" and override == "off" and i >= 4):
                lights_switchOff(1, 5)
            elif (override == "night" and set_daytime != "night"):
                lights_switchOn(1, 5)
            elif (override == "day" and set_daytime != "day"):
                lights_switchOff(1, 5)

            # big-ben-style blinking:
            if (set_daytime == "night" and bigben_done == 0 and now_local[2] % 15 == 0):
                if (now_local[2] == 0):
                    now_local[2] = 60
                lights_BigBen(now_local[1], now_local[2])
                bigben_done = 1

            if (bigben_done == 1 and now_local[2] % 15 != 0):
                bigben_done = 0
    else:
        if(args.TestMode == 1):
            while(True):
                lights_switchOn(0, 2)
                time.sleep(5)
                lights_dimming(0, 2)
                time.sleep(5)
                lights_switchOff(0, 2)
                time.sleep(5)
        else:
            if (suntimes[0][0] <= now_utc[0] <= suntimes[1][0] and set_daytime != "day" and i >= 1):
                lights_switchOn(0, 2)
            # dimming the light
            elif (suntimes[1][0] <= now_utc[0] <= suntimes[2][0] and set_daytime != "evening" and i >= 1):
                lights_dimming(0, 2)
            # night before midnight
            elif (suntimes[2][0] <= now_utc[0] and set_daytime != "night" and i >= 1):
                lights_switchOff(0, 2)
            # night after midnight
            elif (now_utc[0] <= suntimes[0][0] and set_daytime != "night" and i >= 1):
                lights_switchOff(0, 2)

            # dimming the light randomly
            if (random_i == 0):
                random_time_min = randint(suntimes[0][0] + 120, suntimes[2][0] - 120)
                random_time_max = random_time_min + 10
                print("Time to start the random dimming today: " + str(random_time_min).zfill(4), file=f)
            if (random_day != 3 and random_i <= 1):
                random_i += 1
                random_day = randint(0, 4)
                print("The day for running the random dimming is: " + str(random_day) + ". Randomised for the " +
                      str(random_i) + ". time.", file=f)
            if (random_time_min <= now_local[0] <= random_time_max and random_day == 3 and random_i != 5):
                lights_dimming(0, 2)
                print("Starting random dimming.", file=f)
                time.sleep(600)
                lights_switchOn(0, 2)
                print("Ending random dimming.", file=f)
                random_i = 5

    # Break while-loop to reboot:
    if (args.Restart == 1 and reboot_time_min <= now_local[0] <= reboot_time_max and i >= reboot_threshold):
        break

    i += 1
    time.sleep(regular_sleep_time)

prepare_restart()
