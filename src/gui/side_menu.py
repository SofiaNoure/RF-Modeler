from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QPushButton, QLabel, QLineEdit, QMenu, QWidgetAction,
                             QStackedWidget, QTextEdit, QFileDialog, QProgressBar,
                             QSplitter, QScrollArea, QFrame, QDialog, QSpinBox)
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QKeySequence, QShortcut, QImage, QPixmap
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io

from ..core.regression_model import PiecewiseLogarithmicRegression
from ..utils.data_loader import load_data_from_file
from .styles import Styles

class ImageUploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1f2d;
            }
            QLabel {
                color: #e1e5ee;
                font-size: 13px;
            }
            QSpinBox {
                background-color: #242938;
                color: #e1e5ee;
                font-size: 13px;
                padding: 6px;
                border: 1px solid #3a4255;
                border-radius: 4px;
            }
            QSpinBox:focus {
                border: 1px solid #3b82f6;
            }
            QFrame {
                background-color: #242938;
                border-radius: 8px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Image preview section
        preview_group = QFrame()
        preview_group.setFrameStyle(QFrame.Panel | QFrame.Raised)
        preview_layout = QVBoxLayout(preview_group)
        
        preview_label = QLabel("Image Preview")
        preview_label.setStyleSheet("font-weight: 500; font-size: 13px; color: #e1e5ee;")
        preview_layout.addWidget(preview_label)
        
        self.image_label = QLabel()
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px dashed #3a4255; background-color: #1a1f2d;")
        preview_layout.addWidget(self.image_label)
        
        main_layout.addWidget(preview_group)
        
        # Settings section
        settings_group = QFrame()
        settings_group.setFrameStyle(QFrame.Panel | QFrame.Raised)
        settings_layout = QVBoxLayout(settings_group)
        
        settings_label = QLabel("Image Settings")
        settings_label.setStyleSheet("font-weight: 500; font-size: 13px; color: #e1e5ee;")
        settings_layout.addWidget(settings_label)
        
        # Size controls
        size_layout = QGridLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 2000)
        self.width_spin.setValue(400)
        self.width_spin.setSuffix(" px")
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 2000)
        self.height_spin.setValue(300)
        self.height_spin.setSuffix(" px")
        
        size_layout.addWidget(QLabel("Width:"), 0, 0)
        size_layout.addWidget(self.width_spin, 0, 1)
        size_layout.addWidget(QLabel("Height:"), 1, 0)
        size_layout.addWidget(self.height_spin, 1, 1)
        
        settings_layout.addLayout(size_layout)
        main_layout.addWidget(settings_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.resize_btn = QPushButton("Resize")
        self.resize_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        
        self.crop_btn = QPushButton("Crop")
        self.crop_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        
        self.ok_btn = QPushButton("Apply")
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-weight: 500;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #242938;
                color: #e1e5ee;
                font-weight: 500;
                padding: 8px 16px;
                border: 1px solid #3a4255;
                border-radius: 6px;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2d3446;
                border-color: #3b82f6;
            }
            QPushButton:pressed {
                background-color: #1a1f2d;
            }
        """)
        
        button_layout.addWidget(self.resize_btn)
        button_layout.addWidget(self.crop_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # Connect signals
        self.resize_btn.clicked.connect(self.resize_image)
        self.crop_btn.clicked.connect(self.crop_image)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.pil_image = None
        self.processed_image = None
        self._original_size = None

    def set_image(self, image_path):
        self.pil_image = Image.open(image_path)
        self.processed_image = self.pil_image.copy()
        self._original_size = self.processed_image.size
        
        # Set initial spinbox values to match image size
        self.width_spin.setValue(self._original_size[0])
        self.height_spin.setValue(self._original_size[1])
        
        self.update_preview()

    def update_preview(self):
        if self.processed_image:
            # Convert PIL image to QPixmap for display
            img_data = io.BytesIO()
            self.processed_image.save(img_data, format='PNG')
            pixmap = QPixmap()
            pixmap.loadFromData(img_data.getvalue())
            
            # Scale pixmap to fit label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            
            # Update dimension labels
            current_size = self.processed_image.size
            if current_size != self._original_size:
                size_text = f"Current: {current_size[0]}x{current_size[1]} px"
                if hasattr(self, 'size_info_label'):
                    self.size_info_label.setText(size_text)

    def resize_image(self):
        if self.processed_image:
            width = self.width_spin.value()
            height = self.height_spin.value()
            self.processed_image = self.processed_image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )
            self.update_preview()

    def crop_image(self):
        if self.processed_image:
            width = self.width_spin.value()
            height = self.height_spin.value()
            
            # Calculate center crop
            img_width, img_height = self.processed_image.size
            left = (img_width - width) // 2
            top = (img_height - height) // 2
            right = left + width
            bottom = top + height
            
            self.processed_image = self.processed_image.crop((left, top, right, bottom))
            self.update_preview()

class FunctionsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(2)  # Reduced spacing
        self.layout.setContentsMargins(4, 2, 4, 2)  # Reduced margins

        # Create scrollable area for function categories
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        
        # Container for all categories
        container = QWidget()
        self.category_layout = QVBoxLayout(container)
        self.category_layout.setSpacing(2)  # Reduced spacing
        self.category_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(container)
        
        self.layout.addWidget(scroll)
        self._create_function_menu()

    def _create_function_menu(self):
        function_categories = {
            "Basic": [
                {"display": "x", "code": "x"},
                {"display": "x²", "code": "x^2"},
                {"display": "x³", "code": "x^3"},
                {"display": "√x", "code": "sqrt(x)"},
                {"display": "1/x", "code": "1/x"},
                {"display": "|x|", "code": "abs(x)"},
                {"display": "ceil(x)", "code": "ceil(x)"},
                {"display": "floor(x)", "code": "floor(x)"},
                {"display": "round(x)", "code": "round(x)"}
            ],
            "Trigonometric": [
                {"display": "sin(x)", "code": "sin(x)"},
                {"display": "cos(x)", "code": "cos(x)"},
                {"display": "tan(x)", "code": "tan(x)"},
                {"display": "arcsin(x)", "code": "arcsin(x)"},
                {"display": "arccos(x)", "code": "arccos(x)"},
                {"display": "arctan(x)", "code": "arctan(x)"},
                {"display": "sinh(x)", "code": "sinh(x)"},
                {"display": "cosh(x)", "code": "cosh(x)"},
                {"display": "tanh(x)", "code": "tanh(x)"}
            ],
            "Exponential & Logarithmic": [
                {"display": "eˣ", "code": "exp(x)"},
                {"display": "ln(x)", "code": "log(x)"},
                {"display": "log₁₀(x)", "code": "log10(x)"},
                {"display": "log₂(x)", "code": "log2(x)"},
                {"display": "2ˣ", "code": "2^x"},
                {"display": "10ˣ", "code": "10^x"}
            ],
            "Statistical": [
                {"display": "erf(x)", "code": "erf(x)"},
                {"display": "Γ(x)", "code": "gamma(x)"},
                {"display": "β(x)", "code": "beta(x)"},
                {"display": "sinc(x)", "code": "sinc(x)"}
            ],
            "Constants & Operations": [
                {"display": "π", "code": "pi"},
                {"display": "e", "code": "e"},
                {"display": "x + y", "code": " + "},
                {"display": "x - y", "code": " - "},
                {"display": "x × y", "code": " * "},
                {"display": "x ÷ y", "code": " / "},
                {"display": "x mod y", "code": " % "},
                {"display": "x^y", "code": "^"}
            ]
        }

        # Store category widgets for managing collapse state
        self.category_widgets = {}
        self.current_expanded = None

        for category, functions in function_categories.items():
            # Create category container
            category_container = QWidget()
            category_layout = QVBoxLayout(category_container)
            category_layout.setSpacing(2)
            category_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create category header with toggle button
            header = QPushButton(category)
            header.setCheckable(True)
            header.setChecked(False)  # Start collapsed
            header.setStyleSheet(Styles.BUTTON_CATEGORY)
            category_layout.addWidget(header)
            
            # Create content container
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(2)
            content_layout.setContentsMargins(0, 2, 0, 0)
            
            # Create rows with 3 functions each
            for i in range(0, len(functions), 3):
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(2, 2, 2, 2)
                row_layout.setSpacing(2)
                
                for j in range(3):
                    if i + j < len(functions):
                        func = functions[i + j]
                        btn = QPushButton(func["display"])
                        btn.setFixedSize(70, 32)  # Increased button size
                        btn.setStyleSheet(Styles.BUTTON_FUNCTION)
                        btn.clicked.connect(lambda checked=False, f=func["code"]: 
                                         self.parent.insert_function(f))
                        row_layout.addWidget(btn)
                    else:
                        # Add empty space if row is not full
                        spacer = QWidget()
                        spacer.setFixedSize(70, 32)  # Match button size
                        row_layout.addWidget(spacer)
                
                content_layout.addWidget(row_widget)
            
            # Add content widget to category layout
            category_layout.addWidget(content_widget)
            content_widget.setVisible(False)  # Start collapsed
            
            # Store widgets for this category
            self.category_widgets[category] = {
                'header': header,
                'content': content_widget
            }
            
            # Connect header toggle with auto-collapse behavior
            header.clicked.connect(lambda checked, cat=category: self._handle_category_toggle(cat))
            
            # Add category container to main layout
            self.category_layout.addWidget(category_container)
            
        # Add stretch at the end to push categories to the top
        self.category_layout.addStretch()

    def _handle_category_toggle(self, category):
        """Handle category toggle with auto-collapse behavior"""
        if self.current_expanded == category:
            # Clicking the expanded category - collapse it
            self.category_widgets[category]['content'].setVisible(False)
            self.category_widgets[category]['header'].setChecked(False)
            self.current_expanded = None
        else:
            # Collapse currently expanded category if any
            if self.current_expanded:
                self.category_widgets[self.current_expanded]['content'].setVisible(False)
                self.category_widgets[self.current_expanded]['header'].setChecked(False)
            
            # Expand clicked category
            self.category_widgets[category]['content'].setVisible(True)
            self.category_widgets[category]['header'].setChecked(True)
            self.current_expanded = category

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
        self.cached_graph_view = None
        self.cached_heatmap_view = None
        self.last_active_tab = 0

        # Create input fields as instance variables
        self.max_input = QLineEdit()
        self.tolerance_input = QLineEdit()
        self.min_input = QLineEdit()

        # Create loading indicator
        self.loading_bar = QProgressBar()
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setMaximumHeight(2)
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #02070b;
            }
            QProgressBar::chunk {
                background-color: #123458;
            }
        """)
        self.loading_bar.hide()

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

    def _create_tab_buttons(self):
        button_container = QWidget()
        button_container.setStyleSheet("background-color: #1a1f2d; border: none; margin: 0px; padding: 5px; border-radius: 6px;")
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
        auto_layout.setSpacing(8)  # Reduced spacing
        auto_layout.setContentsMargins(10, 10, 10, 10)

        upload_container = QWidget()
        upload_layout = QHBoxLayout(upload_container)
        upload_layout.setContentsMargins(0, 0, 0, 5)

        self.upload_btn = QPushButton("Upload File")
        self.upload_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        upload_layout.addWidget(self.upload_btn)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet(Styles.LABEL)
        upload_layout.addWidget(self.file_label)
        upload_layout.addStretch()
        auto_layout.addWidget(upload_container)

        # Parameter inputs with consistent styling
        parameters = [
            ("MAX - Breaking points:", "Default Value : 5", self.max_input),
            ("Tolerance:", "Default Value : 1.00", self.tolerance_input),
            ("Min - Segment Length:", "Default Value : 3", self.min_input)
        ]

        for label_text, placeholder, input_field in parameters:
            param_container = QWidget()
            param_layout = QVBoxLayout(param_container)
            param_layout.setSpacing(4)  # Reduced spacing
            param_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(label_text)
            label.setStyleSheet(Styles.LABEL)
            
            input_field.setPlaceholderText(placeholder)
            input_field.setStyleSheet(Styles.INPUT_FIELD)
            input_field.setFixedHeight(32)
            
            param_layout.addWidget(label)
            param_layout.addWidget(input_field)
            auto_layout.addWidget(param_container)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 5, 0, 0)

        self.view_toggle_btn = QPushButton("Graph View")
        self.view_toggle_btn.setCheckable(True)
        self.view_toggle_btn.setStyleSheet(Styles.BUTTON_TOGGLE)
        self.view_toggle_btn.setToolTip("Toggle between Graph and Heatmap views (Ctrl+T)")
        button_layout.addWidget(self.view_toggle_btn)

        self.view_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.view_shortcut.activated.connect(self.toggle_view)
        
        button_layout.addWidget(self.loading_bar)
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
        manual_layout.setSpacing(8)
        manual_layout.setContentsMargins(10, 10, 10, 10)
        
        # Top part - Function input
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(6)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.function_label = QLabel("Enter function:")
        self.function_label.setStyleSheet(Styles.LABEL)
        input_layout.addWidget(self.function_label)
        
        self.function_input = QTextEdit()
        self.function_input.setPlaceholderText("e.g., sin(x) or x^2")
        self.function_input.setMinimumWidth(250)
        self.function_input.setMaximumHeight(60)
        self.function_input.setStyleSheet(Styles.INPUT_FIELD)
        input_layout.addWidget(self.function_input)
        
        # Add buttons row
        button_row = QHBoxLayout()
        
        # Add image upload button
        self.upload_image_btn = QPushButton("Upload Background")
        self.upload_image_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.upload_image_btn.clicked.connect(self._upload_background_image)
        button_row.addWidget(self.upload_image_btn)
        
        # Add apply button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        button_row.addWidget(self.apply_btn)
        
        input_layout.addLayout(button_row)
        manual_layout.addWidget(input_container)
        
        # Bottom part - Functions panel
        self.functions_panel = FunctionsPanel(self)
        self.functions_panel.setMinimumHeight(250)
        manual_layout.addWidget(self.functions_panel)
        
        manual_layout.addStretch()
        self.stack.addWidget(manual_menu)
        
        # Initialize background image storage
        self.background_image = None

    def _setup_other_menu(self):
        other_menu = QWidget()
        other_layout = QVBoxLayout(other_menu)
        other_layout.setSpacing(10)
        other_layout.setContentsMargins(10, 10, 10, 10)

        # Add input section for x value
        input_label = QLabel("Enter distance (x) value:")
        input_label.setStyleSheet(Styles.LABEL)
        other_layout.addWidget(input_label)

        self.prediction_input = QTextEdit()
        self.prediction_input.setPlaceholderText("Enter a distance value to predict path loss")
        self.prediction_input.setMaximumHeight(60)
        self.prediction_input.setStyleSheet(Styles.INPUT_FIELD)
        other_layout.addWidget(self.prediction_input)

        # Add prediction result label
        self.prediction_result = QLabel("Prediction will appear here")
        self.prediction_result.setStyleSheet(Styles.LABEL)
        self.prediction_result.setWordWrap(True)
        other_layout.addWidget(self.prediction_result)

        # Add predict button
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 5, 0, 0)

        self.predict_btn = QPushButton("Predict Path Loss")
        self.predict_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.predict_btn.clicked.connect(self._predict_path_loss)
        button_layout.addStretch()
        button_layout.addWidget(self.predict_btn)

        other_layout.addWidget(button_container)
        other_layout.addStretch()

        self.stack.addWidget(other_menu)

    def _connect_signals(self):
        self.auto_btn.clicked.connect(lambda: self.show_menu(0))
        self.manual_btn.clicked.connect(lambda: self.show_menu(1))
        self.other_btn.clicked.connect(lambda: self.show_menu(2))
        self.upload_btn.clicked.connect(self.upload_csv)
        self.view_toggle_btn.clicked.connect(self.toggle_view)
        self.apply_btn.clicked.connect(self.plot_function)
        self.auto_apply_btn.clicked.connect(self.auto_plot_function)

    def _cache_current_view(self):
        """Cache the current plot state"""
        if hasattr(self.parent, 'ax') and self.parent.ax is not None:
            self._cached_state = {
                'is_heatmap': self.is_heatmap,
                'xlim': self.parent.ax.get_xlim(),
                'ylim': self.parent.ax.get_ylim()
            }

    def _apply_cached_view(self, cached_data=None):
        """Apply cached view state or redraw plot"""
        if hasattr(self, '_cached_state'):
            self.is_heatmap = self._cached_state['is_heatmap']
            self.view_toggle_btn.setText("Heatmap View" if self.is_heatmap else "Graph View")
            self.view_toggle_btn.setChecked(self.is_heatmap)
            self.auto_plot_function()
            if hasattr(self.parent, 'ax') and self.parent.ax is not None:
                self.parent.ax.set_xlim(self._cached_state['xlim'])
                self.parent.ax.set_ylim(self._cached_state['ylim'])
                self.parent.canvas.draw()
        else:
            self.auto_plot_function()

    def insert_function(self, function_text):
        """Insert function text at current cursor position safely"""
        try:
            current_text = self.function_input.toPlainText()
            cursor = self.function_input.textCursor()
            current_position = cursor.position()
            
            # Ensure position is within bounds
            current_position = min(current_position, len(current_text))
            
            operators = [" + ", " - ", " * ", " / "]
            is_operator = function_text in operators
            
            if is_operator:
                new_text = current_text[:current_position] + function_text + current_text[current_position:]
                new_position = current_position + len(function_text)
            else:
                if current_position > 0 and current_text[current_position-1:current_position].isalnum():
                    new_text = current_text[:current_position] + " * " + function_text + current_text[current_position:]
                    new_position = current_position + len(" * " + function_text)
                else:
                    new_text = current_text[:current_position] + function_text + current_text[current_position:]
                    new_position = current_position + len(function_text)
            
            # Set text first
            self.function_input.setText(new_text)
            
            # Then safely set cursor position
            cursor = self.function_input.textCursor()
            new_position = min(new_position, len(new_text))
            cursor.setPosition(new_position)
            self.function_input.setTextCursor(cursor)
            
        except Exception as e:
            print(f"Error inserting function: {str(e)}")
        
        return False  # Prevent menu from staying open

    def _upload_background_image(self):
        """Handle background image upload and processing"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Upload Background Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            # Show image settings dialog
            dialog = ImageUploadDialog(self)
            dialog.set_image(file_path)
            
            if dialog.exec() == QDialog.Accepted and dialog.processed_image:
                # Convert PIL image to numpy array
                img_array = np.array(dialog.processed_image)
                
                # Update the plot with the background image
                self.parent.figure.clear()
                self.parent.ax = self.parent.figure.add_subplot(111)
                
                # Place image at (0,0) with extent matching image dimensions
                height, width = img_array.shape[:2]
                self.parent.ax.imshow(img_array, extent=[0, width, 0, height], 
                                    aspect='auto', alpha=0.3)
                
                # Store the image dimensions for future reference
                self.background_image = {
                    'image': img_array,
                    'extent': [0, width, 0, height]
                }
                
                # If there's a current function, plot it over the image
                if self.function_input.toPlainText().strip():
                    self.plot_function()
                else:
                    self.parent.ax.grid(True)
                    self.parent.ax.set_xlabel('x')
                    self.parent.ax.set_ylabel('y')
                    self.parent.ax.set_title('Function Plot with Background')
                    self.parent.canvas.draw()

    def plot_function(self):
        # Store current axis limits if they exist
        if hasattr(self.parent, 'ax') and self.parent.ax is not None:
            current_xlim = self.parent.ax.get_xlim()
            current_ylim = self.parent.ax.get_ylim()
            has_previous_view = True
        else:
            has_previous_view = False

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
            
            # Clear any existing colorbars before plotting
            for im in self.parent.ax.images:
                if hasattr(im, 'colorbar'):
                    im.colorbar.remove()
            
            # Evaluate with appropriate range for display
            x, y = self.parent.function_plotter.evaluate_function(function_str)
            
            # Clear previous plot while preserving background image if it exists
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            
            # If there's a background image, display it first
            if hasattr(self, 'background_image') and self.background_image:
                self.parent.ax.imshow(
                    self.background_image['image'],
                    extent=self.background_image['extent'],
                    aspect='auto',
                    alpha=0.3,
                    zorder=0  # Ensure image is behind the plot
                )
            
            # Plot the function with higher zorder to appear above the background
            self.parent.ax.plot(x, y, 'b-', linewidth=2, zorder=2)
            
            # Enhanced grid with proper z-order
            self.parent.ax.grid(True, which='major', linestyle='-', alpha=0.5, zorder=1)
            self.parent.ax.grid(True, which='minor', linestyle=':', alpha=0.2, zorder=1)
            self.parent.ax.minorticks_on()
            
            # Axes
            self.parent.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3, zorder=1)
            self.parent.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3, zorder=1)
            
            # Labels
            self.parent.ax.set_xlabel('x')
            self.parent.ax.set_ylabel('y')
            self.parent.ax.set_title(f'Plot of {function_str}')
            
            # Restore previous view limits if they existed, otherwise set default
            if has_previous_view:
                self.parent.ax.set_xlim(current_xlim)
                self.parent.ax.set_ylim(current_ylim)
            else:
                # Set default view limits to a more focused range
                default_x_range = (-5, 5)
                visible_range = x[(x >= default_x_range[0]) & (x <= default_x_range[1])]
                if len(visible_range) > 0:
                    self.parent.ax.set_xlim(default_x_range)
                    visible_y = y[(x >= default_x_range[0]) & (x <= default_x_range[1])]
                    if len(visible_y) > 0:
                        y_min, y_max = np.min(visible_y), np.max(visible_y)
                        if abs(y_max - y_min) < 1:  # Very small range
                            mid = (y_max + y_min) / 2
                            self.parent.ax.set_ylim(mid - 2, mid + 2)
                        else:
                            padding = (y_max - y_min) * 0.2
                            self.parent.ax.set_ylim(y_min - padding, y_max + padding)
                    else:
                        self.parent.ax.set_ylim(-5, 5)
                else:
                    self.parent.ax.set_xlim(-5, 5)
                    self.parent.ax.set_ylim(-5, 5)
            
            self.parent.canvas.draw()
            
        except Exception as e:
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:97] + "..."
            self.parent.ax.text(0.5, 0.5, f"Error: {error_msg}", 
                        ha='center', va='center', transform=self.parent.ax.transAxes, color='red')
            self.parent.ax.set_title("Function Plot Error")
            self.parent.canvas.draw()
            self.parent.statusBar.showMessage(f"Error plotting function: {str(e)}", 5000)

    def toggle_view(self):
        if not self.csv_data:
            return

        # Store current view state before switching
        self._cache_current_view()
        
        self.is_heatmap = not self.is_heatmap
        self.view_toggle_btn.setText("Heatmap View" if self.is_heatmap else "Graph View")
        self.view_toggle_btn.setChecked(self.is_heatmap)
        
        # Show loading indicator
        self.loading_bar.show()
        self.loading_bar.setRange(0, 0)  # Indeterminate mode
        self.view_toggle_btn.setEnabled(False)
        
        # Use timer to allow UI to update
        QTimer.singleShot(50, self._delayed_view_update)

    def _delayed_view_update(self):
        try:
            self.auto_plot_function()
        finally:
            # Hide loading indicator
            self.loading_bar.hide()
            self.loading_bar.setRange(0, 100)
            self.view_toggle_btn.setEnabled(True)

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
                
                # Automatically plot the graph if we're in the Auto tab
                if self.stack.currentIndex() == 0:  # Auto tab
                    self.auto_plot_function()
                    
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
            
        # Clear any existing colorbars before creating new plot
        self.parent.figure.clear()
        self.parent.ax = self.parent.figure.add_subplot(111)
        
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
        
        # Use tight_layout with a bit more padding
        self.parent.figure.tight_layout(pad=1.1)

    def _plot_regression(self, max_points, tolerance, min_length):
        if self.csv_data is None:
            self.parent.ax.text(0.5, 0.5, 
                "Please upload a CSV file first", 
                ha='center', va='center', transform=self.parent.ax.transAxes)
            self.parent.ax.set_title("No Data")
            return
            
        x, y = self.csv_data
        
        # Create progress text on plot
        self.parent.ax.text(0.5, 0.5, "Fitting model...", 
                          ha='center', va='center', transform=self.parent.ax.transAxes)
        self.parent.canvas.draw()
        
        model = PiecewiseLogarithmicRegression(
            max_breakpoints=max_points,
            min_segment_length=min_length,
            tolerance=tolerance,
            verbose=True
        )
        model.fit(x, y)
        self.current_model = model

        # Clear the figure for the enhanced plot
        self.parent.figure.clear()
        self.parent.ax = self.parent.figure.add_subplot(111)

        # Plot original data points
        self.parent.ax.scatter(x, y, s=30, alpha=0.5, color='blue')

        # Generate fine-grained x values for smooth curve plotting
        x_fine = np.logspace(np.log10(x.min()), np.log10(x.max()), 1000)
        y_pred_fine = model.predict(x_fine)

        # Plot segments with confidence intervals
        num_segments = len(model.breakpoints_) - 1
        colors = plt.cm.viridis(np.linspace(0, 0.8, num_segments))

        for i in range(num_segments):
            mask = (x_fine >= model.breakpoints_[i]) & (x_fine <= model.breakpoints_[i + 1])
            if i < len(model.models_) and model.models_[i] is not None:
                # Plot fitted line for this segment
                self.parent.ax.semilogx(x_fine[mask], y_pred_fine[mask], '-', 
                                      linewidth=2, color=colors[i])
                
                # Get confidence intervals for this segment only
                x_segment = x_fine[mask]
                y_segment = y_pred_fine[mask]
                if len(x_segment) > 0:
                    segment_intervals = model.get_confidence_intervals(x_segment)
                    for interval_mask, interval in segment_intervals:
                        # Ensure interval array matches segment size
                        if len(interval) == len(x_segment):
                            self.parent.ax.fill_between(
                                x_segment,
                                y_segment - interval,
                                y_segment + interval,
                                color=colors[i], alpha=0.2
                            )

        # Add breakpoint indicators
        for i, bp in enumerate(model.breakpoints_[1:-1], 1):
            self.parent.ax.axvline(bp, color='k', linestyle='--', alpha=0.5, linewidth=1)
            # Add breakpoint value annotation
            y_pos = np.interp(bp, x_fine, y_pred_fine)
            self.parent.ax.annotate(f'BP{i}\n({bp:.1f})', 
                                  (bp, y_pos),
                                  xytext=(5, 5), textcoords='offset points',
                                  fontsize=8, bbox=dict(facecolor='white', alpha=0.7))

        # Enhance the plot appearance
        self.parent.ax.set_xlabel('Distance (log scale)')
        self.parent.ax.set_ylabel('Path Loss (dB)')
        self.parent.ax.grid(True, which='both', alpha=0.2)
        self.parent.ax.grid(True, which='major', alpha=0.5)
        
        # Create title with stats
        title = 'Piecewise Logarithmic Regression'
        stats = f'R² = {model.r2_:.4f} | MSE = {model.mse_:.4f} | Segments = {num_segments}'
        self.parent.ax.set_title(f'{title}\n{stats}', pad=10)

        # Adjust layout
        self.parent.figure.tight_layout()
        
        # Update canvas
        self.parent.canvas.draw()

    def show_menu(self, index):
        previous_tab = self.last_active_tab
        self.last_active_tab = index
        
        self.auto_btn.setChecked(False)
        self.manual_btn.setChecked(False)
        self.other_btn.setChecked(False)
        
        # Cache view state when switching FROM Auto or Other tab
        if previous_tab in [0, 2] and index == 1:  # Switching to Manual
            # Store current view state
            self._cache_current_view()
            
            # Reset to graph view in UI only
            self.is_heatmap = False
            self.view_toggle_btn.setText("Graph View")
            self.view_toggle_btn.setChecked(False)
            
            self.parent.init_plot()
            self.plot_function()
        elif previous_tab == 1 and index in [0, 2]:  # Switching FROM Manual TO Auto/Other
            # Restore previous Auto/Other tab view
            self._apply_cached_view()
        elif previous_tab in [0, 2] and index in [0, 2]:  # Switching between Auto and Other
            # Keep current view state, no need to reset
            pass
        
        # Update the active tab button
        if index == 0:
            self.auto_btn.setChecked(True)
        elif index == 1:
            self.manual_btn.setChecked(True)
        else:
            self.other_btn.setChecked(True)
            
        self.stack.setCurrentIndex(index)

        # Update prediction display if switching to Other tab with a fitted model
        if index == 2 and self.current_model is not None:
            self.prediction_result.setText("Enter a distance value above to predict path loss using the current model.")
            # Update the plot if a prediction point exists
            if hasattr(self.parent, 'ax'):
                self.parent.canvas.draw()

    def _predict_path_loss(self):
        try:
            # Check if we have a model
            if self.current_model is None:
                self.prediction_result.setText("Error: Please upload a CSV file and fit a model first by using the Auto panel.")
                return
            
            # Get the distance value from input
            distance_str = self.prediction_input.toPlainText().strip()
            if not distance_str:
                self.prediction_result.setText("Error: Please enter a distance value to predict path loss.")
                return
                
            try:
                distance = float(distance_str)
                if distance <= 0:
                    self.prediction_result.setText("Error: Distance must be greater than 0 for path loss prediction.")
                    return
            except ValueError:
                self.prediction_result.setText("Error: Please enter a valid numeric value for distance.")
                return
                
            # Check if distance is within the model's range
            model_range = (min(self.csv_data[0]), max(self.csv_data[0]))
            is_in_range = model_range[0] <= distance <= model_range[1]
            
            # Make prediction
            prediction = self.current_model.predict([distance])[0]
            
            # Get confidence intervals
            intervals = None
            try:
                if is_in_range:  # Only calculate confidence intervals for in-range predictions
                    interval_results = self.current_model.get_confidence_intervals([distance])
                    if interval_results and len(interval_results) > 0:
                        for mask, interval in interval_results:
                            if mask[0]:  # If this interval applies to our point
                                intervals = interval
                                break
            except Exception as e:
                print(f"Warning: Could not calculate confidence intervals: {str(e)}")
            
            # Update plot to show prediction point
            if hasattr(self.parent, 'ax'):
                # Remove previous prediction points and annotations
                for artist in self.parent.ax.get_children():
                    if (isinstance(artist, plt.Line2D) and getattr(artist, 'is_prediction', False)) or \
                       (isinstance(artist, plt.Text) and getattr(artist, 'is_prediction_label', False)):
                        artist.remove()
                
                if is_in_range:
                    # Plot new prediction point
                    prediction_point = self.parent.ax.scatter([distance], [prediction], 
                                                            color='red', s=100, zorder=5,
                                                            marker='*', label='Prediction')
                    prediction_point.is_prediction = True
                    
                    # Add annotation
                    annotation = self.parent.ax.annotate(
                        f'({distance:.1f}, {prediction:.1f})',
                        (distance, prediction),
                        xytext=(10, 10),
                        textcoords='offset points',
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='red'),
                        color='red',
                        zorder=5
                    )
                    annotation.is_prediction_label = True
                
                # Update canvas
                self.parent.canvas.draw()
            
            # Format the prediction result text
            if not is_in_range:
                self.prediction_result.setText(
                    f"⚠️ Warning: Distance {distance:.2f} is outside the model's range "
                    f"({model_range[0]:.2f} to {model_range[1]:.2f}).\n\n"
                    f"Predicted path loss: {prediction:.2f} dB\n"
                    f"Note: This prediction is an extrapolation and may be less reliable."
                )
            else:
                result_text = f"Distance: {distance:.2f}\nPredicted path loss: {prediction:.2f} dB"
                if intervals is not None and len(intervals) > 0:
                    confidence = intervals[0]
                    result_text += f"\n95% Confidence interval: {prediction:.2f} ± {confidence:.2f} dB"
                self.prediction_result.setText(result_text)
            
        except Exception as e:
            self.prediction_result.setText(f"Error: An unexpected error occurred.\n{str(e)}")