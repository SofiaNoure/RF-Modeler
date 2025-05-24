# RF-Modeler

RF-Modeler is a sophisticated application designed for modeling and visualizing mathematical functions and data, with a particular focus on radio frequency (RF) signal analysis. The application features a modern graphical user interface built with PySide6 and incorporates advanced mathematical modeling capabilities.

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

2. Create and activate a virtual environment (recommended):
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
pip3 install -r requirements.txt #In case of using linux
```

## Running the Application

1. Run the application using Python:
```bash
python App.py
python3 App.py #In case of using linux
```

2. For Windows users, you can also build a standalone executable:
```bash
.\build_windows.bat
```
The executable will be created in the `dist` folder.

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

## Support

For issues, bugs, or feature requests, please submit an issue through the project's issue tracker.

## License
XXXXXXXXXX
