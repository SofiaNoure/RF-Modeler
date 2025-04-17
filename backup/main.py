import sys
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, QMenu,
                              QWidgetAction, QGridLayout, QStatusBar, QToolButton,
                              QStackedWidget, QTextEdit, QFileDialog)
from PySide6.QtCore import Qt, QSize, QTimer, QDateTime
from PySide6.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from plotter import FunctionPlotter

class CustomNavigationToolbar(NavigationToolbar):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.setStyleSheet("""
            QToolBar { 
                background: #02070b;
                border: none;
                spacing: 5px;
                padding: 3px;
                border-radius: 4px;
            }
            QToolButton {
                background: #123458;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
            }
            QToolButton:hover {
                background: #132e49;
            }
            QToolButton:pressed {
                background: #02070b;
            }
            QToolButton:checked {
                background: #02070b;
            }
        """)
        for button in self.findChildren(QToolButton):
            button.setIconSize(QSize(20, 20))
            button.setFixedSize(32, 32)

class SideMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Add view mode tracking
        self.is_heatmap = False
        # Add data tracking
        self.csv_data = None
        self.current_model = None

        # Set the background color of the side menu
        self.setStyleSheet("""
            SideMenu {
                background-color: #02070b;
                border: none;
                padding: 10px;
            }
        """)
        
        # Buttons container
        button_container = QWidget()
        button_container.setStyleSheet("border: none; margin: 0px; padding: 0px;")  # Make container transparent
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        # Create buttons
        self.auto_btn = QPushButton("Auto")
        self.manual_btn = QPushButton("Manual")
        self.other_btn = QPushButton("Other")
        
        # Style buttons
        button_style = """
            QPushButton {
                padding: 8px 16px;
                background-color: #123458;
                color: white;
                border: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #132e49;
            }
            QPushButton:pressed {
                background-color: #02070b;
            }
            QPushButton:checked {
                background-color: #02070b;
            }
        """
        for btn in (self.auto_btn, self.manual_btn, self.other_btn):
            btn.setStyleSheet(button_style)
            btn.setCheckable(True)
            button_layout.addWidget(btn)
        
        # Add button container to main layout
        self.layout.addWidget(button_container)
        
        # Create stacked widget for different menus
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QWidget {
                background: #02070b;
                border: none;
                border-bottom-right-radius: 6px;
                border-bottom-left-radius: 6px;
                
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        
        # Create menu contents
        auto_menu = QWidget()
        auto_layout = QVBoxLayout(auto_menu)
        auto_layout.setSpacing(10)

        # Add Upload File button at the top
        upload_container = QWidget()
        upload_layout = QHBoxLayout(upload_container)
        upload_layout.setContentsMargins(0, 0, 0, 10)

        self.upload_btn = QPushButton("Upload File")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #123458;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #132e49;
            }
            QPushButton:pressed {
                background-color: #02070b;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_csv)
        upload_layout.addWidget(self.upload_btn)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: white;")
        upload_layout.addWidget(self.file_label)
        upload_layout.addStretch()

        auto_layout.addWidget(upload_container)

        # First row - MAX Breaking points
        max_label = QLabel("MAX - Breaking points:")
        max_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: white;
            }
        """)
        max_input = QLineEdit()
        max_input.setPlaceholderText("Default Value : 5")
        max_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 6px;
                background-color: white;
                color: black;
                border: none;
                border-radius: 4px;
            }
        """)
        auto_layout.addWidget(max_label)
        auto_layout.addWidget(max_input)

        # Second row - Tolerance
        tolerance_label = QLabel("Tolerance:")
        tolerance_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: white;
            }
        """)
        tolerance_input = QLineEdit()
        tolerance_input.setPlaceholderText("Default Value : 1.00")
        tolerance_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 6px;
                background-color: white;
                color: black;
                border: none;
                border-radius: 4px;
            }
        """)
        auto_layout.addWidget(tolerance_label)
        auto_layout.addWidget(tolerance_input)

        # Third row - Min Segment Length
        min_label = QLabel("Min - Segment Length:")
        min_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: white;
            }
        """)
        min_input = QLineEdit()
        min_input.setPlaceholderText("Default Value : 3")
        min_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 6px;
                background-color: white;
                color: black;
                border: none;
                border-radius: 4px;
            }
        """)
        auto_layout.addWidget(min_label)
        auto_layout.addWidget(min_input)

        # Add Apply button
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)  # Add some top margin
        
        # Add view toggle button
        self.view_toggle_btn = QPushButton("Graph View")
        self.view_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #123458;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #132e49;
            }
            QPushButton:pressed {
                background-color: #02070b;
            }
        """)
        self.view_toggle_btn.clicked.connect(self.toggle_view)
        button_layout.addWidget(self.view_toggle_btn)
        
        button_layout.addStretch()  # Push Apply button to the right
        auto_apply_btn = QPushButton("Apply")
        auto_apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #123458;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #132e49;
            }
            QPushButton:pressed {
                background-color: #02070b;
            }
        """)
        button_layout.addWidget(auto_apply_btn)
        auto_layout.addWidget(button_container)

        # Add stretch to push everything to the top
        auto_layout.addStretch()
        
        manual_menu = QWidget()
        manual_layout = QVBoxLayout(manual_menu)
        manual_layout.setSpacing(10)  # Add some spacing between rows
        
        # First row - Label
        self.function_label = QLabel("Enter function:")
        self.function_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: white;
                
            }
        """)
        manual_layout.addWidget(self.function_label)
        
        # Second row - TextEdit
        self.function_input = QTextEdit()
        self.function_input.setPlaceholderText("e.g., sin(x) or x^2")
        self.function_input.setMinimumWidth(300)
        self.function_input.setMaximumHeight(80)  # Increased height from 60 to 80
        self.function_input.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                padding: 6px;
                background-color: white;
                color: black;
                border: none;
                border-radius: 4px;
            }
        """)
        manual_layout.addWidget(self.function_input)
        
        # Third row - Buttons
        button_row = QHBoxLayout()
        
        self.function_menu_btn = QPushButton("Functions")
        self.function_menu_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding: 6px 12px;
                background-color: #123458;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #132e49;
            }
            QPushButton:pressed {
                background-color: #02070b;
            }
        """)
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #123458;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #132e49;
            }
            QPushButton:pressed {
                background-color: #02070b;
            }
        """)
        
        button_row.addWidget(self.function_menu_btn)
        button_row.addStretch()  # Add stretch to push Apply button to the right
        button_row.addWidget(self.apply_btn)
        manual_layout.addLayout(button_row)
        
        # Add some stretch at the bottom to push everything up
        manual_layout.addStretch()
        
        manual_menu.setLayout(manual_layout)
        
        other_menu = QWidget()
        other_layout = QVBoxLayout(other_menu)
        other_layout.addWidget(QLabel("Other Menu Content"))
        
        # Add menus to stack
        self.stack.addWidget(auto_menu)
        self.stack.addWidget(manual_menu)
        self.stack.addWidget(other_menu)
        
        # Add stack to main layout
        self.layout.addWidget(self.stack)
        
        # Create the function menu
        self.create_function_menu()
        
        # Connect buttons
        self.auto_btn.clicked.connect(lambda: self.show_menu(0))
        self.manual_btn.clicked.connect(lambda: self.show_menu(1))
        self.other_btn.clicked.connect(lambda: self.show_menu(2))
        
        # Connect signals for plotting
        self.apply_btn.clicked.connect(self.plot_function)
        auto_apply_btn.clicked.connect(self.auto_plot_function)
        
        # Store references to auto inputs
        self.max_input = max_input
        self.tolerance_input = tolerance_input
        self.min_input = min_input
        
        # Set Auto as default
        self.auto_btn.setChecked(True)
        self.stack.setCurrentIndex(0)
    
    def create_function_menu(self):
        self.function_menu = QMenu(self)
        
        # Organize functions in categories for better user experience
        function_categories = {
            "Basic": [
                {"display": "x", "code": "x"},
                {"display": "x²", "code": "x^2"},
                {"display": "x³", "code": "x^3"},
                {"display": "√x", "code": "sqrt(x)"},
                {"display": "1/x", "code": "1/x"},
                {"display": "|x|", "code": "abs(x)"}
            ],
            "Trigonometric": [
                {"display": "sin(x)", "code": "sin(x)"},
                {"display": "cos(x)", "code": "cos(x)"},
                {"display": "tan(x)", "code": "tan(x)"},
                {"display": "arcsin(x)", "code": "arcsin(x)"},
                {"display": "arccos(x)", "code": "arccos(x)"},
                {"display": "arctan(x)", "code": "arctan(x)"}
            ],
            "Exponential & Logarithmic": [
                {"display": "eˣ", "code": "exp(x)"},
                {"display": "ln(x)", "code": "log(x)"},
                {"display": "log₁₀(x)", "code": "log10(x)"},
                {"display": "log₂(x)", "code": "log2(x)"},
                {"display": "2ˣ", "code": "2^x"},
                {"display": "10ˣ", "code": "10^x"}
            ],
            "Constants & Operations": [
                {"display": "π", "code": "pi"},
                {"display": "e", "code": "e"},
                {"display": "x + y", "code": " + "},
                {"display": "x - y", "code": " - "},
                {"display": "x × y", "code": " * "},
                {"display": "x ÷ y", "code": " / "}
            ]
        }
        
        # Add categories to menu
        for category, functions in function_categories.items():
            category_menu = self.function_menu.addMenu(category)
            
            # Create a submenu with a grid layout for this category
            grid_menu = QMenu(category_menu)
            grid_widget = QWidget()
            grid_layout = QVBoxLayout(grid_widget)
            
            # Update menu styling
            self.function_menu.setStyleSheet("""
                QMenu {
                    background-color: #123458;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 4px;
                }
                QMenu::item {
                    background-color: transparent;
                    padding: 5px 20px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #02070b;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #02070b;
                    margin: 5px 0px;
                }
            """)
            grid_menu.setStyleSheet(self.function_menu.styleSheet())
            
            # Create rows with 3 functions each
            for i in range(0, len(functions), 3):
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(2, 2, 2, 2)
                row_layout.setSpacing(2)
                
                # Add up to 3 buttons per row
                for j in range(3):
                    if i + j < len(functions):
                        func = functions[i + j]
                        btn = QPushButton(func["display"])
                        btn.setFixedSize(80, 30)
                        btn.setStyleSheet("""
                            QPushButton {
                                background-color: #123458;
                                color: white;
                                border: none;
                                border-radius: 4px;
                            }
                            QPushButton:hover {
                                background-color: #132e49;
                            }
                            QPushButton:pressed {
                                background-color: #02070b;
                            }
                        """)
                        btn.clicked.connect(lambda checked=False, f=func["code"]: 
                                           self.insert_function(f) or grid_menu.close())
                        row_layout.addWidget(btn)
                
                grid_layout.addWidget(row_widget)
            
            # Add the grid widget to the menu
            grid_action = QWidgetAction(category_menu)
            grid_action.setDefaultWidget(grid_widget)
            category_menu.addAction(grid_action)
        
        self.function_menu_btn.setMenu(self.function_menu)

    def insert_function(self, function_text):
        current_text = self.function_input.toPlainText()
        cursor = self.function_input.textCursor()
        current_position = cursor.position()
        
        # Check if the function_text is an operator
        operators = [" + ", " - ", " * ", " / "]
        is_operator = function_text in operators
        
        if is_operator:
            # For operators, just insert at cursor position
            new_text = current_text[:current_position] + function_text + current_text[current_position:]
            self.function_input.setText(new_text)
            cursor.setPosition(current_position + len(function_text))
            self.function_input.setTextCursor(cursor)
        else:
            # For functions, check if we need a multiplication symbol
            if current_position > 0 and current_text[current_position-1].isalnum():
                new_text = current_text[:current_position] + " * " + function_text + current_text[current_position:]
                self.function_input.setText(new_text)
                cursor.setPosition(current_position + len(" * " + function_text))
                self.function_input.setTextCursor(cursor)
            else:
                new_text = current_text[:current_position] + function_text + current_text[current_position:]
                self.function_input.setText(new_text)
                cursor.setPosition(current_position + len(function_text))
                self.function_input.setTextCursor(cursor)
        
        return False

    def plot_function(self):
        function_str = self.function_input.toPlainText().strip()
        if not function_str:
            return
        
        try:
            # Use the parent's FunctionPlotter to evaluate the function
            x, y = self.parent.function_plotter.evaluate_function(function_str)
            
            # Clear previous plot
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            
            # Plot the function
            self.parent.ax.plot(x, y, 'b-')
            self.parent.ax.grid(True)
            self.parent.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            self.parent.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            self.parent.ax.set_xlabel('x')
            self.parent.ax.set_ylabel('y')
            self.parent.ax.set_title(f'Plot of {function_str}')
            
            # Set x-axis limits to default 0-20 range
            self.parent.ax.set_xlim(0, 20)
            
            # Check if the y values in the visible x range are within 0-20
            visible_y = y[(x >= 0) & (x <= 20)]
            if len(visible_y) > 0:
                y_min, y_max = np.min(visible_y), np.max(visible_y)
                if y_min >= -5 and y_max <= 25:  # Give some padding around 0-20
                    self.parent.ax.set_ylim(0, 20)
                else:
                    # Use the original dynamic limits if function goes outside our preferred range
                    y_min, y_max = self.parent.function_plotter.get_plot_limits(visible_y)
                    self.parent.ax.set_ylim(y_min, y_max)
            else:
                self.parent.ax.set_ylim(0, 20)
            
            # Enable pan/zoom
            self.parent.toolbar.update()
            self.parent.canvas.draw()
            
        except Exception as e:
            self.parent.ax.text(0.5, 0.5, f"Error: {str(e)}", 
                        ha='center', va='center', transform=self.parent.ax.transAxes, color='red')
            self.parent.ax.set_title("Function Plot Error")
            self.parent.canvas.draw()
            print(f"Error plotting function: {e}")

    def toggle_view(self):
        self.is_heatmap = not self.is_heatmap
        self.view_toggle_btn.setText("Heatmap View" if self.is_heatmap else "Graph View")
        # Trigger replot with current view mode
        self.auto_plot_function()

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Upload CSV File",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                from AutoCalcModel import load_data_from_file, PiecewiseLogarithmicRegression
                
                # Load the data using the existing function
                x, y, _ = load_data_from_file(file_path)
                self.csv_data = (x, y)
                
                # Update the file label
                self.file_label.setText(file_path.split("/")[-1])
                
                # Store the filename
                self.csv_filename = file_path.split("/")[-1]
                
                return True
            except Exception as e:
                self.parent.statusBar.showMessage(f"Error loading CSV file: {str(e)}", 5000)
                return False

    def auto_plot_function(self):
        try:
            # Get values from inputs, use defaults if empty
            max_points = int(self.max_input.text()) if self.max_input.text() else 5
            tolerance = float(self.tolerance_input.text()) if self.tolerance_input.text() else 1.00
            min_length = int(self.min_input.text()) if self.min_input.text() else 3
            
            # Clear previous plot
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            
            if self.is_heatmap:
                if self.csv_data is None:
                    # Show message to upload file first
                    self.parent.ax.text(0.5, 0.5, 
                        "Please upload a CSV file first", 
                        ha='center', va='center', transform=self.parent.ax.transAxes)
                    self.parent.ax.set_title("No Data")
                else:
                    # Get data from CSV
                    x, y = self.csv_data
                    
                    # Create a grid for the heatmap
                    grid_size = 500  # Increased for better resolution
                    x_min, x_max = x.min(), x.max()
                    
                    # Create x array for interpolation
                    xi = np.linspace(x_min, x_max, grid_size)
                    
                    # Initialize Z array (1D for path loss vs distance)
                    Z = np.full(grid_size, np.max(y))
                    
                    # For each point in our data, update nearby points with interpolation
                    for dist, loss in zip(x, y):
                        # Find indices within influence range
                        idx = np.abs(xi - dist).argsort()[:5]  # Take 5 nearest points
                        distances = np.abs(xi[idx] - dist)
                        weights = 1 / (1 + distances)  # Weight by inverse distance
                        weights = weights / np.sum(weights)  # Normalize weights
                        Z[idx] = np.minimum(Z[idx], loss)
                    
                    # Create 2D arrays for visualization
                    Z_2d = np.tile(Z, (50, 1))  # Repeat the 1D array 50 times
                    
                    # Create heatmap with custom colormap (red=good signal, blue=bad signal)
                    im = self.parent.ax.imshow(Z_2d, 
                                             extent=[x_min, x_max, 0, 1],
                                             aspect='auto',
                                             origin='lower',
                                             cmap='RdYlBu_r')  # Reversed RedYellowBlue colormap
                    
                    # Add colorbar
                    cbar = self.parent.figure.colorbar(im)
                    cbar.set_label('Path Loss (dB)', rotation=270, labelpad=15)
                    
                    # Plot the actual data points
                    self.parent.ax.scatter(x, [0.5] * len(x), c=y, 
                                         cmap='RdYlBu_r', 
                                         s=50, 
                                         edgecolor='white')
                    
                    # Set labels and title
                    self.parent.ax.set_xlabel('Distance')
                    self.parent.ax.set_yticks([])  # Hide y-axis ticks
                    self.parent.ax.set_title('Path Loss Heatmap\nWarmer colors = Better signal (lower loss)')
                    
                    # Adjust layout
                    self.parent.figure.tight_layout()
            else:
                if self.csv_data is None:
                    self.parent.ax.text(0.5, 0.5, 
                        "Please upload a CSV file first", 
                        ha='center', va='center', transform=self.parent.ax.transAxes)
                    self.parent.ax.set_title("No Data")
                else:
                    from AutoCalcModel import PiecewiseLogarithmicRegression, plot_results
                    
                    # Create and fit the model with the current parameters
                    x, y = self.csv_data
                    model = PiecewiseLogarithmicRegression(
                        max_breakpoints=max_points,
                        min_segment_length=min_length,
                        tolerance=tolerance,
                        verbose=True
                    )
                    model.fit(x, y)
                    self.current_model = model

                    # Clear the figure but keep the axes
                    self.parent.figure.clear()
                    self.parent.ax = self.parent.figure.add_subplot(111)

                    # Plot data points
                    self.parent.ax.scatter(x, y, s=30, alpha=0.5, color='blue')

                    # Generate colors for segments using a colormap
                    num_segments = len(model.breakpoints_) - 1
                    colors = plt.cm.rainbow(np.linspace(0, 1, num_segments))

                    # Plot fitted curve segment by segment with different colors
                    x_fine = np.linspace(x.min(), x.max(), 5000)
                    for i in range(num_segments):
                        mask = (x_fine >= model.breakpoints_[i]) & (x_fine <= model.breakpoints_[i + 1])
                        if i < len(model.models_) and model.models_[i] is not None:
                            A, B = model.models_[i]
                            x_segment = x_fine[mask]
                            y_segment = A + B * np.log(x_segment)
                            self.parent.ax.semilogx(x_segment, y_segment, '-', 
                                                  linewidth=2, 
                                                  color=colors[i])
                    
                    # Add breakpoints vertical lines
                    for bp in model.breakpoints_[1:-1]:
                        self.parent.ax.axvline(bp, color='k', linestyle='--', alpha=0.7, linewidth=1.5)

                    # Set labels and title
                    self.parent.ax.set_xlabel('x (log scale)')
                    self.parent.ax.set_ylabel('y')
                    self.parent.ax.set_title(f'Piecewise Logarithmic Regression\nR² = {model.r2_:.4f}, MSE = {model.mse_:.4f}')
                    self.parent.ax.grid(True, which='both', alpha=0.4)
                    
                    # Adjust layout
                    self.parent.figure.tight_layout()

            self.parent.canvas.draw()
            
        except ValueError as e:
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            self.parent.ax.text(0.5, 0.5, f"Error: Please enter valid numbers\n{str(e)}", 
                        ha='center', va='center', transform=self.parent.ax.transAxes, color='red')
            self.parent.ax.set_title("Auto Plot Error")
            self.parent.canvas.draw()

    def show_menu(self, index):
        # Uncheck all buttons
        self.auto_btn.setChecked(False)
        self.manual_btn.setChecked(False)
        self.other_btn.setChecked(False)
        
        # Reset to graph view if switching away from auto panel
        if index != 0 and self.is_heatmap:
            self.is_heatmap = False
            self.view_toggle_btn.setText("Graph View")
            self.parent.init_plot()  # This will handle the basic plot setup
            if index == 1:
                self.plot_function()  # If switching to manual, show current function if any
        
        # Check the clicked button
        if index == 0:
            self.auto_btn.setChecked(True)
        elif index == 1:
            self.manual_btn.setChecked(True)
        else:
            self.other_btn.setChecked(True)
            
        self.stack.setCurrentIndex(index)

class MathPlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project 19")
        self.setMinimumSize(1000, 700)

        # Set the main window background color
        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
            }
            QMenuBar {
                background-color: #02070b;
                color: white;
                border: none;
            }
            QMenuBar::item {
                background-color: #02070b;
                color: white;
                padding: 4px 10px;
            }
            QMenuBar::item:selected {
                background-color: #132e49;
            }
            QMenuBar::item:pressed {
                background-color: #123458;
            }
            QMenu {
                background-color: #02070b;
                color: white;
                border: none;
                padding: 5px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #132e49;
            }
            QMenu::separator {
                height: 1px;
                background-color: #123458;
                margin: 5px 0px;
            }
        """)

        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        upload_action = file_menu.addAction("Upload CSV")
        upload_action.triggered.connect(self.upload_csv)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Zoom In")
        view_menu.addAction("Zoom Out")
        view_menu.addAction("Reset View")
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About")

        # Initialize the plotter
        self.function_plotter = FunctionPlotter()

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create horizontal layout for graph and side menu
        content_layout = QHBoxLayout()
        
        # Graph container (2/3 of width)
        graph_container = QWidget()
        graph_layout = QVBoxLayout(graph_container)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        
        # Graph area
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = CustomNavigationToolbar(self.canvas, self)
        graph_layout.addWidget(self.toolbar)
        graph_layout.addWidget(self.canvas)
        
        # Side menu (1/3 of width)
        self.side_menu = SideMenu(self)  # Pass self as parent to access function_plotter
        
        # Add widgets to content layout with stretch factors
        content_layout.addWidget(graph_container, stretch=2)
        content_layout.addWidget(self.side_menu, stretch=1)
        
        # Add content layout to main layout
        main_layout.addLayout(content_layout)

        # Status bar for coordinates and time
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Create permanent widgets for the status bar
        self.coord_label = QLabel("(x: 0.0000, y: 0.0000)")
        self.time_label = QLabel()
        
        # Add widgets to status bar
        self.statusBar.addWidget(self.coord_label)
        self.statusBar.addPermanentWidget(self.time_label)  # Permanent widgets are aligned to the right
        
        # Start the timer to update date and time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Update every second
        self.update_datetime()  # Initial update

        # Connect mouse events
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        self.canvas.mpl_connect('scroll_event', self.on_mouse_wheel)

        # Initialize with empty plot
        self.init_plot()

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Upload CSV File",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # Read CSV file using numpy
                data = np.genfromtxt(file_path, delimiter=',', skip_header=1)
                if data.shape[1] >= 2:  # Ensure we have at least 2 columns
                    # Store the data for later use
                    self.csv_x_data = data[:, 0]
                    self.csv_y_data = data[:, 1]
                    self.csv_filename = file_path.split("/")[-1]
                    return True
                else:
                    raise ValueError("CSV file must have at least 2 columns")
            except Exception as e:
                # Show error in status bar instead of plot
                self.statusBar.showMessage(f"Error loading CSV file: {str(e)}", 5000)  # Show for 5 seconds
                return False

    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("yyyy-MM-dd hh:mm:ss")
        self.time_label.setText(formatted_datetime)

    def init_plot(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True)
        self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('Function Plot')
        # Set the default view range
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 20)
        self.canvas.draw()

    def on_mouse_move(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.coord_label.setText(f"(x: {x:.4f}, y: {y:.4f})")
        else:
            self.coord_label.setText("(x: 0.0000, y: 0.0000)")

    def on_mouse_click(self, event):
        if event.inaxes and event.button == 1:  # Left click
            x, y = event.xdata, event.ydata
            self.coord_label.setText(f"Clicked at (x: {x:.4f}, y: {y:.4f})")
        else:
            self.coord_label.setText("(x: 0.0000, y: 0.0000)")

    def on_mouse_wheel(self, event):
        # Get the current x and y axis limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        # Get the cursor position
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None:
            return
        
        # Set the zoom factor
        base_scale = 1.1
        
        # Calculate the new limits based on scroll direction
        if event.button == 'up':
            # Zoom in
            scale_factor = 1 / base_scale
        else:
            # Zoom out
            scale_factor = base_scale
        
        # Calculate new x limits
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_xlim = [
            xdata - (xdata - cur_xlim[0]) * scale_factor,
            xdata + (cur_xlim[1] - xdata) * scale_factor
        ]
        
        # Calculate new y limits
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        new_ylim = [
            ydata - (ydata - cur_ylim[0]) * scale_factor,
            ydata + (cur_ylim[1] - ydata) * scale_factor
        ]
        
        # Set the new limits
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        
        # Redraw the plot
        self.canvas.draw_idle()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MathPlotterApp()
    window.show()
    sys.exit(app.exec())