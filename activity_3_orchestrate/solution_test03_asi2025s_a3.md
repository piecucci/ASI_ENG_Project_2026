# Activity 3: Orchestrate a Pipeline — Test & Solutions

## References

All answers are grounded in:
- **Instructions**: `activity_3_orchestrate/instructions.md`
- **Makefile**: `asi-project/Makefile`
- **Config**: `asi-project/config.yaml`
- **Scripts**: `train.py` (MODEL_MAP pattern), `validate.py` (quality gate), `evaluate.py` (experiment logging)
- **Experiment log**: `asi-project/experiment_log.csv`

---

## Question 1

**In the old workflow, changing from LinearRegression to RandomForest requires editing `train.py`. In the config-driven workflow, only `config.yaml` is edited. Why is the config approach better?**

- YAML files execute faster than Python code changes
- Python cannot instantiate models from strings — only YAML can
- **✅ Config changes don't risk introducing code bugs, are trivially reversible, and create an auditable history of what was tried — code changes require testing, review, and risk breaking the pipeline**
- Editing Python files requires recompiling the code

### Step-by-step Explanation

1. **Code changes carry risk.** When you edit `train.py` to swap a model, you might accidentally introduce a syntax error, break an import, or change logic unintentionally. Config changes (editing a YAML value) cannot introduce code bugs — the Python code stays untouched.

2. **Reversibility.** Reverting a YAML change is trivial: change one string back. Reverting a code change requires understanding what exactly was modified, and might involve git operations.

3. **Audit trail.** With config-driven experiments, the YAML file is the single source of truth for "what was tried." You can version-control `config.yaml` and see a clean history of experiment configurations. Code diffs are noisier and harder to audit.

4. **Why the other options are wrong:**
   - YAML is a data format — it doesn't "execute" and has no speed advantage.
   - Python absolutely can instantiate models from strings — the `MODEL_MAP` dictionary in `train.py` does exactly this.
   - Python is interpreted, not compiled — there is no "recompilation" step.

---

## Question 2

**A Makefile defines: `all: prepare train evaluate validate promote`. Running `make all` causes `validate` to fail (exit code 1) because R2 is below threshold. What happens to `promote`?**

- `promote` runs anyway — `make all` executes all listed targets regardless
- **✅ `promote` never runs — Make halts on the first target that returns a non-zero exit code, and `validate` failed before `promote`**
- `promote` runs but with a warning message
- Make retries `validate` three times before skipping to `promote`

### Step-by-step Explanation

1. **Make's error handling rule:** When a recipe command returns a non-zero exit code, Make considers the target **failed** and immediately stops execution. It does not continue to subsequent targets.

2. **In our Makefile**, the dependency chain is: `all: prepare train evaluate validate promote`. Make runs them left-to-right. When `validate` runs `validate.py` and it calls `sys.exit(1)` because R2 < `min_r2`, Make receives exit code 1.

3. **Make halts immediately.** The `promote` target (which copies `model.pkl` → `production_model.pkl`) is never reached. This is the **quality gate** pattern: a failing validation prevents bad models from being promoted.

4. **This mirrors CI/CD behavior:** just like a failing test stops deployment in a CI/CD pipeline, a failing validation stops model promotion in our Makefile pipeline.

---

## Question 3

**A Makefile has: `promote: validate` and `validate: evaluate`. Running `make promote` triggers which targets, in what order?**

- Only `promote` — Make runs the requested target directly
- All three run simultaneously in parallel
- `promote`, then `validate`, then `evaluate` — Make runs in reverse order
- **✅ `evaluate` first, then `validate`, then `promote` — Make resolves the dependency chain backward from the requested target**

### Step-by-step Explanation

1. **Make builds a dependency graph.** When you request `make promote`, Make looks at `promote`'s prerequisites: `validate`. Then it looks at `validate`'s prerequisites: `evaluate`. It continues recursively until it finds targets with no prerequisites.

2. **Execution order is bottom-up.** Make resolves dependencies from the leaves of the graph upward to the requested target:
   - `evaluate` runs first (no unsatisfied prerequisites)
   - `validate` runs second (its prerequisite `evaluate` is now satisfied)
   - `promote` runs last (its prerequisite `validate` is now satisfied)

3. **This is analogous to the `all` target.** In our Makefile: `all: prepare train evaluate validate promote` — Make resolves the full chain because each target depends on the previous one.

4. **Make never runs targets "in reverse."** Dependencies define what must happen *before*, not after. The execution order always respects the dependency chain.

---

## Question 4

**Two engineers both run `make all` with identical `config.yaml` files and the same code, but get slightly different R2 values (0.8324 vs 0.8301). What is the most likely cause?**

- Make introduces random variation when running targets
- **✅ They are running on different environments (different OS, Python patch version, or library versions) — Make orchestrates execution order but does not guarantee environment reproducibility; that is Docker's job**
- One engineer ran `make clean` first and the other did not
- The `config.yaml` files are not actually identical — YAML is whitespace-sensitive

### Step-by-step Explanation

1. **Make orchestrates order, not environment.** The Makefile ensures `prepare → train → evaluate → validate → promote` runs in sequence. It does nothing to ensure both engineers have the same Python version, scikit-learn version, or OS-level numerical libraries (e.g., BLAS/LAPACK implementations).

2. **Numerical differences across environments.** Floating-point operations can produce slightly different results on different hardware (x86 vs ARM), OS versions, or library builds. Scikit-learn's internal optimizations may vary across patch versions.

3. **This is exactly why Activity 2 (Containerize) exists.** Docker pins the base image, Python version, and all library versions. Running inside the same Docker image guarantees byte-identical results.

4. **Why other options are wrong:**
   - Make itself introduces zero randomness — it just runs shell commands.
   - `make clean` would cause failures (missing files), not slight numeric differences.
   - YAML is **not** whitespace-sensitive for values (only for structure/indentation).

---

## Question 5

**`make clean` deletes `data/processed/`, `models/model.pkl`, and `experiment_log.csv`. A colleague argues this is dangerous: "What if I accidentally lose my best model?" How should the pipeline structure protect against this?**

- `make clean` should require a confirmation prompt before deleting anything
- `make clean` should be removed from the Makefile — it is too risky to include
- **✅ The `promote` target copies the validated model to `models/production_model.pkl`, which `make clean` does NOT delete — intermediate artifacts are ephemeral, but the promoted production model is a protected artifact**
- All models should be committed to git before running `make clean`

### Step-by-step Explanation

1. **The pipeline distinguishes between intermediate and promoted artifacts.** `models/model.pkl` is an intermediate artifact — it is regenerated every time you run `make all`. `models/production_model.pkl` is the promoted artifact — it only exists if a model passed the quality gate.

2. **`make clean` is designed to delete only intermediate/ephemeral files:** processed data, the intermediate model, and the experiment log. The promoted `production_model.pkl` is a protected artifact that survives `make clean`.

3. **This separation is intentional.** The `promote` step creates a durable copy. You can safely `make clean && make all` to try new experiments without losing your best validated model.

4. **Why other options are wrong:**
   - Confirmation prompts are impractical in automated pipelines (CI/CD, cron jobs).
   - Removing `make clean` defeats the purpose of reproducible experiments.
   - Committing large binary model files to git is an anti-pattern (bloats history).

---

## Question 6

**You run 5 experiments by editing `config.yaml` and running `make clean && make all` each time. A colleague suggests skipping `make clean` to save time. When does this cause incorrect results?**

- Never — Make always overwrites all outputs, so `make clean` is purely cosmetic
- **✅ If the new config changes preprocessing parameters (e.g., different `test_size` or feature engineering), but Make uses file-based targets, it may skip `prepare` because the output files already exist — training then proceeds on stale data from the previous experiment**
- Skipping `make clean` causes a memory leak in the Python process
- `make clean` is only needed on the first run — subsequent runs are always safe without it

### Step-by-step Explanation

1. **Make uses file-based timestamps for dependency resolution.** When targets are files, Make checks if the output file already exists and is newer than its dependencies. If so, it skips the target.

2. **The real danger:** If you change `config.yaml`'s `test_size` from 0.2 to 0.3 but don't clean, the processed data from the previous experiment may still exist. `prepare` might be skipped, and training happens on stale data.

3. **Best practice:** Always run `make clean && make all` between experiments. The instructions explicitly warn: *"Not running `make clean` between experiments: If you change the config but do not clean, old processed data and models may persist."*

---

## Question 7

**The config.yaml uses a `MODEL_MAP` pattern mapping string names to model classes. Why is this safer than using `eval(config['model_name'])` to instantiate models dynamically?**

- **✅ `eval()` executes arbitrary code — a malicious or mistaken config value like `__import__('os').system('rm -rf /')` would be executed; MODEL_MAP restricts instantiation to a safe, predefined set of classes**
- `eval()` is slower than dictionary lookup
- `eval()` cannot instantiate scikit-learn classes
- `eval()` is deprecated in Python 3

### Step-by-step Explanation

1. **`eval()` is a code execution function.** It takes any string and executes it as Python code. A malicious config value would be executed directly.

2. **The `MODEL_MAP` pattern is a whitelist.** In `train.py`:
   ```python
   MODEL_MAP = {
       "LinearRegression": LinearRegression,
       "RandomForestRegressor": RandomForestRegressor,
       "GradientBoostingRegressor": GradientBoostingRegressor,
   }
   model_class = MODEL_MAP[config["model"]["type"]]
   ```
   An invalid string raises a `KeyError` — no code is executed. Only predefined classes can be instantiated.

3. **Security principle: least privilege.** MODEL_MAP restricts what the config can do. `eval()` grants the config the ability to execute *anything*.

4. **Why other options are wrong:**
   - Performance is irrelevant compared to the security risk.
   - `eval()` can instantiate scikit-learn classes — that's the danger.
   - `eval()` is **not** deprecated in Python 3.

---

## Question 8

**Five experiments all pass the `min_r2=0.70` threshold. Their R2 values range from 0.8324 to 0.9703. If they all pass, what is the point of running multiple experiments?**

- There is no point — any model above 0.70 is equally good
- **✅ Passing the gate means "acceptable minimum quality"; comparing experiments reveals which model is best — the gate prevents bad models, but doesn't identify the optimal one**
- Running multiple experiments wastes compute resources
- The threshold should be raised to 0.97 so only one experiment passes

### Step-by-step Explanation

1. **The quality gate (`min_r2=0.70`) is a minimum bar, not a ranking.** It answers: "Is this model good enough?" not "Is this the best model?"

2. **The purpose of multiple experiments is model selection.** By running 5 configs and comparing R2/RMSE/MAE in `experiment_log.csv`, you find the optimal one.

3. **From our experiment log:** GradientBoostingRegressor achieves R2 = 0.9703, far superior to a baseline. Both pass the gate, but one is clearly better.

---

## Question 9

**All 5 experiments are run manually by editing config.yaml and running `make all` each time. Automating this with a bash loop is proposed. What architectural concern does this raise?**

- **✅ Automated looping works but creates a tracking problem — without experiment logging, results cannot be compared across runs because each `make all` overwrites the previous model and metrics files**
- Bash scripts cannot read YAML files
- Make does not support being called from bash scripts
- Running 5 experiments sequentially is always slower than running 1

### Step-by-step Explanation

1. **Each `make all` overwrites artifacts.** The pipeline writes `models/model.pkl` and metrics. Without the appending CSV log, each run destroys the previous run's results.

2. **The experiment log partially solves this.** `evaluate.py` appends a row to `experiment_log.csv` on each run. But the model file is still overwritten — only the last model is available on disk.

3. **The architectural concern is tracking and comparison.** Without robust experiment tracking (CSV log or MLflow from Activity 4), you cannot compare or retrieve previous models.

---

## Question 10

**The CFO asks: "You tested 5 model configurations. How do I know the best one is actually deployed?" Walk through the evidence chain that `make all` provides.**

- "Trust me — I remember which one was best"
- "Docker guarantees the best model is deployed automatically"
- "The MLflow dashboard shows all experiments — pick the best one"
- **✅ "The Makefile enforces a deterministic chain: config.yaml specifies the model → train.py trains it → evaluate.py writes metrics → validate.py checks the quality gate → promote copies the validated model to production_model.pkl. The config file, metrics file, and production model are all auditable artifacts"**

### Step-by-step Explanation

1. **The evidence chain is deterministic and auditable:**
   - `config.yaml` → documents which model and hyperparameters were used
   - `train.py` → trains that exact model (config-driven, no code changes)
   - `evaluate.py` → computes metrics and appends to `experiment_log.csv`
   - `validate.py` → checks R2 ≥ `min_r2` (quality gate)
   - `promote` → copies `model.pkl` to `production_model.pkl` (only if validation passes)

2. **Auditable artifacts:** `config.yaml`, `experiment_log.csv`, `models/production_model.pkl`

3. **Why other options are wrong:**
   - "Trust me" provides zero evidence.
   - Docker ensures environment reproducibility, not model selection.
   - MLflow is Activity 4 — at this stage, we rely on the Makefile chain and CSV log.

---

## Summary of Correct Answers

| Q  | Correct Answer |
|----|---------------|
| 1  | Config changes don't risk code bugs, are trivially reversible, and create an auditable history |
| 2  | `promote` never runs — Make halts on non-zero exit code from `validate` |
| 3  | `evaluate` → `validate` → `promote` (dependency chain resolved bottom-up) |
| 4  | Different environments (OS, Python, library versions) — Docker's job, not Make's |
| 5  | `promote` copies to `production_model.pkl`, which `make clean` does NOT delete |
| 6  | Make may skip `prepare` if output files exist — training proceeds on stale data |
| 7  | `eval()` executes arbitrary code; MODEL_MAP restricts to a safe predefined set |
| 8  | The gate prevents bad models; comparing experiments identifies the best one |
| 9  | Without experiment logging, each `make all` overwrites previous results — tracking problem |
| 10 | Deterministic chain: config → train → evaluate → validate → promote, all auditable |

---

*Solution for Test 03 — ASI Engineering 2025/2026, Activity 3: Orchestrate a Pipeline*
