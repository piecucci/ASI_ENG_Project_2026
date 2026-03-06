# Activity 3: Orchestrate a Pipeline

## Objective

Add a Makefile for reproducible, one-command execution and externalize all hyperparameters to `config.yaml` so you can change experiments without editing code.

## Context

After Activity 2, you have a containerized pipeline. But the CFO wants more: a single command that runs everything — from data preparation through model validation — and only promotes a model to production if it passes the quality gate.

> *"We need this to run monthly with one command. And don't deploy a bad model."* — Jordan Hayes, CFO

In this activity you will add a Makefile for reproducible, one-command execution, externalize all hyperparameters to `config.yaml`, and implement **validation and promotion gates**. The Makefile becomes a primitive CI/CD pipeline: `make all` chains prepare → train → evaluate → validate → promote. If validation fails, promotion never happens.

## Prerequisites

A working Activity 2 project. If you do not have one, check out the `a2-checkpoint` branch:

```bash
git checkout a2-checkpoint
```

## What You Receive

| Item | Location | Description |
|------|----------|-------------|
| Makefile skeleton | `starter/Makefile` | Pre-defined targets and dependency structure with TODO placeholders |
| Config template | `starter/config.yaml` | YAML configuration with 5 experiment presets in comments |
| Smoke test | `starter/tests/test_prepare.py` | A provided pytest that verifies `prepare.py` output |
| Check script | `check_activity.py` | Automated validator you run before submitting |

## What You Deliver

1. A working `make all` that runs prepare → train → evaluate → validate → promote in sequence.
2. A `config.yaml` with the active experiment configuration (you will modify it multiple times).
3. A passing `make test`.
4. An `experiment_log.csv` with at least one row (produced by your pipeline).
5. Multiple runs logged by modifying `config.yaml` and re-running `make all`.
6. A `models/production_model.pkl` file (promoted only if validation passes).

## Project Structure After This Activity

```
asi-project/
├── pyproject.toml
├── Dockerfile
├── Makefile                # NEW -- pipeline orchestration
├── config.yaml             # NEW -- externalized configuration
├── experiment_log.csv      # NEW -- logged experiment results
├── src/
│   ├── __init__.py
│   ├── prepare.py          # MODIFIED -- reads from config.yaml
│   ├── train.py            # MODIFIED -- reads from config.yaml
│   ├── evaluate.py         # MODIFIED -- reads from config.yaml, appends to log
│   ├── validate.py          # FROM A1 -- reads min_r2 from config.yaml
├── data/
│   ├── raw/iowa_liquor_train.csv
│   └── processed/
├── models/
│   ├── model.pkl
│   └── production_model.pkl   # NEW -- promoted model (only if validation passes)
└── tests/
    └── test_prepare.py     # NEW -- provided smoke test
```

## Step-by-Step Instructions

### Step 1: Copy the Starter Files

Copy the three starter files into your project root:

```bash
# From the activities directory, copy into your asi-project
cp starter/Makefile       /path/to/asi-project/Makefile
cp starter/config.yaml    /path/to/asi-project/config.yaml
mkdir -p /path/to/asi-project/tests
cp starter/tests/test_prepare.py /path/to/asi-project/tests/test_prepare.py
```

Also add `pytest` and `pyyaml` to your dependencies if they are not already present:

```bash
cd /path/to/asi-project
uv add pyyaml pytest
```

### Step 2: Read and Understand the Makefile

Open the `Makefile` and study its structure. Notice:

- **Targets**: `prepare`, `train`, `evaluate`, `validate`, `promote`, `test`, `all`, `clean`.
- **Dependencies**: `train` depends on `prepare`; `evaluate` depends on `train`; `validate` depends on `evaluate`; `promote` depends on `validate`; `all` runs all five in order.
- **TODO markers**: The actual commands are left for you to fill in.

The Makefile is a lightweight pipeline definition. Each target is one step, and the dependency graph ensures correct ordering. When you run `make all`, Make automatically runs `prepare` first, then `train`, then `evaluate`.

**Important**: Makefile commands must be indented with a **tab character**, not spaces. Most editors handle this correctly, but if `make` prints `*** missing separator`, check your indentation.

### Step 3: Fill in the Makefile Commands

Replace each `# TODO` comment with the actual command. For example:

```makefile
prepare:
	uv run python src/prepare.py
```

Do the same for `train`, `evaluate`, `test`, and `clean`. Hints are provided in the skeleton file.

After filling in all commands, test that `make prepare` runs your preparation script:

```bash
make prepare
```

### Step 3b: Add Validate and Promote Targets

The Makefile includes two new targets:

- **`validate`**: Runs `validate.py`, which checks the model's R2 against `config["validation"]["min_r2"]`. If validation fails (exit code 1), Make stops — the `promote` target never runs.
- **`promote`**: Copies `models/model.pkl` to `models/production_model.pkl`. This simple file-based promotion teaches the concept without infrastructure overhead.

Fill in the TODO commands for both targets.

Also update your `validate.py` (from Activity 1) to read the threshold from `config.yaml` instead of hardcoding 0.70:

```python
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

min_r2 = config["validation"]["min_r2"]
```

### Step 4: Modify Your Scripts to Read from config.yaml

This is the key learning step. Currently your scripts have hardcoded values like:

```python
# Hardcoded in A1
test_size = 0.2
random_state = 42
model = LinearRegression()
```

You need to change them to read from `config.yaml` instead. Here is the pattern:

```python
import yaml

# Load configuration
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Use config values instead of hardcoded ones
test_size = config["dataset"]["test_size"]
random_state = config["dataset"]["random_state"]
```

#### Modify `prepare.py`

Read the following values from `config.yaml`:
- `config["dataset"]["raw_path"]` -- path to the raw CSV
- `config["dataset"]["processed_dir"]` -- directory for processed output
- `config["dataset"]["target_column"]` -- the target column name
- `config["dataset"]["test_size"]` -- train/test split ratio
- `config["dataset"]["random_state"]` -- random seed

Replace all hardcoded equivalents in your `prepare.py` with these config lookups.

#### Modify `train.py`

Read the following values from `config.yaml`:
- `config["dataset"]["processed_dir"]` -- where to load splits from
- `config["model"]["type"]` -- which model class to use
- `config["model"]["params"]` -- model hyperparameters
- `config["output"]["model_path"]` -- where to save the trained model

For the model type, use a mapping to dynamically select the sklearn class:

```python
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

MODEL_MAP = {
    "LinearRegression": LinearRegression,
    "RandomForestRegressor": RandomForestRegressor,
    "GradientBoostingRegressor": GradientBoostingRegressor,
}

model_class = MODEL_MAP[config["model"]["type"]]
model_params = config["model"].get("params", {})
model = model_class(**model_params)
```

#### Modify `evaluate.py`

Read the following values from `config.yaml`:
- `config["dataset"]["processed_dir"]` -- where to load test data from
- `config["output"]["model_path"]` -- where to load the model from
- `config["output"]["metrics_log"]` -- path to `experiment_log.csv`
- `config["model"]["type"]` -- for logging which model was used

After computing metrics, append a row to `experiment_log.csv`:

```python
import csv
import os
from datetime import datetime

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
```

### Step 5: Run `make all`

```bash
make all
```

You should see output from each step in order (prepare → train → evaluate → validate → promote), ending with:

```
RMSE: <value>
R2: <value>
MAE: <value>
Validation passed.
Pipeline complete.
```

If any step fails, read the error carefully, fix it, and run `make all` again.

### Step 6: Run `make test`

```bash
make test
```

This runs the provided smoke test (`tests/test_prepare.py`). It checks:
- That processed data files exist (`X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`)
- That feature engineering produced more than 5 columns
- That the target column is not leaked into the feature set

All three tests should pass. Fix any failures before continuing.

### Step 7: Try Different Experiments

Open `config.yaml`. The default configuration uses `LinearRegression`. Now change it to try a different model. The file contains commented-out experiment blocks. Uncomment one and copy its values to the active `model:` section.

For example, to try Random Forest:

```yaml
model:
  type: "RandomForestRegressor"
  params:
    n_estimators: 50
    max_depth: 10
    random_state: 42
```

Then run:

```bash
make clean
make all
```

Note the new RMSE, R2, and MAE values. They will differ from the LinearRegression baseline.

Repeat for at least 3-4 different configurations from the experiment blocks in `config.yaml`. Each run appends a row to `experiment_log.csv`.

### Step 8: Verify Reproducibility

Run `make clean` to delete all generated files, then `make all` to regenerate everything:

```bash
make clean
make all
```

The metrics should be identical to your previous run with the same config. This demonstrates reproducibility: same config + same code + same data = same result.

### Step 9: Run the Check Script

```bash
cd ..
uv run python check_activity.py
```

All checks should show PASS. Fix any failures before submitting.

### Step 10: Record Your Results

Write down:
- The RMSE, R2, and MAE for each experiment configuration you ran.
- Which model had the best R2.
- Which model had the lowest RMSE.

You will need these for the MCQ test.

## Key Concepts

### Why Externalize Configuration?

In Activity 1, changing the model or a hyperparameter meant editing Python code. This has problems:
- You might introduce bugs while editing.
- You cannot easily compare runs -- the code changed between them.
- Another person cannot reproduce your experiment without knowing what you changed.

With `config.yaml`, the code is fixed and the experiment is defined by data (the YAML file). To try a new model, you edit `config.yaml` and re-run. The code never changes. This is the foundation of reproducible ML.

### Makefile as a Pipeline

A Makefile is one of the simplest ways to define a pipeline:
- Each **target** is a pipeline step.
- **Dependencies** define the execution order.
- `make all` runs the full pipeline.
- `make clean` resets everything for a fresh run.

In production, you would use tools like Kedro, Airflow, or Kubeflow for more complex pipelines. But the concept is the same: define steps, define dependencies, run with one command.

### Quality Gates in Pipelines

The `validate` → `promote` pattern is a **quality gate**: a checkpoint that prevents bad models from reaching production. In the Makefile, `promote` depends on `validate`, which depends on `evaluate`. If `validate.py` returns exit code 1, Make halts immediately. The `promote` target never runs, and `models/production_model.pkl` is never created (or updated).

This is the same pattern used in CI/CD systems: a failing test stops deployment. Here, a failing validation stops model promotion.

**Business impact example**: If the model's RMSE is $390 across 500 store-category combinations, the total monthly forecast error is approximately $195,000. A GradientBoosting model with RMSE of $165 reduces this to ~$82,500 — saving $112,500 per month in potential inventory misallocation.

### Reproducibility

A pipeline is reproducible if: `same code + same data + same config = same result`. The Makefile ensures the steps run in order. The config file pins all parameters. The `random_state` pins the randomness. Together, they guarantee anyone can reproduce your experiment.

## Estimated Time

60-90 minutes.

## The "Aha" Moment

"In Activity 1, I hardcoded everything. Now I change `config.yaml` and re-run `make all` -- no code changes needed. I can compare five different models just by editing a YAML file."

## Common Mistakes

1. **Using spaces instead of tabs in the Makefile**: Make requires tab characters for indentation. If you see `*** missing separator`, your editor replaced tabs with spaces. Configure your editor to use tabs for Makefiles.
2. **Forgetting to load `config.yaml` in all three scripts**: All three scripts (`prepare.py`, `train.py`, `evaluate.py`) need to read the config. If one still uses hardcoded values, the pipeline is only partially config-driven.
3. **Not running `make clean` between experiments**: If you change the config but do not clean, old processed data and models may persist. Always run `make clean && make all` for a fresh experiment.
4. **Wrong model class name in config.yaml**: The `type` field must exactly match one of: `LinearRegression`, `RandomForestRegressor`, `GradientBoostingRegressor`. Check spelling carefully.
5. **Missing `pyyaml` dependency**: If you get `ModuleNotFoundError: No module named 'yaml'`, run `uv add pyyaml`.
6. **Running `make` from the wrong directory**: Always run `make` from the project root (where the Makefile is located).

## Hints

- **Read `config.yaml` at the top of each script**: Load it once at the start and use the config dictionary throughout.
- **The `MODEL_MAP` pattern**: Using a dictionary to map string names to classes is a common Python pattern for config-driven code. Study it -- you will see it in production codebases.
- **`csv.DictWriter`**: The `log_experiment()` function uses `csv.DictWriter` with a fixed `fieldnames` list. This ensures every row has the same columns, even if you add new experiments later.
- **`make -n`**: Run `make -n all` to see what commands Make *would* run without actually running them. Useful for debugging your Makefile.
