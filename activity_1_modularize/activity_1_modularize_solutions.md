# Activity 1 Quiz Solutions

---

## Question 1

**Answer: Notebooks mix exploration, visualization, and pipeline logic in a single linear flow, making them fragile for automated execution (cell order dependencies, hidden state, manual restarts on failure)**

**Justification:** Jupyter notebooks are designed for interactive exploration, not automated production pipelines. They have hidden state (cells can be run in any order), cell dependencies, and require manual intervention when failures occur. While cron technically can run notebooks via `jupyter nbconvert`, the core problem is that notebooks are fundamentally not built for robust, automated, scheduled execution — they require human oversight.

---

## Question 2

**Answer: The entire `prepare.py` executes (including the data cleaning call at the bottom), then `clean_data` becomes available — the `if __name__ == "__main__"` guard would prevent this**

**Justification:** Without the `if __name__ == "__main__":` guard, any code at the top level of `prepare.py` (including function calls at the bottom) runs when the file is imported. This is exactly what happened in Activity 1 — we used the guard in all our scripts. The correct pattern is:

```python
def clean_data():
    ...

if __name__ == "__main__":
    clean_data()  # Only runs when executed directly
```

---

## Question 3

**Answer: `np.log(0)` produces `-inf`, which propagates through the model as NaN predictions; `np.log1p(0) = log(1) = 0`, which is safe**

**Justification:** This was explicitly mentioned in the Activity 1 instructions as a common mistake to avoid. The `np.log1p()` function computes `log(1 + x)`, which safely handles zero values (`log(1) = 0`). Using `np.log()` directly would cause `-inf` for any zero values in the data, which then propagates through the model as NaN predictions, breaking the entire pipeline.

---

## Question 4

**Answer: `train.py` crashes with `FileNotFoundError` because it still looks for `X_train.csv` — modular scripts communicate through agreed-upon file names, and breaking that contract breaks the pipeline**

**Justification:** This is the core lesson of modular pipelines. Scripts communicate through fixed interfaces (file names, function signatures). When `prepare.py` changes output file names without updating `train.py`, the contract is broken. This is not handled automatically — Python will raise a `FileNotFoundError`. This is why the Activity 1 pinned values are so important.

---

## Question 5

**Answer: Stdout is human-readable text that requires fragile string parsing; `evaluate.py` should also save metrics to a structured file (e.g., `metrics.json`) that downstream scripts and CI systems can load reliably**

**Justification:** While printing to stdout works for human inspection, CI systems need machine-readable data. Parsing "RMSE: 390.82" from stdout is fragile (string matching, edge cases). A better approach is saving metrics to a structured format like JSON that can be reliably loaded by downstream scripts. This follows the same principle as using `sys.exit()` codes for automation.

---

## Question 6

**Answer: Exit code 0 — the model passes because 0.8324 >= 0.70**

**Justification:** Looking at our `validate.py` implementation:
- When R2 >= min_r2 (0.70), it prints "VALIDATION PASSED" and returns `True`
- The `__main__` block uses `sys.exit(0 if passed else 1)`
- Since 0.8324 >= 0.70, validation passes and exits with code 0

This was confirmed when we ran the pipeline — it printed "VALIDATION PASSED (R2=0.8324)" with exit code 0.

---

## Question 7

**Answer: Separate scripts have separate failure modes — if evaluation crashes, you know the bug is in evaluation, not training; merged scripts make debugging harder and force you to retrain every time you change evaluation logic**

**Justification:** This is a key benefit of modularity we observed in Activity 1. With separate scripts:
1. If `evaluate.py` fails, you know the bug is in evaluation, not training
2. You can modify evaluation logic without retraining the model
3. Each script can be tested independently
4. Intermediate outputs (X_test.csv, model.pkl) can be reused

Merging them would force re-training every time you want to tweak evaluation, which was exactly the scenario described in Question 9.

---

## Question 8

**Answer: Exit codes are machine-readable signals consumed by shell scripts, CI/CD systems, Make, and Docker; printed text is only human-readable and cannot drive automated decisions**

**Justification:** This was demonstrated in Activity 1's `validate.py`:
```python
if __name__ == "__main__":
    ...
    sys.exit(0 if passed else 1)
```

Exit codes (0 for success, 1 for failure) are consumed by:
- Shell scripts: `if ./validate.py; then ...`
- CI/CD: to determine if a pipeline should continue
- Make: to check if a step succeeded
- Docker: to determine container success/failure

Printed text cannot drive these automated decisions.

---

## Question 9

**Answer: You can skip `prepare.py` and `train.py` entirely and run only `evaluate.py`, because intermediate files (`X_test.csv`, `model.pkl`) already exist from the previous run — a monolithic notebook would require re-running everything from the top**

**Justification:** This is one of the key benefits of modular pipelines that we experienced. Since:
- `prepare.py` outputs are saved to `data/processed/`
- `train.py` outputs are saved to `models/model.pkl`

We can iterate on `evaluate.py` or `validate.py` without re-running the slow preparation step. In a monolithic notebook, changing evaluation logic would require re-running the entire notebook from the beginning.

---

## Question 10

**Answer: The main logic (function calls at the bottom of the file) is not protected by `if __name__ == "__main__":` — so importing the module executes all top-level code as a side effect**

**Justification:** This is exactly what the `if __name__ == "__main__":` guard prevents. Our Activity 1 scripts all use this pattern:

```python
if __name__ == "__main__":
    df = load_data("data/raw/iowa_liquor_train.csv")
    df = engineer_features(df)
    ...
```

Without this guard, importing the module runs all top-level code, causing the entire pipeline to execute as a side effect.