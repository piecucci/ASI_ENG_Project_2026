"""
Validation Script
-----------------
Loads the trained model and test data, computes R2, and checks
whether it meets the minimum threshold.

Usage: python src/validate.py
"""

import os
import sys

import joblib
import pandas as pd
from sklearn.metrics import r2_score


def load_model(filepath: str) -> object:
    """Load a trained model from disk using joblib.

    Args:
        filepath: Path to the saved model file.

    Returns:
        The loaded model object.
    """
    # TODO: implement
    pass


def load_test_data(input_dir: str) -> tuple:
    """Load X_test.csv and y_test.csv from the processed data directory."""
    # TODO: implement
    pass


def validate_model(model, X_test, y_test, min_r2: float = 0.70) -> bool:
    """Validate model performance against a minimum R2 threshold."""
    # TODO: implement
    pass


if __name__ == "__main__":
    model = load_model("models/model.pkl")
    X_test, y_test = load_test_data("data/processed")
    passed = validate_model(model, X_test, y_test, min_r2=0.70)
    sys.exit(0 if passed else 1)
