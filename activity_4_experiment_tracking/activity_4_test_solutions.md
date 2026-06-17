# Activity 4: Experiment Tracking Test — Solutions

---

## Question 1

**Answer: A — An experiment tracking system (e.g., MLflow) — it persistently logs parameters, metrics, and artifacts for every run, making them searchable and comparable after the fact**

**Explanation:** Terminal outputs are ephemeral — they get overwritten, scrolled away, or lost when the session closes. An experiment tracking system like MLflow is designed specifically for this: it records every run's parameters, metrics, and artifacts to a persistent backend, making them searchable, comparable, and recoverable long after the terminal is gone. Git tracks code changes (not runtime results), a longer scrollback just delays the inevitable, and a manual spreadsheet is error-prone and doesn't capture artifacts.

---

## Question 2

**Answer: D — The semantics are reversed: R2 is an output metric (should use `log_metric`), and learning_rate is an input parameter (should use `log_param`); swapping them makes filtering and comparison in the UI confusing and misleading**

**Explanation:** MLflow has two distinct concepts:
- **Parameters** (`log_param`): input configuration — things you set before running (learning_rate, n_estimators, model_type)
- **Metrics** (`log_metric`): output results — things you measure after running (R2, RMSE, MAE)

Swapping them works syntactically (both calls succeed) but breaks the MLflow UI: `learning_rate` won't appear in the Parameters column for filtering/comparison, and `r2_score` won't be available for metric comparison charts. The calls succeed because MLflow doesn't enforce the semantics — it trusts the user to use them correctly.

---

## Question 3

**Answer: B — `params.model_type = "GradientBoostingRegressor" AND metrics.r2 > 0.96` — parameters are prefixed with `params.` and metrics with `metrics.`, and the value must match exactly what was logged**

**Explanation:** MLflow's search syntax uses prefixes to distinguish between different namespaces:
- `params.` for parameters (values logged with `log_param`)
- `metrics.` for metrics (values logged with `log_metric`)
- `tags.` for tags
- `attributes.` for run attributes (status, artifact_uri, etc.)

The exact string value must match what was logged, including case — so if the model was logged as `"GradientBoostingRegressor"` (the actual sklearn class name), searching for `"GradientBoosting"` would not match.

---

## Question 4

**Answer: C — `learning_rate` appears in the Metrics column instead of the Parameters column — it cannot be used to filter runs by input configuration, it clutters metric comparison charts, and it misleads viewers into thinking learning rate is an output of the experiment rather than an input**

**Explanation:** Because `log_metric` stores values in the metrics namespace, `learning_rate` will appear alongside actual performance metrics (R2, RMSE) in charts and the Metrics column. This is confusing because:
1. A viewer can't distinguish inputs from outputs at a glance
2. The metric comparison charts are cluttered with non-metric values
3. You cannot filter by `params.learning_rate` since it was never logged as a parameter
4. It subtly communicates that learning_rate is something the model *produced* rather than something the experimenter *chose*

---

## Question 5

**Answer: B — They would have to ask the original author, search through chat messages, or guess from file timestamps — without MLflow, the decision context (which configs were tried, which metrics were compared, why this model won) is tribal knowledge that leaves with the person who made the decision**

**Explanation:** Without an experiment tracking system:
- `git log` only shows code changes, not experiment results
- `config.yaml` might show the final configuration but not what was tried and rejected
- Retraining all models is expensive and may not be reproducible
- The decision rationale (e.g., "GradientBoosting was chosen over RandomForest because it had better test-set R2 and was faster to tune") is nowhere in the file system

MLflow solves this by persistently recording every experiment attempt alongside its results, making the decision context discoverable even months later by someone who wasn't in the room.

---

## Question 6

**Answer: B — MLflow stores artifacts (model files, plots, configs) alongside metrics, provides a programmatic API for querying runs, and automatically logs run metadata (timestamp, git commit, user) — spreadsheets only store the numbers you manually enter**

**Explanation:** A spreadsheet can replicate some of MLflow's tabular functionality (comparing metrics in columns), but cannot:
1. Store and retrieve the actual model files (`.pkl`), training plots, and configuration files alongside the metrics
2. Provide a programmatic API (`MlflowClient().search_runs(...)`) for automated experiment retrieval
3. Auto-capture metadata like git commit hash, run timestamp, and who ran the experiment
4. Serve as a model registry for production deployment tracking

A spreadsheet requires manual data entry, is disconnected from the actual model artifacts, and has no API.

---

## Question 7

**Answer: D — Each scientist has a local `mlruns` directory — experiments are not shared; they cannot see each other's runs or compare results across the team without manually copying directories**

**Explanation:** The `file:` tracking URI stores MLflow data in a local directory. When Team Member A logs runs on their laptop, the data goes to `~/mlruns/` on their machine. Team Member B's runs go to `~/mlruns/` on their own laptop. Neither can see the other's experiments.

To share experiments across a team, you need a shared backend like:
- **SQLite + shared filesystem** (NFS, network drive)
- **PostgreSQL/MySQL** (database backend)
- **Databricks tracking server** (hosted)
- **Self-hosted MLflow tracking server** (HTTP backend)

The `file:` backend is fine for individual exploration but breaks down for team collaboration.

---

## Question 8

**Answer: C — The tag on the run links the production model back to its exact parameters, metrics, training data version, and artifacts — the new team member can trace the complete lineage of the production model from a single MLflow query**

**Explanation:** When you tag a run (e.g., `mlflow.set_tag("production_stage", "production")`), MLflow preserves the full context:
- All input parameters (learning_rate, n_estimators, model_type, etc.)
- All output metrics (R2, RMSE, MAE on training and test sets)
- All artifacts (model.pkl, confusion matrices, feature importance plots)
- Run metadata (timestamp, git commit, user)

A new team member can open the MLflow UI, find the tagged run, and immediately see exactly what configuration produced the production model, how it performed, and what code version was used. No tribal knowledge required.

---

## Question 9

**Answer: B — 4 runs — the 4 non-linear models (RF50, RF100, GB_default, GB_tuned) all have R2 > 0.95; LinearRegression (R2=0.8324) is excluded**

**Explanation:** Based on the Activity 4 experiment results:
- RF50: R2=0.9562 — passes
- RF100: R2=0.9579 — passes
- GB_default: R2=0.9703 — passes
- GB_tuned: R2=0.9664 — passes
- LinearRegression: R2=0.8324 — fails (0.8324 < 0.95)

So 4 out of 5 runs satisfy `metrics.r2 > 0.95`. The linear regression model, while not terrible, falls well below the non-linear models' performance and is excluded by the filter.

---

## Question 10

**Answer: A — The model is experiencing drift — real-world data has changed since training, but nothing monitors the production model's performance on new data; a drift detection and closed-loop retraining system is needed (Activity 5)**

**Explanation:** This is the classic concept of **model drift** (or concept drift):
- **Training data** represents the world at the time of training (6 months ago)
- **Real-world data** has shifted — customer behavior, economic conditions, seasonal patterns, etc.
- The model's internal weights haven't changed (MLflow still shows R2=0.9703 on the original test set)
- But the model's performance on *today's* data has degraded

MLflow tracks the static experiment results — it is not a monitoring system. Activity 5 introduces production monitoring, drift detection, and automated retraining to close the loop. Without this, you won't know the model has degraded until customers complain.
