import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QMenuBar, QMenu, QStatusBar)
from PySide6.QtCore import QTimer, QDateTime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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