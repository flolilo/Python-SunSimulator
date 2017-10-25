#!/usr/bin/python3
# SunSimulator  v2.23 - By flolilo, 2017-09-05
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
parser.add_argument("--mode", dest="mode", help="aquarium, outside", default="none")
parser.add_argument("--log", dest="log", help="0 = no debug-info, 1 = debug-info.", type=int, default=0)
parser.add_argument("--EnableOverride", dest="EnableOverride", help="Only with --mode outside.", type=int, default=1)
args = parser.parse_args()

# DEFINITION: Counting GPIO via Pins, deactivating warnings
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

if (args.log == 1):
    f = open("./log.txt", mode='a')
else:
    f = sys.stdout

# DEFINITION: Specifying pinout for each application:
if (args.mode == "outside"):
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
elif (args.mode == "aquarium"):
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
    print("--mode not specified - exiting!", file=f)
    f.close()
    sys.exit(0)

set_daytime = "none"  # specifies in which mode the script currently is to prevent re-doing the same thing.
sensed_darkness = 0  # --mode outside only. Increasing value shows that sensor reports light-intensity below threshold.
override = "off"  # --mode outside only. If sensor does not work, this will decide light states via pyephem.
bigben_done = 0  # --mode outside only. Specifies if lights_BigBen was already working.
regular_sleep_time = 20  # time (in seconds) that the script idles between two iterations
# DEFINITION: Values for function time_GetSet:
now = 0
now_hours_utc = 0
now_minutes_utc = 0
now_hours = 0
now_hours_PM = now_hours
sunrise_total = 0
sunset_total = 0
dusk_total = 0
now_total_utc = 0

# DEFINITION: specify the time to reboot: (Max-time is needed, otherwise endless reboots would occur.)
if (args.mode == "outside"):
    reboot_time_min = 65
    reboot_time_max = reboot_time_min + 5
else:
    reboot_time_min = 725
    reboot_time_max = reboot_time_min + 5

# DEFINITION: --mode aquarium only. Prepare values for random dimming:
random_i = 0
random_day = 0
random_time_min = 9999
random_time_max = random_time_min + 5


# DEFINITION: Switching on the lights:
def lights_switchOn(pin_first, pin_last):
    global f
    global args
    global set_daytime
    global pins
    if (args.mode == "outside"):
        for k in range(pin_first, pin_last + 1):
            GPIO.output(pins[k], lighton[k])
            time.sleep(0.3)
        print("It was dark for long enough time - Switching ON the lights.", file=f)
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
    if (args.mode == "outside"):
        for k in range(pin_first, pin_last + 1):
            GPIO.output(pins[k], lightoff[k])
            time.sleep(0.3)
        print("It was bright for long enough time - Switching OFF the lights.", file=f)
        set_daytime = "day"
    else:
        for k in range(len(pins)):
            GPIO.output(pins[k], lightoff[k])
        print("It is night now - Light OFF (False), Dimmer OFF (True).", file=f)
        set_daytime = "night"


# DEFINITION: Dimming the lights: (only --mode "aquarium")
def lights_dimming(pin_first, pin_last):
    global f
    global set_daytime
    global pins
    for k in range(len(pins)):
        GPIO.output(pins[k], lightdim[k])
    print("Dimming the light, as the sun is setting - Light ON (True), Dimmer ON (False).", file=f)
    set_daytime = "evening"


# DEFINITION: Every quarter of the hour, show the time with flashing the lights: (only --mode "outside")
def lights_BigBen(hour, minute):
    global f
    global set_daytime
    global pins
    global bigben_done
    lights_switchOff(1, 4)
    time.sleep(7)
    for x in range(0, hour, 1):
        print("Hour " + str(x), file=f)
        for k in range(1, 5):
            GPIO.output(pins[k], lighton[k])
        time.sleep(0.9)
        for k in range(1, 5):
            GPIO.output(pins[k], lightoff[k])
        time.sleep(0.3)
    time.sleep(1.8)
    y = 1
    for x in range(0, minute, 15):
        print("Minute " + str(x), file=f)
        for k in range(y):
            GPIO.output(pins[k + 1], lighton[k + 1])
        time.sleep(0.6)
        for j in range(1, 5):
            GPIO.output(pins[j], lightoff[j])
        time.sleep(0.2)
        y += 1
    time.sleep(7)
    lights_switchOn(1, 4)
    bigben_done = 1


# DEFINITION: Getting the time, sunrise & sunset, setting variables accordingly:
def time_SetGet():
    global f
    global args
    global now
    global now_hours_utc
    global now_minutes_utc
    global now_hours
    global now_hours_PM
    global sunrise_total
    global sunset_total
    global now_total_utc
    global dusk_total
    dusk_hours = 0
    dusk_minutes = 0
    # figure out what time it is now
    now = datetime.datetime.now()
    now_hours_utc = time.gmtime(time.time())[3]
    now_minutes_utc = time.gmtime(time.time())[4]
    now_hours = time.localtime(time.time())[3]
    now_hours_PM = now_hours
    if (args.mode == "outside"):
        # for blinking: use AM-style times, make midnight to 12:00.
        if (now_hours == 0):
            now_hours = 12
        elif (now_hours >= 13):
            now_hours -= 12
    # now_day = now.strftime("%A")

    # current location, set horizon level
    sun_rise = ephem.Observer()
    sun_set = ephem.Observer()
    sun_rise.elev = 0
    sun_rise.date = now
    sun_set.elev = 0
    sun_set.date = now
    sun_dusk = ephem.Observer()
    sun_dusk.elev = 0
    sun_dusk.date = now
    if (args.mode == "outside"):
        sun_rise.lat = '48.2292'
        sun_rise.lon = '13.9362'
        sun_rise.horizon = '-9'
        sun_set.lat = sun_rise.lat
        sun_set.lon = sun_rise.lon
        sun_set.horizon = '-0.5'
    else:
        sun_rise.lat = '48.2292'
        sun_rise.lon = '13.9362'
        sun_rise.horizon = '18'
        sun_set.lat = sun_rise.lat
        sun_set.lon = sun_rise.lon
        sun_set.horizon = '-3'
        sun_dusk.lat = sun_rise.lat
        sun_dusk.lon = sun_rise.lon
        sun_dusk.horizon = '-12'
    sun = ephem.Sun()

    # figure out sunrise and sunset (and dusk)
    sunrise_hours = sun_rise.next_rising(sun, use_center=True).tuple()[3]
    sunrise_minutes = sun_rise.next_rising(sun, use_center=True).tuple()[4]
    sunset_hours = sun_set.next_setting(sun, use_center=True).tuple()[3]
    sunset_minutes = sun_set.next_setting(sun, use_center=True).tuple()[4]
    if (args.mode == "aquarium"):
        dusk_hours = sun_dusk.next_setting(sun, use_center=True).tuple()[3]
        dusk_minutes = sun_dusk.next_setting(sun, use_center=True).tuple()[4]

    # doing some maths to make calculations easier
    sunrise_total = sunrise_hours * 60 + sunrise_minutes
    sunset_total = sunset_hours * 60 + sunset_minutes
    if (args.mode == "aquarium"):
        dusk_total = dusk_hours * 60 + dusk_minutes
    now_total_utc = now_hours_utc * 60 + now_minutes_utc
    print("\n" + str(now_hours_utc) + ":" + str(now_minutes_utc) + " (UTC) / " + str(now_hours_PM) +
          ":" + str(now_minutes_utc) + " (@AT) / " + str(now_total_utc) + " (Total UTC)", file=f)

    if (args.mode == "outside"):
        print("Sunrise: " + str(sunrise_hours) + ":" + str(sunrise_minutes) + " / " + str(sunrise_total) +
              ", Sunset: " + str(sunset_hours) + ":" + str(sunset_minutes) + " / " + str(sunset_total), file=f)
    else:
        print("Sunrise: " + str(sunrise_hours) + ":" + str(sunrise_minutes) + " / " + str(sunrise_total) +
              ", Sunset: " + str(sunset_hours) + ":" + str(sunset_minutes) + " / " + str(sunset_total) +
              ", Dusk: " + str(dusk_hours) + ":" + str(dusk_minutes) + " / " + str(dusk_total), file=f)
    print("Daytime-Variable = " + str(set_daytime), file=f)


# DEFINITION: Getting the values of the sensor:
def sensor_readout():
    global f
    global sensed_darkness
    global pins
    # Checking brightness, saving to variable
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
    print(" You pressed Ctrl + C  --  Exiting!", file=f)
    time.sleep(1)
    f.close()
    time.sleep(1)
    GPIO.cleanup(pins)
    time.sleep(1)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

i = 0
# DEFINITION: Loop for repetition of getting the current time:
while True:
    time_SetGet()
    if (args.mode == "outside"):
        sensor_readout()
        # If dark enough or late enough: switch light on, else: switch it off
        if (sensed_darkness >= 4 and set_daytime != "night" and override == "off" and i >= 4):
            lights_switchOn(1, 5)
        elif (sensed_darkness <= 0 and set_daytime != "day" and override == "off" and i >= 4):
            lights_switchOff(1, 5)
        elif (override == "night" and set_daytime != "night"):
            lights_switchOn(1, 5)
        elif (override == "day" and set_daytime != "day"):
            lights_switchOff(1, 5)

        # overrides for different times:
        if (args.EnableOverride == 1):
            if (3 <= now_hours_PM <= 13):
                if (override != "day"):
                    print("It has to be day by now - Override is set to 'day'. \n", file=f)
                    override = "day"
            elif (sunset_total <= now_total_utc or now_total_utc <= sunrise_total):
                if (override != "night"):
                    print("It has to be night by now - Override is set to 'night'. \n", file=f)
                    override = "night"
            else:
                if (override != "off"):
                    print("It could be dark by now - Override is set to 'off'. \n", file=f)
                    override = "off"

        # big-ben-style blinking:
        if (set_daytime == "night" and bigben_done == 0):
            if (now_minutes_utc == 15 or now_minutes_utc == 30 or now_minutes_utc == 45):
                lights_BigBen(now_hours, now_minutes_utc)
            elif (now_minutes_utc == 0):
                now_minutes_utc = 60
                lights_BigBen(now_hours, now_minutes_utc)

        if (bigben_done == 1 and 1 <= now_minutes_utc <= 14 or 16 <= now_minutes_utc <= 29 or
                31 <= now_minutes_utc <= 44 or 46 <= now_minutes_utc <= 59):
            bigben_done = 0

        # Break while-loop to reboot:
        if (reboot_time_min <= now_total_utc <= reboot_time_max and i >= 1440):
            break

    else:
        if (sunrise_total <= now_total_utc <= sunset_total and set_daytime != "day" and i >= 1):
            lights_switchOn(0, 2)
        # dimming the light
        elif (sunset_total <= now_total_utc <= dusk_total and set_daytime != "evening" and i >= 1):
            lights_dimming(0, 2)
        # night before midnight
        elif (dusk_total <= now_total_utc and set_daytime != "night" and i >= 1):
            lights_switchOff(0, 2)
        # night after midnight
        elif (now_total_utc <= sunrise_total and set_daytime != "night" and i >= 1):
            lights_switchOff(0, 2)

        # dimming the light randomly
        if (random_i == 0):
            random_time_min = randint(sunrise_total + 120, dusk_total - 120)
            random_time_max = random_time_min + 10
            print("Time to start the random dimming today: " + str(random_time_min), file=f)
        if (random_day != 3 and random_i <= 1):
            random_i += 1
            random_day = randint(0, 6)
            print("The day for running the random dimming is: " + str(random_day) + ". Randomised for the " +
                  str(random_i) + ". time.", file=f)
        if (random_time_min <= now_total_utc <= random_time_max and random_day == 3 and random_i != 5):
            lights_dimming(0, 2)
            print("RANDOM DIMMING!", file=f)
            time.sleep(600)
            lights_switchOn(0, 2)
            print("Ending random dimming.", file=f)
            random_i = 5

        # Break while-loop to reboot:
        if (reboot_time_min <= now_total_utc <= reboot_time_max and i >= 1440):
            break

    i += 1
    time.sleep(regular_sleep_time)

prepare_restart()
