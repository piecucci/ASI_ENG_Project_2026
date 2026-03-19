# Activity 1 Quiz Questions

---

**Question 1**

A 500-cell Jupyter notebook loads data, engineers features, trains a model, and evaluates it. The DevOps team needs to run this pipeline nightly via a cron job. What is the core problem?

- Jupyter notebooks cannot be scheduled — cron only supports `.py` files
- The notebook is too large — Python has a 100-cell limit per file
- Notebooks mix exploration, visualization, and pipeline logic in a single linear flow, making them fragile for automated execution (cell order dependencies, hidden state, manual restarts on failure)
- Cron jobs can only run shell scripts, not Python

---

**Question 2**

A notebook is split into `prepare.py` and `train.py`. In `prepare.py`, a helper function `clean_data()` is defined and called at the bottom of the file. Later, `train.py` does `from prepare import clean_data`. What happens when `train.py` runs?

- The entire `prepare.py` executes (including the data cleaning call at the bottom), then `clean_data` becomes available — the `if __name__ == "__main__"` guard would prevent this
- Only `clean_data()` is imported — nothing else executes
- Python raises an `ImportError` because `.py` files cannot be imported
- `train.py` gets a copy of the function but it runs in `prepare.py`'s memory space

---

**Question 3**

A feature pipeline applies `np.log1p(x)` to the `bottles_sold` column. What is the concrete risk of replacing it with `np.log(x)`?

- `np.log()` is slower than `np.log1p()` for large arrays
- `np.log(0)` produces `-inf`, which propagates through the model as NaN predictions; `np.log1p(0) = log(1) = 0`, which is safe
- `np.log()` only works with integers, not floats
- `np.log()` requires importing a separate library

---

**Question 4**

`prepare.py` saves 4 CSV files. `train.py` loads `X_train.csv` and `y_train.csv`. If you rename the output to `features_train.csv` in `prepare.py` but forget to update `train.py`, what happens?

- Python automatically finds the renamed file by scanning the directory
- The pipeline still works because `uv run` resolves file paths automatically
- `train.py` silently trains on an empty dataset
- `train.py` crashes with `FileNotFoundError` because it still looks for `X_train.csv` — modular scripts communicate through agreed-upon file names, and breaking that contract breaks the pipeline

---

**Question 5**

`evaluate.py` computes RMSE, R2, and MAE, and prints them to stdout. A CI system needs to read the R2 value programmatically to decide whether to proceed. Why is printing alone insufficient?

- `print()` is deprecated in Python 3 for production use
- Stdout is human-readable text that requires fragile string parsing; `evaluate.py` should also save metrics to a structured file (e.g., `metrics.json`) that downstream scripts and CI systems can load reliably
- CI systems cannot capture stdout from Python scripts
- Printing metrics violates the single-responsibility principle

---

**Question 6**

`validate.py` checks `R2 >= min_r2` where `min_r2=0.70`. The model achieves R2=0.8324. What exit code does `validate.py` return?

- Exit code 0 — the model passes because 0.8324 >= 0.70
- Exit code 1 — the model's R2 is not exactly 0.70
- Exit code 83 — validate.py returns the R2 percentage as the exit code
- Exit code 42 — matching the random_state seed

---

**Question 7**

Your pipeline has `prepare.py` → `train.py` → `evaluate.py` → `validate.py`. A colleague suggests merging `train.py` and `evaluate.py` into one script because "training and evaluation always happen together." What is the strongest argument against merging?

- Python files have a maximum line count that would be exceeded
- Separate scripts have separate failure modes — if evaluation crashes, you know the bug is in evaluation, not training; merged scripts make debugging harder and force you to retrain every time you change evaluation logic
- `evaluate.py` uses different Python libraries that are incompatible with `train.py`
- Two scripts run faster in parallel than one combined script

---

**Question 8**

The pipeline uses `sys.exit(0)` for success and `sys.exit(1)` for failure in `validate.py`, rather than simply printing "PASSED" or "FAILED". Why?

- `print()` is deprecated in Python 3 — `sys.exit()` is the modern replacement
- `sys.exit()` is faster than `print()` for large output
- Exit codes are machine-readable signals consumed by shell scripts, CI/CD systems, Make, and Docker; printed text is only human-readable and cannot drive automated decisions
- Exit codes are required by the Python language specification

---

**Question 9**

After modularizing, you realize `prepare.py` takes 5 minutes to run (processing 30K rows). During development, you are iterating on `evaluate.py` to fix a bug. How does the modular structure save time?

- Modular scripts run faster than notebooks because Python optimizes `.py` files
- `evaluate.py` automatically detects that the data has not changed and skips preparation
- You can skip `prepare.py` and `train.py` entirely and run only `evaluate.py`, because intermediate files (`X_test.csv`, `model.pkl`) already exist from the previous run — a monolithic notebook would require re-running everything from the top
- You must still run all four scripts every time — modularity does not help here

---

**Question 10**

A colleague's `prepare.py` works perfectly when run directly (`uv run python src/prepare.py`). But when a test file does `from src.prepare import load_data`, the entire data pipeline runs as a side effect — loading data, engineering features, splitting, and saving files. What is the root cause?

- The main logic (function calls at the bottom of the file) is not protected by `if __name__ == "__main__":` — so importing the module executes all top-level code as a side effect
- Test files cannot import functions from pipeline scripts — they are incompatible
- `pytest` automatically runs all functions in imported modules
- The `from ... import` syntax always executes the entire file — there is no way to prevent it