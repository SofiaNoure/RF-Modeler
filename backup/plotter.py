import numpy as np
import re

class FunctionPlotter:
    def __init__(self):
        # Set x range to be closer to our default view while still allowing zoom out
        self.x_range = (-10000, 10000)
        # Increased number of points for smoother curves
        self.num_points = 10000
        # Add max value bounds to prevent overflow
        self.max_y_bound = 1e6

    def prepare_function_string(self, function_str):
        """Convert mathematical notation to numpy equivalents"""
        # First, handle constants that might be in the string
        constants = {
            'pi': 'np.pi',
            'e': 'np.e'
        }
        
        # Use word boundaries to replace only whole words
        for const, replacement in constants.items():
            function_str = re.sub(rf'\b{const}\b', replacement, function_str)

        # Handle functions
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
        
        # Replace functions, but only if they're not already prefixed with np.
        for func, replacement in functions.items():
            # Don't replace if it's already prefixed with np.
            function_str = re.sub(rf'\b(?<!np\.){func}\b', replacement, function_str)

        # Handle power operator last
        function_str = function_str.replace('^', '**')
        
        return function_str

    def evaluate_function(self, function_str):
        """Evaluate the function and return x, y values"""
        x = np.linspace(self.x_range[0], self.x_range[1], self.num_points)
        processed_func = self.prepare_function_string(function_str)
        
        try:
            y = eval(processed_func, {"x": x, "np": np})
            # Clip extremely large values to prevent display issues
            y = np.clip(y, -self.max_y_bound, self.max_y_bound)
            return x, y
        except Exception as e:
            raise ValueError(f"Error evaluating function: {str(e)}")

    def get_plot_limits(self, y):
        """Calculate appropriate y-axis limits"""
        y_valid = y[np.isfinite(y)]
        if len(y_valid) == 0:
            return -100, 100

        y_min, y_max = np.min(y_valid), np.max(y_valid)
        
        # If the range is very small, add padding
        if abs(y_max - y_min) < 10:
            padding = max(1, (y_max - y_min) * 0.1)
            return y_min - padding, y_max + padding
            
        # If the range is very large, use log-based padding
        if abs(y_max - y_min) > 1000:
            padding = (y_max - y_min) * 0.05
            return y_min - padding, y_max + padding
            
        # For medium ranges, use proportional padding
        padding = (y_max - y_min) * 0.1
        return y_min - padding, y_max + padding