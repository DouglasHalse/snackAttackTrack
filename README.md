# Snack Attack Track

Snack Attack Track is a subscription/membership management software meant to run on a raspberry pi with a touchscreen.

## Features

- **User Management**: Create and manage user accounts with RFID card linking
- **PIN Security**: 4-digit PIN authentication for enhanced account security
- **Inventory Tracking**: Monitor snack inventory and sales
- **Transaction History**: Track purchases, top-ups, and transactions
- **Gamble Mode**: Optional wheel of snacks feature
- **Statistics**: User and store statistics tracking

## Security

### PIN Authentication

All new users are required to create a 4-digit PIN during registration. This PIN is:
- **Hashed**: PINs are stored using SHA-256 hashing, never in plaintext
- **Required**: Users must enter their PIN after card scan or user selection
- **Secure**: Prevents unauthorized access even if someone has your RFID card

### Admin Panel Access

The admin panel is protected by a separate admin PIN for enhanced security:
- **Admin PIN**: `4444` (default)
- **Protected Access**: Users must enter the admin PIN to access settings and admin features
- **Settings Button**: Click the settings icon in any screen's navigation header to be prompted for admin PIN

To change the admin PIN, edit the `ADMIN_PIN` constant in `GuiApp/widgets/popups/adminPinEntryPopup.py`

**For existing installations**: Run the migration script to add PIN support:
```shell
python migrate_add_pin.py
```

Existing users without PINs can continue to log in normally until they set a PIN through their profile.

## Setup development environment

> [!TIP]
> If you are trying to follow these steps for the first time, PLEASE let us know if you run into any problems so we can update the setup process

### Windows

#### Prerequisites

1. Python 3.9 (preferably installed [from the Microsoft store](ms-windows-store://pdp/?ProductId=9p7qfqmjrfp7))
2. [git](https://git-scm.com/download/win)

#### Recommended dev-tools

1. [GitHub Desktop](https://desktop.github.com/download) (if you prefer GUI for git)
2. [Visual Studio Code](https://code.visualstudio.com/download)

#### Installation

Clone the repository either with GUI or following terminal commands

```shell
git clone https://github.com/DouglasHalse/snackAttackTrack.git
.\setupDevEnvironmentWindows.bat
```

#### Start GUI with debugging (with Visual Studio Code)

1. In Visual Studio Code: Select `File > Open Folder...` and select the cloned repository
2. Hit <kbd>^ Ctrl</kbd> + <kbd>⇧ Shift</kbd> + <kbd>P</kbd> and write `select interpreter` and click `Python: Select Interpreter`
3. Select the Python executable found in `venv/Scripts/python.exe`
4. Hit <kbd>F5</kbd> to start debugging with the preset `Python: Run Snack Attack Track GUI`

#### Start GUI without debugging

Run `runGuiWindows.bat`

### Linux

#### Prerequisites

1. Python 3.9 or Python 3.10

#### Recommended dev-tools

1. [GitKraken Client](https://www.gitkraken.com/download) if you prefer GUI for git
2. [Visual Studio Code](https://code.visualstudio.com/download)

#### Installation
Clone the repository either with GUI or following terminal commands

```shell
git clone https://github.com/DouglasHalse/snackAttackTrack.git
bash setupDevEnvironmentUbuntu.sh
```

#### Start GUI with debugging (with Visual Studio Code)

1. In Visual Studio Code: Select `File > Open Folder...` and select the cloned repository
2. Hit <kbd>^ Ctrl</kbd> + <kbd>⇧ Shift</kbd> + <kbd>P</kbd> and write `select interpreter` and click `Python: Select Interpreter`
3. Select the Python executable found in `venv/bin/python`
4. Hit <kbd>F5</kbd> to start debugging with the preset `Python: Run Snack Attack Track GUI`

#### Start GUI without debugging

1. Run `bash runGuiUbuntu.sh` in a terminal

### Debugging gui layouts
1. Press <kbd>^ Ctrl</kbd> + <kbd>E</kbd> to start kivy inspector

### Raspberry Pi Deployment

For production deployment on Raspberry Pi with automatic boot:

> **Note:** These commands run **on the Raspberry Pi**, not on Windows. Use SSH or direct terminal access.

**Quick Setup (run on the Pi):**
```bash
# SSH into your Raspberry Pi first:
# ssh pi@raspberrypi.local

# Then run:
curl -sSL https://raw.githubusercontent.com/DouglasHalse/snackAttackTrack/main/rpi-setup/quick-deploy.sh | bash
sudo reboot
```

**Detailed Guide:**
See [rpi-setup/README.md](rpi-setup/README.md) for complete instructions on:
- Accessing Raspberry Pi from Windows (SSH setup)
- Creating custom bootable images
- Auto-start configuration on Raspberry Pi OS Lite
- Display and touchscreen setup
- Performance optimization
- Creating distributable images

The Raspberry Pi setup uses OS Lite (no desktop environment) for:
- ⚡ Fast boot time (~10-15 seconds)
- 💾 Minimal resource usage (~200MB RAM)
- 🎯 Direct kiosk-mode operation
- 🔧 Longer SD card lifespan

### Pre-commit
This will run `pylint` and `black` to format the code and check for any violations of the `PEP 8` Python coding standards.

```shell
pip install black pylint pre-commit
pre-commit install
pre-commit run -a
```
