"""
train.py - Model training and persistence.

This module handles the second stage of the ML pipeline:
1. Load training splits from disk
2. Train a LinearRegression model
3. Save the trained model to disk
"""

import os

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression


def load_splits(input_dir: str) -> tuple:
    """Load training data splits from CSV files.

    Parameters
    ----------
    input_dir : str
        Directory containing X_train.csv and y_train.csv
        (e.g., "data/processed").

    Returns
    -------
    tuple
        (X_train, y_train)
    """
    # TODO: implement
    pass


def train_model(X_train, y_train) -> object:
    """Train a LinearRegression model on the training data."""
    # TODO: implement
    pass


def save_model(model, filepath: str) -> None:
    """Save the trained model to disk using joblib."""
    # TODO: implement
    pass


if __name__ == "__main__":
    X_train, y_train = load_splits("data/processed")
    model = train_model(X_train, y_train)
    save_model(model, "models/model.pkl")
    print(f"Model trained and saved to models/model.pkl")
