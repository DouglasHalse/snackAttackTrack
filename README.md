# Snack Attack Track

Snack Attack Track is a subscription/membership management software meant to run on a raspberry pi with a touchscreen.

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

### Pre-commit
This will run `pylint` and `black` to format the code and check for any violations of the `PEP 8` Python coding standards.

```shell
pip install black pylint pre-commit
pre-commit install
pre-commit run -a
```
