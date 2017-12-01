# Changelog
All notable changes to this project will be documented in this file.

(The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).)


## 2.26 - 2017-12-01
### Changed
- `EmulatorGUI_board.py`: Properly import tkinter
- `sunsimulator.py`: Print two digits for all hours/minutes and four digits for total times (e.g. `01:59 / 0119`)


## 2.25 - 2017-10-26
### Added
- As my WittyPi2 doesn't like reboots any longer, i added the parameter `--Restart` into the script so one can choose to reboot the device periodically (or never) from outside the script.


## 2.24 - 2017-10-25
### Changed
- All parameters now start with upper case (`--Mode`,`--TestMode`,`--EnableOverride`,`--Log`).

### Added
- `--TestMode` - Mode to loop functions of specified `--Mode` every 5 seconds. (Good for testing GPIO pins).


## 2.23 - 2017-10-25
### Changed
- `Try`-`except` for import of GPIO-module.


## 2.22 - 2017-09-05
### Initial version (for changelog).
