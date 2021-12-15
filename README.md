
# Font Selector

This is a simple project which made it easier to select fonts for CNC and laser engraving projects.

## Getting started

In the below if your default 'python' is python3 then change the below commands to just be 'python'.

1. Ubuntu: Install necessary prerequisites
   ```
   sudo apt install -y python3
   python3 -m pip install --user --upgrade pip
   python3 -m pip install --user virtualenv
   ```
   In Ubuntu to allow PyQT - along with QtCreator - to work do:
   ```
   sudo apt-get update -y
   sudo apt-get install libxcb-icccm4 libxcb-xkb1 libxcb-icccm4 libxcb-image0 libxcb-render-util0 libxcb-randr0 libxcb-keysyms1 libxcb-xinerama0
   sudo apt-get install qtcreator qt5-default qt5-doc qtbase5-examples qt5-doc-html qtbase5-doc-html
   ```
1. Windows:  It is useful to use QtDesigner which can be downloaded from https://build-system.fman.io/qt-designer-download.

1. Create a new virtual environment within the same directory as the git checkout.
   ```
   cd FontSelector
   python3 -m virtualenv --python=python3 env
   ```
   or for windows use:
   ```
   cd FontSelector
   python -m venv env
   ```
1. Activate the new virtual environment
   ```
   source env/bin/activate
   ```
   or 
   ```
   env\scripts\activate.bat
   ```
   if you are on windows.
1. Install, into the new virtual environment, the required python modules for this specific environment.  This will be installed within the virtual env which was activated earlier.
   ```
   python3 -m pip install -r requirements.txt
   ```

   Then you can just run 
   ```
   python3 FontSelector.py
   ```

## Additional
There is no real documentation here beyond the code.  IF necessary then I will augment at some future date.

