# ASI — AI Systems Architectures

## Course Overview

You are a junior ML engineer at **Hawkeye Spirits**, a fictional Iowa liquor distributor. The company's data scientist built a sales prediction model in a Jupyter notebook. Your job across five activities is to take that model from a messy notebook to a production-ready, monitored ML system.

Each activity builds on the previous one, following a realistic MLOps progression:

| # | Activity | What You Learn | Estimated Time |
|---|----------|---------------|----------------|
| 0 | [Environment Setup](activity_0_setup/instructions.md) | Install `uv`, Docker, Git | 30–60 min |
| 1 | [Modularize a Notebook](activity_1_modularize/instructions.md) | Refactor a notebook into `prepare.py`, `train.py`, `evaluate.py`, `validate.py` | 90–120 min |
| 2 | [Containerize the Pipeline](activity_2_containerize/instructions.md) | Write a Dockerfile, build and run a reproducible container | 60–90 min |
| 3 | [Orchestrate with Make & Config](activity_3_orchestrate/instructions.md) | Create a `Makefile` and `config.yaml`, add tests and a promotion gate | 90–120 min |
| 4 | [Track Experiments with MLflow](activity_4_track/instructions.md) | Log parameters, metrics, and artifacts; compare model variants | 60–90 min |
| 5 | [Detect Drift and Retrain](activity_5_drift/instructions.md) | Monitor model on COVID-era data, detect drift, retrain, validate, and promote | 90–120 min |

Read the [Hawkeye Spirits brief](hawkeye_spirits_brief.md) and the [data dictionary](dataset/data_dictionary.md) before starting Activity 1 — they provide the business context and column documentation used throughout the course.

## Prerequisites

Complete **Activity 0** before the first lab. You need three tools installed and working:

- **[uv](https://docs.astral.sh/uv/)** — Python package and environment manager (replaces pip, venv, pyenv)
- **[Docker](https://www.docker.com/products/docker-desktop/)** — container runtime
- **[Git](https://git-scm.com/)** — version control

No cloud accounts are required. Everything runs on your local machine.

## Repository Structure

```
.
├── activity_0_setup/          # Environment setup (not graded)
│   └── instructions.md
├── activity_1_modularize/     # Notebook → modular Python scripts
│   ├── instructions.md
│   ├── check_activity.py      # Automated validator
│   ├── notebook/              # Messy reference notebook
│   └── starter/               # Project skeleton with TODO stubs
├── activity_2_containerize/   # Docker containerization
│   ├── instructions.md
│   ├── check_activity.py
│   └── starter/               # Dockerfile skeleton
├── activity_3_orchestrate/    # Makefile + config.yaml + tests
│   ├── instructions.md
│   ├── check_activity.py
│   └── starter/               # Makefile and config templates
├── activity_4_track/          # MLflow experiment tracking
│   ├── instructions.md
│   ├── check_activity.py
│   └── starter/               # MLflow integration snippet
├── activity_5_drift/          # Drift detection and retraining
│   ├── instructions.md
│   ├── check_activity.py
│   └── starter/               # detect_drift.py skeleton
├── dataset/                   # Shared dataset and documentation
│   ├── data_dictionary.md
│   ├── iowa_liquor_train.csv
│   ├── iowa_liquor_drift_test.csv
│   └── iowa_liquor_holdout.csv
├── checkpoints/               # Safety net branches (see below)
│   └── README.md
└── hawkeye_spirits_brief.md   # Business scenario
```

## How to Work Through the Activities

### 1. Read the instructions

Each activity folder contains an `instructions.md` with detailed step-by-step guidance, pinned values, hints, and common mistakes. Read the full document before writing any code.

### 2. Implement in the starter

Each activity provides a `starter/` directory with skeleton files containing TODO stubs. Fill in the implementations following the instructions. Do not change function signatures, file names, or pinned values.

### 3. Run the check script

Every activity (except Activity 0) includes a `check_activity.py` validator. Run it before considering the activity complete:

```bash
uv run python check_activity.py
```

All checks must show **PASS**. The check script tells you exactly what failed and why.

### 4. Take the test on Edux

After completing each activity, take the corresponding test on the **Edux** platform.

## Assessment

Each activity is assessed through a separate **online test on Edux**:

| | Details |
|---|---|
| **Format** | Multiple-choice, 4 options per question, exactly 1 correct answer |
| **Questions** | 10 per activity |
| **Scoring** | +1 point for a correct answer, 0 points for a wrong answer (no negative points) |
| **Time window** | 48 hours from the moment the test opens |
| **Total** | 5 tests × 10 questions = 50 points maximum |

The questions are based on the work you do in each activity — the exact metric values your pipeline produces, the concepts you apply, and the decisions you make. **Record your metric values** (RMSE, R2, MAE, drift months, model versions, etc.) as you work. You will need them to answer the test questions.

## Checkpoints

Activities are sequential — each one builds on the output of the previous. If your Activity N is broken, you cannot start Activity N+1.

**Checkpoints are your safety net.** Each checkpoint is a Git branch containing the known-good output of a completed activity:

| Branch | Use Before Starting |
|--------|---------------------|
| `a1-checkpoint` | Activity 2 |
| `a2-checkpoint` | Activity 3 |
| `a3-checkpoint` | Activity 4 |
| `a4-checkpoint` | Activity 5 |

To use a checkpoint:

```bash
git checkout a4-checkpoint   # replace with the checkpoint you need
uv sync                      # install any new dependencies
```

See [checkpoints/README.md](checkpoints/README.md) for detailed usage instructions.

Using a checkpoint is not cheating — it is good engineering practice. Every professional project has recovery mechanisms.

## The Dataset

**Iowa Liquor Sales** aggregated to the store–category–month level. One row = one store + one category + one month.

| Split | File | Years | Rows |
|-------|------|-------|------|
| Train | `iowa_liquor_train.csv` | 2017–2019 | 20,916 |
| Drift | `iowa_liquor_drift_test.csv` | 2020–2021 | 13,944 |
| Holdout | `iowa_liquor_holdout.csv` | 2022–2023 | 13,944 |

The prediction target is **`total_sales`** (total dollar sales for a store-category-month combination).

The 2020–2021 data exhibits distributional shift due to the COVID-19 pandemic (bar closures, stockpiling, category mix changes), making it a natural test set for drift detection in Activity 5.

See [dataset/data_dictionary.md](dataset/data_dictionary.md) for the full column reference.

## Technology Stack

| Tool | Purpose |
|------|---------|
| **Python 3.11** | Programming language |
| **uv** | Package and environment management |
| **scikit-learn** | Model training and evaluation |
| **pandas / numpy** | Data manipulation |
| **joblib** | Model serialization |
| **Docker** | Containerization (Activity 2) |
| **Make** | Pipeline orchestration (Activity 3+) |
| **PyYAML** | Configuration management (Activity 3+) |
| **pytest** | Testing (Activity 3+) |
| **MLflow** | Experiment tracking (Activity 4+) |

## Quick Reference: Key Commands

```bash
# Environment setup
uv sync                                    # Install dependencies

# Activity 1: Run the pipeline
uv run python src/prepare.py
uv run python src/train.py
uv run python src/evaluate.py
uv run python src/validate.py

# Activity 2: Docker
docker build -t asi-project .
docker run -v "$(pwd)/models:/app/models" -v "$(pwd)/data:/app/data" asi-project

# Activity 3+: Makefile
make all                                   # Run full pipeline
make clean                                 # Remove generated artifacts
make test                                  # Run tests

# Activity 5: Drift detection
uv run python src/detect_drift.py

# Validation (all activities)
uv run python check_activity.py
```
