# Activity 5: Detect Drift and Retrain

## Objective

Monitor your trained model on new "production" data, detect when performance degrades (drift), and retrain the model to recover accuracy.

## Context

It's March 2020. COVID-19 hits Iowa. Bar closures shift sales from on-premise to retail. Bottle sizes change. Volume spikes from stockpiling. Seasonal patterns shatter.

> *"COVID just hit. Our model is wrong. Fix it — and make sure it fixes itself next time."* — Jordan Hayes, CFO

Your model was trained on 2017-2019 data. It learned the purchasing patterns of that era. Now "production" data arrives from 2020-2021, and everything has changed:

- **Bar closures** shifted sales from on-premise (bars, restaurants) to off-premise (retail stores). Category mix changed dramatically.
- **Bottle size shifts** — consumers bought larger bottles for home consumption instead of single servings.
- **Volume spikes** — panic buying and stockpiling distorted the volume-to-sales relationship.
- **Seasonal pattern disruption** — lockdowns flattened the usual holiday spikes and created new peaks around reopening phases.

In this activity, you won't just detect drift and retrain once. You'll implement a **closed-loop monitoring system** that runs monthly:

1. Load the production model
2. Score on the new month's data
3. Check for drift (R2 below threshold)
4. If drift: retrain on expanded data
5. Validate the retrained model
6. **Compare** retrained vs. production on the same data
7. **Promote only if the retrained model wins**
8. Continue monitoring with the (possibly updated) production model

This is the full MLOps loop — detect, retrain, validate, compare, promote (or not), repeat.

## Prerequisite

A working Activity 4 project (with MLflow experiment tracking). If your Activity 4 output is broken or incomplete, use the `a4-checkpoint` branch to start from a known-good state:

```bash
git checkout a4-checkpoint
```

**Important:** Before running drift detection, set your `config.yaml` model type back to `LinearRegression`. Drift detection is designed to reveal the limitations of a simple model on COVID-era data. Advanced models like GradientBoosting may not show measurable drift on this dataset, making the activity uncompletable.

## What You Receive

| Item | Location | Description |
|------|----------|-------------|
| Your A4 project | Project root | Working pipeline with `prepare.py`, `train.py`, `evaluate.py`, and MLflow tracking |
| Drift detection starter | `starter/detect_drift.py` | Script with complete structure and TODO-stub functions |
| Drift test data | `data/raw/iowa_liquor_drift_test.csv` | 2020-2021 data with `year_month` column (e.g., "2020-01", "2020-02", ..., "2021-12") |
| Check script | `check_activity.py` | Automated validator you run before submitting |

## What You Deliver

A completed `src/detect_drift.py` script that:

1. Loads your production model from Activity 4
2. Iterates over each month of 2020-2021 production data (24 months)
3. Evaluates the model on each month
4. Detects drift when R2 drops below a configured threshold
5. When drift is detected: retrains on expanded data, validates the retrained model, **compares it against the current production model**, and **promotes only if the retrained model is better**
6. Produces `drift_report.csv` with columns: `year_month`, `rmse`, `r2`, `mae`, `n_samples`, `drift_detected`, `model_version`, `retrained`, `promoted`, `production_r2`, `candidate_r2`
7. Updates `models/production_model.pkl` when a retrained model is promoted

Run it with:

```bash
uv run python src/detect_drift.py
```

## Pinned Values (Do Not Change)

| Parameter | Value |
|-----------|-------|
| `test_size` | `0.2` |
| `random_state` | `42` |
| Target column | `"total_sales"` |
| Drift R2 threshold | `0.80` (retrain if R2 drops below this) |
| Drift test data path | `"data/raw/iowa_liquor_drift_test.csv"` |
| Report output path | `"drift_report.csv"` |

### Drift Report Schema

| Column | Type | Description |
|--------|------|-------------|
| `year_month` | string | Month identifier (e.g., "2020-04") |
| `rmse` | float | Root Mean Squared Error for this month |
| `r2` | float | R-squared score for this month |
| `mae` | float | Mean Absolute Error for this month |
| `n_samples` | int | Number of samples in this month |
| `drift_detected` | bool | True if R2 < threshold |
| `model_version` | int | Current production model version (starts at 1) |
| `retrained` | bool | True if model was retrained this month |
| `promoted` | bool | True if retrained model replaced production model |
| `production_r2` | float | Production model's R2 on this month's data |
| `candidate_r2` | float | Retrained model's R2 (null if no retrain) |

## Step-by-Step Instructions

### Step 0: Update Your Configuration

Add a `drift` section to your `config.yaml`:

```yaml
drift:
  threshold_r2: 0.80
  test_data_path: "data/raw/iowa_liquor_drift_test.csv"
  report_path: "drift_report.csv"
```

This keeps all magic numbers in configuration, not scattered through your code. The threshold of 0.80 means: if R2 drops below 0.80, the model is no longer useful and must be retrained.

### Step 1: Place the Drift Test Data

Copy `iowa_liquor_drift_test.csv` into your project's `data/raw/` directory. This file contains the same columns as your training data, plus an extra `year_month` column (e.g., "2020-01") that identifies which month each row belongs to.

Verify the file is in place:

```bash
head -1 data/raw/iowa_liquor_drift_test.csv
```

You should see the familiar column headers plus `year_month`.

### Step 2: Copy the Starter Script

Copy `detect_drift.py` from the starter directory into your project's `src/` directory:

```bash
cp <path-to-starter>/detect_drift.py src/detect_drift.py
```

### Step 3: Read and Understand the Starter Script

Open `src/detect_drift.py` and read the entire file before writing any code. Understand the flow:

1. `main()` loads the config, model, drift data, and original training data
2. It iterates over each unique `year_month` in the drift data (sorted chronologically)
3. For each month, it calls `evaluate_on_month()` to get metrics
4. It calls `check_drift()` to compare R2 against the threshold
5. If drift is detected, it retrains on expanded data, validates the candidate, compares it against the production model, and promotes only if the candidate wins
6. All results are logged to a list and saved as `drift_report.csv`

The `main()` function and the overall loop are already complete. Your job is to implement the six TODO functions.

### Step 4: Implement `engineer_features_for_month()`

This function must apply the **exact same** feature engineering as your `prepare.py` -- same category bucketing, same one-hot encoding, same cyclical month features, same log transform, same column drops. If the features do not match, the model's predictions will be meaningless.

**Important**: The drift test data has a `year_month` column that your training data does not. You must drop it before (or during) feature engineering so it does not appear as a feature.

Tips:
- Open your completed `prepare.py` side-by-side and copy the logic from `engineer_features()`.
- After engineering, make sure the resulting columns match `X_train.csv` exactly. If the drift data has categories that were not in the top 10 during training, they should be mapped to "Other" -- just like in training.
- If a dummy column from training is missing (because that category does not appear in this month's data), add it as a column of zeros. If an extra dummy column appears (because a new category is now in the top 10 for this month), drop it. The model expects the same feature set it was trained on.
- One approach: after creating dummies, use `df = df.reindex(columns=expected_columns, fill_value=0)` where `expected_columns` is the list from your saved `X_train.csv`.

### Step 5: Implement `evaluate_on_month()`

This function takes a model, one month of raw data, and the target column name. It should:

1. Call `engineer_features_for_month()` to transform the raw data
2. Separate features (X) from target (y) -- drop the target column from features
3. Generate predictions using the model
4. Calculate RMSE, R2, and MAE using scikit-learn metrics
5. Return a dictionary: `{"rmse": ..., "r2": ..., "mae": ..., "n_samples": len(df_month)}`

### Step 6: Implement `check_drift()`

This is the simplest function. Compare the R2 value in the metrics dictionary against the threshold. Return `True` if R2 is below the threshold (drift detected), `False` otherwise.

```python
def check_drift(metrics: dict, threshold_r2: float) -> bool:
    return metrics["r2"] < threshold_r2
```

Yes, it really is that simple. In production systems, drift detection can be much more sophisticated (statistical tests, sliding windows, multiple metrics), but threshold-based monitoring is the foundation.

### Step 7: Implement `retrain_model()`

When drift is detected, retrain the model on combined data (original training data + drift data up to the current month). This function should:

1. Apply feature engineering to the combined data (use the same logic as `prepare.py`)
2. Separate features and target
3. Train a new model (same type as in Activity 1 -- `LinearRegression`)
4. Optionally save the retrained model to disk
5. Return the newly trained model

The `main()` function passes in the already-combined DataFrame, so you do not need to handle concatenation here.

### Step 8: Implement `validate_retrained_model()`

This new function evaluates a retrained model on the current month's data:

```python
def validate_retrained_model(model, df_month, target_col, expected_columns, min_r2):
    """Evaluate a retrained model on the current month's data.

    Returns a dict with 'r2', 'rmse', 'mae', 'passed' keys.
    """
```

It should:
1. Apply feature engineering to df_month
2. Predict and compute metrics
3. Return a dict including `passed: r2 >= min_r2`

### Step 9: Implement `compare_and_promote()`

```python
def compare_and_promote(production_metrics, candidate_metrics):
    """Compare production vs candidate model. Return True if candidate wins."""
    return candidate_metrics["r2"] > production_metrics["r2"]
```

The retrained model is promoted only if it outperforms the current production model on the same month's data.

### Step 10: Run the Script

```bash
uv run python src/detect_drift.py
```

You should see output like:

```
Monitoring model on 24 months of production data...
Drift threshold: R2 < 0.80
------------------------------------------------------------
  2020-01: R2=0.xx, RMSE=xxxx.xx [OK]
  2020-02: R2=0.xx, RMSE=xxxx.xx [OK]
  ...
  2020-xx: R2=0.xx, RMSE=xxxx.xx [DRIFT DETECTED]

  >>> Retraining triggered at 2020-xx!
  >>> Retrained model R2=0.xxxx (production R2=0.xxxx)
  >>> Candidate promoted! New production model version: 2

  2020-xx: R2=0.xx, RMSE=xxxx.xx [OK]
  ...
  2021-xx: R2=0.xx, RMSE=xxxx.xx [DRIFT DETECTED]

  >>> Retraining triggered at 2021-xx!
  >>> Retrained model R2=0.xxxx (production R2=0.xxxx)
  >>> Candidate NOT promoted (production model is still better). Continuing...

  ...

Drift report saved to drift_report.csv
Drift first detected: 2020-xx
Total retrains: X
Total promotions: X
Final model version: X
```

### Step 11: Examine the Drift Report

Open `drift_report.csv` and look at the data:

```bash
cat drift_report.csv
```

Answer these questions for yourself:
- Which month first triggered drift? Note the exact `year_month` value.
- What was the R2 at that point?
- Did retraining improve performance on subsequent months?
- How does the RMSE trend look before and after retraining?

### Step 12: Run the Check Script

```bash
uv run python check_activity.py
```

All checks should show PASS. Fix any failures before submitting.

### Step 13: Record Your Values for the MCQ Test

Write down:
- The first month where drift was detected
- The R2 value at the drift point
- Whether retraining improved subsequent months' R2 above the threshold

You will need these exact values for the multiple-choice test.

## Key Concepts

### Data Drift vs. Model Drift

- **Data drift** (also called covariate shift): The distribution of input features changes. In our case, COVID changed which categories were purchased, how much volume was sold, and seasonal patterns.
- **Model drift** (also called concept drift): The relationship between features and target changes. Even if someone buys the same volume, the price-per-liter may have changed due to supply chain disruptions.
- In practice, both happen together. The effect you observe is **performance degradation** -- metrics like R2 and RMSE get worse.

### Monitoring Metrics Over Time

Instead of evaluating once on a static test set, you evaluate on each new batch of data (here, monthly). This gives you a time series of performance metrics that reveals trends and sudden drops.

### Threshold-Based Alerting

The simplest monitoring approach: set a threshold (R2 < 0.80) and trigger an alert when metrics cross it. More sophisticated approaches include:
- Statistical tests (e.g., KS test on feature distributions)
- Sliding window comparisons
- Population Stability Index (PSI)
- Multi-metric alerting (combine R2, RMSE, and feature drift scores)

For this activity, threshold-based monitoring is sufficient.

### Retraining Strategies

When drift is detected, you have several options:
1. **Full retrain** on all available data (what we do here)
2. **Sliding window** -- train only on recent data, dropping old data
3. **Online learning** -- update the model incrementally with each new batch
4. **Ensemble** -- combine old and new models

We use option 1 for simplicity. In production, the choice depends on how quickly the data distribution shifts and how much historical data remains relevant.

## Common Mistakes

1. **Feature mismatch**: The drift data must be processed with the exact same feature engineering as the training data. If columns differ (wrong dummy variables, missing features), predictions will be garbage. Always align columns after one-hot encoding.
2. **Forgetting to drop `year_month`**: This column is metadata for the monitoring loop, not a feature. If you feed it to the model, you will get errors or meaningless predictions.
3. **Hardcoding the threshold**: Use `config["drift"]["threshold_r2"]`, not a literal `0.80` in your code. Configuration-driven development means all tunable values live in `config.yaml`.
4. **Not handling missing dummy columns**: If a month's data does not contain all 10+ categories, `pd.get_dummies` will produce fewer columns. You must add the missing columns as zeros.
5. **Not comparing before promoting**: The closed loop requires comparing the retrained model against the production model. Don't automatically promote — only promote if the candidate R2 exceeds the production R2 on the same data.
6. **Wrong column alignment after retraining**: After retraining on combined data, the model may expect a slightly different feature set if new categories appear. Make sure `retrain_model()` produces consistent features.

## Estimated Time

90-120 minutes.

## Hints

- **Start with `check_drift()`** -- it is one line of code. Get the easy win first.
- **Then implement `engineer_features_for_month()`** -- this is the hardest function because it must exactly match your `prepare.py` logic. Copy-paste from your working `prepare.py` and adapt.
- **Load `X_train.csv` at the top of main** to get the expected column list: `expected_columns = pd.read_csv("data/processed/X_train.csv", nrows=0).columns.tolist()`. Pass this to `engineer_features_for_month()` so it can align columns.
- **Use `df.reindex(columns=expected_columns, fill_value=0)`** to ensure the feature DataFrame has the exact columns the model expects, in the correct order, with zeros for any missing categories.
- **Test on a single month first**: Before running the full loop, try calling `evaluate_on_month()` on just the January 2020 data to make sure it works. Print the resulting metrics and sanity-check them.
