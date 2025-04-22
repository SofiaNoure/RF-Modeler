@echo off
REM Install PyInstaller if not already installed
pip install pyinstaller

REM Clean any previous build files
rmdir /s /q build dist

REM Create the executable with PyInstaller
REM --onefile: Create a single executable file
REM --windowed: No console window when running the app (GUI only)
REM --name: Set the name of the output file
REM --icon: Set the icon file (if you have one, otherwise remove this option)
REM --add-data: Include additional data files (adjust paths as needed)
REM --hidden-import: Include any imports that PyInstaller might miss
pyinstaller --onefile --windowed --name="RF-Modeler" ^
    --add-data="src;src" ^
    App.py

echo Windows build completed. Executable is in the dist folder.