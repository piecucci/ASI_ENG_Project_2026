"""
evaluate.py - Model evaluation and metric computation.

This module handles the third stage of the ML pipeline:
1. Load the trained model from disk
2. Load test data splits
3. Compute evaluation metrics (RMSE, R2, MAE)
4. Append results to experiment_log.csv
"""

import csv
import os
from datetime import datetime

import joblib
import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error


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
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    return {"rmse": rmse, "r2": r2, "mae": mae}


def log_experiment(config, metrics):
    """Append one row to the experiment log CSV."""
    log_path = config["output"]["metrics_log"]
    file_exists = os.path.exists(log_path)

    fieldnames = ["timestamp", "model_type", "params", "rmse", "r2", "mae"]

    with open(log_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "model_type": config["model"]["type"],
            "params": str(config["model"].get("params", {})),
            "rmse": f"{metrics['rmse']:.4f}",
            "r2": f"{metrics['r2']:.4f}",
            "mae": f"{metrics['mae']:.4f}",
        })


if __name__ == "__main__":
    # Load configuration
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    model = load_model(config["output"]["model_path"])
    X_test, y_test = load_test_data(config["dataset"]["processed_dir"])
    metrics = evaluate_model(model, X_test, y_test)

    print(f"RMSE: {metrics['rmse']:.2f}")
    print(f"R2: {metrics['r2']:.2f}")
    print(f"MAE: {metrics['mae']:.2f}")

    log_experiment(config, metrics)
    print(f"Results logged to {config['output']['metrics_log']}")
