class Styles:
    MAIN_WINDOW = """
        * {
            font-family: 'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        }
        QMainWindow {
            background-color: #1a1f2d;
        }
        QMenuBar {
            background-color: #242938;
            color: #e1e5ee;
            border: none;
            font-size: 12px;
        }
        QMenuBar::item {
            background-color: #242938;
            color: #e1e5ee;
            padding: 4px 8px;
        }
        QMenuBar::item:selected {
            background-color: #2d3446;
        }
        QMenuBar::item:pressed {
            background-color: #3a4255;
        }
        QMenu {
            background-color: #242938;
            color: #e1e5ee;
            border: 1px solid #3a4255;
            padding: 4px;
            border-radius: 4px;
        }
        QMenu::item {
            background-color: transparent;
            padding: 4px 16px;
        }
        QMenu::item:selected {
            background-color: #2d3446;
        }
        QMenu::separator {
            height: 1px;
            background-color: #3a4255;
            margin: 4px 0px;
        }
    """

    SIDE_MENU = """
        QWidget {
            background-color: #242938;
            border: none;
            padding: 10px;
        }
    """

    BUTTON_PRIMARY = """
        QPushButton {
            background-color: #3b82f6;
            color: white;
            font-weight: 500;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #2563eb;
        }
        QPushButton:pressed {
            background-color: #1d4ed8;
        }
    """

    BUTTON_TAB = """
        QPushButton {
            padding: 10px 20px;
            background-color: #2d3446;
            color: #e1e5ee;
            border: none;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
            font-size: 13px;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #3a4255;
        }
        QPushButton:pressed {
            background-color: #242938;
        }
        QPushButton:checked {
            background-color: #242938;
            border-bottom: 2px solid #3b82f6;
        }
    """

    BUTTON_TOGGLE = """
        QPushButton {
            background-color: #3b82f6;
            color: white;
            font-weight: 500;
            font-size: 13px;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #2563eb;
        }
        QPushButton:pressed {
            background-color: #1d4ed8;
        }
        QPushButton:checked {
            background-color: #242938;
            border: 2px solid #3b82f6;
            color: #3b82f6;
        }
        QPushButton:disabled {
            background-color: #374151;
            color: #9ca3af;
        }
    """

    INPUT_FIELD = """
        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
            font-size: 13px;
            font-weight: 400;
            padding: 6px 8px;
            background-color: #1a1f2d;
            color: #e1e5ee;
            border: 1px solid #3a4255;
            border-radius: 4px;
        }
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #3b82f6;
            background-color: #242938;
        }
        QLineEdit::placeholder, QTextEdit::placeholder {
            color: #9ca3af;
        }
        /* Style SpinBox arrows - might need adjustments based on OS/theme */
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 16px;
            border-left: 1px solid #3a4255;
            border-bottom: 1px solid #3a4255;
            border-top-right-radius: 4px;
            background-color: #242938;
        }
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
             background-color: #2d3446;
        }
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
            image: url(none); /* Hide default arrow if needed, replace with custom icon */
            width: 10px;
            height: 10px;
        }
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 16px;
            border-left: 1px solid #3a4255;
            border-top: 1px solid #3a4255;
            border-bottom-right-radius: 4px;
            background-color: #242938;
        }
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
             background-color: #2d3446;
        }
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
            image: url(none); /* Hide default arrow if needed, replace with custom icon */
            width: 10px;
            height: 10px;
        }
    """

    LABEL = """
        QLabel {
            color: #e1e5ee;
            font-weight: 500;
            font-size: 13px;
        }
    """

    FUNCTION_MENU = """
        QMenu {
            background-color: #1a1f2d;
            color: #e1e5ee;
            border: 1px solid #3a4255;
            padding: 4px;
        }
        QMenu::item {
            padding: 4px 8px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #242938;
        }
    """

    BUTTON_CATEGORY = """
        QPushButton {
            background-color: #242938;
            color: #e1e5ee;
            font-family: 'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            font-weight: 500;
            font-size: 13px;
            text-align: left;
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #2d3446;
        }
        QPushButton:checked {
            background-color: #3a4255;
            border-left: 3px solid #3b82f6;
        }
    """

    BUTTON_FUNCTION = """
        QPushButton {
            background-color: #1a1f2d;
            color: #e1e5ee;
            font-family: 'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            font-size: 13px;
            font-weight: 500;
            padding: 6px 10px;
            border: 1px solid #3a4255;
            border-radius: 4px;
            min-width: 65px;
        }
        QPushButton:hover {
            background-color: #242938;
            border-color: #3b82f6;
        }
        QPushButton:pressed {
            background-color: #3a4255;
        }
    """