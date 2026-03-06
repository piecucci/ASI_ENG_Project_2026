"""
Activity 3 Validator: Orchestrate a Pipeline
=============================================
Run from the activity_3_orchestrate/ directory:

    uv run python check_activity.py

This script checks that the student's asi-project has:
  1. A Makefile with real commands (not just TODO comments)
  2. A valid config.yaml
  3. A passing `make all`
  4. A passing `make test`
  5. An experiment_log.csv with at least 1 row
  6. The 4 expected processed data files
"""
import os
import subprocess
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# The student project is expected to be at ../checkpoints/a3-checkpoint
# or can be overridden via the ASI_PROJECT_DIR environment variable.
# If neither exists, try the sibling 'starter' directory for basic checks.
PROJECT_DIR = os.environ.get(
    "ASI_PROJECT_DIR",
    os.getcwd(),
)

EXPECTED_PROCESSED_FILES = [
    "data/processed/X_train.csv",
    "data/processed/X_test.csv",
    "data/processed/y_train.csv",
    "data/processed/y_test.csv",
]

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


def run_command(cmd: list[str], cwd: str, timeout: int = 120) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def main() -> None:
    global passed, failed

    print("=" * 60)
    print("Activity 3 Check: Orchestrate a Pipeline")
    print("=" * 60)

    if not os.path.isdir(PROJECT_DIR):
        print(f"\nERROR: Project directory not found: {PROJECT_DIR}")
        print("Set the ASI_PROJECT_DIR environment variable to your project path.")
        print("Example: ASI_PROJECT_DIR=/path/to/asi-project uv run python check_activity.py")
        sys.exit(1)

    print(f"\nProject directory: {os.path.abspath(PROJECT_DIR)}\n")

    # ------------------------------------------------------------------
    # 1. Makefile exists and has real commands
    # ------------------------------------------------------------------
    makefile_path = os.path.join(PROJECT_DIR, "Makefile")
    makefile_exists = os.path.isfile(makefile_path)
    check("Makefile exists", makefile_exists)

    if makefile_exists:
        with open(makefile_path) as f:
            makefile_content = f.read()

        # Check that TODO comments have been replaced with actual commands
        has_todo = "# TODO:" in makefile_content
        check(
            "Makefile has real commands (no TODO comments remaining)",
            not has_todo,
            "Replace all '# TODO:' lines with actual commands.",
        )

        # Check for expected targets
        for target in ["prepare", "train", "evaluate", "validate", "promote", "test", "clean"]:
            has_target = f"{target}:" in makefile_content or f"{target} :" in makefile_content
            check(
                f"Makefile has '{target}' target",
                has_target,
            )
    else:
        # Skip Makefile content checks
        for _ in range(6):
            check("Makefile content check (skipped -- file missing)", False)

    # ------------------------------------------------------------------
    # 2. config.yaml exists and is valid YAML
    # ------------------------------------------------------------------
    config_path = os.path.join(PROJECT_DIR, "config.yaml")
    config_exists = os.path.isfile(config_path)
    check("config.yaml exists", config_exists)

    config = None
    if config_exists:
        try:
            import yaml

            with open(config_path) as f:
                config = yaml.safe_load(f)
            check("config.yaml is valid YAML", config is not None)
        except ImportError:
            check(
                "config.yaml is valid YAML",
                False,
                "pyyaml is not installed. Run: uv add pyyaml",
            )
        except Exception as e:
            check("config.yaml is valid YAML", False, str(e))

        if config is not None:
            # Check required keys
            has_dataset = "dataset" in config
            has_model = "model" in config
            has_output = "output" in config
            check("config.yaml has 'dataset' section", has_dataset)
            check("config.yaml has 'model' section", has_model)
            check("config.yaml has 'output' section", has_output)

            if has_model:
                model_type = config.get("model", {}).get("type", "")
                valid_types = [
                    "LinearRegression",
                    "RandomForestRegressor",
                    "GradientBoostingRegressor",
                ]
                check(
                    f"config.yaml model type is valid ('{model_type}')",
                    model_type in valid_types,
                    f"Expected one of {valid_types}, got '{model_type}'.",
                )

            if config is not None:
                has_validation = (
                    "validation" in config
                    and isinstance(config.get("validation"), dict)
                    and "min_r2" in config.get("validation", {})
                )
                check(
                    "config.yaml has 'validation.min_r2'",
                    has_validation,
                    "Add a 'validation:' section with 'min_r2: 0.70' to config.yaml.",
                )
    else:
        for _ in range(4):
            check("config.yaml content check (skipped -- file missing)", False)

    # ------------------------------------------------------------------
    # 3. make all succeeds
    # ------------------------------------------------------------------
    print()  # visual separator
    rc, stdout, stderr = run_command(["make", "all"], cwd=PROJECT_DIR, timeout=180)
    check(
        "'make all' succeeds (exit code 0)",
        rc == 0,
        f"Exit code: {rc}. Stderr: {stderr[:200]}" if rc != 0 else "",
    )

    # ------------------------------------------------------------------
    # 4. Processed data files exist
    # ------------------------------------------------------------------
    for fpath in EXPECTED_PROCESSED_FILES:
        full = os.path.join(PROJECT_DIR, fpath)
        check(f"File exists: {fpath}", os.path.isfile(full))

    # ------------------------------------------------------------------
    # 5. make test succeeds
    # ------------------------------------------------------------------
    rc, stdout, stderr = run_command(["make", "test"], cwd=PROJECT_DIR, timeout=120)
    check(
        "'make test' succeeds (exit code 0)",
        rc == 0,
        f"Exit code: {rc}. Stderr: {stderr[:200]}" if rc != 0 else "",
    )

    # ------------------------------------------------------------------
    # 6. experiment_log.csv exists with at least 1 row
    # ------------------------------------------------------------------
    log_path = os.path.join(PROJECT_DIR, "experiment_log.csv")
    log_exists = os.path.isfile(log_path)
    check("experiment_log.csv exists", log_exists)

    if log_exists:
        with open(log_path) as f:
            lines = f.readlines()
        # First line is header, subsequent lines are data rows
        data_rows = len(lines) - 1 if len(lines) > 1 else 0
        check(
            f"experiment_log.csv has at least 1 data row (found {data_rows})",
            data_rows >= 1,
            "Run 'make all' at least once to generate a log entry.",
        )

        # Check expected columns in header
        if lines:
            header = lines[0].strip().lower()
            for col in ["model_type", "rmse", "r2", "mae"]:
                check(
                    f"experiment_log.csv header contains '{col}'",
                    col in header,
                )
    else:
        for _ in range(5):
            check("experiment_log.csv content check (skipped -- file missing)", False)

    # ------------------------------------------------------------------
    # 7. production_model.pkl exists after make all
    # ------------------------------------------------------------------
    prod_model = os.path.join(PROJECT_DIR, "models", "production_model.pkl")
    check(
        "models/production_model.pkl exists (promoted model)",
        os.path.isfile(prod_model),
        "Run 'make all' — the promote target should copy model.pkl to production_model.pkl.",
    )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    total = passed + failed
    print()
    print("=" * 60)
    print(f"Results: {passed}/{total} checks passed")
    if failed == 0:
        print("All checks passed. Activity 3 is complete.")
    else:
        print(f"{failed} check(s) failed. Review the FAIL messages above.")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
