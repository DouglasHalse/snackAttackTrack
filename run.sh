#!/bin/bash

# Change to the script's directory (works from any path)
cd "$(dirname "$0")"

# Verify venv exists
if [[ ! -d ./venv ]]
then
    echo "Virtual environment not found"
    exit 1
fi

# Activate venv
source ./venv/bin/activate

# Verify venv was activated
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "Virtual environment not activated"
    exit 1
fi

# Run GUI with Pi production settings
python GuiApp/main.py -- --no-inspector --rotate-screen 180 --hide-cursor
