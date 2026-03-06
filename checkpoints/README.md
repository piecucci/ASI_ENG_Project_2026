# Checkpoints

## What Are Checkpoints?

Each activity in the ASI course builds on the output of the previous activity. If your Activity 2 submission is broken, you cannot start Activity 3. Checkpoints are your safety net.

A checkpoint is a **Git branch** containing the known-good output of a specific activity. It represents exactly what your project should look like after successfully completing that activity. If your previous activity's output is broken, incomplete, or missing, you can use a checkpoint to start the next activity from a clean, working state.

## Available Checkpoints

| Branch Name | Contains | Use Before Starting |
|-------------|----------|---------------------|
| `a1-checkpoint` | Completed Activity 1: modular `prepare.py`, `train.py`, `evaluate.py`, `validate.py`, saved splits, trained model | Activity 2 |
| `a2-checkpoint` | Completed Activity 2: working Dockerfile (runs prepare + train + evaluate + validate), containerized pipeline with exit code semantics | Activity 3 |
| `a3-checkpoint` | Completed Activity 3: `config.yaml`-driven pipeline with `validation.min_r2`, Makefile with validate/promote targets, `models/production_model.pkl` | Activity 4 |
| `a4-checkpoint` | Completed Activity 4: MLflow experiment tracking (5+ runs), `experiment_log.csv`, `mlruns/`, `models/production_model.pkl` (best model) | Activity 5 |

## How to Use a Checkpoint

### Option A: Starting fresh (no existing project)

Clone the repository and switch to the checkpoint branch:

```bash
git clone <repo-url>
cd asi-project
git checkout a1-checkpoint
```

Replace `a1-checkpoint` with whichever checkpoint you need.

### Option B: Replacing your broken project

If you have an existing project that is not working, you can reset to a checkpoint. **This will discard your current changes**, so back up any work you want to keep first:

```bash
# Back up your current work (optional)
cp -r asi-project asi-project-backup

# Switch to the checkpoint
cd asi-project
git checkout a1-checkpoint
```

### Option C: Starting a new branch from a checkpoint

If you want to keep your old work on a separate branch:

```bash
cd asi-project
git checkout a1-checkpoint
git checkout -b my-activity-2
```

This creates a new branch called `my-activity-2` based on the `a1-checkpoint` state, leaving your previous work untouched on its original branch.

## After Checking Out a Checkpoint

After switching to a checkpoint branch:

1. **Install dependencies** -- the checkpoint may have added new packages to `pyproject.toml`:
   ```bash
   uv sync
   ```

2. **Verify the pipeline works** by running the activity's check script or the pipeline commands described in that activity's instructions.

3. **Start the next activity** following its instructions normally.

## Important Notes

- **Use checkpoints without shame.** They exist specifically for the situation where something went wrong. Every professional software project has recovery mechanisms. Using a checkpoint is not cheating -- it is good engineering practice.

- **Checkpoints contain only the project state, not explanation.** If you want to understand what the code does, read the activity instructions for that checkpoint's activity.

- **The actual checkpoint branches will be created by the instructor** after the reference implementation for each activity is built and verified. If a checkpoint branch does not exist yet, it means that activity's reference has not been finalized.

- **Checkpoints are read-only reference points.** Do not push changes to a checkpoint branch. Always create your own branch for new work (as shown in Option C above).
