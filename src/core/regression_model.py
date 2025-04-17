import numpy as np
from sklearn.metrics import r2_score
from scipy.linalg import solve


class PiecewiseLogarithmicRegression:
    def __init__(self, max_breakpoints=5, min_segment_length=3, tolerance=1.00, max_iter=100, verbose=False):
        self.max_breakpoints = max_breakpoints
        self.min_segment_length = min_segment_length
        self.tolerance = tolerance
        self.max_iter = max_iter
        self.verbose = verbose
        self.breakpoints_ = None
        self.models_ = None
        self.r2_ = None
        self.mse_ = None

    def _solve_logarithmic_regression(self, X, y):
        X_log = np.log(X)
        X_design = np.column_stack([np.ones_like(X_log), X_log])
        return np.linalg.lstsq(X_design, y, rcond=None)[0]

    def _apply_continuity_constraints(self, x_segments, y_segments, breakpoints):
        models = []
        k = len(breakpoints) - 1
        X_all = []
        y_all = []
        for i in range(k):
            X_log = np.log(x_segments[i])
            X_design = np.column_stack([np.ones_like(X_log), X_log])
            X_all.append(X_design)
            y_all.append(y_segments[i])

        X_block = np.block([[X if i == j else np.zeros_like(X) for j in range(k)] for i, X in enumerate(X_all)])
        y_block = np.concatenate(y_all)

        C = np.zeros((k - 1, 2 * k))
        for j in range(1, k):
            xi = breakpoints[j]
            row = np.array([1, np.log(xi)])
            C[j - 1, (j - 1) * 2: (j - 1) * 2 + 2] = row
            C[j - 1, j * 2: j * 2 + 2] = -row

        A = X_block.T @ X_block
        b = X_block.T @ y_block

        KKT = np.block([[2 * A, C.T], [C, np.zeros((C.shape[0], C.shape[0]))]])
        rhs = np.concatenate([2 * b, np.zeros(C.shape[0])])
        solution = solve(KKT, rhs, assume_a='sym')

        for j in range(k):
            models.append(tuple(solution[j * 2: j * 2 + 2]))
        return models

    def _optimize_breakpoints(self, x, y, initial_breakpoints):
        breakpoints = np.sort(initial_breakpoints.copy())
        for _ in range(self.max_iter):
            new_breakpoints = breakpoints.copy()
            for i in range(1, len(breakpoints) - 1):
                left_bp = breakpoints[i - 1]
                right_bp = breakpoints[i + 1]
                delta = 0.2 * (right_bp - left_bp)
                neighborhood = np.linspace(breakpoints[i] - delta, breakpoints[i] + delta, 10)

                best_mse = float('inf')
                best_candidate = breakpoints[i]

                for candidate in neighborhood:
                    temp_breakpoints = breakpoints.copy()
                    temp_breakpoints[i] = candidate
                    try:
                        mse = self._calculate_mse(x, y, temp_breakpoints)
                        if mse < best_mse:
                            best_mse = mse
                            best_candidate = candidate
                    except:
                        continue

                new_breakpoints[i] = best_candidate

            if np.allclose(new_breakpoints, breakpoints, atol=1e-6):
                break
            breakpoints = new_breakpoints

        return breakpoints

    def _remove_redundant_breakpoints(self, x, y, breakpoints):
        if len(breakpoints) <= 2:
            return breakpoints

        current_mse = self._calculate_mse(x, y, breakpoints)
        improved = True

        while improved and len(breakpoints) > 2:
            improved = False
            for i in range(1, len(breakpoints) - 1):
                reduced = np.delete(breakpoints, i)
                try:
                    reduced_mse = self._calculate_mse(x, y, reduced)
                    rho = reduced_mse / current_mse
                    if rho < self.tolerance:
                        breakpoints = reduced
                        current_mse = reduced_mse
                        improved = True
                        break
                except:
                    continue

        return breakpoints

    def _calculate_mse(self, x, y, breakpoints):
        y_pred = self._predict_with_breakpoints(x, y, breakpoints)
        return np.mean((y_pred - y) ** 2)

    def _predict_with_breakpoints(self, x, y, breakpoints):
        y_pred = np.zeros_like(x)
        for i in range(len(breakpoints) - 1):
            mask = (x >= breakpoints[i]) & (x <= breakpoints[i + 1])
            x_segment = x[mask]
            if len(x_segment) == 0:
                continue
            A, B = self._solve_logarithmic_regression(x_segment, y[mask])
            y_pred[mask] = A + B * np.log(x_segment)
        return y_pred

    def fit(self, x, y):
        x = np.asarray(x).flatten()
        y = np.asarray(y).flatten()
        sort_idx = np.argsort(x)
        x, y = x[sort_idx], y[sort_idx]

        percentiles = np.linspace(0, 100, min(self.max_breakpoints + 2, len(x) // self.min_segment_length + 1))
        initial_breakpoints = np.unique(np.percentile(x, percentiles))

        optimized_breakpoints = self._optimize_breakpoints(x, y, initial_breakpoints)
        final_breakpoints = self._remove_redundant_breakpoints(x, y, optimized_breakpoints)

        self.breakpoints_ = final_breakpoints
        self.models_ = []

        x_segments = []
        y_segments = []
        for i in range(len(final_breakpoints) - 1):
            mask = (x >= final_breakpoints[i]) & (x <= final_breakpoints[i + 1])
            x_seg = x[mask]
            y_seg = y[mask]
            x_segments.append(x_seg)
            y_segments.append(y_seg)

        self.models_ = self._apply_continuity_constraints(x_segments, y_segments, final_breakpoints)

        y_pred = self.predict(x)
        self.r2_ = r2_score(y, y_pred)
        self.mse_ = np.mean((y_pred - y) ** 2)
        return self

    def predict(self, x):
        x = np.asarray(x).flatten()
        y_pred = np.zeros_like(x)
        for i in range(len(self.breakpoints_) - 1):
            mask = (x >= self.breakpoints_[i]) & (x <= self.breakpoints_[i + 1])
            x_segment = x[mask]
            if len(x_segment) == 0 or self.models_[i] is None:
                continue
            A, B = self.models_[i]
            y_pred[mask] = A + B * np.log(x_segment)
        return y_pred

    def get_equations(self):
        equations = []
        for i in range(len(self.breakpoints_) - 1):
            if self.models_[i] is None:
                continue
            A, B = self.models_[i]
            equations.append(
                f"For {self.breakpoints_[i]:.2f} ≤ x ≤ {self.breakpoints_[i + 1]:.2f}: y = {A:.4f} + {B:.4f} * log(x)"
            )
        return equations

    def get_universal_function(self):
        segments = []
        for i in range(len(self.breakpoints_) - 1):
            if self.models_[i] is None:
                continue
            A, B = self.models_[i]
            a = self.breakpoints_[i]
            b = self.breakpoints_[i + 1]
            segment = (
                f"({A:.6f} + {B:.6f}*np.log(x)) * "
                f"(np.heaviside(x-{a:.6f}) - np.heaviside(x-{b:.6f}, 0))"
            )
            segments.append(segment)

        full_expr = " + ".join(segments)
        if self.verbose:
            print("\nFULL HEAVISIDE EXPRESSION:\n" + full_expr)
        return full_expr