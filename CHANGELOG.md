# Changelog
All notable changes to this project will be documented in this file.

(The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).)


## 2.29 - 2018-03-31
### Added
- `--Log` now has 3 options: `0` for no output at all, `1` for console-only, and `2` for text-file only.


## 2.28 - 2018-03-22
### Changed
- Improved readability of output (now: local time / UTC / UTC in total), also added it to all fields so it is less confusing.


## 2.27 - 2018-02-17
### Changed
- Minor PEP-8 changes according to flake8 in `sunsimulator.py` and `EmulatorGUI_board.py`.


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
