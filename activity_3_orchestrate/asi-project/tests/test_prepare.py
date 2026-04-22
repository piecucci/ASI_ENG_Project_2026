"""Smoke test for the data preparation step.
Run with: uv run python -m pytest tests/test_prepare.py -v
"""
import os
import pandas as pd


def test_processed_data_exists():
    """Check that prepare.py produced the expected output files."""
    processed_dir = "data/processed"
    expected_files = ["X_train.csv", "X_test.csv", "y_train.csv", "y_test.csv"]
    for fname in expected_files:
        path = os.path.join(processed_dir, fname)
        assert os.path.exists(path), f"Missing: {path}. Did you run 'make prepare'?"


def test_feature_count():
    """Check that feature engineering produced the expected number of columns."""
    X_train = pd.read_csv("data/processed/X_train.csv")
    # After feature engineering: numeric features + category dummies + month_sin + month_cos
    assert X_train.shape[1] > 5, (
        f"Expected >5 features, got {X_train.shape[1]}. Check engineer_features()."
    )


def test_no_target_leakage():
    """Check that the target column is not in the feature set."""
    X_train = pd.read_csv("data/processed/X_train.csv")
    assert "total_sales" not in X_train.columns, (
        "Target 'total_sales' found in features -- data leakage!"
    )
