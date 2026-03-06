#!/usr/bin/env python3
"""
Activity 1 Validator
====================
Run this script from the activity_1_modularize/ directory to verify
that your implementation meets all requirements.

Usage:
    cd activity_1_modularize
    uv run python check_activity.py
"""

import ast
import os
import subprocess
import sys

STARTER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "starter")

REQUIRED_MODULES = {
    "src/prepare.py": ["load_data", "engineer_features", "split_data", "save_splits"],
    "src/train.py": ["load_splits", "train_model", "save_model"],
    "src/evaluate.py": ["load_model", "load_test_data", "evaluate_model"],
    "src/validate.py": ["load_model", "load_test_data", "validate_model"],
}

REQUIRED_SPLITS = ["X_train.csv", "X_test.csv", "y_train.csv", "y_test.csv"]

MODEL_PATH = "models/model.pkl"

results = []


def check(name: str, passed: bool, detail: str = "") -> None:
    """Record a check result."""
    status = "PASS" if passed else "FAIL"
    msg = f"  [{status}] {name}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    results.append(passed)


def get_function_names(filepath: str) -> list[str]:
    """Parse a Python file and return top-level function names."""
    with open(filepath, "r") as f:
        tree = ast.parse(f.read(), filename=filepath)
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    ]


def check_module_functions(rel_path: str, expected_funcs: list[str]) -> None:
    """Check that a module file exists and contains the required functions."""
    abs_path = os.path.join(STARTER_DIR, rel_path)

    # Check file exists
    exists = os.path.isfile(abs_path)
    check(f"{rel_path} exists", exists)
    if not exists:
        for func_name in expected_funcs:
            check(f"{rel_path}::{func_name} defined", False, detail="file missing")
        return

    # Check functions
    try:
        found_funcs = get_function_names(abs_path)
    except SyntaxError as e:
        check(f"{rel_path} parses without syntax errors", False, detail=str(e))
        for func_name in expected_funcs:
            check(f"{rel_path}::{func_name} defined", False, detail="syntax error")
        return

    for func_name in expected_funcs:
        check(
            f"{rel_path}::{func_name} defined",
            func_name in found_funcs,
            detail="" if func_name in found_funcs else "function not found",
        )


def check_todo_stubs_removed(rel_path: str) -> None:
    """Check that no TODO stubs remain (i.e., functions are implemented)."""
    abs_path = os.path.join(STARTER_DIR, rel_path)
    if not os.path.isfile(abs_path):
        return

    with open(abs_path, "r") as f:
        source = f.read()

    # Check for bare "pass" in function bodies that suggests stubs remain
    tree = ast.parse(source, filename=abs_path)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            body = node.body
            # Skip docstrings
            stmts = [
                s for s in body
                if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
            ]
            is_stub = (
                len(stmts) == 1
                and isinstance(stmts[0], ast.Pass)
            )
            check(
                f"{rel_path}::{node.name} implemented (not a stub)",
                not is_stub,
                detail="function body is just 'pass'" if is_stub else "",
            )


def check_splits_exist() -> None:
    """Check that processed data splits exist."""
    processed_dir = os.path.join(STARTER_DIR, "data", "processed")
    for filename in REQUIRED_SPLITS:
        filepath = os.path.join(processed_dir, filename)
        exists = os.path.isfile(filepath)
        check(f"data/processed/{filename} exists", exists)
        if exists:
            # Check file is non-empty
            size = os.path.getsize(filepath)
            check(
                f"data/processed/{filename} is non-empty",
                size > 0,
                detail=f"{size} bytes" if size > 0 else "file is empty",
            )


def check_model_exists() -> None:
    """Check that the trained model file exists."""
    model_path = os.path.join(STARTER_DIR, MODEL_PATH)
    exists = os.path.isfile(model_path)
    check(f"{MODEL_PATH} exists", exists)
    if exists:
        size = os.path.getsize(model_path)
        check(
            f"{MODEL_PATH} is non-empty",
            size > 0,
            detail=f"{size} bytes" if size > 0 else "file is empty",
        )


def check_evaluate_output() -> None:
    """Run evaluate.py and check that it prints RMSE and R2."""
    evaluate_path = os.path.join(STARTER_DIR, "src", "evaluate.py")
    if not os.path.isfile(evaluate_path):
        check("evaluate.py produces output", False, detail="file missing")
        return

    # Check that model and test data exist before running
    model_path = os.path.join(STARTER_DIR, MODEL_PATH)
    test_x = os.path.join(STARTER_DIR, "data", "processed", "X_test.csv")
    if not os.path.isfile(model_path) or not os.path.isfile(test_x):
        check(
            "evaluate.py produces output",
            False,
            detail="model or test data missing; run prepare.py and train.py first",
        )
        return

    try:
        result = subprocess.run(
            ["uv", "run", "python", "src/evaluate.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=STARTER_DIR,
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            check(
                "evaluate.py runs without errors",
                False,
                detail=f"exit code {result.returncode}: {stderr[:200]}",
            )
            check("evaluate.py output contains RMSE", False, detail="script failed")
            check("evaluate.py output contains R2", False, detail="script failed")
            return

        check("evaluate.py runs without errors", True)

        has_rmse = "RMSE:" in stdout
        has_r2 = "R2:" in stdout
        check(
            "evaluate.py output contains RMSE",
            has_rmse,
            detail=f"stdout: {stdout[:100]}" if not has_rmse else "",
        )
        check(
            "evaluate.py output contains R2",
            has_r2,
            detail=f"stdout: {stdout[:100]}" if not has_r2 else "",
        )

        if has_rmse and has_r2:
            print(f"\n  Evaluation output:\n  {stdout.replace(chr(10), chr(10) + '  ')}")

    except subprocess.TimeoutExpired:
        check("evaluate.py produces output", False, detail="timed out after 60s")
    except Exception as e:
        check("evaluate.py produces output", False, detail=str(e))


def check_validate_output() -> None:
    """Run validate.py and check that it prints VALIDATION PASSED and exits 0."""
    validate_path = os.path.join(STARTER_DIR, "src", "validate.py")
    if not os.path.isfile(validate_path):
        check("validate.py produces output", False, detail="file missing")
        return

    model_path = os.path.join(STARTER_DIR, MODEL_PATH)
    test_x = os.path.join(STARTER_DIR, "data", "processed", "X_test.csv")
    if not os.path.isfile(model_path) or not os.path.isfile(test_x):
        check(
            "validate.py produces output",
            False,
            detail="model or test data missing; run prepare.py and train.py first",
        )
        return

    try:
        result = subprocess.run(
            ["uv", "run", "python", "src/validate.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=STARTER_DIR,
        )
        stdout = result.stdout.strip()

        check(
            "validate.py exits with code 0",
            result.returncode == 0,
            detail=f"exit code {result.returncode}" if result.returncode != 0 else "",
        )

        has_validation = "VALIDATION PASSED" in stdout
        check(
            "validate.py output contains VALIDATION PASSED",
            has_validation,
            detail=f"stdout: {stdout[:100]}" if not has_validation else "",
        )

        if has_validation:
            print(f"\n  Validation output:\n  {stdout}")

    except subprocess.TimeoutExpired:
        check("validate.py produces output", False, detail="timed out after 60s")
    except Exception as e:
        check("validate.py produces output", False, detail=str(e))


def main() -> None:
    print("=" * 60)
    print("  Activity 1 Validator")
    print("=" * 60)
    print()

    print("1. Checking module files and function signatures...")
    for rel_path, funcs in REQUIRED_MODULES.items():
        check_module_functions(rel_path, funcs)
    print()

    print("2. Checking that TODO stubs are implemented...")
    for rel_path in REQUIRED_MODULES:
        check_todo_stubs_removed(rel_path)
    print()

    print("3. Checking processed data splits...")
    check_splits_exist()
    print()

    print("4. Checking trained model...")
    check_model_exists()
    print()

    print("5. Checking evaluate.py output...")
    check_evaluate_output()
    print()

    print("6. Checking validate.py output...")
    check_validate_output()
    print()

    # Summary
    total = len(results)
    passed = sum(results)
    failed = total - passed
    print("=" * 60)
    print(f"  SUMMARY: {passed}/{total} checks passed, {failed} failed")
    if failed == 0:
        print("  All checks passed! Your Activity 1 is ready for submission.")
    else:
        print("  Some checks failed. Review the FAIL items above and fix them.")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
