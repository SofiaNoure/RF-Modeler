from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QMenu, QWidgetAction,
                             QStackedWidget, QTextEdit, QFileDialog)
from PySide6.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt

from ..core.regression_model import PiecewiseLogarithmicRegression
from ..utils.data_loader import load_data_from_file
from .styles import Styles

class SideMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.is_heatmap = False
        self.csv_data = None
        self.current_model = None

        # Create input fields as instance variables
        self.max_input = QLineEdit()
        self.tolerance_input = QLineEdit()
        self.min_input = QLineEdit()

        self.setStyleSheet(Styles.SIDE_MENU)
        self._setup_ui()
        self._connect_signals()
        
        self.auto_btn.setChecked(True)
        self.stack.setCurrentIndex(0)

    def _setup_ui(self):
        self._create_tab_buttons()
        self._create_stacked_widget()
        self._setup_auto_menu()
        self._setup_manual_menu()
        self._setup_other_menu()
        self._create_function_menu()

    def _create_tab_buttons(self):
        button_container = QWidget()
        button_container.setStyleSheet("background-color: #000000; border: none; margin: 0px; padding: 5px; border-radius: 6px;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        self.auto_btn = QPushButton("Auto")
        self.manual_btn = QPushButton("Manual")
        self.other_btn = QPushButton("Other")
        
        for btn in (self.auto_btn, self.manual_btn, self.other_btn):
            btn.setStyleSheet(Styles.BUTTON_TAB)
            btn.setCheckable(True)
            button_layout.addWidget(btn)
        
        self.layout.addWidget(button_container)

    def _create_stacked_widget(self):
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QWidget {
                background: #02070b;
                border: none;
                border-bottom-right-radius: 6px;
                border-bottom-left-radius: 6px;
            }
        """)
        self.layout.addWidget(self.stack)

    def _setup_auto_menu(self):
        auto_menu = QWidget()
        auto_layout = QVBoxLayout(auto_menu)
        auto_layout.setSpacing(13)  # Reduced spacing between elements
        auto_layout.setContentsMargins(10, 10, 10, 10)  # Consistent margins

        upload_container = QWidget()
        upload_layout = QHBoxLayout(upload_container)
        upload_layout.setContentsMargins(0, 0, 0, 5)  # Reduced bottom margin

        self.upload_btn = QPushButton("Upload File")
        self.upload_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        upload_layout.addWidget(self.upload_btn)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet(Styles.LABEL)
        upload_layout.addWidget(self.file_label)
        upload_layout.addStretch()
        auto_layout.addWidget(upload_container)

        parameters = [
            ("MAX - Breaking points:", "Default Value : 5", self.max_input),
            ("Tolerance:", "Default Value : 1.00", self.tolerance_input),
            ("Min - Segment Length:", "Default Value : 3", self.min_input)
        ]

        for label_text, placeholder, input_field in parameters:
            # Create container for label and input
            param_container = QWidget()
            param_layout = QVBoxLayout(param_container)
            param_layout.setSpacing(10)  # Very small space between label and input
            param_layout.setContentsMargins(0, 0, 0, 0)  # No margins for container
            
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 12px;  /* Reduced font size */
                    padding: 0;
                    margin: 0;
                }
            """)
            
            input_field.setPlaceholderText(placeholder)
            input_field.setStyleSheet("""
                QLineEdit {
                    font-size: 13px;
                    padding: 4px;  /* Reduced padding */
                    background-color: white;
                    color: black;
                    border: none;
                    border-radius: 4px;
                    min-height: 20px;  /* Reduced height */
                }
            """)
            input_field.setFixedHeight(28)  # Set fixed height for consistency
            
            param_layout.addWidget(label)
            param_layout.addWidget(input_field)
            auto_layout.addWidget(param_container)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 5, 0, 0)  # Reduced top margin

        self.view_toggle_btn = QPushButton("Graph View")
        self.view_toggle_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        button_layout.addWidget(self.view_toggle_btn)
        
        button_layout.addStretch()
        
        self.auto_apply_btn = QPushButton("Apply")
        self.auto_apply_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        button_layout.addWidget(self.auto_apply_btn)
        
        auto_layout.addWidget(button_container)
        auto_layout.addStretch()
        
        self.stack.addWidget(auto_menu)

    def _setup_manual_menu(self):
        manual_menu = QWidget()
        manual_layout = QVBoxLayout(manual_menu)
        manual_layout.setSpacing(10)
        
        self.function_label = QLabel("Enter function:")
        self.function_label.setStyleSheet(Styles.LABEL)
        manual_layout.addWidget(self.function_label)
        
        self.function_input = QTextEdit()
        self.function_input.setPlaceholderText("e.g., sin(x) or x^2")
        self.function_input.setMinimumWidth(300)
        self.function_input.setMaximumHeight(80)
        self.function_input.setStyleSheet(Styles.INPUT_FIELD)
        manual_layout.addWidget(self.function_input)
        
        button_row = QHBoxLayout()
        self.function_menu_btn = QPushButton("Functions")
        self.function_menu_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        
        button_row.addWidget(self.function_menu_btn)
        button_row.addStretch()
        button_row.addWidget(self.apply_btn)
        manual_layout.addLayout(button_row)
        
        manual_layout.addStretch()
        self.stack.addWidget(manual_menu)

    def _setup_other_menu(self):
        other_menu = QWidget()
        other_layout = QVBoxLayout(other_menu)
        other_layout.addWidget(QLabel("Other Menu Content"))
        self.stack.addWidget(other_menu)

    def _create_function_menu(self):
        self.function_menu = QMenu(self)
        self.function_menu.setStyleSheet(Styles.FUNCTION_MENU)
        
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

        for category, functions in function_categories.items():
            category_menu = self.function_menu.addMenu(category)
            grid_menu = QMenu(category_menu)
            grid_widget = QWidget()
            grid_layout = QVBoxLayout(grid_widget)
            
            for i in range(0, len(functions), 3):
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(2, 2, 2, 2)
                row_layout.setSpacing(2)
                
                for j in range(3):
                    if i + j < len(functions):
                        func = functions[i + j]
                        btn = QPushButton(func["display"])
                        btn.setFixedSize(80, 30)
                        btn.setStyleSheet(Styles.BUTTON_PRIMARY)
                        btn.clicked.connect(lambda checked=False, f=func["code"]: 
                                         self.insert_function(f) or grid_menu.close())
                        row_layout.addWidget(btn)
                
                grid_layout.addWidget(row_widget)
            
            grid_action = QWidgetAction(category_menu)
            grid_action.setDefaultWidget(grid_widget)
            category_menu.addAction(grid_action)
        
        self.function_menu_btn.setMenu(self.function_menu)

    def _connect_signals(self):
        self.auto_btn.clicked.connect(lambda: self.show_menu(0))
        self.manual_btn.clicked.connect(lambda: self.show_menu(1))
        self.other_btn.clicked.connect(lambda: self.show_menu(2))
        self.upload_btn.clicked.connect(self.upload_csv)
        self.view_toggle_btn.clicked.connect(self.toggle_view)
        self.apply_btn.clicked.connect(self.plot_function)
        self.auto_apply_btn.clicked.connect(self.auto_plot_function)

    def insert_function(self, function_text):
        current_text = self.function_input.toPlainText()
        cursor = self.function_input.textCursor()
        current_position = cursor.position()
        
        operators = [" + ", " - ", " * ", " / "]
        is_operator = function_text in operators
        
        if is_operator:
            new_text = current_text[:current_position] + function_text + current_text[current_position:]
            self.function_input.setText(new_text)
            cursor.setPosition(current_position + len(function_text))
        else:
            if current_position > 0 and current_text[current_position-1].isalnum():
                new_text = current_text[:current_position] + " * " + function_text + current_text[current_position:]
                cursor.setPosition(current_position + len(" * " + function_text))
            else:
                new_text = current_text[:current_position] + function_text + current_text[current_position:]
                cursor.setPosition(current_position + len(function_text))
                
        self.function_input.setText(new_text)
        self.function_input.setTextCursor(cursor)
        return False

    def plot_function(self):
        function_str = self.function_input.toPlainText().strip()
        if not function_str:
            return
        
        try:
            # Show evaluating status in the plot area
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            self.parent.ax.text(0.5, 0.5, "Evaluating function...", 
                              ha='center', va='center', transform=self.parent.ax.transAxes)
            self.parent.canvas.draw()
            
            # Basic security validation
            forbidden = ['import', 'exec', 'eval', 'open', '__']
            if any(term in function_str.lower() for term in forbidden):
                raise ValueError("Invalid function: Contains forbidden terms")
            
            # Evaluate with appropriate range for display
            x, y = self.parent.function_plotter.evaluate_function(function_str)
            
            # Clear previous plot
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            
            # Plot the function
            self.parent.ax.plot(x, y, 'b-', linewidth=2)
            
            # Enhanced grid
            self.parent.ax.grid(True, which='major', linestyle='-', alpha=0.5)
            self.parent.ax.grid(True, which='minor', linestyle=':', alpha=0.2)
            self.parent.ax.minorticks_on()
            
            # Axes
            self.parent.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            self.parent.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            
            # Labels
            self.parent.ax.set_xlabel('x')
            self.parent.ax.set_ylabel('y')
            self.parent.ax.set_title(f'Plot of {function_str}')
            
            # Set view limits
            visible_range = x[(x >= -20) & (x <= 20)]  # Expanded visible range
            if len(visible_range) > 0:
                self.parent.ax.set_xlim(-20, 20)  # Show both positive and negative x
                visible_y = y[(x >= -20) & (x <= 20)]
                if len(visible_y) > 0:
                    y_min, y_max = np.min(visible_y), np.max(visible_y)
                    if abs(y_max - y_min) < 1:  # Very small range
                        mid = (y_max + y_min) / 2
                        self.parent.ax.set_ylim(mid - 1, mid + 1)
                    else:
                        padding = (y_max - y_min) * 0.1
                        self.parent.ax.set_ylim(y_min - padding, y_max + padding)
            
            self.parent.toolbar.update()
            self.parent.canvas.draw()
            
        except Exception as e:
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            error_msg = str(e)
            if len(error_msg) > 100:  # Truncate long error messages
                error_msg = error_msg[:97] + "..."
            self.parent.ax.text(0.5, 0.5, f"Error: {error_msg}", 
                        ha='center', va='center', transform=self.parent.ax.transAxes, color='red')
            self.parent.ax.set_title("Function Plot Error")
            self.parent.canvas.draw()
            self.parent.statusBar.showMessage(f"Error plotting function: {str(e)}", 5000)

    def toggle_view(self):
        self.is_heatmap = not self.is_heatmap
        self.view_toggle_btn.setText("Heatmap View" if self.is_heatmap else "Graph View")
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
                x, y, _ = load_data_from_file(file_path)
                self.csv_data = (x, y)
                self.file_label.setText(file_path.split("/")[-1])
                self.csv_filename = file_path.split("/")[-1]
                return True
            except Exception as e:
                self.parent.statusBar.showMessage(f"Error loading CSV file: {str(e)}", 5000)
                return False

    def auto_plot_function(self):
        try:
            max_points = int(self.max_input.text()) if self.max_input.text() else 5
            tolerance = float(self.tolerance_input.text()) if self.tolerance_input.text() else 1.00
            min_length = int(self.min_input.text()) if self.min_input.text() else 3
            
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            
            if self.is_heatmap:
                self._plot_heatmap()
            else:
                self._plot_regression(max_points, tolerance, min_length)

            self.parent.canvas.draw()
            
        except ValueError as e:
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            self.parent.ax.text(0.5, 0.5, f"Error: Please enter valid numbers\n{str(e)}", 
                        ha='center', va='center', transform=self.parent.ax.transAxes, color='red')
            self.parent.ax.set_title("Auto Plot Error")
            self.parent.canvas.draw()

    def _plot_heatmap(self):
        if self.csv_data is None:
            self.parent.ax.text(0.5, 0.5, 
                "Please upload a CSV file first", 
                ha='center', va='center', transform=self.parent.ax.transAxes)
            self.parent.ax.set_title("No Data")
            return
            
        x, y = self.csv_data
        
        # Validate data
        if len(x) < 3:
            self.parent.ax.text(0.5, 0.5, 
                "Need at least 3 data points for heatmap", 
                ha='center', va='center', transform=self.parent.ax.transAxes)
            self.parent.ax.set_title("Insufficient Data")
            return
            
        grid_size = 500
        x_min, x_max = x.min(), x.max()
        y_min, y_max = y.min(), y.max()
        xi = np.linspace(x_min, x_max, grid_size)
        Z = np.full(grid_size, np.max(y))
        
        for dist, loss in zip(x, y):
            idx = np.abs(xi - dist).argsort()[:5]
            distances = np.abs(xi[idx] - dist)
            weights = 1 / (1 + distances)
            weights = weights / np.sum(weights)
            Z[idx] = np.minimum(Z[idx], loss)
        
        # Clear any existing colorbars
        for im in self.parent.ax.images:
            im.colorbar.remove() if hasattr(im, 'colorbar') else None
            
        Z_2d = np.tile(Z, (50, 1))
        
        im = self.parent.ax.imshow(Z_2d, 
                                 extent=[x_min, x_max, y_min, y_max],
                                 aspect='auto',
                                 origin='lower',
                                 cmap='RdYlBu_r')
        
        cbar = self.parent.figure.colorbar(im)
        cbar.set_label('Path Loss (dB)', rotation=270, labelpad=15)
        
        self.parent.ax.scatter(x, [y_min + (y_max - y_min) * 0.5] * len(x), c=y, 
                             cmap='RdYlBu_r', 
                             s=50, 
                             edgecolor='white')
        
        self.parent.ax.set_xlabel('Distance')
        self.parent.ax.set_ylabel('Path Loss (dB)')
        self.parent.ax.set_title('Path Loss Heatmap\nWarmer colors = Better signal (lower loss)')
        
        self.parent.figure.tight_layout()

    def _plot_regression(self, max_points, tolerance, min_length):
        if self.csv_data is None:
            self.parent.ax.text(0.5, 0.5, 
                "Please upload a CSV file first", 
                ha='center', va='center', transform=self.parent.ax.transAxes)
            self.parent.ax.set_title("No Data")
            return
            
        x, y = self.csv_data
        model = PiecewiseLogarithmicRegression(
            max_breakpoints=max_points,
            min_segment_length=min_length,
            tolerance=tolerance,
            verbose=True
        )
        model.fit(x, y)
        self.current_model = model

        self.parent.ax.scatter(x, y, s=30, alpha=0.5, color='blue')

        num_segments = len(model.breakpoints_) - 1
        colors = plt.cm.rainbow(np.linspace(0, 1, num_segments))

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
        
        for bp in model.breakpoints_[1:-1]:
            self.parent.ax.axvline(bp, color='k', linestyle='--', alpha=0.7, linewidth=1.5)

        self.parent.ax.set_xlabel('x (log scale)')
        self.parent.ax.set_ylabel('y')
        self.parent.ax.set_title(f'Piecewise Logarithmic Regression\nR² = {model.r2_:.4f}, MSE = {model.mse_:.4f}')
        self.parent.ax.grid(True, which='both', alpha=0.4)
        
        self.parent.figure.tight_layout()

    def show_menu(self, index):
        self.auto_btn.setChecked(False)
        self.manual_btn.setChecked(False)
        self.other_btn.setChecked(False)
        
        if index != 0 and self.is_heatmap:
            self.is_heatmap = False
            self.view_toggle_btn.setText("Graph View")
            self.parent.init_plot()
            if index == 1:
                self.plot_function()
        
        if index == 0:
            self.auto_btn.setChecked(True)
        elif index == 1:
            self.manual_btn.setChecked(True)
        else:
            self.other_btn.setChecked(True)
            
        self.stack.setCurrentIndex(index)