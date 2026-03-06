"""
prepare.py - Data loading, feature engineering, and train/test splitting.

This module handles the first stage of the ML pipeline:
1. Load raw CSV data
2. Engineer features (category encoding, cyclical time features, log transforms)
3. Split into train/test sets
4. Save splits to disk
"""

import os

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def load_data(filepath: str) -> pd.DataFrame:
    """Load raw CSV data into a DataFrame.

    Parameters
    ----------
    filepath : str
        Path to the raw CSV file (e.g., "data/raw/iowa_liquor_train.csv").

    Returns
    -------
    pd.DataFrame
        The loaded dataset.
    """
    # TODO: implement
    pass


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply feature engineering transformations."""
    # TODO: implement
    pass


def split_data(
    df: pd.DataFrame,
    target_col: str,
    test_size: float,
    random_state: int,
) -> tuple:
    """Split the dataset into train and test sets."""
    # TODO: implement
    pass


def save_splits(
    X_train,
    X_test,
    y_train,
    y_test,
    output_dir: str,
) -> None:
    """Save train/test splits to CSV files."""
    # TODO: implement
    pass


if __name__ == "__main__":
    df = load_data("data/raw/iowa_liquor_train.csv")
    df = engineer_features(df)
    X_train, X_test, y_train, y_test = split_data(
        df,
        target_col="total_sales",
        test_size=0.2,
        random_state=42,
    )
    save_splits(X_train, X_test, y_train, y_test, "data/processed")
    print(f"Splits saved: X_train={X_train.shape}, X_test={X_test.shape}")
