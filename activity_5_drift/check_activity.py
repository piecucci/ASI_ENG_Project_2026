"""
Activity 5 Check Script
-----------------------
Validates that Activity 5 (Drift Detection and Retraining) is complete.

Usage:
    cd <your-asi-project-directory>
    uv run python check_activity.py

This script checks:
1. detect_drift.py exists in src/ and has no remaining `pass` stubs in function bodies
2. drift_report.csv exists
3. drift_report.csv has the required columns
4. drift_report.csv has at least 12 rows (months of 2020-2021 data)
5. At least one row has drift_detected=True
6. config.yaml has a drift section with threshold_r2
7. At least 2 rows with retrained=True (closed-loop)
8. At least 1 row with promoted=True
9. model_version has values > 1
10. models/production_model.pkl exists
"""

import os
import sys
import csv

PASS = "PASS"
FAIL = "FAIL"

results = []


def check(name: str, condition: bool, message: str = "") -> None:
    """Record a check result."""
    status = PASS if condition else FAIL
    results.append((name, status, message))
    symbol = "+" if condition else "-"
    display_msg = f" -- {message}" if message else ""
    print(f"  [{symbol}] {name}{display_msg}")


def main():
    print("=" * 60)
    print("Activity 5: Detect Drift and Retrain -- Validation")
    print("=" * 60)
    print()

    project_root = os.getcwd()

    # ---------------------------------------------------------------
    # Check 1: detect_drift.py exists
    # ---------------------------------------------------------------
    print("1. Checking detect_drift.py exists...")
    drift_script = os.path.join(project_root, "src", "detect_drift.py")
    script_exists = os.path.isfile(drift_script)
    check("detect_drift.py exists", script_exists,
          f"Expected at {drift_script}")

    # ---------------------------------------------------------------
    # Check 2: detect_drift.py has no remaining `pass` stubs
    # ---------------------------------------------------------------
    print("\n2. Checking detect_drift.py for remaining TODO stubs...")
    if script_exists:
        with open(drift_script, "r") as f:
            source = f.read()

        # Look for `pass` that appears as the only statement in a function body.
        # We check for lines that are just whitespace + "pass" (ignoring comments).
        lines = source.split("\n")
        pass_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == "pass":
                pass_lines.append(i)

        no_pass_stubs = len(pass_lines) == 0
        if no_pass_stubs:
            check("No pass stubs remaining", True)
        else:
            check("No pass stubs remaining", False,
                  f"Found 'pass' on line(s): {pass_lines}. "
                  f"Replace these with your implementation.")
    else:
        check("No pass stubs remaining", False,
              "Cannot check -- file does not exist")

    # ---------------------------------------------------------------
    # Check 3: drift_report.csv exists
    # ---------------------------------------------------------------
    print("\n3. Checking drift_report.csv exists...")
    report_path = os.path.join(project_root, "drift_report.csv")
    report_exists = os.path.isfile(report_path)
    check("drift_report.csv exists", report_exists,
          f"Expected at {report_path}")

    # ---------------------------------------------------------------
    # Check 4: drift_report.csv has required columns
    # ---------------------------------------------------------------
    print("\n4. Checking drift_report.csv columns...")
    required_columns = {"year_month", "rmse", "r2", "drift_detected", "model_version", "retrained", "promoted", "production_r2", "candidate_r2"}
    if report_exists:
        with open(report_path, "r") as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames) if reader.fieldnames else set()

        missing = required_columns - headers
        has_columns = len(missing) == 0
        if has_columns:
            check("Required columns present", True,
                  f"Found: {sorted(headers)}")
        else:
            check("Required columns present", False,
                  f"Missing columns: {sorted(missing)}. "
                  f"Found: {sorted(headers)}")
    else:
        check("Required columns present", False,
              "Cannot check -- file does not exist")

    # ---------------------------------------------------------------
    # Check 5: drift_report.csv has at least 12 rows
    # ---------------------------------------------------------------
    print("\n5. Checking drift_report.csv row count...")
    if report_exists:
        with open(report_path, "r") as f:
            reader = csv.reader(f)
            row_count = sum(1 for _ in reader) - 1  # subtract header

        has_enough_rows = row_count >= 12
        check("At least 12 data rows", has_enough_rows,
              f"Found {row_count} rows (need >= 12 for 2020-2021 monthly data)")
    else:
        check("At least 12 data rows", False,
              "Cannot check -- file does not exist")

    # ---------------------------------------------------------------
    # Check 6: At least one row has drift_detected=True
    # ---------------------------------------------------------------
    print("\n6. Checking for drift detection...")
    if report_exists and has_columns if report_exists else False:
        with open(report_path, "r") as f:
            reader = csv.DictReader(f)
            drift_flags = []
            for row in reader:
                val = row.get("drift_detected", "").strip()
                drift_flags.append(val)

        any_drift = any(v.lower() in ("true", "1", "yes") for v in drift_flags)
        check("Drift detected in at least one month", any_drift,
              f"drift_detected values: {drift_flags[:6]}{'...' if len(drift_flags) > 6 else ''}")
    else:
        check("Drift detected in at least one month", False,
              "Cannot check -- report missing or missing columns")

    # ---------------------------------------------------------------
    # Check 7: At least 2 rows with retrained=True (closed-loop)
    # ---------------------------------------------------------------
    print("\n7. Checking for closed-loop retraining...")
    if report_exists:
        with open(report_path, "r") as f:
            reader = csv.DictReader(f)
            retrain_flags = [row.get("retrained", "").strip() for row in reader]

        retrain_count = sum(1 for v in retrain_flags if v.lower() in ("true", "1", "yes"))
        check("At least 2 rows with retrained=True", retrain_count >= 2,
              f"Found {retrain_count} retrained rows (need >= 2 for closed-loop)")
    else:
        check("At least 2 rows with retrained=True", False,
              "Cannot check -- report missing")

    # ---------------------------------------------------------------
    # Check 8: At least 1 row with promoted=True
    # ---------------------------------------------------------------
    print("\n8. Checking for model promotion...")
    if report_exists:
        with open(report_path, "r") as f:
            reader = csv.DictReader(f)
            promote_flags = [row.get("promoted", "").strip() for row in reader]

        promote_count = sum(1 for v in promote_flags if v.lower() in ("true", "1", "yes"))
        check("At least 1 row with promoted=True", promote_count >= 1,
              f"Found {promote_count} promoted rows")
    else:
        check("At least 1 row with promoted=True", False,
              "Cannot check -- report missing")

    # ---------------------------------------------------------------
    # Check 9: model_version has values > 1
    # ---------------------------------------------------------------
    print("\n9. Checking model version progression...")
    if report_exists:
        with open(report_path, "r") as f:
            reader = csv.DictReader(f)
            versions = []
            for row in reader:
                v = row.get("model_version", "").strip()
                if v:
                    try:
                        versions.append(int(v))
                    except ValueError:
                        pass

        has_version_gt1 = any(v > 1 for v in versions)
        max_version = max(versions) if versions else 0
        check("model_version progresses beyond 1", has_version_gt1,
              f"Max model_version: {max_version}")
    else:
        check("model_version progresses beyond 1", False,
              "Cannot check -- report missing")

    # ---------------------------------------------------------------
    # Check 10: production_model.pkl exists (updated by closed loop)
    # ---------------------------------------------------------------
    print("\n10. Checking production model...")
    prod_model = os.path.join(project_root, "models", "production_model.pkl")
    check("models/production_model.pkl exists", os.path.isfile(prod_model),
          "The closed-loop should save promoted models to models/production_model.pkl")

    # ---------------------------------------------------------------
    # Check 11: config.yaml has drift section
    # ---------------------------------------------------------------
    print("\n11. Checking config.yaml for drift configuration...")
    config_path = os.path.join(project_root, "config.yaml")
    config_exists = os.path.isfile(config_path)

    if config_exists:
        try:
            import yaml
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            has_drift_section = (
                isinstance(config, dict)
                and "drift" in config
                and isinstance(config["drift"], dict)
            )
            check("config.yaml has 'drift' section", has_drift_section)

            if has_drift_section:
                has_threshold = "threshold_r2" in config["drift"]
                check("drift.threshold_r2 configured", has_threshold,
                      f"Value: {config['drift'].get('threshold_r2', 'MISSING')}")
            else:
                check("drift.threshold_r2 configured", False,
                      "Cannot check -- 'drift' section missing")

        except ImportError:
            check("config.yaml has 'drift' section", False,
                  "PyYAML not installed. Run: uv add pyyaml")
        except Exception as e:
            check("config.yaml has 'drift' section", False,
                  f"Error reading config: {e}")
    else:
        check("config.yaml has 'drift' section", False,
              f"config.yaml not found at {config_path}")

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    passed = sum(1 for _, s, _ in results if s == PASS)
    total = len(results)
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print("\nAll checks passed! Activity 5 is complete.")
    else:
        print("\nSome checks failed. Review the output above and fix the issues.")
        failed = [(name, msg) for name, status, msg in results if status == FAIL]
        print("\nFailed checks:")
        for name, msg in failed:
            print(f"  - {name}: {msg}")

    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
