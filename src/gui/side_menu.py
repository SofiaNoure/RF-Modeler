from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QPushButton, QLabel, 
                             QStackedWidget, QTextEdit, QFileDialog, QProgressBar,
                             QScrollArea, QFrame, QDialog, QSpinBox, QCheckBox,
                             QDoubleSpinBox, QApplication)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QPixmap, QPainter, QPen, QColor
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
import os

from ..core.regression_model import PiecewiseLogarithmicRegression
from ..utils.data_loader import load_data_from_file
from .styles import Styles
from ..utils.plot_utils import generate_heatmap_data, plot_regression_segments

class SelectableImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selection_start = event.pos()
            self.selection_end = event.pos()
            self.is_selecting = True
            
    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.selection_end = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = False
            if self.selection_start and self.selection_end:
                self.update()
                
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selection_start and self.selection_end:
            painter = QPainter(self)
            pen = QPen(QColor(59, 130, 246), 2)  # Blue color matching theme
            painter.setPen(pen)
            
            x = min(self.selection_start.x(), self.selection_end.x())
            y = min(self.selection_start.y(), self.selection_end.y())
            w = abs(self.selection_end.x() - self.selection_start.x())
            h = abs(self.selection_end.y() - self.selection_start.y())
            
            # Draw semi-transparent overlay
            painter.fillRect(0, 0, self.width(), self.height(), 
                           QColor(0, 0, 0, 100))
            # Clear selection rectangle
            painter.fillRect(x, y, w, h, QColor(255, 255, 255, 0))
            # Draw selection border
            painter.drawRect(x, y, w, h)

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
        
        self.image_label = SelectableImageLabel()
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px dashed #3a4255; background-color: #1a1f2d;")
        preview_layout.addWidget(self.image_label)
        
        # Add size info label
        self.size_info_label = QLabel("")
        self.size_info_label.setStyleSheet("color: #e1e5ee; font-size: 12px;")
        self.size_info_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.size_info_label)
        
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
        
        # Add checkbox for maintaining aspect ratio
        self.maintain_aspect_ratio = QCheckBox("Maintain aspect ratio")
        self.maintain_aspect_ratio.setStyleSheet("color: #e1e5ee;")
        self.maintain_aspect_ratio.setChecked(True)
        size_layout.addWidget(self.maintain_aspect_ratio, 2, 0, 1, 2)
        
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
        self.ok_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(Styles.BUTTON_SECONDARY)
        
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
        
        # Connect spinbox signals for aspect ratio maintenance
        self.width_spin.valueChanged.connect(self._on_width_changed)
        self.height_spin.valueChanged.connect(self._on_height_changed)
        
        # Internal state tracking
        self._updating_spinbox = False  # Flag to prevent recursive updates
        self.pil_image = None
        self.processed_image = None
        self._original_size = None
        self._scale_factor = 1.0

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
            
            # Check for valid dimensions
            if width <= 0 or height <= 0:
                return
                
            try:
                if self.maintain_aspect_ratio.isChecked():
                    aspect_ratio = self._original_size[0] / self._original_size[1]
                    if width / height > aspect_ratio:
                        width = int(height * aspect_ratio)
                        self.width_spin.setValue(width)
                    else:
                        height = int(width / aspect_ratio)
                        self.height_spin.setValue(height)
                
                self.processed_image = self.processed_image.resize(
                    (width, height),
                    Image.Resampling.LANCZOS
                )
                
                # Update the image preview
                self.update_preview()
                
                # Update size info label
                self.size_info_label.setText(f"Current: {width}x{height} px")
            except Exception as e:
                print(f"Error resizing image: {e}")

    def crop_image(self):
        if not self.processed_image or not self.image_label.selection_start:
            return
            
        # Get selection coordinates in label space
        x1 = min(self.image_label.selection_start.x(), self.image_label.selection_end.x())
        y1 = min(self.image_label.selection_start.y(), self.image_label.selection_end.y())
        x2 = max(self.image_label.selection_start.x(), self.image_label.selection_end.x())
        y2 = max(self.image_label.selection_start.y(), self.image_label.selection_end.y())
        
        # Check if selection has minimum size
        if x2 - x1 < 5 or y2 - y1 < 5:
            return  # Selection too small to crop
            
        # Get the actual pixmap displayed in the label
        pixmap = self.image_label.pixmap()
        if not pixmap:
            return
        
        # Get the pixmap's position within the label (for centering)
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()
        
        # Calculate offset if image is centered in the label
        offset_x = max(0, (label_width - pixmap_width) // 2)
        offset_y = max(0, (label_height - pixmap_height) // 2)
        
        # Adjust selection coordinates to account for centering
        x1 = max(0, x1 - offset_x)
        y1 = max(0, y1 - offset_y)
        x2 = min(pixmap_width, x2 - offset_x)
        y2 = min(pixmap_height, y2 - offset_y)
        
        # If selection is outside the image area, return
        if x1 >= pixmap_width or y1 >= pixmap_height or x2 <= 0 or y2 <= 0:
            return
        
        # Convert selection coordinates to original image coordinates
        scale_x = self.processed_image.size[0] / pixmap_width
        scale_y = self.processed_image.size[1] / pixmap_height
        
        img_x1 = int(x1 * scale_x)
        img_y1 = int(y1 * scale_y)
        img_x2 = int(x2 * scale_x)
        img_y2 = int(y2 * scale_y)
        
        # Ensure coordinates are within image bounds
        img_x1 = max(0, img_x1)
        img_y1 = max(0, img_y1)
        img_x2 = min(self.processed_image.size[0], img_x2)
        img_y2 = min(self.processed_image.size[1], img_y2)
        
        # Crop the image
        try:
            self.processed_image = self.processed_image.crop((img_x1, img_y1, img_x2, img_y2))
            
            # Update spinboxes with new size
            self.width_spin.setValue(self.processed_image.size[0])
            self.height_spin.setValue(self.processed_image.size[1])
            
            # Clear selection and update preview
            self.image_label.selection_start = None
            self.image_label.selection_end = None
            self.update_preview()
            
            # Update size info label
            self.size_info_label.setText(f"Current: {self.processed_image.size[0]}x{self.processed_image.size[1]} px")
        except Exception as e:
            print(f"Error cropping image: {e}")
            # If crop fails, reset selection
            self.image_label.selection_start = None
            self.image_label.selection_end = None
            self.update_preview()

    def _on_width_changed(self, value):
        if self._updating_spinbox or not self.maintain_aspect_ratio.isChecked():
            return
        self._updating_spinbox = True
        try:
            aspect_ratio = self._original_size[0] / self._original_size[1]
            new_height = int(value / aspect_ratio)
            self.height_spin.setValue(new_height)
        finally:
            self._updating_spinbox = False

    def _on_height_changed(self, value):
        if self._updating_spinbox or not self.maintain_aspect_ratio.isChecked():
            return
        self._updating_spinbox = True
        try:
            aspect_ratio = self._original_size[0] / self._original_size[1]
            new_width = int(value * aspect_ratio)
            self.width_spin.setValue(new_width)
        finally:
            self._updating_spinbox = False

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

        # Create input fields as instance variables using specialized widgets
        self.max_input = QSpinBox()
        self.max_input.setRange(1, 100) # Set a reasonable range
        self.max_input.setValue(5) # Default value

        self.tolerance_input = QDoubleSpinBox()
        self.tolerance_input.setRange(0.01, 100.0) # Set a reasonable range
        self.tolerance_input.setSingleStep(0.1)
        self.tolerance_input.setDecimals(2)
        self.tolerance_input.setValue(1.00) # Default value

        self.min_input = QSpinBox()
        self.min_input.setRange(1, 1000) # Set a reasonable range
        self.min_input.setValue(3) # Default value

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

        # Initially disable predict button
        self.predict_btn.setEnabled(False)

    def _setup_ui(self):
        self._create_tab_buttons()
        self._create_stacked_widget()
        self._setup_auto_menu()
        self._setup_manual_menu()
        self._setup_comparison_menu()
        self._setup_other_menu()

    def _create_tab_buttons(self):
        button_container = QWidget()
        button_container.setStyleSheet("background-color: #1a1f2d; border: none; margin: 0px; padding: 5px; border-radius: 6px;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        self.auto_btn = QPushButton("Auto")
        self.manual_btn = QPushButton("Manual")
        self.comparison_btn = QPushButton("Comparison")
        self.other_btn = QPushButton("Prediction")

        # Add tooltips to tab buttons
        self.auto_btn.setToolTip("Automatic regression modeling based on uploaded CSV data.")
        self.manual_btn.setToolTip("Plot mathematical functions manually.")
        self.comparison_btn.setToolTip("Compare multiple datasets with regression models.")
        self.other_btn.setToolTip("Predict path loss using the fitted model or view other analyses.")

        for btn in (self.auto_btn, self.manual_btn, self.comparison_btn, self.other_btn):
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

        # Create view toggle button
        self.view_toggle_btn = QPushButton("Graph View")
        self.view_toggle_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.view_toggle_btn.setToolTip("Switch between graph and heatmap visualization")
        self.view_toggle_btn.setCheckable(True)

        # Parameter inputs with consistent styling
        parameters = [
            ("MAX - Breaking points:", "Max number of segments (integer)", self.max_input),
            ("Tolerance:", "Fitting tolerance (float)", self.tolerance_input),
            ("Min - Segment Length:", "Minimum data points per segment (integer)", self.min_input)
        ]

        for label_text, tooltip, input_field in parameters:
            param_container = QWidget()
            param_layout = QVBoxLayout(param_container)
            param_layout.setSpacing(4)  # Reduced spacing
            param_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(label_text)
            label.setStyleSheet(Styles.LABEL)
            
            # Apply common style and add tooltip
            input_field.setStyleSheet(Styles.INPUT_FIELD) # Use INPUT_FIELD style for spin boxes too
            input_field.setFixedHeight(32)
            input_field.setToolTip(tooltip) # Add tooltip here
            
            param_layout.addWidget(label)
            param_layout.addWidget(input_field)
            auto_layout.addWidget(param_container)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        button_layout.addWidget(self.view_toggle_btn)
        button_layout.addWidget(self.loading_bar)
        button_layout.addStretch()
        
        self.auto_apply_btn = QPushButton("Apply")
        self.auto_apply_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.auto_apply_btn.setToolTip("Fit the regression model to the uploaded data.") # Add tooltip
        button_layout.addWidget(self.auto_apply_btn)
        
        auto_layout.addWidget(button_container)

        # Add display function button at the bottom
        display_function_container = QWidget()
        display_function_layout = QHBoxLayout(display_function_container)
        display_function_layout.setContentsMargins(0, 10, 0, 0)  # Add top margin
        
        self.display_function_btn = QPushButton("Display Function")
        self.display_function_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.display_function_btn.setEnabled(False)  # Initially disabled until model is fitted
        self.display_function_btn.setToolTip("View the fitted mathematical function")  # Add tooltip
        self.display_function_btn.clicked.connect(self._show_universal_function)
        display_function_layout.addWidget(self.display_function_btn)

        auto_layout.addWidget(display_function_container)
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
        self.apply_btn.setToolTip("Plot the entered mathematical function.") # Add tooltip
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

    def _setup_comparison_menu(self):
        comparison_menu = QWidget()
        comparison_layout = QVBoxLayout(comparison_menu)
        comparison_layout.setSpacing(8)
        comparison_layout.setContentsMargins(10, 10, 10, 10)

        # List to store multiple datasets
        self.datasets = []  # Will store tuples of (filename, x, y)
        
        # Button to add new dataset
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 5)

        self.add_dataset_btn = QPushButton("Add Dataset")
        self.add_dataset_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.add_dataset_btn.clicked.connect(self._add_dataset)
        button_layout.addWidget(self.add_dataset_btn)

        # Dataset list widget to show loaded files
        self.dataset_list = QWidget()
        self.dataset_list_layout = QVBoxLayout(self.dataset_list)
        self.dataset_list_layout.setSpacing(5)
        self.dataset_list_layout.setContentsMargins(0, 0, 0, 0)
        self.dataset_list_layout.addStretch()

        # Scroll area for dataset list
        scroll = QScrollArea()
        scroll.setWidget(self.dataset_list)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1a1f2d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #3b4253;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        comparison_layout.addWidget(button_container)
        comparison_layout.addWidget(scroll)

        # Add apply button at the bottom
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 5, 0, 0)

        self.comparison_apply_btn = QPushButton("Apply")
        self.comparison_apply_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.comparison_apply_btn.clicked.connect(self._plot_comparison)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.comparison_apply_btn)

        comparison_layout.addWidget(bottom_container)
        self.stack.addWidget(comparison_menu)

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
        self.predict_btn.setToolTip("Predict path loss for a given distance using the fitted model.") # Add tooltip
        button_layout.addStretch()
        button_layout.addWidget(self.predict_btn)

        other_layout.addWidget(button_container)
        other_layout.addStretch()

        self.stack.addWidget(other_menu)

    def _connect_signals(self):
        self.auto_btn.clicked.connect(lambda: self.show_menu(0))
        self.manual_btn.clicked.connect(lambda: self.show_menu(1))
        self.comparison_btn.clicked.connect(lambda: self.show_menu(2))
        self.other_btn.clicked.connect(lambda: self.show_menu(3))
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

    def _apply_cached_view(self):
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
            self.parent.ax.invert_yaxis()  # Invert y-axis for path loss
            
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
        # Show loading bar for model fitting
        self.loading_bar.show()
        self.loading_bar.setRange(0, 0) # Indeterminate mode
        self.auto_apply_btn.setEnabled(False) # Disable apply while processing
        self.parent.statusBar.showMessage("Fitting regression model...", 0) # Persistent message

        # Use QTimer to allow UI update before heavy computation
        QTimer.singleShot(50, self._perform_auto_plot)

    def _perform_auto_plot(self):
        try:
            # Read values from spin boxes
            max_points = self.max_input.value()
            tolerance = self.tolerance_input.value()
            min_length = self.min_input.value()

            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)

            if self.is_heatmap:
                self.parent.statusBar.showMessage("Generating heatmap...", 0)
                QApplication.processEvents() # Allow UI update
                self._plot_heatmap()
                self.parent.statusBar.showMessage("Heatmap generated.", 3000)
            else:
                self.parent.statusBar.showMessage("Fitting model and plotting regression...", 0)
                QApplication.processEvents() # Allow UI update
                self._plot_regression(max_points, tolerance, min_length)
                # Enable predict button only if model fitting was successful
                self.predict_btn.setEnabled(self.current_model is not None)
                # Enable report generation in main window
                self.parent.update_report_action_state(self.current_model is not None)

                if self.current_model:
                    self.parent.statusBar.showMessage("Regression model fitted and plotted.", 3000)
                else:
                    # If model fitting failed within _plot_regression (e.g., insufficient data)
                    self.parent.statusBar.showMessage("Model fitting failed.", 5000)

                # Enable display function button if model is fitted
                self.display_function_btn.setEnabled(self.current_model is not None)

            self.parent.canvas.draw()

        except ValueError as e:
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            self.parent.ax.text(0.5, 0.5, f"Error: Invalid input parameters\n{str(e)}",
                        ha='center', va='center', transform=self.parent.ax.transAxes, color='red')
            self.parent.ax.set_title("Auto Plot Error")
            self.parent.canvas.draw()
            self.parent.statusBar.showMessage(f"Error: Invalid input - {str(e)}", 5000)
            self.predict_btn.setEnabled(False) # Disable predict on error
            self.parent.update_report_action_state(False) # Disable report on error
            self.display_function_btn.setEnabled(False) # Disable display function button on error

        finally:
            # Hide loading bar and re-enable button regardless of success/failure
            self.loading_bar.hide()
            self.loading_bar.setRange(0, 100) # Reset range
            self.auto_apply_btn.setEnabled(True)
            # Clear persistent status message if one wasn't set by success/failure cases
            if self.parent.statusBar.currentMessage().endswith("..."):
                 self.parent.statusBar.clearMessage()

    def _plot_heatmap(self):
        if self.csv_data is None:
            self.parent.ax.text(0.5, 0.5, 
                "Please upload a CSV file first", 
                ha='center', va='center', transform=self.parent.ax.transAxes)
            self.parent.ax.set_title("No Data")
            return
            
        x, y = self.csv_data
        
        # Validate data
        heatmap_data = generate_heatmap_data(x, y)
        if heatmap_data:
            xi, Z, x_min, x_max, y_min, y_max = heatmap_data
            Z_2d = np.tile(Z, (50, 1))
            
            im = self.parent.ax.imshow(Z_2d, 
                                     extent=[x_min, x_max, y_min, y_max],
                                     aspect='auto',
                                     origin='upper',  # This inverts the y-axis for heatmap
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
        else:
            # Handle case where utility function returns None (insufficient data)
            self.parent.ax.text(0.5, 0.5, 
                "Need at least 3 data points for heatmap", 
                ha='center', va='center', transform=self.parent.ax.transAxes)
            self.parent.ax.set_title("Insufficient Data")
        
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
        QApplication.processEvents() # Ensure text is shown

        # Update status bar
        self.parent.statusBar.showMessage("Optimizing breakpoints...", 0)
        QApplication.processEvents()

        model = PiecewiseLogarithmicRegression(
            max_breakpoints=max_points,
            min_segment_length=min_length,
            tolerance=tolerance,
            verbose=True
        )
        model.fit(x, y)
        self.current_model = model
        # Enable the display function button since we have a fitted model
        self.display_function_btn.setEnabled(True)

        # Clear the figure for the enhanced plot
        self.parent.figure.clear()
        self.parent.ax = self.parent.figure.add_subplot(111)

        # Update status bar
        self.parent.statusBar.showMessage("Plotting results...", 0)
        QApplication.processEvents()

        # Plot original data points
        self.parent.ax.scatter(x, y, s=30, alpha=0.5, color='blue')

        # Generate fine-grained x values for smooth curve plotting
        x_fine = np.logspace(np.log10(x.min()), np.log10(x.max()), 1000)
        y_pred_fine = model.predict(x_fine)

        # Plot segments with confidence intervals using the utility function
        num_segments = len(model.breakpoints_) - 1
        colors = plt.cm.viridis(np.linspace(0, 0.8, num_segments))
        plot_regression_segments(self.parent.ax, model, x_fine, y_pred_fine, colors)

        # Ensure y-axis is inverted
        self.parent.ax.invert_yaxis()

        # Plot confidence intervals (this part remains as it's specific to this plot)
        for i in range(num_segments):
            mask = (x_fine >= model.breakpoints_[i]) & (x_fine <= model.breakpoints_[i + 1])
            if i < len(model.models_) and model.models_[i] is not None:
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

        # Clear status bar after short delay
        QTimer.singleShot(100, lambda: self.parent.statusBar.showMessage("Model fitting complete.", 3000) if self.current_model else None)

    def show_menu(self, index):
        previous_tab = self.last_active_tab
        self.last_active_tab = index
        
        self.auto_btn.setChecked(False)
        self.manual_btn.setChecked(False)
        self.comparison_btn.setChecked(False)
        self.other_btn.setChecked(False)
        
        # Cache view state when switching FROM Auto, Comparison or Other tab
        if previous_tab in [0, 2, 3] and index == 1:  # Switching to Manual
            self._cache_current_view()
            self.is_heatmap = False
            self.view_toggle_btn.setText("Graph View")
            self.view_toggle_btn.setChecked(False)
            self.parent.init_plot()
            self.plot_function()
        elif previous_tab == 1 and index in [0, 2, 3]:  # Switching FROM Manual
            self._apply_cached_view()
        elif previous_tab in [0, 2] and index == 3:  # Switching TO Prediction
            # Keep Auto tab's graph by re-plotting with current model
            if self.current_model is not None:
                # Store current view state
                current_plot_state = {
                    'xlim': self.parent.ax.get_xlim() if hasattr(self.parent, 'ax') else None,
                    'ylim': self.parent.ax.get_ylim() if hasattr(self.parent, 'ax') else None,
                    'is_heatmap': self.is_heatmap
                }
                
                # Ensure we're in graph view for prediction
                self.is_heatmap = False
                self.view_toggle_btn.setText("Graph View")
                self.view_toggle_btn.setChecked(False)
                
                # Replot using auto plot
                self.auto_plot_function()
                
                # Restore view limits if they existed
                if current_plot_state['xlim'] and hasattr(self.parent, 'ax'):
                    self.parent.ax.set_xlim(current_plot_state['xlim'])
                    self.parent.ax.set_ylim(current_plot_state['ylim'])
                    self.parent.canvas.draw()
        elif previous_tab == 3 and index == 0:  # Switching back to Auto from Prediction
            # Restore previous Auto tab state
            if hasattr(self, '_cached_state'):
                self.is_heatmap = self._cached_state.get('is_heatmap', False)
                self.view_toggle_btn.setText("Heatmap View" if self.is_heatmap else "Graph View")
                self.view_toggle_btn.setChecked(self.is_heatmap)
                self.auto_plot_function()
        elif previous_tab in [0, 2, 3] and index in [0, 2]:  # Between Auto/Comparison tabs
            # Preserve plot state but update UI
            current_plot_state = {
                'xlim': self.parent.ax.get_xlim() if hasattr(self.parent, 'ax') else None,
                'ylim': self.parent.ax.get_ylim() if hasattr(self.parent, 'ax') else None
            }
            
            # Update UI and replot as needed
            if index == 0:
                self.auto_plot_function()
            elif index == 2:
                self._plot_comparison()
            
            # Restore view limits if they existed
            if current_plot_state['xlim'] and hasattr(self.parent, 'ax'):
                self.parent.ax.set_xlim(current_plot_state['xlim'])
                self.parent.ax.set_ylim(current_plot_state['ylim'])
                self.parent.canvas.draw()

        # Update active button and tab
        if index == 0:
            self.auto_btn.setChecked(True)
        elif index == 1:
            self.manual_btn.setChecked(True)
        elif index == 2:
            self.comparison_btn.setChecked(True)
        else:
            self.other_btn.setChecked(True)

        self.stack.setCurrentIndex(index)
        
        # Ensure predict button state is correct
        if index == 3:  # Prediction tab
            self.predict_btn.setEnabled(self.current_model is not None)
            self.prediction_result.setText("Enter a distance value above to predict path loss using the current model.")

    def _predict_path_loss(self):
        # Check if we have a model (redundant check, but safe)
        if self.current_model is None:
            self.prediction_result.setText("Error: Please fit a model in the 'Auto' tab first.")
            return

        try:
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

    def _add_dataset(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Upload CSV File",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                x, y, _ = load_data_from_file(file_path)
                filename = os.path.basename(file_path)
                
                # Create a container for this dataset
                dataset_widget = QWidget()
                dataset_widget.setStyleSheet("""
                    QWidget {
                        background-color: #242938;
                        border-radius: 6px;
                        margin: 2px 0px;
                    }
                    QWidget:hover {
                        background-color: #2c334a;
                    }
                """)
                dataset_layout = QHBoxLayout(dataset_widget)
                dataset_layout.setContentsMargins(8, 8, 8, 8)
                
                # Add file icon and name in a sub-container
                file_info_container = QWidget()
                file_info_layout = QHBoxLayout(file_info_container)
                file_info_layout.setContentsMargins(0, 0, 0, 0)
                file_info_layout.setSpacing(8)
                
                # Add file icon
                file_icon = QLabel("📄")
                file_icon.setStyleSheet("color: #61afef; font-size: 14px;")
                file_info_layout.addWidget(file_icon)
                
                # Add filename label
                label = QLabel(filename)
                label.setStyleSheet("color: #e1e5ee; font-size: 13px;")
                file_info_layout.addWidget(label)
                
                dataset_layout.addWidget(file_info_container)
                dataset_layout.addStretch()
                
                # Add remove button
                remove_btn = QPushButton("✕")
                remove_btn.setFixedSize(24, 24)
                remove_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1e2433;
                        color: #e1e5ee;
                        border: none;
                        border-radius: 12px;
                        font-size: 14px;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: #c94b4b;
                        color: white;
                    }
                """)
                remove_btn.clicked.connect(lambda checked, w=dataset_widget: self._remove_dataset(w))
                dataset_layout.addWidget(remove_btn)
                
                # Insert new dataset widget before the stretch
                self.dataset_list_layout.insertWidget(self.dataset_list_layout.count() - 1, dataset_widget)
                
                # Store the dataset
                self.datasets.append((filename, x, y))
                
            except Exception as e:
                self.parent.statusBar.showMessage(f"Error loading CSV file: {str(e)}", 5000)

    def _remove_dataset(self, widget):
        # Find the index of the widget
        index = self.dataset_list_layout.indexOf(widget)
        if index >= 0:
            # Remove the widget
            widget.deleteLater()
            # Remove the corresponding dataset
            if index < len(self.datasets):
                self.datasets.pop(index)

    def _plot_comparison(self):
        if not self.datasets:
            self.parent.statusBar.showMessage("Please add at least one dataset first", 5000)
            return

        try:
            # Setup plot
            self.parent.figure.clear()
            self.parent.ax = self.parent.figure.add_subplot(111)
            
            # Generate colors for different datasets
            colors = plt.cm.tab10(np.linspace(0, 1, len(self.datasets)))
            
            for (filename, x, y), color in zip(self.datasets, colors):
                # Create and fit model with current parameters
                model = PiecewiseLogarithmicRegression(
                    max_breakpoints=self.max_input.value(),
                    min_segment_length=self.min_input.value(),
                    tolerance=self.tolerance_input.value()
                )
                model.fit(x, y)
                
                # Plot original points
                self.parent.ax.scatter(x, y, s=30, alpha=0.5, color=color)
                
                # Generate x values strictly within data range
                x_fine = np.logspace(np.log10(np.min(x)), np.log10(np.max(x)), 1000)
                y_pred = model.predict(x_fine)
                
                # Plot segments with confidence intervals
                num_segments = len(model.breakpoints_) - 1
                for i in range(num_segments):
                    mask = (x_fine >= model.breakpoints_[i]) & (x_fine <= model.breakpoints_[i + 1])
                    if i < len(model.models_) and model.models_[i] is not None:
                        x_segment = x_fine[mask]
                        y_segment = y_pred[mask]
                        self.parent.ax.semilogx(x_segment, y_segment, '-', 
                                              linewidth=2, color=color)
                        
                        # Add confidence intervals
                        if len(x_segment) > 0:
                            intervals = model.get_confidence_intervals(x_segment)
                            for interval_mask, interval in intervals:
                                if len(interval) == len(x_segment):
                                    self.parent.ax.fill_between(
                                        x_segment,
                                        y_segment - interval,
                                        y_segment + interval,
                                        color=color, alpha=0.1
                                    )
                
                # Add breakpoint indicators
                for i, bp in enumerate(model.breakpoints_[1:-1], 1):
                    self.parent.ax.axvline(bp, color=color, linestyle='--', 
                                         alpha=0.3, linewidth=1)
                
                # Add dataset to legend
                self.parent.ax.plot([], [], '-', color=color, linewidth=2,
                                  label=f'{filename} (R²={model.r2_:.3f})')

            # Enhance plot style
            self.parent.ax.grid(True, which='both', alpha=0.2)
            self.parent.ax.grid(True, which='major', alpha=0.5)
            self.parent.ax.set_xlabel('Distance (log scale)')
            self.parent.ax.set_ylabel('Path Loss (dB)')
            self.parent.ax.invert_yaxis()  # Invert y-axis for path loss
            
            # Create compact legend
            legend = self.parent.ax.legend(
                fontsize='x-small',
                frameon=True,
                framealpha=0.8,
                edgecolor='#1a1f2d',
                facecolor='white',
                loc='upper right',
                borderpad=0.4,
                handlelength=1.0,
                handletextpad=0.4,
                borderaxespad=0.4,
                markerscale=0.7
            )
            
            self.parent.ax.set_title('Dataset Comparison')
            
            # Update layout and draw
            self.parent.figure.tight_layout()
            self.parent.canvas.draw()
            
        except Exception as e:
            self.parent.statusBar.showMessage(f"Error plotting comparison: {str(e)}", 5000)
            print(f"Comparison plot error: {e}")

    def _show_universal_function(self):
        """Show the universal function in a formatted dialog"""
        if not self.current_model:
            return
            
        try:
            # Get the universal function from the model
            function_str = self.current_model.get_universal_function()
            
            # Create and show the expression widget
            from .show_function import MathExpressionWidget
            dialog = QDialog(self)
            dialog.setWindowTitle("Model Universal Function")
            dialog.setModal(True)
            dialog.setMinimumWidth(800)
            dialog.setMinimumHeight(400)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #1a1f2d;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Add the math expression widget
            expr_widget = MathExpressionWidget()
            expr_widget.set_expression(function_str)
            layout.addWidget(expr_widget)
            
            # Add buttons
            button_container = QHBoxLayout()
            close_btn = QPushButton("Close")
            close_btn.setStyleSheet(Styles.BUTTON_SECONDARY)
            close_btn.clicked.connect(dialog.close)
            button_container.addStretch()
            button_container.addWidget(close_btn)
            layout.addLayout(button_container)
            
            dialog.exec()
        except Exception as e:
            self.parent.statusBar.showMessage(f"Error displaying function: {str(e)}", 5000)
            print(f"Error in _show_universal_function: {e}")