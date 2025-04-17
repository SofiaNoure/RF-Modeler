from PySide6.QtWidgets import QToolButton
from PySide6.QtCore import QSize
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

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