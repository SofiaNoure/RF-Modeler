import sys
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QWidget, QTextEdit, QPushButton, QHBoxLayout,
                               QScrollArea, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class MathExpressionRenderer:
    """
    A class to render mathematical expressions in PySide6 using LaTeX-style HTML formatting
    """
    
    def __init__(self):
        self.base_font_size = 16
        self.font_family = "Computer Modern, Times New Roman, serif"
        
    def format_expression_html(self, expression):
        """
        Convert mathematical expression to LaTeX-style formatted HTML
        
        Args:
            expression (str): Raw mathematical expression string
            
        Returns:
            str: LaTeX-style HTML formatted expression
        """
        if not expression or not isinstance(expression, str):
            return "<div>No expression provided</div>"
            
        # Start HTML container with LaTeX-like styling
        html = f"""
        <div style='
            font-family: {self.font_family}; 
            font-size: {self.base_font_size}px; 
            line-height: 2.2; 
            padding: 25px;
            background-color: #fdfdfd;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            margin: 15px 0;
            color: #1a1a1a;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        '>
        <div style='
            display: inline-block;
            text-align: left;
            font-size: {self.base_font_size + 2}px;
            padding: 10px 20px;
            background: linear-gradient(145deg, #ffffff, #f8f8f8);
            border-radius: 4px;
            border: 1px solid #eeeeee;
        '>
        """
        
        # Split expression by main addition operators
        segments = self._split_expression_safely(expression)
        
        formatted_segments = []
        for i, segment in enumerate(segments):
            formatted_segment = self._format_segment(segment.strip())
            formatted_segments.append(formatted_segment)
        
        # Add f(x) = annotation at the start
        html += "<span style='font-size: 18px; font-weight: 500; color: #2c3e50; margin-right: 12px;'><i>f</i>(<i>x</i>) =</span>"
        
        # Join segments with LaTeX-style spacing and operators
        if len(formatted_segments) > 1:
            html += "<br/><span style='margin: 0 8px; font-size: 18px;'>+</span> ".join(formatted_segments)
        else:
            html += formatted_segments[0]
            
        html += "</div></div>"
        
        return html
    
    def _split_expression_safely(self, expression):
        """
        Split expression by '+' but respect parentheses grouping
        """
        segments = []
        current_segment = ""
        paren_depth = 0
        
        i = 0
        while i < len(expression):
            char = expression[i]
            
            if char == '(':
                paren_depth += 1
                current_segment += char
            elif char == ')':
                paren_depth -= 1
                current_segment += char
            elif char == '+' and paren_depth == 0:
                # This is a top-level addition
                if current_segment.strip():
                    segments.append(current_segment.strip())
                current_segment = ""
            else:
                current_segment += char
            
            i += 1
        
        # Add the last segment
        if current_segment.strip():
            segments.append(current_segment.strip())
            
        return segments
    
    def _format_segment(self, segment):
        """
        Format individual segment with LaTeX-style mathematical notation
        """
        # Step 1: Replace numpy functions first
        formatted = segment.replace("np.log(x)", "log(x)")
        formatted = formatted.replace("np.log", "log")
        formatted = formatted.replace("np.heaviside", "H")
        formatted = formatted.replace("np.exp", "exp")
        formatted = formatted.replace("np.sin", "sin")
        formatted = formatted.replace("np.cos", "cos")
        formatted = formatted.replace("np.tan", "tan")
        formatted = formatted.replace("np.sqrt", "√")
        
        # Step 2: Format numbers first (before operators to avoid conflicts)
        formatted = self._format_numbers(formatted)
        
        # Step 3: Format mathematical operators with proper spacing
        formatted = formatted.replace("*", " ⋅ ")
        formatted = formatted.replace("**", "<sup>")
        formatted = formatted.replace(" - ", " − ")
        formatted = formatted.replace("(- ", "(−")  # Handle negative numbers in parentheses
        
        # Step 4: Format variables with italics
        formatted = re.sub(r'\b([a-zA-Z])\b(?![\(<])', r'<i>\1</i>', formatted)
        
        # Step 5: Format function calls
        formatted = self._format_function_calls(formatted)
        
        # Step 6: Clean up any double spaces
        formatted = re.sub(r'\s+', ' ', formatted)
        
        return formatted
    
    def _format_numbers(self, text):
        """
        Format numerical coefficients with LaTeX-style appearance
        """
        def format_number(match):
            num_str = match.group()
            num = float(num_str)
            
            if abs(num) < 0.000001:
                # Scientific notation in LaTeX style
                exp_str = f"{num:.2e}"
                base, exp = exp_str.split('e')
                exp_val = int(exp)
                return f"<span style='color: #2c3e50; font-weight: 500;'>{base} × 10<sup>{exp_val}</sup></span>"
            elif abs(num) < 0.01:
                return f"<span style='color: #2c3e50; font-weight: 400;'>{num:.6f}</span>"
            else:
                return f"<span style='color: #2c3e50; font-weight: 500;'>{num:.4f}</span>"
        
        # Match floating point numbers (including negative)
        pattern = r'-?\d+\.\d+'
        return re.sub(pattern, format_number, text)
    
    def _format_function_calls(self, text):
        """
        Format function calls with LaTeX mathematical styling
        """
        # Style function names in LaTeX upright style
        function_patterns = [
            (r'\bln\(([^)]+)\)', r'<span style="color: #1a472a; font-weight: 500;">ln</span>(<i>\1</i>)'),
            (r'\bH\(([^)]+)\)', r'<span style="color: #8b4513; font-weight: bold; font-size: 1.1em;">H</span>(\1)'),
            (r'\b(log|sin|cos|tan|exp|sqrt)\(([^)]+)\)', r'<span style="color: #1a472a; font-weight: 500;">\1</span>(\2)')
        ]
        
        for pattern, replacement in function_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _format_parentheses(self, text):
        """
        Format parentheses with LaTeX-style scaling and spacing
        """
        # Add subtle spacing around parentheses
        text = re.sub(r'\(', '<span style="margin-right: 1px; font-size: 1.1em;">(</span>', text)
        text = re.sub(r'\)', '<span style="margin-left: 1px; font-size: 1.1em;">)</span>', text)
        
        # Handle nested parentheses with slightly different styling
        paren_depth = 0
        result = ""
        i = 0
        while i < len(text):
            if text[i:i+60].startswith('<span style="margin-right: 1px; font-size: 1.1em;">('):
                paren_depth += 1
                if paren_depth > 1:
                    result += '<span style="margin-right: 1px; font-size: 1.15em; font-weight: 500;">('
                    i += 60  # Skip the original span
                else:
                    result += text[i:i+61]
                    i += 61
            elif text[i:i+59].startswith('<span style="margin-left: 1px; font-size: 1.1em;">)'):
                if paren_depth > 1:
                    result += ')</span>'
                    i += 59
                else:
                    result += text[i:i+67]
                    i += 67
                paren_depth = max(0, paren_depth - 1)
            else:
                result += text[i]
                i += 1
        
        return result


class MathExpressionWidget(QWidget):
    """
    A widget to display LaTeX-style formatted mathematical expressions
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.renderer = MathExpressionRenderer()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setMinimumHeight(250)
        
        # Set LaTeX-style font
        font = QFont()
        font.setFamily("Computer Modern, Times New Roman, serif")
        font.setPointSize(14)
        self.text_display.setFont(font)
        
        # LaTeX-style text edit styling
        self.text_display.setStyleSheet("""
            QTextEdit {
                border: 2px solid #d4d4d4;
                border-radius: 8px;
                background-color: #fefefe;
                padding: 8px;
                selection-background-color: #b3d9ff;
            }
            QTextEdit:focus {
                border-color: #5b9bd5;
                box-shadow: 0 0 5px rgba(91, 155, 213, 0.3);
            }
        """)
        
        layout.addWidget(self.text_display)
        
    def set_expression(self, expression):
        """
        Set and display a mathematical expression
        """
        html_content = self.renderer.format_expression_html(expression)
        self.text_display.setHtml(html_content)
        
    def clear_expression(self):
        """
        Clear the displayed expression
        """
        self.text_display.clear()


class MainWindow(QMainWindow):
    """
    Main application window for demonstration
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaTeX-Style Mathematical Expression Renderer")
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add title with LaTeX-style formatting
        title = QLabel("LaTeX-Style Mathematical Expression Renderer")
        title.setStyleSheet("""
            font-size: 22px; 
            font-weight: 300; 
            margin: 15px;
            color: #2c3e50;
            font-family: Computer Modern, Times New Roman, serif;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create expression widget
        self.expression_widget = MathExpressionWidget()
        layout.addWidget(self.expression_widget)
        
        # Create control buttons with LaTeX document styling
        button_layout = QHBoxLayout()
        
        self.demo_button = QPushButton("Load Demo Expression")
        self.clear_button = QPushButton("Clear")
        
        # Style buttons to match LaTeX document aesthetic
        button_style = """
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: Computer Modern, Times New Roman, serif;
                color: #24292f;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
                border-color: #d0d7de;
            }
            QPushButton:pressed {
                background-color: #e9ecef;
            }
        """
        
        self.demo_button.setStyleSheet(button_style)
        self.clear_button.setStyleSheet(button_style)
        
        self.demo_button.clicked.connect(self.load_demo_expression)
        self.clear_button.clicked.connect(self.expression_widget.clear_expression)
        
        button_layout.addWidget(self.demo_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)