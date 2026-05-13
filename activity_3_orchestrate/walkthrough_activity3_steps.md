# Activity 3: Orchestrate — Step-by-Step Walkthrough

This document shows every file change, command, and calculation needed to complete Activity 3.

---

## Step 1: Copy Starter Files

```bash
cd /path/to/asi-project
cp ../starter/Makefile ./Makefile
cp ../starter/config.yaml ./config.yaml
mkdir -p tests
cp ../starter/tests/test_prepare.py ./tests/test_prepare.py
uv add pyyaml pytest
```

---

## Step 2: Fill In the Makefile

The starter Makefile has `# TODO` placeholders. Replace them:

```diff
 prepare:
-	# TODO: Run the data preparation script
-	# Hint: uv run python src/prepare.py
+	uv run python src/prepare.py

 train: prepare
-	# TODO: Run the training script
-	# Hint: uv run python src/train.py
+	uv run python src/train.py

 evaluate: train
-	# TODO: Run the evaluation script
-	# Hint: uv run python src/evaluate.py
+	uv run python src/evaluate.py

 validate: evaluate
-	# TODO: Run the validation script (quality gate)
-	# Hint: uv run python src/validate.py
+	uv run python src/validate.py

 promote: validate
-	# TODO: Copy the trained model to production
-	# Hint: cp models/model.pkl models/production_model.pkl
+	cp models/model.pkl models/production_model.pkl

 test:
-	# TODO: Run the smoke test
-	# Hint: uv run python -m pytest tests/ -v
+	uv run python -m pytest tests/ -v

 clean:
-	# TODO: Remove processed data, models, and experiment log
-	# Hint: rm -f data/processed/*.csv models/*.pkl experiment_log.csv
+	rm -f data/processed/*.csv models/*.pkl experiment_log.csv
```

**Final Makefile** (`asi-project/Makefile`):

```makefile
.PHONY: all prepare train evaluate validate promote test clean

all: prepare train evaluate validate promote
	@echo "Pipeline complete."

prepare:
	uv run python src/prepare.py

train: prepare
	uv run python src/train.py

evaluate: train
	uv run python src/evaluate.py

validate: evaluate
	uv run python src/validate.py

promote: validate
	cp models/model.pkl models/production_model.pkl

test:
	uv run python -m pytest tests/ -v

clean:
	rm -f data/processed/*.csv models/*.pkl experiment_log.csv
```

> **Key concept**: Each target depends on the previous one. `make all` runs the full chain. If `validate` fails (exit 1), `promote` never runs.

---

## Step 3: Modify `prepare.py` — Read from `config.yaml`

Add YAML loading at the top, replace all hardcoded values with config lookups:

```python
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

df = load_data(config["dataset"]["raw_path"])
# ... feature engineering ...
X_train, X_test, y_train, y_test = split_data(
    df,
    target_col=config["dataset"]["target_column"],
    test_size=config["dataset"]["test_size"],
    random_state=config["dataset"]["random_state"],
)
save_splits(X_train, X_test, y_train, y_test, config["dataset"]["processed_dir"])
```

---

## Step 4: Modify `train.py` — MODEL_MAP Pattern

The key change: use a dictionary to map config strings to sklearn classes.

```python
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

MODEL_MAP = {
    "LinearRegression": LinearRegression,
    "RandomForestRegressor": RandomForestRegressor,
    "GradientBoostingRegressor": GradientBoostingRegressor,
}

# In __main__:
with open("config.yaml") as f:
    config = yaml.safe_load(f)

model_class = MODEL_MAP[config["model"]["type"]]
model_params = config["model"].get("params", {})
model = model_class(**model_params)
model.fit(X_train, y_train)
```

> **Why MODEL_MAP, not eval()?** `eval()` executes arbitrary code — a malicious config string could run `rm -rf /`. MODEL_MAP is a safe whitelist.

---

## Step 5: Modify `evaluate.py` — Append to Experiment Log

Add the `log_experiment()` function using `csv.DictWriter`:

```python
import csv
from datetime import datetime

def log_experiment(config, metrics):
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
```

---

## Step 6: Modify `validate.py` — Read Threshold from Config

```python
with open("config.yaml") as f:
    config = yaml.safe_load(f)

min_r2 = config["validation"]["min_r2"]  # Instead of hardcoded 0.70
```

The script exits with code 0 (pass) or 1 (fail). Make uses this exit code to decide whether `promote` runs.

---

## Step 7: Run the Pipeline

```bash
make all
```

Expected output:
```
Splits saved: X_train=(7411, 18), X_test=(1853, 18)
Model (GradientBoostingRegressor) trained and saved to models/model.pkl
RMSE: 164.52
R2: 0.97
MAE: 101.37
VALIDATION PASSED (R2=0.9703)
cp models/model.pkl models/production_model.pkl
Pipeline complete.
```

---

## Step 8: Run Experiments (5 Configurations)

Edit `config.yaml` model section, then `make clean && make all` each time:

| # | Model | Config | R2 | RMSE | MAE |
|---|-------|--------|----|------|-----|
| 1 | LinearRegression | `params: {}` | ~0.8324 | ~390 | ~246 |
| 2 | RandomForest (small) | `n_estimators: 50, max_depth: 10` | ~0.95 | ~210 | ~120 |
| 3 | RandomForest (large) | `n_estimators: 100, max_depth: 20` | ~0.96 | ~185 | ~108 |
| 4 | GradientBoosting (default) | `n_estimators: 100, lr: 0.1, depth: 5` | **0.9703** | **164.52** | **101.37** |
| 5 | GradientBoosting (tuned) | `n_estimators: 200, lr: 0.05, depth: 8` | ~0.97 | ~160 | ~98 |

All 5 pass the `min_r2=0.70` gate. Best model: **GradientBoosting**.

Each run appends to `experiment_log.csv`:
```csv
timestamp,model_type,params,rmse,r2,mae
2026-04-22T23:16:33,GradientBoostingRegressor,"{'n_estimators': 100, ...}",164.5219,0.9703,101.3720
```

---

## Step 9: Run Tests & Check Script

```bash
make test                    # Runs pytest smoke tests
cd .. && uv run python check_activity.py   # Validates all deliverables
```

All checks should show PASS.

---

## Key Architecture Diagram

```
config.yaml ──→ prepare.py ──→ train.py ──→ evaluate.py ──→ validate.py ──→ promote
                    │              │             │               │              │
              data/processed/  model.pkl  experiment_log.csv  exit 0/1  production_model.pkl
```

The Makefile enforces this chain. If any step fails, the pipeline halts.

---

*Walkthrough for Activity 3 — ASI Engineering 2025/2026*
