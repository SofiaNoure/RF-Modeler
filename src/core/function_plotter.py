import numpy as np
import re
import scipy.special

class FunctionPlotter:
    def __init__(self):
        # Adjust ranges for better performance and display
        self.full_range = (-10000, 10000)  # Full calculation range
        self.display_range = (-20, 20)      # Default visible range
        self.num_points = {
            'display': 1500,  # Increased points for smoother display
            'full': 15000    # Increased points for better accuracy
        }
        self.max_y_bound = 1e6

    def prepare_function_string(self, function_str):
        """Convert mathematical notation to numpy equivalents"""
        constants = {
            'pi': 'np.pi',
            'e': 'np.e'
        }
        
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
            'log2': 'np.log2',
            'sinh': 'np.sinh',
            'cosh': 'np.cosh',
            'tanh': 'np.tanh',
            'ceil': 'np.ceil',
            'floor': 'np.floor',
            'round': 'np.round',
            'erf': 'scipy.special.erf',
            'gamma': 'scipy.special.gamma',
            'beta': 'scipy.special.beta',
            'sinc': 'np.sinc'
        }
        
        # Replace constants first
        for const, replacement in constants.items():
            function_str = re.sub(rf'\b{const}\b', replacement, function_str)
        
        # Then replace function names
        for func, replacement in functions.items():
            function_str = re.sub(rf'\b(?<!np\.){func}\b', replacement, function_str)
        
        return function_str.replace('^', '**')

    def evaluate_function(self, function_str):
        """Evaluate the function and return x, y values"""
        processed_func = self.prepare_function_string(function_str)
        
        try:
            # Import scipy.special for advanced functions if needed
            import scipy.special
            
            # Check for functions with special domain requirements
            has_log = any(term in processed_func.lower() for term in ['log(', 'log10(', 'log2('])
            has_arcsin = 'arcsin(' in processed_func
            has_arccos = 'arccos(' in processed_func
            has_gamma = 'gamma(' in processed_func
            has_beta = 'beta(' in processed_func
            has_sqrt = 'sqrt(' in processed_func
            
            # First evaluate in display range with higher density
            x_display = np.linspace(self.display_range[0], self.display_range[1], 
                                  self.num_points['display'])
            
            # Handle domain restrictions
            if has_log or has_sqrt:
                x_display = x_display[x_display > 0]
            if has_arcsin or has_arccos:
                x_display = x_display[(x_display >= -1) & (x_display <= 1)]
            if has_gamma or has_beta:
                x_display = x_display[x_display > 0]
            
            # Evaluate display range
            y_display = eval(processed_func, {"x": x_display, "np": np, "scipy": scipy})
            
            # Then evaluate full range with lower density
            if has_log or has_sqrt:
                # For log/sqrt functions, use only positive values and logarithmic spacing
                x_full = np.concatenate([
                    np.logspace(-6, np.log10(min(x_display)), 
                              self.num_points['full'] // 4),
                    x_display,
                    np.logspace(np.log10(max(x_display)), 6, 
                              self.num_points['full'] // 4)
                ])
            elif has_arcsin or has_arccos:
                # For inverse trig functions, limit to [-1, 1]
                x_full = np.linspace(-1, 1, self.num_points['full'])
            elif has_gamma or has_beta:
                # For gamma/beta functions, use positive values with logarithmic spacing
                x_full = np.concatenate([
                    np.logspace(-3, 0, self.num_points['full'] // 4),
                    np.logspace(0, 3, self.num_points['full'] // 4)
                ])
            else:
                # For regular functions, use linear spacing
                x_full = np.concatenate([
                    np.linspace(self.full_range[0], self.display_range[0], 
                              self.num_points['full'] // 4),
                    x_display,
                    np.linspace(self.display_range[1], self.full_range[1], 
                              self.num_points['full'] // 4)
                ])
            
            x_full = np.unique(x_full)  # Remove duplicates
            
            # Evaluate the function
            y_full = eval(processed_func, {"x": x_full, "np": np, "scipy": scipy})
            
            # Remove invalid values
            mask = np.isfinite(y_full)
            x_full = x_full[mask]
            y_full = y_full[mask]
            
            # Clip extreme values for better display
            y_full = np.clip(y_full, -self.max_y_bound, self.max_y_bound)
            
            return x_full, y_full
            
        except Exception as e:
            # Add descriptive error messages for common issues
            if "log" in str(e).lower():
                raise ValueError("Logarithm error: Cannot compute log of zero or negative values")
            elif "sqrt" in str(e).lower():
                raise ValueError("Square root error: Cannot compute sqrt of negative values")
            elif "arcsin" in str(e).lower() or "arccos" in str(e).lower():
                raise ValueError("Inverse trigonometric error: Input values must be between -1 and 1")
            elif "gamma" in str(e).lower():
                raise ValueError("Gamma function error: Input must be positive")
            elif "beta" in str(e).lower():
                raise ValueError("Beta function error: Both inputs must be positive")
            raise ValueError(f"Error evaluating function: {str(e)}")

    def get_plot_limits(self, y):
        """Calculate appropriate y-axis limits"""
        y_valid = y[np.isfinite(y)]
        if len(y_valid) == 0:
            return -10, 10  # More reasonable default range

        y_min, y_max = np.min(y_valid), np.max(y_valid)
        
        # Handle different range scenarios
        if abs(y_max - y_min) < 0.1:
            # Extremely small range - provide good visibility
            mid = (y_max + y_min) / 2
            return mid - 0.5, mid + 0.5
            
        if abs(y_max - y_min) < 1:
            # Very small range - center around the values
            mid = (y_max + y_min) / 2
            return mid - 1, mid + 1
            
        if abs(y_max - y_min) < 10:
            # Small range - add proportional padding
            padding = max(1, (y_max - y_min) * 0.15)  # Increased padding
            return y_min - padding, y_max + padding
            
        if abs(y_max - y_min) > 1000:
            # Large range - use smaller padding to prevent excessive scale
            padding = (y_max - y_min) * 0.05
            return y_min - padding, y_max + padding
        
        # Medium range - use standard padding
        padding = (y_max - y_min) * 0.1
        return y_min - padding, y_max + padding