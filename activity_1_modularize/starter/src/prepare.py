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
    return pd.read_csv(filepath)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply feature engineering transformations."""
    df = df.dropna()
    
    # Top 10 categories: replace others with "Other"
    top_cats = df['category_name'].value_counts().head(10).index.tolist()
    df['category_name'] = df['category_name'].apply(lambda x: x if x in top_cats else 'Other')
    
    # One-hot encode category_name with dtype=int
    cat_dummies = pd.get_dummies(df['category_name'], prefix='cat', dtype=int)
    df = pd.concat([df, cat_dummies], axis=1)
    
    # Cyclical encoding for month
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # Log transform volume
    df['log_volume'] = np.log1p(df['total_volume_liters'])
    
    # Keep only numeric columns and target
    feature_cols = ['num_transactions', 'total_bottles', 'total_volume_liters',
                    'avg_bottle_price', 'month_sin', 'month_cos', 'log_volume']
    cat_cols = [c for c in df.columns if c.startswith('cat_')]
    feature_cols = feature_cols + cat_cols + ['total_sales']
    
    return df[feature_cols]


def split_data(
    df: pd.DataFrame,
    target_col: str,
    test_size: float,
    random_state: int,
) -> tuple:
    """Split the dataset into train and test sets."""
    X = df.drop(columns=[target_col])
    y = df[target_col]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def save_splits(
    X_train,
    X_test,
    y_train,
    y_test,
    output_dir: str,
) -> None:
    """Save train/test splits to CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    X_train.to_csv(f"{output_dir}/X_train.csv", index=False)
    X_test.to_csv(f"{output_dir}/X_test.csv", index=False)
    y_train.to_csv(f"{output_dir}/y_train.csv", index=False)
    y_test.to_csv(f"{output_dir}/y_test.csv", index=False)


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
