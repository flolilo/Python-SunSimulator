# Python-SunSimulator
A Python script that uses Pyephem to turn an Raspberry Pi into an enhanced time switch

## Disclaimer
#### The script shouldn't damage anything - what can damage things (or you) is the hardware setup. Electrical energy can be a deadly thing, so I strongly discourage anybody to fool around with this if you don't have the qualification to do so legally. Don't blame me if you soldered your fork to your mains outlet via the relais and then get electrocuted on sunrise.

You have been warned. ;-)

## Requirements
-   A Raspberry Pi (any model will work, but without modification, the script will only work with those that have 40 GPIO pins)
-   [PyEphem](http://rhodesmill.org/pyephem/)
-   Any relais that will work with the RasPi's GPIO
    -   `outside` is made for regular switching on/off, while `aquarium` will not only switch on/off, but dim - a description is supplied inside [`aquarium_diagram.PNG`](/files/aquarium_diagram.PNG)
-   For trying it out on your computer: [Pi GPIO Emulator](https://sourceforge.net/projects/pi-gpio-emulator/) (This script brings with it its own version of this in form of `EmulatorGUI_board.py`.)
    -   Pi GPIO Emulator has been marked under the [Creative Commons Attribution License](https://creativecommons.org/licenses/by/4.0/), which I hope to satisfy with my changes and credits.

## Installation on a Raspberry Pi (from scratch)
#### This is just my way of setting things up - there are arguably better, faster, and/or safer ways to do that.
-	Install [Raspbian Lite](https://www.raspberrypi.org/downloads/raspbian/) on your SD-card via e.g. [Rufus](https://rufus.akeo.ie/)
-	Run Raspbian, `sudo raspi-config` set keyboard layout & time zone (UTC), set user PW
-	[WLAN installation via wpa_supplicant](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md)
-	`sudo apt-get update && sudo apt-get dist-upgrade`, if needed: `sudo apt autoremove`. Reboot.
-	`sudo apt-get install rpi-update && sudo rpi-update`, `sudo pip3 install pip-review && sudo pip-review -a`. Reboot.
-	If you have one, install your RTC.
-	`sudo apt-get install python3 python3-doc python3-tk python3-venv python3.4-venv python3.4-doc binfmt-support`
-	`sudo apt-get install python-pip python-dev python3-pip python3-dev python-rpi.gpio python3-rpi.gpio`
-	`sudo pip install pyephem && sudo pip3 install pyephem`
-   [Download SunSimulator.py](https://github.com/flolilo/Python-SunSimulator/archive/master.zip) and extract it to e.g. `/home/pi/Python-SunSimulator/sunsimulator.py`
    - If you use SSH to get into your RasPi, you can also use this: `sudo apt-get update && sudo apt-get install git && git clone https://github.com/flolilo/Python-SunSimulator.git -v`
-	`sudo nano /etc/rc.local` : add `"python3 /home/pi/Python-SunSimulator/sunsimulator.py --Mode XYZ &"` (`XYZ` = `aquarium` or `outside`)
-   `ps -ef | grep python` should then show the script as running even after restarts.

## To do
- [x] Making everything readable for the English-speaking community.
- [ ] Making the GPIO Emulator close properly
- [x] Replacing `daytime_var` -> *Now called `set_daytime` and is a string, so more readable.
