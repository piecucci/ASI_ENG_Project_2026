"""
MLflow Tracking Integration Snippet
------------------------------------
Copy the relevant parts into your train.py and/or evaluate.py.

MLflow stores all data locally in ./mlruns/ directory.
View results with: uv run mlflow ui (then open http://localhost:5000)

Key concepts:
  - Tracking URI:  where MLflow stores run data (local filesystem here)
  - Experiment:    a named group of related runs
  - Run:           one execution of your pipeline with specific parameters
  - Parameter:     an input to the experiment (model type, learning rate, etc.)
  - Metric:        an output of the experiment (RMSE, R2, MAE, etc.)
  - Artifact:      a file produced by the run (trained model, plots, etc.)
"""
import mlflow
import yaml

# ---------------------------------------------------------------------------
# 1. Configure MLflow -- put this near the top of your script
# ---------------------------------------------------------------------------

# Store tracking data in a local directory (no server needed)
mlflow.set_tracking_uri("file:./mlruns")

# Create or select an experiment by name
mlflow.set_experiment("asi-project")

# ---------------------------------------------------------------------------
# 2. Load your project config -- you already have this from Activity 3
# ---------------------------------------------------------------------------

with open("config.yaml") as f:
    config = yaml.safe_load(f)

# ---------------------------------------------------------------------------
# 3. Start a run and log everything
# ---------------------------------------------------------------------------

with mlflow.start_run(run_name=f"{config['model']['type']}"):

    # Log parameters (from config.yaml)
    mlflow.log_param("model_type", config["model"]["type"])
    for param_name, param_value in config["model"].get("params", {}).items():
        mlflow.log_param(param_name, param_value)
    mlflow.log_param("test_size", config["dataset"]["test_size"])
    mlflow.log_param("random_state", config["dataset"]["random_state"])

    # ------------------------------------------------------------------
    # YOUR TRAINING AND EVALUATION CODE GOES HERE
    # ------------------------------------------------------------------
    # Example (replace with your actual code):
    #
    # from src.train import load_splits, train_model, save_model
    # from src.evaluate import load_model, load_test_data, evaluate_model
    #
    # X_train, y_train = load_splits(config["dataset"]["processed_dir"])
    # model = train_model(X_train, y_train)
    # save_model(model, config["output"]["model_path"])
    #
    # model = load_model(config["output"]["model_path"])
    # X_test, y_test = load_test_data(config["dataset"]["processed_dir"])
    # metrics = evaluate_model(model, X_test, y_test)
    # ------------------------------------------------------------------

    # Log metrics (after evaluation)
    # mlflow.log_metric("rmse", metrics["rmse"])
    # mlflow.log_metric("r2", metrics["r2"])
    # mlflow.log_metric("mae", metrics["mae"])

    # Log the trained model file as an artifact
    # mlflow.log_artifact(config["output"]["model_path"])

    pass  # Remove this line when you add your actual code

# ---------------------------------------------------------------------------
# 4. View your results
# ---------------------------------------------------------------------------
# Run this command in your terminal (from the project root):
#
#   uv run mlflow ui
#
# Then open http://localhost:5000 in your browser.
# If port 5000 is in use (common on macOS), try:
#
#   uv run mlflow ui --port 5001
#

# ---------------------------------------------------------------------------
# 5. Optional: MLflow Model Registry (stretch goal)
# ---------------------------------------------------------------------------
# To use the model registry, change the tracking URI to a SQLite backend:
#
#   mlflow.set_tracking_uri("sqlite:///mlflow.db")
#
# Then log and register the model inside your run:
#
#   mlflow.sklearn.log_model(model, "model", registered_model_name="asi-project")
#
# After running all experiments, promote the best model:
#
#   from mlflow.tracking import MlflowClient
#   client = MlflowClient()
#   # Find the version with the best R2
#   client.transition_model_version_stage(
#       name="asi-project",
#       version=best_version,  # replace with actual version number
#       stage="Production"
#   )
#
# This is entirely optional. The file-based approach (cp model.pkl
# production_model.pkl) teaches the same promotion concept.
