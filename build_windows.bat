@echo off
REM Install PyInstaller if not already installed
pip install pyinstaller

REM Clean any previous build files
rmdir /s /q build dist

REM Create the executable with PyInstaller
REM --windowed: No console window when running the app (GUI only)
REM --name: Set the name of the output file
REM --add-data: Include additional data files (adjust paths as needed)
pyinstaller --windowed --name="RF-Modeler" ^
    --add-data="src;src" ^
    App.py

echo Windows build completed. Application folder is in the dist\RF-Modeler directory.