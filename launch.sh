#!/bin/bash

# Activate virtual environment
source /home/pi/snackAttackTrack/venv/bin/activate

# Launch main.py with arguments
python /home/pi/snackAttackTrack/GuiApp/main.py -- --no-inspector --rotate-screen 180
