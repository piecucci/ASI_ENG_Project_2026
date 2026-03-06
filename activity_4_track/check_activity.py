"""
Activity 4 Validator: Track Experiments
=======================================
Run from the activity_4_track/ directory:

    uv run python check_activity.py

This script checks that the student's asi-project has:
  1. mlflow is listed in pyproject.toml dependencies
  2. mlruns/ directory exists
  3. At least 5 MLflow runs are recorded
  4. Each run has logged metrics (rmse, r2, mae)
  5. Each run has logged params (model_type)
"""
import os
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_DIR = os.environ.get(
    "ASI_PROJECT_DIR",
    os.getcwd(),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
passed = 0
failed = 0


def check(description: str, condition: bool, detail: str = ""):
    """Print PASS/FAIL for a single check."""
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {description}")
    else:
        failed += 1
        msg = f"  FAIL  {description}"
        if detail:
            msg += f"\n        -> {detail}"
        print(msg)


def find_run_dirs(mlruns_path: str) -> list[str]:
    """Find all MLflow run directories under mlruns/.

    MLflow stores runs at: mlruns/<experiment_id>/<run_id>/
    A run directory contains a 'meta.yaml' file.
    """
    run_dirs = []
    if not os.path.isdir(mlruns_path):
        return run_dirs

    for experiment_id in os.listdir(mlruns_path):
        exp_path = os.path.join(mlruns_path, experiment_id)
        if not os.path.isdir(exp_path):
            continue
        # Skip the .trash directory and models directory
        if experiment_id.startswith(".") or experiment_id == "models":
            continue

        for run_id in os.listdir(exp_path):
            run_path = os.path.join(exp_path, run_id)
            if not os.path.isdir(run_path):
                continue
            # A valid run directory has a meta.yaml file
            meta_path = os.path.join(run_path, "meta.yaml")
            if os.path.isfile(meta_path):
                run_dirs.append(run_path)

    return run_dirs


def get_run_metrics(run_path: str) -> dict[str, float]:
    """Read metrics from a run directory.

    MLflow stores metrics as individual files under <run>/metrics/
    Each file contains lines of: <timestamp> <value> <step>
    """
    metrics = {}
    metrics_dir = os.path.join(run_path, "metrics")
    if not os.path.isdir(metrics_dir):
        return metrics

    for metric_file in os.listdir(metrics_dir):
        metric_path = os.path.join(metrics_dir, metric_file)
        if os.path.isfile(metric_path):
            with open(metric_path) as f:
                # Read the last line (most recent value)
                lines = f.readlines()
                if lines:
                    parts = lines[-1].strip().split()
                    if len(parts) >= 2:
                        try:
                            metrics[metric_file] = float(parts[1])
                        except ValueError:
                            pass
    return metrics


def get_run_params(run_path: str) -> dict[str, str]:
    """Read parameters from a run directory.

    MLflow stores params as individual files under <run>/params/
    Each file contains the parameter value as a single line.
    """
    params = {}
    params_dir = os.path.join(run_path, "params")
    if not os.path.isdir(params_dir):
        return params

    for param_file in os.listdir(params_dir):
        param_path = os.path.join(params_dir, param_file)
        if os.path.isfile(param_path):
            with open(param_path) as f:
                params[param_file] = f.read().strip()
    return params


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def main() -> None:
    global passed, failed

    print("=" * 60)
    print("Activity 4 Check: Track Experiments")
    print("=" * 60)

    if not os.path.isdir(PROJECT_DIR):
        print(f"\nERROR: Project directory not found: {PROJECT_DIR}")
        print("Set the ASI_PROJECT_DIR environment variable to your project path.")
        print("Example: ASI_PROJECT_DIR=/path/to/asi-project uv run python check_activity.py")
        sys.exit(1)

    print(f"\nProject directory: {os.path.abspath(PROJECT_DIR)}\n")

    # ------------------------------------------------------------------
    # 1. mlflow is in pyproject.toml dependencies
    # ------------------------------------------------------------------
    pyproject_path = os.path.join(PROJECT_DIR, "pyproject.toml")
    pyproject_exists = os.path.isfile(pyproject_path)
    check("pyproject.toml exists", pyproject_exists)

    if pyproject_exists:
        with open(pyproject_path) as f:
            pyproject_content = f.read().lower()
        has_mlflow = "mlflow" in pyproject_content
        check(
            "mlflow is listed in pyproject.toml",
            has_mlflow,
            "Run: uv add mlflow",
        )
    else:
        check("mlflow dependency check (skipped -- pyproject.toml missing)", False)

    # ------------------------------------------------------------------
    # 2. mlruns/ directory exists
    # ------------------------------------------------------------------
    mlruns_path = os.path.join(PROJECT_DIR, "mlruns")
    mlruns_exists = os.path.isdir(mlruns_path)
    check(
        "mlruns/ directory exists",
        mlruns_exists,
        "Run your pipeline with MLflow tracking to create the mlruns/ directory.",
    )

    # ------------------------------------------------------------------
    # 3. At least 3 MLflow runs recorded
    # ------------------------------------------------------------------
    run_dirs = find_run_dirs(mlruns_path) if mlruns_exists else []
    num_runs = len(run_dirs)
    check(
        f"At least 5 MLflow runs recorded (found {num_runs})",
        num_runs >= 5,
        "Run 'make clean && make all' with different config.yaml settings at least 5 times.",
    )

    # ------------------------------------------------------------------
    # 4. Each run has logged metrics (rmse, r2, mae)
    # ------------------------------------------------------------------
    required_metrics = ["rmse", "r2", "mae"]

    if run_dirs:
        all_runs_have_metrics = True
        runs_missing_metrics = []

        for run_path in run_dirs:
            run_id = os.path.basename(run_path)
            metrics = get_run_metrics(run_path)
            metric_names = set(metrics.keys())

            for req in required_metrics:
                if req not in metric_names:
                    all_runs_have_metrics = False
                    runs_missing_metrics.append(f"Run {run_id[:8]}... missing '{req}'")

        check(
            "All runs have metrics: rmse, r2, mae",
            all_runs_have_metrics,
            "; ".join(runs_missing_metrics[:5]) if runs_missing_metrics else "",
        )

        # Show a summary of metrics for each run
        print()
        print("  Run summary:")
        for run_path in run_dirs:
            run_id = os.path.basename(run_path)[:8]
            params = get_run_params(run_path)
            metrics = get_run_metrics(run_path)
            model_type = params.get("model_type", "unknown")
            rmse = metrics.get("rmse", "?")
            r2 = metrics.get("r2", "?")
            mae = metrics.get("mae", "?")
            if isinstance(rmse, float):
                rmse = f"{rmse:.2f}"
            if isinstance(r2, float):
                r2 = f"{r2:.4f}"
            if isinstance(mae, float):
                mae = f"{mae:.2f}"
            print(f"    {run_id}  model={model_type:<30s}  RMSE={rmse}  R2={r2}  MAE={mae}")
        print()
    else:
        check(
            "All runs have metrics: rmse, r2, mae",
            False,
            "No runs found to check.",
        )

    # ------------------------------------------------------------------
    # 5. Each run has logged params (model_type)
    # ------------------------------------------------------------------
    if run_dirs:
        all_runs_have_model_type = True
        runs_missing_param = []

        for run_path in run_dirs:
            run_id = os.path.basename(run_path)
            params = get_run_params(run_path)

            if "model_type" not in params:
                all_runs_have_model_type = False
                runs_missing_param.append(f"Run {run_id[:8]}... missing 'model_type'")

        check(
            "All runs have param: model_type",
            all_runs_have_model_type,
            "; ".join(runs_missing_param[:5]) if runs_missing_param else "",
        )

        # Check that at least 2 different model types were tried
        model_types_used = set()
        for run_path in run_dirs:
            params = get_run_params(run_path)
            mt = params.get("model_type", "")
            if mt:
                model_types_used.add(mt)

        check(
            f"At least 2 different model types tried (found: {', '.join(sorted(model_types_used)) or 'none'})",
            len(model_types_used) >= 2,
            "Try different model types in config.yaml (e.g., LinearRegression, RandomForestRegressor).",
        )
    else:
        check("All runs have param: model_type", False, "No runs found to check.")
        check("Multiple model types tried", False, "No runs found to check.")

    # ------------------------------------------------------------------
    # 6. config.yaml still valid
    # ------------------------------------------------------------------
    config_path = os.path.join(PROJECT_DIR, "config.yaml")
    config_exists = os.path.isfile(config_path)
    check("config.yaml exists", config_exists)

    # ------------------------------------------------------------------
    # 7. production_model.pkl exists (best model promoted)
    # ------------------------------------------------------------------
    prod_model = os.path.join(PROJECT_DIR, "models", "production_model.pkl")
    check(
        "models/production_model.pkl exists (best model promoted)",
        os.path.isfile(prod_model),
        "Copy your best model to models/production_model.pkl.",
    )

    # ------------------------------------------------------------------
    # 8. Makefile still works
    # ------------------------------------------------------------------
    makefile_path = os.path.join(PROJECT_DIR, "Makefile")
    check("Makefile exists", os.path.isfile(makefile_path))

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    total = passed + failed
    print("=" * 60)
    print(f"Results: {passed}/{total} checks passed")
    if failed == 0:
        print("All checks passed. Activity 4 is complete.")
    else:
        print(f"{failed} check(s) failed. Review the FAIL messages above.")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
