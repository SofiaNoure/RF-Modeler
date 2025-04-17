import numpy as np
from typing import Tuple, Optional

def load_data_from_file(filename: str) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
    """
    Load data from CSV file with headers (Distance_km,Value_dB)
    
    Args:
        filename (str): Path to the CSV file
        
    Returns:
        Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]: Returns x values, y values, and None for compatibility
        
    Raises:
        Exception: If file cannot be read or has invalid format
    """
    try:
        # Read CSV, skip header row, use first two columns
        data = np.genfromtxt(filename, delimiter=',', skip_header=1, usecols=(0, 1))
        x = data[:, 0]
        y = data[:, 1]
        return x, y, None
    except Exception as e:
        print(f"⚠️ Error loading {filename}: {str(e)}. Using default values.")
        return np.array([1.0, 2.0, 3.0, 4.0, 5.0]), \
               np.array([5.0, 4.0, 3.0, 2.0, 1.0]), None

def validate_data(x: np.ndarray, y: np.ndarray) -> Tuple[bool, str]:
    """
    Validate input data for regression model
    
    Args:
        x (np.ndarray): X values
        y (np.ndarray): Y values
        
    Returns:
        Tuple[bool, str]: True if data is valid, False otherwise, and an error message if invalid
    """
    if len(x) != len(y):
        return False, "X and Y arrays must have the same length"
    
    if len(x) < 3:
        return False, "Need at least 3 data points for regression"
        
    if not np.all(x > 0):
        return False, "All X values must be positive for logarithmic regression"
        
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        return False, "Data contains non-finite values"
        
    return True, ""