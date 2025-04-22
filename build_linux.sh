#!/bin/bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Clean any previous build files
rm -rf build dist

# Create the executable with PyInstaller
# --onefile: Create a single executable file
# --windowed: No console window when running the app (GUI only)
# --name: Set the name of the output file
# --icon: Set the icon file (if you have one, otherwise remove this option)
# --add-data: Include additional data files (adjust paths as needed)
# --hidden-import: Include any imports that PyInstaller might miss
pyinstaller --onefile --windowed --name="RF-Modeler" \
    --add-data="src:src" \
    App.py

echo "Linux build completed. Executable is in the dist folder."