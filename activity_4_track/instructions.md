# Activity 4: Track Experiments

## Objective

Add MLflow tracking to your pipeline so you can log, compare, and visualize experiments systematically. After this activity, you will have 5-6 logged runs viewable in a local MLflow dashboard.

## Context

The CFO is sold on the pipeline — but now the data scientist wants to explore. She has six model configurations she wants to try, and she needs to know which one gives the best predictions.

> *"The data scientist wants to try 6 different configurations. Track them all and pick the winner."* — Jordan Hayes, CFO

After Activity 3, you have a config-driven pipeline: edit `config.yaml`, run `make all`, see results. But a flat CSV log is hard to compare across runs. In this activity you will integrate MLflow, the industry-standard experiment tracking tool, to automatically log every run with its parameters, metrics, and artifacts. Then you will compare all experiments and **promote the best model to production**.

MLflow runs **entirely locally** in this activity. All data is stored in a `./mlruns/` directory on your filesystem. No accounts, no API keys, no internet connection required. When you run `mlflow ui`, it starts a local web server at `http://localhost:5000` that reads from `./mlruns/`.

## Prerequisites

A working Activity 3 project. If you do not have one, check out the `a3-checkpoint` branch:

```bash
git checkout a3-checkpoint
```

## What You Receive

| Item | Location | Description |
|------|----------|-------------|
| MLflow snippet | `starter/mlflow_snippet.py` | A complete, copy-pasteable integration example |
| Check script | `check_activity.py` | Automated validator you run before submitting |

## What You Deliver

1. MLflow integrated into your pipeline (specifically `train.py` and/or `evaluate.py`).
2. At least **5** MLflow runs logged (one per experiment in the matrix below), each with a different model/hyperparameter configuration.
3. Each run has logged parameters (`model_type`, hyperparameters) and metrics (`rmse`, `r2`, `mae`).
4. A working `mlflow ui` command that shows all your runs at `http://localhost:5000`.
5. A `models/production_model.pkl` containing the best model (highest R2) from your experiments.

## Experiment Matrix

Run all 5 experiments from `config.yaml`. Each uses `test_size=0.2`, `random_state=42`.

| # | Model | Key Parameters | Config Block |
|---|-------|---------------|--------------|
| 1 | LinearRegression | (none) | `type: "LinearRegression"`, `params: {}` |
| 2 | RandomForestRegressor | n_estimators=50, max_depth=10 | Experiment 2 in config.yaml |
| 3 | RandomForestRegressor | n_estimators=100, max_depth=20 | Experiment 3 in config.yaml |
| 4 | GradientBoostingRegressor | n_estimators=100, lr=0.1, max_depth=5 | Experiment 4 in config.yaml |
| 5 | GradientBoostingRegressor | n_estimators=200, lr=0.05, max_depth=8 | Experiment 5 in config.yaml |

For each experiment: edit `config.yaml` with the appropriate model block, then run `make clean && make all`.

## Project Structure After This Activity

```
asi-project/
├── pyproject.toml          # MODIFIED -- mlflow added as dependency
├── Dockerfile
├── Makefile
├── config.yaml
├── experiment_log.csv
├── mlruns/                  # NEW -- MLflow tracking data (auto-created)
│   └── <experiment-id>/
│       └── <run-id>/
│           ├── meta.yaml
│           ├── params/
│           ├── metrics/
│           └── artifacts/
├── src/
│   ├── __init__.py
│   ├── prepare.py
│   ├── train.py            # MODIFIED -- MLflow tracking added
│   └── evaluate.py         # MODIFIED -- MLflow tracking added
├── data/
│   ├── raw/iowa_liquor_train.csv
│   └── processed/
├── models/model.pkl
└── tests/
    └── test_prepare.py
```

## Step-by-Step Instructions

### Step 1: Add MLflow to Your Dependencies

```bash
cd /path/to/asi-project
uv add mlflow
```

This installs MLflow and all its dependencies. It may take a minute.

Verify the installation:

```bash
uv run python -c "import mlflow; print(mlflow.__version__)"
```

You should see the version number printed (e.g., `2.16.0` or similar).

### Step 2: Read the MLflow Starter Snippet

Open `mlflow_snippet.py` (provided in the starter directory). Study the key concepts:

- **`mlflow.set_tracking_uri("file:./mlruns")`**: Tells MLflow to store all data in a local `./mlruns/` directory. No server needed.
- **`mlflow.set_experiment("asi-project")`**: Creates (or selects) an experiment named "asi-project". All runs will be grouped under this experiment.
- **`mlflow.start_run(run_name=...)`**: Starts a new tracked run. Everything logged inside this context manager belongs to this run.
- **`mlflow.log_param(key, value)`**: Logs a parameter (input to the experiment, like model type or learning rate).
- **`mlflow.log_metric(key, value)`**: Logs a metric (output of the experiment, like RMSE or R2).
- **`mlflow.log_artifact(filepath)`**: Logs a file as an artifact (like the trained model).

### Step 3: Integrate MLflow into Your Pipeline

You need to add MLflow tracking to your pipeline. The recommended approach is to add it to `evaluate.py` (since that is where metrics are computed) or split it between `train.py` and `evaluate.py`. The simplest approach is to wrap the logic in `evaluate.py` with an MLflow run.

#### Option A: All tracking in `evaluate.py` (simpler)

Add the following to `evaluate.py`, after computing metrics:

```python
import mlflow
import yaml

# Load config (you should already have this from A3)
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Set up MLflow
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("asi-project")

# ... your existing evaluation code that computes metrics ...

# Log everything to MLflow
with mlflow.start_run(run_name=f"{config['model']['type']}"):
    # Log parameters
    mlflow.log_param("model_type", config["model"]["type"])
    for param_name, param_value in config["model"].get("params", {}).items():
        mlflow.log_param(param_name, param_value)
    mlflow.log_param("test_size", config["dataset"]["test_size"])
    mlflow.log_param("random_state", config["dataset"]["random_state"])

    # Log metrics
    mlflow.log_metric("rmse", metrics["rmse"])
    mlflow.log_metric("r2", metrics["r2"])
    mlflow.log_metric("mae", metrics["mae"])

    # Log the model file as an artifact
    mlflow.log_artifact(config["output"]["model_path"])
```

#### Option B: Tracking split across `train.py` and `evaluate.py` (more realistic)

Start the MLflow run in `train.py` and log parameters there, then log metrics in `evaluate.py`. This requires sharing the run ID between scripts, which is more complex. Option A is recommended for this activity.

### Step 4: Run Your First Tracked Experiment

Make sure `config.yaml` is set to Experiment 1 (LinearRegression baseline):

```yaml
model:
  type: "LinearRegression"
  params: {}
```

Run the pipeline:

```bash
make clean
make all
```

Check that the `mlruns/` directory was created:

```bash
ls mlruns/
```

You should see a directory structure with your experiment data.

### Step 5: Run Experiment 2

Edit `config.yaml` to use Random Forest (small):

```yaml
model:
  type: "RandomForestRegressor"
  params:
    n_estimators: 50
    max_depth: 10
    random_state: 42
```

Run:

```bash
make clean
make all
```

### Step 6: Run Experiments 3-5 (or more)

Repeat the process for each experiment configuration. Edit `config.yaml`, then `make clean && make all`. Here are the remaining experiments from your config file:

**Experiment 3: Random Forest (large)**
```yaml
model:
  type: "RandomForestRegressor"
  params:
    n_estimators: 100
    max_depth: 20
    random_state: 42
```

**Experiment 4: Gradient Boosting (default)**
```yaml
model:
  type: "GradientBoostingRegressor"
  params:
    n_estimators: 100
    learning_rate: 0.1
    max_depth: 5
    random_state: 42
```

**Experiment 5: Gradient Boosting (tuned)**
```yaml
model:
  type: "GradientBoostingRegressor"
  params:
    n_estimators: 200
    learning_rate: 0.05
    max_depth: 8
    random_state: 42
```

After all runs, you should have 5 (or more) tracked experiments.

### Step 7: Launch the MLflow UI

```bash
uv run mlflow ui
```

Open your browser and go to: **http://localhost:5000**

You will see the MLflow dashboard with all your runs listed. For each run you can see:
- **Parameters**: model type, hyperparameters, test size, random state.
- **Metrics**: RMSE, R2, MAE.
- **Artifacts**: the trained model file.

### Step 8: Compare Runs

In the MLflow UI:

1. **Select all runs** by checking the boxes next to each run.
2. Click **Compare** to see a side-by-side comparison.
3. Look at the metrics columns. Answer these questions:
   - Which model had the **best (highest) R2**?
   - Which model had the **lowest RMSE**?
   - Which model had the **lowest MAE**?
   - Did increasing `n_estimators` from 50 to 100 in Random Forest improve the metrics?
   - Did lowering `learning_rate` from 0.1 to 0.05 in Gradient Boosting improve or hurt?

Write down the specific metric values -- you will need them for the MCQ test.

4. You can also use the **Chart** view to visualize metrics across runs.

### Step 9: Tag the Production Model

After comparing all experiments, identify the one with the **highest R2**. This is your production model.

Copy the best model to the production path:

```bash
# If Experiment 4 (GradientBoosting default) was best:
# Re-run with that config, then:
cp models/model.pkl models/production_model.pkl
```

Alternatively, if your `make all` already includes `make promote`, just ensure `config.yaml` is set to your best experiment and run `make all`. The promote target will copy the model automatically.

### Step 10: Optional Stretch — MLflow Model Registry

For students who want to explore how production teams manage models:

1. Change the tracking URI to use a SQLite backend:
   ```python
   mlflow.set_tracking_uri("sqlite:///mlflow.db")
   ```

2. After training, register the model:
   ```python
   mlflow.sklearn.log_model(model, "model", registered_model_name="asi-project")
   ```

3. Promote the best model:
   ```python
   from mlflow.tracking import MlflowClient
   client = MlflowClient()
   client.transition_model_version_stage(
       name="asi-project",
       version=best_version,
       stage="Production"
   )
   ```

This is **entirely optional** and not checked by the validator. The file-based promotion (`model.pkl` → `production_model.pkl`) teaches the same concept without SQLite overhead.

### Step 11: Run the Check Script

```bash
cd ..
uv run python check_activity.py
```

All checks should show PASS.

### Step 12: Record Your Results

Write down:
- The exact RMSE, R2, and MAE for each of your 5-6 runs (to 2 decimal places).
- Which model configuration produced the best R2.
- Which model configuration produced the lowest RMSE.

You will need these for the MCQ test.

## Key Concepts

### Why Track Experiments?

Without tracking, experiment comparison looks like this:
- "I think the Random Forest was better... or was it Gradient Boosting?"
- "What learning rate did I use for that good run last week?"
- "My colleague wants to reproduce my best result -- I don't remember the config."

With MLflow tracking, every run is automatically logged with its full configuration and results. You can compare any two runs instantly, reproduce any result, and share your findings with your team.

### Parameters vs. Metrics

- **Parameters** are the **inputs** to your experiment: model type, learning rate, n_estimators, random state, test size. They are set *before* training.
- **Metrics** are the **outputs** of your experiment: RMSE, R2, MAE. They are computed *after* training and evaluation.

In MLflow, parameters are logged with `mlflow.log_param()` and metrics with `mlflow.log_metric()`. This distinction matters because MLflow lets you sort and filter runs by metrics (e.g., "show me all runs sorted by R2, descending").

### The MLflow Tracking URI

`mlflow.set_tracking_uri("file:./mlruns")` tells MLflow to use the local filesystem. In production, teams typically use a remote tracking server (e.g., `http://mlflow-server:5000`) so that everyone on the team shares the same experiment database. For this course, local file storage is sufficient and requires no setup.

### Artifacts

An artifact is any file produced by your experiment that you want to keep: the trained model, a plot, a configuration file. MLflow copies artifacts into its tracking directory so they are associated with the specific run that produced them.

### MLflow vs. experiment_log.csv

Your A3 `experiment_log.csv` is a simple append-only log. MLflow provides the same data *plus*:
- A web UI for browsing and comparing runs
- Sorting and filtering by any parameter or metric
- Artifact storage linked to each run
- API access for programmatic queries

In production, you would use MLflow (or a similar tool) instead of a CSV log.

## Estimated Time

60-90 minutes.

## MLflow Basics Quick Reference

| Concept | What It Is | Code |
|---------|-----------|------|
| Tracking URI | Where MLflow stores data | `mlflow.set_tracking_uri("file:./mlruns")` |
| Experiment | A named group of related runs | `mlflow.set_experiment("asi-project")` |
| Run | One execution of your pipeline | `with mlflow.start_run():` |
| Parameter | An input value (logged before/during training) | `mlflow.log_param("model_type", "RandomForest")` |
| Metric | An output value (logged after evaluation) | `mlflow.log_metric("rmse", 1234.56)` |
| Artifact | A file produced by the run | `mlflow.log_artifact("models/model.pkl")` |
| UI | Web dashboard for viewing runs | `mlflow ui` then open http://localhost:5000 |

## Common Mistakes

1. **Forgetting `mlflow.set_tracking_uri()`**: Without this, MLflow may default to a different storage location. Always set it explicitly to `"file:./mlruns"`.
2. **Calling `mlflow.log_metric()` outside a run context**: All logging calls must be inside a `with mlflow.start_run():` block. If you call them outside, MLflow raises an error.
3. **Logging the same parameter name twice in one run**: MLflow does not allow duplicate parameter names within a single run. If you accidentally log `model_type` twice, the second call will raise an error.
4. **Not running `make clean` between experiments**: If you skip `make clean`, the prepare step may reuse old data. Always clean before a new experiment.
5. **Running `mlflow ui` from the wrong directory**: `mlflow ui` reads from `./mlruns/` relative to the current directory. Run it from your project root (where `mlruns/` is located).
6. **Port 5000 already in use**: If you see "Address already in use", another process is using port 5000. Either stop that process or run `uv run mlflow ui --port 5001` and open http://localhost:5001 instead. On macOS, AirPlay Receiver sometimes uses port 5000 -- you can disable it in System Settings > General > AirDrop & Handoff.

## Hints

- **Start simple**: Get one run tracked successfully before running all 5-6 experiments.
- **Check `mlruns/` after each run**: Use `ls mlruns/` to verify that new data appeared.
- **Use `run_name` for readability**: `mlflow.start_run(run_name="GradientBoosting_lr0.1")` makes it easy to identify runs in the UI.
- **The MLflow UI auto-refreshes**: After running a new experiment, refresh the browser page to see the new run.
- **You can delete bad runs**: In the MLflow UI, select a run and click "Delete" if you made a mistake. Or delete the corresponding directory under `mlruns/`.
