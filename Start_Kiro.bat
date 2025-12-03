@echo off
:: Sets the directory to the current folder so it always finds the script
cd /d "%~dp0"
:: Runs Kiro silently
start "" pythonw kiro_organizer.py --watch
exit