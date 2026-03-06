"""
evaluate.py - Model evaluation and metric computation.

This module handles the third stage of the ML pipeline:
1. Load the trained model from disk
2. Load test data splits
3. Compute evaluation metrics (RMSE, R2, MAE)
"""

import os

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def load_model(filepath: str) -> object:
    """Load a trained model from disk using joblib.

    Parameters
    ----------
    filepath : str
        Path to the saved model file (e.g., "models/model.pkl").

    Returns
    -------
    object
        The loaded model.
    """
    # TODO: implement
    pass


def load_test_data(input_dir: str) -> tuple:
    """Load test data splits from CSV files."""
    # TODO: implement
    pass


def evaluate_model(model, X_test, y_test) -> dict:
    """Evaluate the model on test data and return metrics."""
    # TODO: implement
    pass


if __name__ == "__main__":
    model = load_model("models/model.pkl")
    X_test, y_test = load_test_data("data/processed")
    metrics = evaluate_model(model, X_test, y_test)
    print(f"RMSE: {metrics['rmse']:.2f}")
    print(f"R2: {metrics['r2']:.2f}")
    print(f"MAE: {metrics['mae']:.2f}")
