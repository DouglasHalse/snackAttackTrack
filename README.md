# Snack Attack Track

Snack Attack Track is a subscription/membership management software meant to run on a raspberry pi with a touchscreen.

## Setup development environment

(If you are trying to follow these steps for the first time, PLEASE let us know if you run into any problems so we can update the setup process)

### Windows

#### Prerequisites

1. Python 3.9 (preferably installed from the Microsoft store)
2. git (<https://git-scm.com/download/win>)

#### Recommended dev-tools

1. GitHub Desktop if you prefer GUI for git (<https://desktop.github.com/>)
2. Visual Studio Code (<https://code.visualstudio.com/>)

#### Installation

1. Clone this repository to your Windows machine using git
2. Run setupDevEnvironmentWindows.bat

#### Start GUI with debugging (with Visual Studio Code)

1. In Visual Studio Code: Select 'Open Folder...' and select the cloned repository
2. Hit Ctrl + Shift + P and write 'select interpreter' and click 'Python: Select Interpreter'
3. Select the Python executable found in \<cloned repository\>/venv/Scripts/python.exe
4. Hit F5 to start debugging with the preset "Python: Run Snack Attack Track GUI" defined in  \<cloned repository\>/.vscode/launch.json

#### Start GUI without debugging

1. Run runGuiWindows.bat

### Ubuntu

#### Prerequisites

1. Python 3.9 or Python 3.10

#### Recommended dev-tools

1. GitKraken Client if you prefer GUI for git (<https://www.gitkraken.com/>)
2. Visual Studio Code (<https://code.visualstudio.com/>)

#### Installation

[//]: <> (<area>-tag to escape hyper-link creation)

1. Clone this repository to your Ubuntu machine using git
2. Run 'bash setupDevEnvironmentUbuntu.<area>sh'

#### Start GUI with debugging (with Visual Studio Code)

1. In Visual Studio Code: Select 'Open Folder...' and select the cloned repository
2. Hit Ctrl + Shift + P and write 'select interpreter' and click 'Python: Select Interpreter'
3. Select the Python executable found in \<cloned repository\>/venv/Scripts/python
4. Hit F5 to start debugging with the preset "Python: Run Snack Attack Track GUI" defined in  \<cloned repository\>/.vscode/launch.json

#### Start GUI without debugging

[//]: <> (<area>-tag to escape hyper-link creation)

1. Run 'bash runGuiUbuntu.<area>sh'
