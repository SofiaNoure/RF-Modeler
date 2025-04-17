import numpy as np
import re

class FunctionPlotter:
    def __init__(self):
        # Adjust ranges for better performance and display
        self.full_range = (-10000, 10000)  # Full calculation range
        self.display_range = (-20, 20)      # Default visible range
        self.num_points = {
            'display': 1000,  # Points for visible range
            'full': 10000    # Points for full range
        }
        self.max_y_bound = 1e6

    def prepare_function_string(self, function_str):
        """Convert mathematical notation to numpy equivalents"""
        constants = {
            'pi': 'np.pi',
            'e': 'np.e'
        }
        
        for const, replacement in constants.items():
            function_str = re.sub(rf'\b{const}\b', replacement, function_str)

        functions = {
            'sin': 'np.sin',
            'cos': 'np.cos',
            'tan': 'np.tan',
            'exp': 'np.exp',
            'log': 'np.log',
            'sqrt': 'np.sqrt',
            'abs': 'np.abs',
            'arcsin': 'np.arcsin',
            'arccos': 'np.arccos',
            'arctan': 'np.arctan',
            'log10': 'np.log10',
            'log2': 'np.log2'
        }
        
        for func, replacement in functions.items():
            function_str = re.sub(rf'\b(?<!np\.){func}\b', replacement, function_str)

        return function_str.replace('^', '**')

    def evaluate_function(self, function_str):
        """Evaluate the function and return x, y values"""
        processed_func = self.prepare_function_string(function_str)
        
        try:
            # First evaluate in display range with higher density
            x_display = np.linspace(self.display_range[0], self.display_range[1], 
                                  self.num_points['display'])
            y_display = eval(processed_func, {"x": x_display, "np": np})
            
            # Then evaluate full range with lower density
            x_full = np.concatenate([
                np.linspace(self.full_range[0], self.display_range[0], 
                          self.num_points['full'] // 4),
                x_display,
                np.linspace(self.display_range[1], self.full_range[1], 
                          self.num_points['full'] // 4)
            ])
            y_full = eval(processed_func, {"x": x_full, "np": np})
            
            # Clip values to prevent display issues
            y_full = np.clip(y_full, -self.max_y_bound, self.max_y_bound)
            
            return x_full, y_full
        except Exception as e:
            raise ValueError(f"Error evaluating function: {str(e)}")

    def get_plot_limits(self, y):
        """Calculate appropriate y-axis limits"""
        y_valid = y[np.isfinite(y)]
        if len(y_valid) == 0:
            return -100, 100

        y_min, y_max = np.min(y_valid), np.max(y_valid)
        
        # Handle different range scenarios
        if abs(y_max - y_min) < 1:
            # Very small range - center around the values
            mid = (y_max + y_min) / 2
            return mid - 1, mid + 1
            
        if abs(y_max - y_min) < 10:
            # Small range - add proportional padding
            padding = max(1, (y_max - y_min) * 0.1)
            return y_min - padding, y_max + padding
            
        if abs(y_max - y_min) > 1000:
            # Large range - use smaller padding
            padding = (y_max - y_min) * 0.05
            return y_min - padding, y_max + padding
            
        # Medium range - use standard padding
        padding = (y_max - y_min) * 0.1
        return y_min - padding, y_max + padding