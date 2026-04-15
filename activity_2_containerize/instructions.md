# Activity 2: Containerize the Pipeline

## Prerequisite

A fully working Activity 1. You must be able to run:

```bash
cd starter
uv run python src/prepare.py
uv run python src/train.py
uv run python src/evaluate.py
```

and see RMSE, R2, and MAE printed to stdout. If you do not have a working
Activity 1, use the `a1-checkpoint` branch provided by the instructor.

## Objective

Package your ML pipeline from Activity 1 into a Docker container so that it can
run reproducibly on any machine, regardless of the local Python version or
installed packages.

## Context

Hawkeye Spirits' CFO, Jordan Hayes, is impressed with the modular pipeline — but
there's a problem. The IT team can't run Jupyter notebooks or rely on your
specific laptop setup. They need the pipeline to run identically on any machine.

> *"IT can't run Jupyter notebooks. Package this so it runs anywhere."* — Jordan Hayes, CFO

Docker solves this by packaging your code, dependencies, and runtime into a
single portable image. In this activity you will write a Dockerfile that builds
an image containing your entire ML pipeline. When you run a container from this
image, it will execute `prepare.py`, `train.py`, `evaluate.py`, **and
`validate.py`** in sequence. The container's exit code tells you whether the
model passed validation: exit code 0 means the model is good, exit code 1 means
it failed the quality gate.

## What You Receive

| Item | Location | Description |
|------|----------|-------------|
| Your A1 project | `starter/` | Working pipeline with `src/`, `data/raw/`, `pyproject.toml` |
| Dockerfile | `starter/Dockerfile` | A skeleton Dockerfile with commented-out instructions |
| Check script | `check_activity.py` | Automated validator you run before submitting |

## What You Deliver

1. A completed `Dockerfile` inside `starter/`.
2. A successfully built Docker image tagged `asi-project`.
3. A container run that produces the same RMSE/R2 as your local execution and
   prints VALIDATION PASSED, exiting with code 0.

The two key commands:

```bash
cd starter
docker build -t asi-project .
docker run -v "$(pwd)/models:/app/models" -v "$(pwd)/data:/app/data" asi-project
# Check exit code:
docker run -v "$(pwd)/models:/app/models" -v "$(pwd)/data:/app/data" asi-project && echo "PASSED" || echo "FAILED"
```

## Key Concepts

Before starting, make sure you understand these Docker concepts:

### Image vs. Container

- An **image** is a read-only blueprint (like a class). You build it once with
  `docker build`.
- A **container** is a running instance of an image (like an object). You create
  one with `docker run`.

### Base Image

Every Dockerfile starts with `FROM <base-image>`. For Python projects,
`python:3.11-slim` is a good choice: it includes a full Python interpreter but
omits unnecessary OS packages, keeping the image small (~150 MB vs. ~900 MB for
the full image).

### Layer Caching

Docker builds images in layers. Each instruction (`FROM`, `COPY`, `RUN`, etc.)
creates a new layer. Docker caches layers and re-uses them if the input has not
changed. This is why you should:
1. **Copy the dependency file (`pyproject.toml`) first** and install
   dependencies.
2. **Copy the rest of the code second.**

If you only change your Python code, Docker re-uses the cached dependency layer
and skips the slow `pip install` step. If you copy everything at once, any code
change invalidates the dependency cache and forces a full reinstall.

### Bind Mounts

By default, files created inside a container disappear when the container
stops. To persist outputs (like `models/model.pkl` and `data/processed/*.csv`),
you use **bind mounts**:

```bash
-v "$(pwd)/models:/app/models"
```

This maps your local `models/` directory to `/app/models` inside the container.
Any file the container writes to `/app/models` appears in your local `models/`
folder.

### WORKDIR

`WORKDIR /app` sets the working directory inside the container. All subsequent
`COPY`, `RUN`, and `CMD` instructions execute relative to `/app`. It is similar
to `cd /app` in a shell.

### Exit Code Semantics

Every process returns an **exit code** when it finishes:
- **Exit code 0**: Success. The pipeline ran and the model passed validation.
- **Exit code 1** (or any non-zero): Failure. Something went wrong, or the
  model failed the quality gate.

In CI/CD systems, the exit code determines what happens next. A container that
exits with code 0 triggers deployment; a container that exits with code 1 halts
the pipeline. Your `validate.py` script already uses this convention:
`sys.exit(0)` if R2 >= threshold, `sys.exit(1)` otherwise.

You can test this from the command line:
```bash
docker run ... asi-project && echo "SUCCESS: Model passed validation" || \
  echo "FAILURE: Model failed validation"
```

This one-liner runs the container and prints SUCCESS if exit code is 0,
FAILURE otherwise.

## Step-by-Step Instructions

### Step 1: Verify Docker Is Installed

```bash
docker run hello-world
```

You should see "Hello from Docker!" If not, install Docker Desktop from
[docker.com](https://www.docker.com/products/docker-desktop/) before proceeding.

### Step 2: Copy Your A1 Project

If you are starting fresh, copy your completed Activity 1 `starter/` directory
into this activity's `starter/` folder. If you are continuing in the same
repository, your code is already in place. Make sure the directory structure
looks like this:

```
starter/
├── Dockerfile          <-- you will complete this
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── prepare.py
│   ├── train.py
│   └── evaluate.py
├── data/
│   └── raw/
│       └── iowa_liquor_train.csv
└── models/
```

### Step 3: Examine the Dockerfile

Open `starter/Dockerfile`. You will see a skeleton with TODO comments. Each
TODO corresponds to a single Dockerfile instruction you need to fill in.

### Step 4: Complete the Dockerfile

Fill in each TODO:

1. **`FROM`**: Choose a base image. Use `python:3.11-slim` for a lightweight
   Python runtime.

2. **`WORKDIR`**: Set the working directory to `/app`. All subsequent paths
   will be relative to this.

3. **First `COPY`**: Copy only `pyproject.toml` into the container. This is for
   layer caching -- dependencies change rarely, code changes often.

4. **`RUN`**: Install `uv` and then install the project dependencies. Two
   approaches work:
   - `pip install uv && uv sync` (installs uv via pip, then uses uv to install
     deps)
   - `pip install -r <requirements>` (if you exported a requirements file)

   The recommended approach for this project:
   ```dockerfile
   RUN pip install --no-cache-dir uv && uv sync
   ```

5. **Second `COPY`**: Copy the rest of the project files (`. .` copies
   everything from the build context into `/app`).

6. **`CMD`**: Set the default command to run all four pipeline steps in
   sequence:
   ```dockerfile
   CMD uv run python src/prepare.py && uv run python src/train.py && \
       uv run python src/evaluate.py && uv run python src/validate.py
   ```
   The `&&` operator ensures each step runs only if the previous one
   succeeded. If `validate.py` fails (exit code 1), the container exits with
   code 1.

### Step 5: Build the Image

```bash
cd starter
docker build -t asi-project .
```

Watch the output. If a step fails, read the error message, fix the Dockerfile,
and rebuild. Docker caches successful layers, so rebuilds are fast.

### Step 6: Run with Volume Mounts

```bash
docker run -v "$(pwd)/models:/app/models" -v "$(pwd)/data:/app/data" \
  asi-project
```

This runs the full pipeline inside the container. The `-v` flags ensure that:
- The trained model (`model.pkl`) is written to your local `models/` directory.
- The processed data splits are written to your local `data/processed/`
  directory.

You should see the same RMSE, R2, and MAE values as your local run.

### Step 7: Verify Output Matches

Compare the Docker output with your local output:

```bash
# Local run (from Step 7 of Activity 1)
uv run python src/evaluate.py

# Docker run (from the previous step's output)
```

The RMSE, R2, and MAE values must be identical.

### Step 8: Run the Check Script

```bash
cd ..
uv run python check_activity.py
```

All checks should show PASS. Fix any failures before submitting.

## Estimated Time

60-90 minutes (assumes Docker is already installed from homework zero).

## Hints

- **Layer caching saves time**: If you only change `src/evaluate.py`, Docker
  re-uses the cached layers for `FROM`, `COPY pyproject.toml`, and
  `RUN pip install`. Only the `COPY . .` layer and beyond are rebuilt. This
  turns a 2-minute build into a 5-second rebuild.
- **Use shell form for CMD**: The exec form `CMD ["cmd", "arg1", ...]` does not
  support shell operators like `&&`. Use the shell form
  `CMD cmd1 && cmd2 && cmd3` instead.
- **`.dockerignore`**: If your build context is large (e.g., many `.mp4`
  files), create a `.dockerignore` file to exclude them. For this activity it
  is optional since the project is small.
- **Volume mount paths must be absolute on the host**: `$(pwd)/models`
  expands to an absolute path. Do not use relative paths in `-v` flags.
- **If the container fails**: Run it interactively to debug:
  ```bash
  docker run -it -v "$(pwd)/models:/app/models" \
    -v "$(pwd)/data:/app/data" asi-project /bin/bash
  ```
  This drops you into a shell inside the container where you can run commands
  manually.

## Common Mistakes

1. **Forgetting to copy data**: The raw CSV file must be present inside the
   image or mounted via a volume. Since we `COPY . .`, the
   `data/raw/iowa_liquor_train.csv` file is included in the image.
2. **Wrong `WORKDIR`**: If your `WORKDIR` is not `/app`, the relative paths in
   your Python code (e.g., `"data/raw/..."`) will not resolve correctly.
3. **Using exec form for multi-command CMD**:
   `CMD ["python", "src/prepare.py", "&&", "python", "src/train.py"]` does
   not work -- `&&` is interpreted as a literal argument, not a shell operator.
4. **Not mounting volumes**: Without `-v` flags, the model and processed data
   exist only inside the container and disappear when it stops.
5. **Building from the wrong directory**: Run `docker build` from the
   `starter/` directory (where the Dockerfile lives), not from the parent
   directory.
