# RF-Modeler

RF-Modeler is a modeling and visualization application designed to analyze radio frequency (RF) signal behavior using mathematical approximation techniques. The application generates the best-fitting curve from a set of data points, enabling accurate visualization of signal propagation and RF coverage. Built with PySide6, it features a modern and interactive graphical user interface and incorporates advanced mathematical modeling capabilities for analyzing and exploring RF signal data.

## Features

- Interactive function plotting with real-time visualization
- Auto-regression modeling with piecewise logarithmic fitting
- Manual function input with support for various mathematical operations
- Data visualization with both graph and heatmap views
- Background image support for data overlay
- CSV data import and analysis
- Path loss prediction capabilities
- Built-in mathematical function library
- Report generation functionality

## Requirements

- Python 3.6 or higher
- Required Python packages (specified in requirements.txt):
  - numpy >= 1.21.0
  - matplotlib >= 3.4.0
  - PySide6 >= 6.0.0
  - scikit-learn >= 1.0.0
  - scipy >= 1.7.0
  - Pillow >= 9.0.0
  - sympy >= 1.10.0

## Installation

1. Clone the repository or download the source code:
```bash
git clone <repository-url>
cd RF-Modeler
```

### Windows Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Build a standalone executable (optional):
```bash
.\build_windows.bat
```
The executable will be created in the `dist\RF-Modeler` folder. You can run the application by double-clicking `RF-Modeler.exe`.

### Linux Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the required dependencies:
```bash
pip3 install -r requirements.txt
```

3. Build a standalone executable (optional):
```bash
chmod +x build_linux.sh  # Make the build script executable
./build_linux.sh
```
The executable will be created in the `dist/RF-Modeler` folder.

## Running the Application

### Running from Source

#### Windows
1. Activate the virtual environment if not already activated:
```bash
.\venv\Scripts\activate
```

2. Run the application:
```bash
python App.py
```

#### Linux
1. Activate the virtual environment if not already activated:
```bash
source venv/bin/activate
```

2. Run the application:
```bash
python3 App.py
```

### Running the Standalone Executable

#### Windows
Navigate to the `dist\RF-Modeler` folder and double-click `RF-Modeler.exe`, or run from command prompt:
```bash
.\dist\RF-Modeler\RF-Modeler.exe
```

#### Linux
Navigate to the `dist/RF-Modeler` folder and run:
```bash
./dist/RF-Modeler/RF-Modeler
```

## Usage Guide

### Main Interface
- The application window is divided into two main sections:
  - Left: Graph/visualization area
  - Right: Control panel with multiple tabs

### Tabs
1. **Auto Tab**
   - Upload CSV data files
   - Configure regression parameters
   - Switch between graph and heatmap views
   - Generate automatic model fitting

2. **Manual Tab**
   - Enter custom mathematical functions
   - Use the built-in function library
   - Plot single or segmented functions
   - Add background images for reference

3. **Comparison Tab**
   - Load multiple datasets
   - Compare different models or data sets
   - Visualize overlaid plots

4. **Prediction Tab**
   - Input distance values
   - Get path loss predictions
   - View prediction confidence intervals

### Basic Operations
1. **Plotting Functions**
   - Enter a mathematical expression in the manual tab
   - Click "Apply" to visualize the function
   - Use the toolbar for zoom, pan, and save operations

2. **Data Analysis**
   - Upload CSV data through the Auto tab
   - Adjust breaking points and tolerance
   - View automatic regression results
   - Toggle between graph and heatmap views

3. **Report Generation**
   - Use the File menu to generate reports
   - Export plots and analysis results
   - Save data for future reference

## Project Structure

```
RF-Modeler/
├── src/
│   ├── core/           # Core mathematical and plotting functionality
│   ├── gui/            # Graphical user interface components
│   ├── utils/          # Utility functions and helpers
│   └── assets/         # Application resources and icons
├── App.py              # Main application entry point
├── build_linux.sh      # Linux build script
├── build_windows.bat   # Windows build script
└── requirements.txt    # Python dependencies
```

