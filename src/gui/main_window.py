import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QMenuBar, QMenu, QStatusBar, QMessageBox,
                              QFileDialog)
from PySide6.QtCore import QTimer, QDateTime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import numpy as np
import re

from ..core.function_plotter import FunctionPlotter
from .toolbar import CustomNavigationToolbar
from .side_menu import SideMenu
from .styles import Styles

class MathPlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project 19")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        self._setup_menu_bar()
        self._initialize_plotter()
        self._setup_central_widget()
        self._setup_status_bar()
        self._setup_timer()
        self._connect_signals()
        
        # Initialize with empty plot
        self.init_plot()

    def _setup_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        upload_action = file_menu.addAction("Upload CSV")
        upload_action.triggered.connect(self.upload_csv)
        
        # Add Generate Report action
        generate_report_action = file_menu.addAction("Generate Report")
        generate_report_action.triggered.connect(self._generate_report)
        
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        copy_action = edit_menu.addAction("Copy")
        copy_action.triggered.connect(self._copy_function)
        paste_action = edit_menu.addAction("Paste")
        paste_action.triggered.connect(self._paste_function)
        
        # View menu
        view_menu = menubar.addMenu("View")
        zoom_in_action = view_menu.addAction("Zoom In")
        zoom_in_action.triggered.connect(lambda: self._zoom_view(1.25))
        zoom_out_action = view_menu.addAction("Zoom Out")
        zoom_out_action.triggered.connect(lambda: self._zoom_view(0.8))
        reset_view_action = view_menu.addAction("Reset View")
        reset_view_action.triggered.connect(self._reset_view)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about_dialog)

    def _copy_function(self):
        """Copy current function from manual input"""
        if hasattr(self.side_menu, 'function_input'):
            self.side_menu.function_input.copy()

    def _paste_function(self):
        """Paste text into manual function input"""
        if hasattr(self.side_menu, 'function_input'):
            self.side_menu.function_input.paste()

    def _zoom_view(self, factor):
        """Zoom the plot view by a given factor"""
        if not hasattr(self, 'ax') or self.ax is None:
            return
            
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        # Calculate center points
        xcenter = (cur_xlim[1] + cur_xlim[0]) / 2
        ycenter = (cur_ylim[1] + cur_ylim[0]) / 2
        
        # Calculate new ranges
        xrange = (cur_xlim[1] - cur_xlim[0]) / 2
        yrange = (cur_ylim[1] - cur_ylim[0]) / 2
        
        # Set new limits
        self.ax.set_xlim([xcenter - xrange/factor, xcenter + xrange/factor])
        self.ax.set_ylim([ycenter - yrange/factor, ycenter + yrange/factor])
        
        self.canvas.draw_idle()

    def _reset_view(self):
        """Reset to original view"""
        if not hasattr(self, 'ax') or self.ax is None:
            return
            
        # Get current tab
        current_tab = self.side_menu.stack.currentIndex()
        
        if current_tab == 0:  # Auto tab
            # Replot with cached view if available
            if hasattr(self.side_menu, '_cached_state'):
                self.side_menu._apply_cached_view()
            else:
                self.side_menu.auto_plot_function()
        else:  # Manual tab
            function_str = self.side_menu.function_input.toPlainText().strip()
            if function_str:
                self.side_menu.plot_function()
            else:
                self.init_plot()

    def _show_about_dialog(self):
        """Show about dialog with mock data"""
        about = QMessageBox(self)
        about.setWindowTitle("About RF-Modeler")
        about.setText("RF-Modeler v1.0.0")
        about.setInformativeText(
            "A tool for modeling and visualizing RF signal propagation.\n\n"
            "Features:\n"
            "• CSV data visualization\n"
            "• Mathematical function plotting\n"
            "• Piecewise logarithmic regression\n"
            "• Heatmap visualization\n\n"
            "© 2025 RF-Modeler Team"
        )
        about.setIcon(QMessageBox.Information)
        about.exec_()

    def _initialize_plotter(self):
        self.function_plotter = FunctionPlotter()
        self.figure = Figure(constrained_layout=True)  # Enable constrained_layout for better spacing
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = CustomNavigationToolbar(self.canvas, self)

    def _setup_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create horizontal layout for graph and side menu
        content_layout = QHBoxLayout()
        
        # Graph container (2/3 of width)
        graph_container = QWidget()
        graph_layout = QVBoxLayout(graph_container)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        
        graph_layout.addWidget(self.toolbar)
        graph_layout.addWidget(self.canvas)
        
        # Side menu (1/3 of width)
        self.side_menu = SideMenu(self)
        
        content_layout.addWidget(graph_container, stretch=2)
        content_layout.addWidget(self.side_menu, stretch=1)
        main_layout.addLayout(content_layout)

    def _setup_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.coord_label = QLabel("(x: 0.0000, y: 0.0000)")
        self.time_label = QLabel()
        
        self.statusBar.addWidget(self.coord_label)
        self.statusBar.addPermanentWidget(self.time_label)

    def _setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()

    def _connect_signals(self):
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        self.canvas.mpl_connect('scroll_event', self.on_mouse_wheel)

    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("yyyy-MM-dd hh:mm:ss")
        self.time_label.setText(formatted_datetime)

    def init_plot(self):
        # Clear any existing plots and colorbars
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        # Remove any existing colorbars
        for im in self.ax.images:
            if hasattr(im, 'colorbar'):
                im.colorbar.remove()
        
        self.ax.grid(True)
        self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('Function Plot')
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 20)
        self.canvas.draw()

    def upload_csv(self):
        # Forward to side menu's upload method which handles the data storage properly
        self.side_menu.upload_csv()
        if self.side_menu.csv_data is not None:
            # Reset view to Auto tab and trigger a plot
            self.side_menu.show_menu(0)
            self.side_menu.auto_plot_function()

    def _generate_report(self):
        """Generate a PDF report with regression model graph, heatmap and formatted equation"""
        # Check if we have a current model to report
        if not hasattr(self.side_menu, 'current_model') or self.side_menu.current_model is None:
            self.statusBar.showMessage("No model data to generate report", 5000)
            msg_box = QMessageBox()
            msg_box.setWindowTitle("No Model Data")
            msg_box.setText("Please run regression analysis in the Auto panel first")
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.exec_()
            return
            
        if not hasattr(self.side_menu, 'csv_data') or self.side_menu.csv_data is None:
            self.statusBar.showMessage("No CSV data to generate report", 5000)
            return

        # Ask user for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save RF Model Report",
            os.path.expanduser("~") + "/rf_model_report.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return  # User cancelled
            
        # Get the model and data
        model = self.side_menu.current_model
        x, y = self.side_menu.csv_data
        
        # Create a PDF with matplotlib
        with PdfPages(file_path) as pdf:
            # Report header page
            fig_title = plt.figure(figsize=(8.5, 11))
            fig_title.suptitle("RF Signal Propagation Model Report", fontsize=16, y=0.95)
            
            # Add timestamp and basic info
            current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            plt.figtext(0.1, 0.85, f"Generated: {current_datetime}", fontsize=12)
            plt.figtext(0.1, 0.80, f"Data source: {getattr(self.side_menu, 'csv_filename', 'Unknown')}", fontsize=12)
            
            # Add model stats
            stats_text = (
                f"Model Statistics:\n"
                f"R² = {model.r2_:.4f}\n"
                f"MSE = {model.mse_:.4f}\n"
                f"Number of segments = {len(model.breakpoints_) - 1}\n"
                f"Breakpoints = {', '.join([f'{bp:.2f}' for bp in model.breakpoints_])}"
            )
            plt.figtext(0.1, 0.70, stats_text, fontsize=12)
            pdf.savefig(fig_title)
            plt.close(fig_title)
            
            # Plot 1: Regression Graph
            fig_regression = plt.figure(figsize=(8.5, 8))
            ax_reg = fig_regression.add_subplot(111)
            
            # Generate fine-grained x values for smooth curve plotting
            x_fine = np.logspace(np.log10(x.min()), np.log10(x.max()), 1000)
            y_pred_fine = model.predict(x_fine)
            
            # Plot original data points
            ax_reg.scatter(x, y, s=30, alpha=0.5, color='blue')
            
            # Plot segments with different colors
            num_segments = len(model.breakpoints_) - 1
            colors = plt.cm.viridis(np.linspace(0, 0.8, num_segments))
            
            for i in range(num_segments):
                mask = (x_fine >= model.breakpoints_[i]) & (x_fine <= model.breakpoints_[i + 1])
                if i < len(model.models_) and model.models_[i] is not None:
                    # Plot fitted line for this segment
                    ax_reg.semilogx(x_fine[mask], y_pred_fine[mask], '-', 
                              linewidth=2, color=colors[i])
            
            # Add breakpoint indicators
            for i, bp in enumerate(model.breakpoints_[1:-1], 1):
                ax_reg.axvline(bp, color='k', linestyle='--', alpha=0.5, linewidth=1)
                # Add breakpoint value annotation
                y_pos = np.interp(bp, x_fine, y_pred_fine)
                ax_reg.annotate(f'BP{i}\n({bp:.1f})', 
                              (bp, y_pos),
                              xytext=(5, 5), textcoords='offset points',
                              fontsize=8, bbox=dict(facecolor='white', alpha=0.7))
            
            ax_reg.set_xlabel('Distance (log scale)')
            ax_reg.set_ylabel('Path Loss (dB)')
            ax_reg.grid(True, which='both', alpha=0.2)
            ax_reg.grid(True, which='major', alpha=0.5)
            
            title = 'Piecewise Logarithmic Regression'
            stats = f'R² = {model.r2_:.4f} | MSE = {model.mse_:.4f} | Segments = {num_segments}'
            ax_reg.set_title(f'{title}\n{stats}', pad=10)
            
            fig_regression.tight_layout()
            pdf.savefig(fig_regression)
            plt.close(fig_regression)
            
            # Plot 2: Heatmap
            fig_heatmap = plt.figure(figsize=(8.5, 4))
            ax_hm = fig_heatmap.add_subplot(111)
            
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
                
            Z_2d = np.tile(Z, (50, 1))
            
            im = ax_hm.imshow(Z_2d, 
                           extent=[x_min, x_max, y_min, y_max],
                           aspect='auto',
                           origin='lower',
                           cmap='RdYlBu_r')
            
            cbar = fig_heatmap.colorbar(im)
            cbar.set_label('Path Loss (dB)', rotation=270, labelpad=15)
            
            ax_hm.scatter(x, [y_min + (y_max - y_min) * 0.5] * len(x), c=y, 
                       cmap='RdYlBu_r', 
                       s=50, 
                       edgecolor='white')
            
            ax_hm.set_xlabel('Distance')
            ax_hm.set_title('Path Loss Heatmap\nWarmer colors = Better signal (lower loss)')
            
            fig_heatmap.tight_layout(pad=1.1)
            pdf.savefig(fig_heatmap)
            plt.close(fig_heatmap)
            
            # Plot 3: Piecewise Equations (Segment-by-segment)
            fig_equation = plt.figure(figsize=(8.5, 5))
            fig_equation.suptitle("Piecewise Logarithmic Model", fontsize=16, y=0.95)
            
            # Create an axis for the equations - no need for actual plotting here
            ax_eq = fig_equation.add_subplot(111)
            ax_eq.axis('off')  # Hide axes
            
            # Get the equations for each segment
            segment_equations = model.get_equations()
            
            # Format the segment equations
            y_position = 0.85
            
            for i, eq in enumerate(segment_equations):
                # Extract the range and formula parts
                range_part, formula_part = eq.split(": ", 1)
                
                # Format range part
                plt.figtext(0.1, y_position, range_part + ":", fontsize=12, weight='bold')
                y_position -= 0.04
                
                # Format formula with LaTeX
                formula = formula_part.replace("y = ", "")
                formula = formula.replace("log(x)", "\\ln(x)")
                plt.figtext(0.5, y_position, f"$y = {formula}$", fontsize=13, ha='center')
                y_position -= 0.06
            
            pdf.savefig(fig_equation)
            plt.close(fig_equation)
            
            # Plot 4: Universal Function (on its own page)
            try:
                if hasattr(model, 'get_universal_function'):
                    # Create a new figure for the universal function
                    fig_universal = plt.figure(figsize=(8.5, 6))
                    fig_universal.suptitle("Universal Mathematical Model", fontsize=16, y=0.98)
                    
                    # Create an axis for the universal equation - no need for actual plotting here
                    ax_univ = fig_universal.add_subplot(111)
                    ax_univ.axis('off')  # Hide axes
                    
                    # Get the universal function
                    universal_func = model.get_universal_function()
                    
                    # Clean up the universal function for nice display
                    # Replace log(x) with ln(x) for LaTeX
                    universal_func = universal_func.replace("log(x)", "\\ln(x)")
                    
                    # Replace np.heaviside with H for better readability
                    universal_func = universal_func.replace("np.heaviside(", "H(")
                    universal_func = universal_func.replace("Heaviside(", "H(")
                    universal_func = universal_func.replace(", 1)", ")")
                    universal_func = universal_func.replace(", 1.0)", ")")
                    
                    # Replace * with · for better readability
                    universal_func = universal_func.replace("*", "\\cdot ")
                    
                    # Format numeric coefficients
                    def replace_coeffs(match):
                        num = float(match.group(1))
                        if num == int(num):
                            return str(int(num))
                        return f"{num:.4f}".rstrip('0').rstrip('.')
                    
                    universal_func = re.sub(r'(\d+\.\d+)', replace_coeffs, universal_func)
                    
                    # Display the universal function title
                    plt.figtext(0.5, 0.85, "Complete Universal Function:", 
                              fontsize=14, ha='center', weight='bold')
                    
                    # Break equation into multiple lines for better readability
                    # Break at logical points like + and -
                    max_line_length = 50  # characters per line
                    
                    # Find potential break points (after +, -)
                    break_points = []
                    for i in range(1, len(universal_func)):
                        if universal_func[i-1] in ['+', '-'] and universal_func[i-2] != '(':
                            break_points.append(i-1)
                    
                    # If we have a long equation, break it into lines
                    if len(universal_func) > max_line_length and break_points:
                        lines = []
                        start_idx = 0
                        
                        current_length = 0
                        for bp in break_points:
                            if current_length + (bp - start_idx) > max_line_length:
                                lines.append(universal_func[start_idx:bp])
                                start_idx = bp
                                current_length = 0
                            current_length += bp - start_idx
                        
                        # Add the last part
                        lines.append(universal_func[start_idx:])
                        
                        # If we couldn't break it properly, try a different approach
                        if len(lines) <= 1 and len(universal_func) > max_line_length:
                            lines = []
                            remaining = universal_func
                            while len(remaining) > max_line_length:
                                # Try to find a good breaking point
                                split_point = -1
                                for op in ['+', '-']:
                                    possible_point = remaining[:max_line_length].rfind(op)
                                    if possible_point > max_line_length // 2:  # Only split if we've covered enough text
                                        split_point = possible_point
                                        break
                                
                                # If no good split found, just split at max length
                                if split_point <= max_line_length // 2:
                                    split_point = max_line_length
                                
                                lines.append(remaining[:split_point+1])  # Keep the operator at the end
                                remaining = remaining[split_point+1:]
                            
                            # Add whatever is left
                            if remaining:
                                lines.append(remaining)
                        
                        # Display each line with proper formatting
                        y_position = 0.75
                        for i, line in enumerate(lines):
                            if i == 0:
                                # First line includes "y = "
                                plt.figtext(0.5, y_position, f"$y = {line}$", 
                                          fontsize=12, ha='center')
                            else:
                                # Continuation lines are indented visually
                                plt.figtext(0.5, y_position, f"$\\quad {line}$", 
                                          fontsize=12, ha='center')
                            y_position -= 0.05
                    else:
                        # Equation fits on one line
                        plt.figtext(0.5, 0.75, f"$y = {universal_func}$", 
                                  fontsize=13, ha='center')
                    
                    # Add explanation about model components
                    y_position = min(y_position, 0.5)  # Ensure we're below the equation
                    explanation_text = (
                        "This universal function combines all segments of the piecewise model into a "
                        "single mathematical equation using Heaviside step functions (H). "
                        "The Heaviside function acts as a switch to activate different parts of "
                        "the equation based on the input distance value."
                    )
                    plt.figtext(0.5, y_position, explanation_text, 
                              fontsize=10, ha='center', va='center', 
                              wrap=True, bbox=dict(facecolor='#f9f9f9', alpha=0.2))
                    
                    pdf.savefig(fig_universal)
                    plt.close(fig_universal)
            except Exception as e:
                # Create a page showing the error
                fig_error = plt.figure(figsize=(8.5, 3))
                fig_error.suptitle("Universal Function Error", fontsize=14, y=0.9)
                plt.figtext(0.5, 0.5, f"Unable to display universal function: {str(e)}", 
                          fontsize=12, ha='center', va='center', color='red')
                pdf.savefig(fig_error)
                plt.close(fig_error)
            
            # Add a legend page explaining mathematical notation
            fig_legend = plt.figure(figsize=(8.5, 2))
            fig_legend.suptitle("Mathematical Notation Guide", fontsize=14, y=0.9)
            
            notation_text = (
                "$\\ln(x)$ : Natural logarithm of x\n"
                "$\\cdot$ : Multiplication\n"
                "$H(x)$ : Heaviside step function (0 when x<0, 1 when x≥0)"
            )
            
            plt.figtext(0.5, 0.5, notation_text, fontsize=12, ha='center', va='center')
            
            pdf.savefig(fig_legend)
            plt.close(fig_legend)
        
        # Show success message
        self.statusBar.showMessage(f"Report saved to {file_path}", 5000)

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
        if not event.inaxes:
            return
            
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        xdata, ydata = event.xdata, event.ydata
        
        base_scale = 1.1
        scale_factor = 1 / base_scale if event.button == 'up' else base_scale
        
        new_xlim = [
            xdata - (xdata - cur_xlim[0]) * scale_factor,
            xdata + (cur_xlim[1] - xdata) * scale_factor
        ]
        new_ylim = [
            ydata - (ydata - cur_ylim[0]) * scale_factor,
            ydata + (cur_ylim[1] - ydata) * scale_factor
        ]
        
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.canvas.draw_idle()

def main():
    app = QApplication(sys.argv)
    window = MathPlotterApp()
    window.show()
    sys.exit(app.exec())