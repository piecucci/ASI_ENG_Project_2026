"""
train.py - Model training and persistence.

This module handles the second stage of the ML pipeline:
1. Load training splits from disk
2. Train the configured model
3. Save the trained model to disk
"""

import os

import joblib
import pandas as pd
import yaml
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor


MODEL_MAP = {
    "LinearRegression": LinearRegression,
    "RandomForestRegressor": RandomForestRegressor,
    "GradientBoostingRegressor": GradientBoostingRegressor,
}


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
    X_train = pd.read_csv(f"{input_dir}/X_train.csv")
    y_train = pd.read_csv(f"{input_dir}/y_train.csv")
    return X_train, y_train


def train_model(X_train, y_train, model_type: str, model_params: dict) -> object:
    """Train a model on the training data using config-driven model selection."""
    model_class = MODEL_MAP[model_type]
    model = model_class(**model_params)
    model.fit(X_train, y_train)
    return model


def save_model(model, filepath: str) -> None:
    """Save the trained model to disk using joblib."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)


if __name__ == "__main__":
    # Load configuration
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    X_train, y_train = load_splits(config["dataset"]["processed_dir"])
    model = train_model(
        X_train,
        y_train,
        model_type=config["model"]["type"],
        model_params=config["model"].get("params", {}),
    )
    save_model(model, config["output"]["model_path"])
    print(f"Model ({config['model']['type']}) trained and saved to {config['output']['model_path']}")
