# Activity 1: Modularize a Notebook

## Objective

Transform a messy, monolithic Jupyter notebook into a clean, modular Python pipeline composed of four standalone scripts: `prepare.py`, `train.py`, `evaluate.py`, and `validate.py`.

## Context

You work as a junior ML engineer at **Hawkeye Spirits**, an Iowa liquor distributor. The company's data scientist has built a working Jupyter notebook that predicts **total sales** (`total_sales`) for store-month-category combinations using Iowa Liquor Sales data (~30,000 rows). The CFO, Jordan Hayes, wants this model running in production — but a notebook won't cut it.

> *"Our data scientist built a model in a notebook. It works on her laptop. Make it production-ready."* — Jordan Hayes, CFO

Your job is to refactor the notebook into production-quality modular code that can later be containerized, orchestrated, and monitored. You'll also add a **validation gate** — a script that checks whether the model meets a minimum quality threshold before it can be considered for deployment.

See the [Hawkeye Spirits brief](../hawkeye_spirits_brief.md) for full business context and the [data dictionary](../dataset/data_dictionary.md) for column documentation.

## What You Receive

| Item | Location | Description |
|------|----------|-------------|
| Messy notebook | `notebook/exploration.ipynb` | A working but disorganized notebook with all logic in one place |
| Raw dataset | `starter/data/raw/iowa_liquor_train.csv` | Curated Iowa Liquor Sales data (~30K rows). See `../dataset/data_dictionary.md` for column documentation |
| Starter skeleton | `starter/` | Project structure with TODO-stub files in `src/` |
| Check script | `check_activity.py` | Automated validator you run before submitting |

## What You Deliver

A working pipeline that executes successfully as four sequential commands:

```bash
cd starter
uv run python src/prepare.py
uv run python src/train.py
uv run python src/evaluate.py
uv run python src/validate.py
```

The pipeline produces:
- `data/processed/X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`
- `models/model.pkl`
- `evaluate.py` prints RMSE, R2, and MAE to stdout
- `validate.py` prints VALIDATION PASSED or VALIDATION FAILED and exits with code 0 (pass) or 1 (fail)

## Pinned Values (Do Not Change)

These values are **hardcoded** and must not be modified. They ensure all students produce identical, testable results.

| Parameter | Value |
|-----------|-------|
| `test_size` | `0.2` |
| `random_state` | `42` |
| Model | `sklearn.linear_model.LinearRegression` |
| Target column | `"total_sales"` |
| Raw data path | `"data/raw/iowa_liquor_train.csv"` |
| Processed data dir | `"data/processed"` |
| Model path | `"models/model.pkl"` |
| `min_r2` | `0.70` |

## Step-by-Step Instructions

### Step 1: Set Up Your Environment

Navigate to the `starter/` directory and initialize the project with `uv`:

```bash
cd starter
uv sync
```

This installs all dependencies listed in `pyproject.toml` into a local virtual environment.

### Step 2: Examine the Messy Notebook

Open `notebook/exploration.ipynb` and read through it carefully. Identify:
- How the data is loaded
- What feature engineering steps are applied
- Which model is trained
- How the model is evaluated

Take notes on the logic -- you will need to reorganize it into functions.

### Step 3: Read the TODO-Stub Files

Open each file in `src/`:
- `src/prepare.py` -- data loading, feature engineering, splitting, saving
- `src/train.py` -- loading splits, training model, saving model
- `src/evaluate.py` -- loading model, loading test data, computing metrics

Each file has function signatures, docstrings, and `# TODO: implement` markers. The `if __name__ == "__main__"` blocks are already written for you.

### Step 4: Implement `prepare.py`

Fill in the four functions:

1. **`load_data(filepath: str) -> pd.DataFrame`**: Read the CSV file into a DataFrame and return it.

2. **`engineer_features(df: pd.DataFrame) -> pd.DataFrame`**: Apply the following transformations:
   - Identify the top 10 most frequent values in `category_name`. Replace all others with `"Other"`.
   - Create one-hot dummy columns for `category_name` (use `pd.get_dummies` with `prefix="cat"`).
   - Use the existing `month` column (integer 1–12) to create `month_sin` and `month_cos` columns for cyclical encoding: `sin(2 * pi * month / 12)` and `cos(2 * pi * month / 12)`.
   - Log-transform `total_volume_liters` into a new column `log_volume` using `np.log1p`.
   - Drop non-numeric and original columns that are no longer needed. Keep only numeric features and the target (`total_sales`).

3. **`split_data(df, target_col, test_size, random_state) -> tuple`**: Separate features (X) from target (y), then use `train_test_split` to split. Return `(X_train, X_test, y_train, y_test)`.

4. **`save_splits(X_train, X_test, y_train, y_test, output_dir) -> None`**: Create the output directory if it does not exist. Save each DataFrame/Series as a CSV file (`X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`) with `index=False`.

### Step 5: Implement `train.py`

Fill in the three functions:

1. **`load_splits(input_dir: str) -> tuple`**: Load `X_train.csv` and `y_train.csv` from the directory. Return `(X_train, y_train)`.

2. **`train_model(X_train, y_train) -> object`**: Create a `LinearRegression` model, fit it on the training data, and return the fitted model.

3. **`save_model(model, filepath: str) -> None`**: Save the model to disk using `joblib.dump`. Create parent directories if they do not exist.

### Step 6: Implement `evaluate.py`

Fill in the three functions:

1. **`load_model(filepath: str) -> object`**: Load and return the model from disk using `joblib.load`.

2. **`load_test_data(input_dir: str) -> tuple`**: Load `X_test.csv` and `y_test.csv` from the directory. Return `(X_test, y_test)`.

3. **`evaluate_model(model, X_test, y_test) -> dict`**: Generate predictions, then compute and return a dictionary with keys `"rmse"`, `"r2"`, and `"mae"` using `sklearn.metrics`.

### Step 7: Implement `validate.py`

Fill in the three functions:

1. **`load_model(filepath: str) -> object`**: Load and return the model from disk using `joblib.load`.

2. **`load_test_data(input_dir: str) -> tuple`**: Load `X_test.csv` and `y_test.csv` from the directory. Return `(X_test, y_test)`.

3. **`validate_model(model, X_test, y_test, min_r2: float = 0.70) -> bool`**: Generate predictions, compute R2, print `VALIDATION PASSED (R2=X.XXXX)` or `VALIDATION FAILED (R2=X.XXXX, threshold=Y.YY)`, and return True/False.

The `__main__` block is pre-written: it loads the model and test data, runs validation with `min_r2=0.70`, and exits with code 0 (pass) or 1 (fail).

### Step 8: Run the Full Pipeline

```bash
uv run python src/prepare.py
uv run python src/train.py
uv run python src/evaluate.py
uv run python src/validate.py
```

You should see output like:
```
RMSE: <value>
R2: <value>
MAE: <value>
VALIDATION PASSED (R2=<value>)
```

### Step 9: Run the Check Script

```bash
cd ..
uv run python check_activity.py
```

All checks should show PASS. Fix any failures before submitting.

### Step 10: Record Your Metric Values

Write down the exact RMSE, R2, and MAE values printed by `evaluate.py`. You will need these for the MCQ test.

## Estimated Time

90-120 minutes.

## Hints

- **Use the notebook as reference** for the logic (data transformations, model choice, metric computation), but reorganize everything into the function signatures provided.
- **`pd.get_dummies`** returns a DataFrame. Make sure you drop the original `category_name` column after creating dummies. In pandas 2.x, `get_dummies` returns boolean columns by default — these are excluded by `select_dtypes(include=[np.number])`. Use `pd.get_dummies(..., dtype=int)` to produce numeric dummy columns.
- **`np.log1p(x)`** computes `log(1 + x)`, which safely handles zero values.
- **Cyclical encoding** of months ensures that December (12) and January (1) are treated as close together. The formulas are: `month_sin = sin(2 * pi * month / 12)` and `month_cos = cos(2 * pi * month / 12)`.
- **`os.makedirs(path, exist_ok=True)`** creates directories without failing if they already exist.

## Common Mistakes

1. **Forgetting `if __name__ == "__main__"`**: Without this guard, importing a module will execute its main block. The stubs already include it -- do not remove it.
2. **Wrong import paths**: Run scripts from the `starter/` directory (not from `src/`). Paths like `"data/raw/..."` are relative to the working directory.
3. **Not saving CSVs with `index=False`**: If you save with the index, loading will create an extra `Unnamed: 0` column that breaks downstream steps.
4. **Forgetting to drop non-numeric columns**: After feature engineering, your DataFrame should contain only numeric columns. Use `df.select_dtypes(include=[np.number])` or explicitly drop string columns.
5. **Using `np.log` instead of `np.log1p`**: `np.log(0)` produces `-inf`. Always use `np.log1p` for safety.
6. **Not creating output directories**: `save_splits` and `save_model` must create their output directories if they do not exist.
