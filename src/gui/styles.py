class Styles:
    MAIN_WINDOW = """
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
    """

    SIDE_MENU = """
        QWidget {
            background-color: #02070b;
            border: none;
            padding: 10px;
        }
    """

    BUTTON_PRIMARY = """
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
    """

    BUTTON_TAB = """
        QPushButton {
            padding: 8px 16px;
            background-color: #123458;
            color: white;
            border: none;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px;
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

    BUTTON_TOGGLE = """
        QPushButton {
            background-color: #123458;
            color: white;
            font-weight: bold;
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #132e49;
        }
        QPushButton:pressed {
            background-color: #02070b;
        }
        QPushButton:checked {
            background-color: #02070b;
            border: 2px solid #123458;
        }
        QPushButton:disabled {
            background-color: #1a1a1a;
            color: #808080;
        }
    """

    INPUT_FIELD = """
        QLineEdit, QTextEdit {
            font-size: 14px;
            padding: 6px;
            background-color: white;
            color: black;
            border: none;
            border-radius: 4px;
        }
    """

    LABEL = """
        QLabel {
            color: white;
            font-weight: bold;
            font-size: 14px;
        }
    """

    FUNCTION_MENU = """
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
    """