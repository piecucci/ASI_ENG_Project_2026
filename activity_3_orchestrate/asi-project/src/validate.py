"""
Validation Script
-----------------
Loads the trained model and test data, computes R2, and checks
whether it meets the minimum threshold from config.yaml.

Usage: python src/validate.py
"""

import os
import sys

import joblib
import pandas as pd
import yaml
from sklearn.metrics import r2_score


def load_model(filepath: str) -> object:
    """Load a trained model from disk using joblib.

    Args:
        filepath: Path to the saved model file.

    Returns:
        The loaded model object.
    """
    return joblib.load(filepath)


def load_test_data(input_dir: str) -> tuple:
    """Load X_test.csv and y_test.csv from the processed data directory."""
    X_test = pd.read_csv(f"{input_dir}/X_test.csv")
    y_test = pd.read_csv(f"{input_dir}/y_test.csv")
    return X_test, y_test


def validate_model(model, X_test, y_test, min_r2: float = 0.70) -> bool:
    """Validate model performance against a minimum R2 threshold."""
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    if r2 >= min_r2:
        print(f"VALIDATION PASSED (R2={r2:.4f})")
        return True
    else:
        print(f"VALIDATION FAILED (R2={r2:.4f}, threshold={min_r2:.2f})")
        return False


if __name__ == "__main__":
    # Load configuration
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    min_r2 = config["validation"]["min_r2"]

    model = load_model(config["output"]["model_path"])
    X_test, y_test = load_test_data(config["dataset"]["processed_dir"])
    passed = validate_model(model, X_test, y_test, min_r2=min_r2)
    sys.exit(0 if passed else 1)
