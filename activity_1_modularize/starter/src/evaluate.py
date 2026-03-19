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
    return joblib.load(filepath)


def load_test_data(input_dir: str) -> tuple:
    """Load test data splits from CSV files."""
    X_test = pd.read_csv(f"{input_dir}/X_test.csv")
    y_test = pd.read_csv(f"{input_dir}/y_test.csv")
    return X_test, y_test


def evaluate_model(model, X_test, y_test) -> dict:
    """Evaluate the model on test data and return metrics."""
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    return {"rmse": rmse, "r2": r2, "mae": mae}


if __name__ == "__main__":
    model = load_model("models/model.pkl")
    X_test, y_test = load_test_data("data/processed")
    metrics = evaluate_model(model, X_test, y_test)
    print(f"RMSE: {metrics['rmse']:.2f}")
    print(f"R2: {metrics['r2']:.2f}")
    print(f"MAE: {metrics['mae']:.2f}")
