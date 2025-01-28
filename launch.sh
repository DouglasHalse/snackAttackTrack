#!/bin/bash

# Activate venv
source /home/pi/snackAttackTrack/venv/bin/activate

# Change directory to snackAttackTrack
cd /home/pi/snackAttackTrack

# Launch main.py with arguments
python GuiApp/main.py -- --no-inspector --rotate-screen 180 --hide-cursor
