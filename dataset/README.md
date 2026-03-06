# Dataset: Iowa Liquor Sales (Aggregated)

This directory contains pre-prepared CSV files used across all activities.

## Files

| File | Description | Years |
|------|-------------|-------|
| `iowa_liquor_train.csv` | Training data | 2017--2019 |
| `iowa_liquor_drift_test.csv` | Drift detection data (includes `year_month` column) | 2020--2021 |
| `iowa_liquor_holdout.csv` | Final holdout set | 2022--2023 |

## Column Reference

See [`data_dictionary.md`](data_dictionary.md) for full column descriptions, data types, and known characteristics.

## Quick Start

Each activity's `starter/data/raw/` directory contains the CSV files you need. You do not need to download or prepare any data yourself -- just run `uv sync` inside the starter directory and follow the activity instructions.
