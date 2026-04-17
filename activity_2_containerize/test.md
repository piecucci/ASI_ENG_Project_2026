# Activity 2: Containerization Knowledge Test

## Question 1
An ML pipeline produces `R2=0.8324` on macOS with Python 3.11.4 and scikit-learn 1.3.0. The same code on a CI server (Ubuntu, Python 3.11.7, scikit-learn 1.3.2) produces `R2=0.8301`. What category of problem is this?
- [ ] A bug in scikit-learn — different versions should never produce different results
- [ ] The macOS result is wrong — Linux results are always more accurate
- [ ] The CI server has less RAM, causing rounding errors
- [ ] An environment reproducibility problem — different OS, Python patch version, and library versions can cause numerical differences even with `random_state=42` fixed

## Question 2
The Dockerfile uses `CMD "python src/prepare.py && python src/train.py && python src/evaluate.py && python src/validate.py"`. `prepare.py` exits with code 1 due to a missing data file. Which scripts run, and what is the container's exit code?
- [ ] All four scripts run — `&&` in Docker CMD means "and also run"
- [ ] Only `prepare.py` runs; the `&&` operator short-circuits on exit code 1, so train, evaluate, and validate never execute; the container exits with code 1
- [ ] `prepare.py` and `train.py` run, then the chain stops
- [ ] The container hangs waiting for the missing file

## Question 3
The containerized pipeline runs successfully and `model.pkl` is saved inside the container. After `docker rm`, the model file is gone. What should have been done?
- [ ] Used a volume mount (`-v ./models:/app/models`) to map the container's model output directory to the host filesystem, so files persist after container removal
- [ ] Used `docker commit` to save the container state as a new image
- [ ] Used `docker export` to extract files before removing the container
- [ ] Rebuilt the Docker image — the model is cached in the image layers

## Question 4
The containerized pipeline produces `R2=0.8324` — identical to the local Activity 1 result. What specifically has this match proven?
- [ ] That Docker makes models more accurate
- [ ] That the model is correct and ready for production
- [ ] That the container reproduces the exact same environment as local execution — same Python, same libraries, same numerical results — confirming environment-level reproducibility
- [ ] That Docker adds no value — the results would be identical without it

## Question 5
A CI pipeline runs: `docker run asi-project && bash deploy.sh`. The container's `validate.py` finds `R2=0.75` (below threshold 0.80) and exits with code 1. What happens to deployment?
- [ ] `deploy.sh` runs anyway — CI pipelines always execute all steps
- [ ] `deploy.sh` never runs — the shell `&&` operator stops on the container's non-zero exit code, preventing deployment of a subpar model
- [ ] `deploy.sh` runs but with a warning flag
- [ ] The CI system retries the Docker run 3 times before giving up

## Question 6
In the same CI scenario, the container's R2 is 0.8324 (above threshold 0.80) and exits with code 0. `deploy.sh` runs. The CFO asks: "What guarantee does exit code 0 give me?" What is the accurate answer?
- [ ] "Exit code 0 means the model is perfect and will never make wrong predictions"
- [ ] "Exit code 0 guarantees the model will perform identically in production on new data"
- [ ] "Exit code 0 means Docker ran without errors — it says nothing about model quality"
- [ ] "Exit code 0 means the model met the minimum R2 threshold we defined — it passed our quality gate, but the threshold itself is a business decision about acceptable risk"

## Question 7
A Docker image is 900MB (using `python:3.11`). Rebuilding with `python:3.11-slim` produces 150MB with identical pipeline results. When would the 900MB image be necessary?
- [ ] When the pipeline needs to compile C extensions during the Docker build (e.g., packages requiring `gcc`), which slim images don't include
- [ ] When deploying to production — larger images are more reliable
- [ ] When the model needs more memory at runtime — image size determines available RAM
- [ ] Never — always use the smallest image

## Question 8
The Dockerfile's CMD chains 4 scripts: prepare → train → evaluate → validate. Why not call them all from a single `run_all.py` wrapper script?
- [ ] CMD chains run faster than Python function calls
- [ ] Docker cannot execute Python scripts directly — only shell commands
- [ ] Each script is an independent process with its own exit code; if train.py crashes, the shell reports exactly which step failed and the container's exit code reflects that failure — a Python wrapper requires explicit try/except to achieve the same
- [ ] CMD chains allow parallel execution of all 4 scripts

## Question 9
A Dockerfile installs dependencies with `uv sync`. Another approach uses `pip install -r requirements.txt`. Both achieve the same installed packages. What advantage does uv provide inside Docker specifically?
- [ ] `uv` produces smaller Docker images than `pip`
- [ ] `uv` resolves and installs packages significantly faster than `pip`, which directly reduces Docker build time — especially important when the dependency cache is invalidated
- [ ] `pip` cannot install packages inside Docker containers
- [ ] `uv` automatically creates a virtual environment; `pip` does not

## Question 10
An IT manager says: "I want a one-command pipeline that either fully succeeds or fully fails — no partial states." How does the Dockerfile's `CMD` chain with `&&` satisfy this requirement?
- [ ] The `&&` chain ensures atomic-like behavior: if any step fails, all subsequent steps are skipped and the container reports failure; success means every step completed — prepare, train, evaluate, and validate all passed
- [ ] It doesn't — partial states are still possible if the machine loses power mid-execution
- [ ] Docker automatically rolls back partial executions to a clean state
- [ ] The `CMD` runs all scripts in a transaction like a database
