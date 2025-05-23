import numpy as np
import re
import scipy.special

class FunctionPlotter:
    def __init__(self):
        # Adjust ranges for better performance and display
        self.full_range = (-10000, 10000)  # Full calculation range
        self.display_range = (-20, 20)      # Default visible range
        self.num_points = {
            'display': 5000,  # Increased points for smoother display
            'full': 50000     # Increased points for full range
        }
        self.max_y_bound = 1e6
        self.periodic_funcs = ['sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh']

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
            import scipy.special
            
            has_periodic = any(func in processed_func.lower() for func in self.periodic_funcs)
            has_log = any(term in processed_func.lower() for term in ['log(', 'log10(', 'log2('])
            has_sqrt = 'sqrt(' in processed_func
            
            if has_periodic:
                # For periodic functions, use a denser sampling that scales with the range
                # and ensures we capture enough points per period
                x_ranges = []
                base_points = self.num_points['display']
                
                # Generate ranges with increasing density for periodic functions
                ranges = [
                    (-10000, -1000, base_points),
                    (-1000, -100, base_points),
                    (-100, -20, base_points),
                    (-20, 20, self.num_points['display']),  # Higher density in visible range
                    (20, 100, base_points),
                    (100, 1000, base_points),
                    (1000, 10000, base_points)
                ]
                
                for start, end, points in ranges:
                    if has_log and start <= 0:  # Skip negative ranges for log functions
                        continue
                    x_ranges.append(np.linspace(start, end, points))
                
                x_full = np.concatenate(x_ranges)
                
            elif has_log or has_sqrt:
                # For log/sqrt, use logarithmic spacing
                x_ranges = []
                if not has_sqrt:  # Allow small negative numbers for log only
                    x_ranges.append(np.linspace(-20, -0.001, self.num_points['display'] // 4))
                x_ranges.extend([
                    np.logspace(-3, 0, self.num_points['display'] // 2),
                    np.logspace(0, 4, self.num_points['display'])
                ])
                x_full = np.concatenate(x_ranges)
            else:
                # For regular functions, use adaptive linear spacing
                x_ranges = []
                base_points = self.num_points['display'] // 4
                
                # Define ranges with different densities
                ranges = [
                    (-10000, -1000, base_points),
                    (-1000, -100, base_points),
                    (-100, -20, base_points),
                    (-20, 20, self.num_points['display']),  # Higher density in visible range
                    (20, 100, base_points),
                    (100, 1000, base_points),
                    (1000, 10000, base_points)
                ]
                
                for start, end, points in ranges:
                    x_ranges.append(np.linspace(start, end, points))
                
                x_full = np.concatenate(x_ranges)
            
            x_full = np.unique(x_full)  # Remove duplicates
            y_full = eval(processed_func, {"x": x_full, "np": np, "scipy": scipy})
            
            # Remove invalid values and extreme values
            mask = np.isfinite(y_full)
            x_full = x_full[mask]
            y_full = y_full[mask]
            y_full = np.clip(y_full, -self.max_y_bound, self.max_y_bound)
            
            return x_full, y_full
            
        except Exception as e:
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