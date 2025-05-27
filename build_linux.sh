#!/bin/bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Clean any previous build files
rm -rf build dist

# Create the executable with PyInstaller
# --windowed: No console window when running the app (GUI only)
# --name: Set the name of the output file
# --add-data: Include additional data files (adjust paths as needed)
pyinstaller --windowed --name="RF-Modeler" \
    --add-data="src:src" \
    App.py

echo "Linux build completed. Application folder is in the dist/RF-Modeler directory."