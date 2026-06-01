#!/bin/bash

# Update apt
sudo apt update

# Install dependencies for kivy + udisks2 for USB auto-mount
sudo apt -y install python3-setuptools git-core python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   libgstreamer1.0-dev \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   libmtdev-dev \
   xclip xsel libjpeg-dev python3-venv udisks2

# Check if venv already exists
if [ -d "./venv" ]
then
    # Remove old venv
    sudo rm -r ./venv
fi

# Install virtualenv
python3 -m pip install --upgrade pip setuptools virtualenv

# Create venv
python3 -m venv ./venv

# Activate venv
source ./venv/bin/activate

# Verify venv was activated
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "Virtual environment not activated"
    exit 1
fi

# Install Pi requirements in venv (includes RFID reader module)
./venv/bin/python -m pip install -r requirements-raspberry-pi.txt

echo "Setup complete"
echo "To run the GUI, run the command: 'bash run.sh'"
