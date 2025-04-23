import numpy as np

def generate_heatmap_data(x, y, grid_size=500):
    """
    Generates data required for plotting a heatmap based on x, y scatter data.

    Args:
        x (np.array): Array of x-coordinates (e.g., distance).
        y (np.array): Array of y-coordinates (e.g., path loss).
        grid_size (int): The resolution of the grid for heatmap calculation.

    Returns:
        tuple: Contains xi (grid points), Z (heatmap values), x_min, x_max, y_min, y_max.
               Returns None if input data is insufficient.
    """
    if x is None or y is None or len(x) < 3:
        return None

    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()

    xi = np.linspace(x_min, x_max, grid_size)
    # Initialize Z with a value representing high loss (or max observed loss)
    Z = np.full(grid_size, np.max(y)) 

    # Simple nearest-neighbor interpolation/assignment for heatmap effect
    for dist, loss in zip(x, y):
        # Find indices of the 5 nearest grid points
        idx = np.abs(xi - dist).argsort()[:5] 
        # Calculate distances to these nearest points
        distances = np.abs(xi[idx] - dist)
        # Simple inverse distance weighting (add 1 to avoid division by zero)
        weights = 1 / (1 + distances) 
        # Normalize weights
        weights = weights / np.sum(weights) 
        # Update Z: take the minimum loss seen near this grid point
        # This creates the effect of 'signal strength' spreading slightly
        Z[idx] = np.minimum(Z[idx], loss) 

    return xi, Z, x_min, x_max, y_min, y_max

def plot_regression_segments(ax, model, x_fine, y_pred_fine, colors=None):
    """
    Plots the individual segments of a piecewise regression model on a given matplotlib axis.

    Args:
        ax (matplotlib.axes.Axes): The axes to plot on.
        model (PiecewiseLogarithmicRegression): The fitted regression model.
        x_fine (np.array): Fine-grained x-values for smooth plotting.
        y_pred_fine (np.array): Predicted y-values corresponding to x_fine.
        colors (list, optional): List of colors for each segment. Defaults to None (uses viridis cmap).
    """
    num_segments = len(model.breakpoints_) - 1
    if colors is None:
        import matplotlib.pyplot as plt
        colors = plt.cm.viridis(np.linspace(0, 0.8, num_segments))

    for i in range(num_segments):
        mask = (x_fine >= model.breakpoints_[i]) & (x_fine <= model.breakpoints_[i + 1])
        if i < len(model.models_) and model.models_[i] is not None:
            # Plot fitted line for this segment
            ax.semilogx(x_fine[mask], y_pred_fine[mask], '-', 
                      linewidth=2, color=colors[i])
