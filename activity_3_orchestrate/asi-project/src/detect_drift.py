"""
Drift Detection and Retraining Script (Closed-Loop)
----------------------------------------------------
Evaluates a trained model on monthly "production" data (2020-2021).
Detects performance drift, retrains when needed, validates the retrained
model, compares it against the current production model, and promotes
only if the retrained model is better.

Usage: python src/detect_drift.py
"""

import pandas as pd
import numpy as np
import yaml
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_model(filepath: str) -> object:
    """Load a trained model from disk."""
    return joblib.load(filepath)


def engineer_features_for_month(
    df_month: pd.DataFrame, expected_columns: list
) -> pd.DataFrame:
    """Apply the same feature engineering as prepare.py to a single month's data.

    This must produce the exact same features as the training pipeline.
    Reuse the logic from prepare.py's engineer_features().

    After engineering, the resulting DataFrame is reindexed to match
    expected_columns exactly (adding missing columns as 0, dropping extras).

    Args:
        df_month: Raw data for one month (may include year_month column).
        expected_columns: List of column names the model expects (from X_train).

    Returns:
        DataFrame with engineered features matching expected_columns exactly.
    """
    df = df_month.copy()
    if 'year_month' in df.columns:
        df = df.drop(columns=['year_month'])
    df = df.dropna()
    
    cat_cols_in_expected = [c for c in expected_columns if c.startswith("cat_") and c != "cat_Other"]
    top_cats = [c.replace("cat_", "") for c in cat_cols_in_expected]
    
    df['category_name'] = df['category_name'].apply(lambda x: x if x in top_cats else 'Other')
    cat_dummies = pd.get_dummies(df['category_name'], prefix='cat', dtype=int)
    df = pd.concat([df, cat_dummies], axis=1)
    
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['log_volume'] = np.log1p(df['total_volume_liters'])
    
    df_features = df.reindex(columns=expected_columns, fill_value=0)
    return df_features


def evaluate_on_month(
    model: object,
    df_month: pd.DataFrame,
    target_col: str,
    expected_columns: list,
) -> dict:
    """Evaluate the model on one month of data.

    Args:
        model: Trained sklearn model.
        df_month: Raw data for one month.
        target_col: Name of the target column.
        expected_columns: List of feature column names the model expects.

    Returns:
        dict with keys: 'rmse', 'r2', 'mae', 'n_samples'
    """
    df_clean = df_month.dropna()
    y = df_clean[target_col]
    X = engineer_features_for_month(df_clean, expected_columns)
    
    y_pred = model.predict(X)
    
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    
    return {
        "rmse": rmse,
        "r2": r2,
        "mae": mae,
        "n_samples": len(df_clean)
    }


def check_drift(metrics: dict, threshold_r2: float) -> bool:
    """Check if model performance has drifted below acceptable threshold.

    Args:
        metrics: dict with 'r2' key.
        threshold_r2: minimum acceptable R2 score.

    Returns:
        True if drift detected (R2 < threshold), False otherwise.
    """
    return metrics["r2"] < threshold_r2


def retrain_model(
    df_combined: pd.DataFrame, target_col: str, config: dict
) -> object:
    """Retrain model on combined original + new data.

    Args:
        df_combined: Combined training data (original + new data up to drift point).
        target_col: Name of the target column.
        config: Configuration dict with model type and params.

    Returns:
        Newly trained model.
    """
    expected_columns = pd.read_csv(
        config["dataset"]["processed_dir"] + "/X_train.csv", nrows=0
    ).columns.tolist()
    
    cat_cols_in_expected = [c for c in expected_columns if c.startswith("cat_") and c != "cat_Other"]
    top_cats = [c.replace("cat_", "") for c in cat_cols_in_expected]
    
    df = df_combined.copy()
    if 'year_month' in df.columns:
        df = df.drop(columns=['year_month'])
    df = df.dropna()
    
    df['category_name'] = df['category_name'].apply(lambda x: x if x in top_cats else 'Other')
    cat_dummies = pd.get_dummies(df['category_name'], prefix='cat', dtype=int)
    df = pd.concat([df, cat_dummies], axis=1)
    
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['log_volume'] = np.log1p(df['total_volume_liters'])
    
    X = df.reindex(columns=expected_columns, fill_value=0)
    y = df[target_col]
    
    model = LinearRegression()
    model.fit(X, y)
    return model


def validate_retrained_model(
    model: object,
    df_month: pd.DataFrame,
    target_col: str,
    expected_columns: list,
    min_r2: float,
) -> dict:
    """Evaluate a retrained model on the current month's data.

    Args:
        model: Retrained sklearn model.
        df_month: Raw data for the current month.
        target_col: Name of the target column.
        expected_columns: List of feature column names the model expects.
        min_r2: Minimum acceptable R2 score.

    Returns:
        dict with keys: 'r2', 'rmse', 'mae', 'passed' (bool: r2 >= min_r2)
    """
    metrics = evaluate_on_month(model, df_month, target_col, expected_columns)
    metrics["passed"] = metrics["r2"] >= min_r2
    return metrics


def compare_and_promote(production_metrics: dict, candidate_metrics: dict) -> bool:
    """Compare production model vs candidate (retrained) model.

    Args:
        production_metrics: dict with 'r2' key from production model evaluation.
        candidate_metrics: dict with 'r2' key from candidate model evaluation.

    Returns:
        True if candidate R2 > production R2 (candidate should be promoted).
    """
    return candidate_metrics["r2"] > production_metrics["r2"]


def main():
    """Main closed-loop drift detection and retraining."""
    config = load_config()

    # Load the production model from Activity 4
    model = load_model(config["output"]["model_path"])

    # Load drift test data
    drift_data = pd.read_csv(config["drift"]["test_data_path"])

    # Load original training data (for potential retraining)
    train_data = pd.read_csv(config["dataset"]["raw_path"])

    # Load expected feature columns from saved training data
    expected_columns = pd.read_csv(
        config["dataset"]["processed_dir"] + "/X_train.csv", nrows=0
    ).columns.tolist()

    # Get unique months, sorted
    months = sorted(drift_data["year_month"].unique())

    # Prepare drift report
    report_rows = []
    model_version = 1

    # Drift threshold from config
    threshold_r2 = config["drift"]["threshold_r2"]
    min_r2 = config.get("validation", {}).get("min_r2", 0.70)

    print(f"Monitoring model on {len(months)} months of production data...")
    print(f"Drift threshold: R2 < {threshold_r2}")
    print("-" * 60)

    for month in months:
        df_month = drift_data[drift_data["year_month"] == month].copy()

        # Evaluate production model on this month
        metrics = evaluate_on_month(
            model, df_month, config["dataset"]["target_column"], expected_columns
        )

        # Check for drift
        drift_detected = check_drift(metrics, threshold_r2)

        # Default values for this row
        retrained = False
        promoted = False
        production_r2 = round(metrics["r2"], 4)
        candidate_r2 = None

        status = "DRIFT DETECTED" if drift_detected else "OK"
        print(
            f"  {month}: R2={metrics['r2']:.2f}, RMSE={metrics['rmse']:.2f} [{status}]"
        )

        # If drift detected, attempt retrain → validate → compare → promote
        if drift_detected:
            print(f"\n  >>> Retraining triggered at {month}!")

            # Combine original data + all drift data up to this month
            past_drift = drift_data[drift_data["year_month"] <= month]
            combined = pd.concat(
                [train_data, past_drift.drop(columns=["year_month"])],
                ignore_index=True,
            )

            candidate_model = retrain_model(
                combined, config["dataset"]["target_column"], config
            )
            retrained = True

            # Validate retrained model on this month's data
            candidate_result = validate_retrained_model(
                candidate_model, df_month, config["dataset"]["target_column"],
                expected_columns, min_r2,
            )
            candidate_r2 = round(candidate_result["r2"], 4)

            print(
                f"  >>> Retrained model R2={candidate_r2:.4f} "
                f"(production R2={production_r2:.4f})"
            )

            # Compare and potentially promote
            if compare_and_promote(metrics, candidate_result):
                model = candidate_model
                model_version += 1
                promoted = True

                # Save promoted model
                joblib.dump(model, "models/production_model.pkl")

                print(
                    f"  >>> Candidate promoted! New production model version: "
                    f"{model_version}\n"
                )
            else:
                print(
                    f"  >>> Candidate NOT promoted (production model is "
                    f"still better). Continuing...\n"
                )

        # Log to report
        report_rows.append(
            {
                "year_month": month,
                "rmse": round(metrics["rmse"], 2),
                "r2": round(metrics["r2"], 2),
                "mae": round(metrics["mae"], 2),
                "n_samples": metrics["n_samples"],
                "drift_detected": drift_detected,
                "model_version": model_version,
                "retrained": retrained,
                "promoted": promoted,
                "production_r2": production_r2,
                "candidate_r2": candidate_r2 if candidate_r2 is not None else "",
            }
        )

    # Save drift report
    report_path = config["drift"]["report_path"]
    report_df = pd.DataFrame(report_rows)
    report_df.to_csv(report_path, index=False)
    print(f"\nDrift report saved to {report_path}")

    # Summary
    drift_months = report_df[report_df["drift_detected"]]
    retrain_count = report_df[report_df["retrained"]].shape[0]
    promote_count = report_df[report_df["promoted"]].shape[0]

    if len(drift_months) > 0:
        print(f"Drift first detected: {drift_months['year_month'].iloc[0]}")
    else:
        print("Drift first detected: Never")
    print(f"Total retrains: {retrain_count}")
    print(f"Total promotions: {promote_count}")
    print(f"Final model version: {model_version}")


if __name__ == "__main__":
    main()
