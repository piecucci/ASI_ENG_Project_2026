#!/usr/bin/env python3
"""
Activity 2 Validator
====================
Run this script from the activity_2_containerize/ directory to verify
that your Dockerfile and Docker image meet all requirements.

Usage:
    cd activity_2_containerize
    uv run python check_activity.py

Prerequisites:
    - Docker must be installed and running.
    - You must have completed Activity 1 (working src/ files in starter/).
"""

import os
import subprocess
import sys

STARTER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "starter")
DOCKERFILE_PATH = os.path.join(STARTER_DIR, "Dockerfile")
IMAGE_NAME = "asi-project"

results = []


def check(name: str, passed: bool, detail: str = "") -> None:
    """Record a check result."""
    status = "PASS" if passed else "FAIL"
    msg = f"  [{status}] {name}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    results.append(passed)


def docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_dockerfile_exists() -> bool:
    """Check that the Dockerfile exists."""
    exists = os.path.isfile(DOCKERFILE_PATH)
    check("Dockerfile exists", exists)
    return exists


def check_dockerfile_not_template() -> bool:
    """Check that the Dockerfile has been filled in (not still the TODO template)."""
    if not os.path.isfile(DOCKERFILE_PATH):
        check("Dockerfile has a FROM instruction", False, detail="file missing")
        return False

    with open(DOCKERFILE_PATH, "r") as f:
        content = f.read()

    has_from = False
    for line in content.splitlines():
        stripped = line.strip()
        # Skip comments and empty lines
        if stripped.startswith("#") or not stripped:
            continue
        if stripped.upper().startswith("FROM "):
            has_from = True
            break

    check(
        "Dockerfile has a FROM instruction (not a template)",
        has_from,
        detail="" if has_from else "no uncommented FROM instruction found",
    )

    # Also check for other required instructions
    has_workdir = False
    has_copy = False
    has_run = False
    has_cmd = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        upper = stripped.upper()
        if upper.startswith("WORKDIR "):
            has_workdir = True
        if upper.startswith("COPY "):
            has_copy = True
        if upper.startswith("RUN "):
            has_run = True
        if upper.startswith("CMD "):
            has_cmd = True

    check("Dockerfile has WORKDIR instruction", has_workdir)
    check("Dockerfile has COPY instruction", has_copy)
    check("Dockerfile has RUN instruction", has_run)
    check("Dockerfile has CMD instruction", has_cmd)

    return has_from


def check_image_exists() -> bool:
    """Check that the Docker image has been built."""
    try:
        result = subprocess.run(
            ["docker", "images", "-q", IMAGE_NAME],
            capture_output=True,
            text=True,
            timeout=15,
        )
        image_exists = bool(result.stdout.strip())
        check(
            f"Docker image '{IMAGE_NAME}' exists",
            image_exists,
            detail="" if image_exists else "run: docker build -t asi-project .",
        )
        return image_exists
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        check(f"Docker image '{IMAGE_NAME}' exists", False, detail=str(e))
        return False


def check_container_run() -> bool:
    """Run the container and check that it produces RMSE and R2 output."""
    print("  Running container (this may take a minute)...")

    models_dir = os.path.join(STARTER_DIR, "models")
    data_dir = os.path.join(STARTER_DIR, "data")

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{models_dir}:/app/models",
                "-v", f"{data_dir}:/app/data",
                IMAGE_NAME,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            check(
                "Container runs without errors",
                False,
                detail=f"exit code {result.returncode}: {stderr[:300]}",
            )
            check("Container output contains RMSE", False, detail="container failed")
            check("Container output contains R2", False, detail="container failed")
            return False

        check("Container runs without errors", True)

        has_rmse = "RMSE:" in stdout
        has_r2 = "R2:" in stdout
        check(
            "Container output contains RMSE",
            has_rmse,
            detail=f"stdout: {stdout[:200]}" if not has_rmse else "",
        )
        check(
            "Container output contains R2",
            has_r2,
            detail=f"stdout: {stdout[:200]}" if not has_r2 else "",
        )

        has_validation = "VALIDATION" in stdout
        check(
            "Container output contains VALIDATION result",
            has_validation,
            detail=f"stdout: {stdout[:200]}" if not has_validation else "",
        )

        if has_rmse and has_r2:
            # Print just the evaluation lines
            eval_lines = [
                line for line in stdout.splitlines()
                if any(metric in line for metric in ["RMSE:", "R2:", "MAE:"])
            ]
            if eval_lines:
                print(f"\n  Container evaluation output:")
                for line in eval_lines:
                    print(f"    {line}")

        return has_rmse and has_r2

    except subprocess.TimeoutExpired:
        check("Container runs without errors", False, detail="timed out after 120s")
        return False
    except Exception as e:
        check("Container runs without errors", False, detail=str(e))
        return False


def check_model_created_via_mount() -> None:
    """Check that model.pkl was created on the host via the volume mount."""
    model_path = os.path.join(STARTER_DIR, "models", "model.pkl")
    exists = os.path.isfile(model_path)
    check(
        "models/model.pkl created on host via volume mount",
        exists,
        detail="" if exists else "file not found; check your -v mount path",
    )


def main() -> None:
    print("=" * 60)
    print("  Activity 2 Validator")
    print("=" * 60)
    print()

    # Pre-check: Docker available?
    if not docker_available():
        print("  [ERROR] Docker is not installed or not running.")
        print("  Install Docker Desktop: https://www.docker.com/products/docker-desktop/")
        print("  Then start Docker and re-run this script.")
        sys.exit(1)

    print("1. Checking Dockerfile...")
    dockerfile_exists = check_dockerfile_exists()
    dockerfile_valid = check_dockerfile_not_template() if dockerfile_exists else False
    print()

    print("2. Checking Docker image...")
    image_exists = check_image_exists()
    print()

    if image_exists:
        print("3. Running container and checking output...")
        check_container_run()
        print()

        print("4. Checking volume-mounted outputs...")
        check_model_created_via_mount()
        print()
    else:
        print("3. Skipping container run (image not built).")
        check("Container runs without errors", False, detail="image not built yet")
        check("Container output contains RMSE", False, detail="image not built yet")
        check("Container output contains R2", False, detail="image not built yet")
        print()
        print("4. Skipping volume mount check (image not built).")
        check("models/model.pkl created on host via volume mount", False, detail="image not built yet")
        print()

    # Summary
    total = len(results)
    passed = sum(results)
    failed = total - passed
    print("=" * 60)
    print(f"  SUMMARY: {passed}/{total} checks passed, {failed} failed")
    if failed == 0:
        print("  All checks passed! Your Activity 2 is ready for submission.")
    else:
        print("  Some checks failed. Review the FAIL items above and fix them.")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
