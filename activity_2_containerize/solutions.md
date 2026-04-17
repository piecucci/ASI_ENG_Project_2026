# Activity 2: Containerization Knowledge Test - Solutions

## Question 1
**Answer:** An environment reproducibility problem — different OS, Python patch version, and library versions can cause numerical differences even with `random_state=42` fixed
**Explanation:** Even when setting random seeds, differences in underlying OS architectures, C-library implementations, and exact package versions can lead to float formatting, underlying numerical optimizations, and precision differences that result in small variations in model outputs. This is exactly why Docker (containerization) is used to freeze the entire OS and dependency environment.

## Question 2
**Answer:** Only `prepare.py` runs; the `&&` operator short-circuits on exit code 1, so train, evaluate, and validate never execute; the container exits with code 1
**Explanation:** The shell `&&` (logical AND) operator executes the right-hand command only if the left-hand command succeeds (returns exit code 0). Since `prepare.py` exits with 1, the chain breaks immediately ("short-circuits") and the container stops with exit code 1.

## Question 3
**Answer:** Used a volume mount (`-v ./models:/app/models`) to map the container's model output directory to the host filesystem, so files persist after container removal
**Explanation:** Files created inside a running container exist only in the container's ephemeral write layer. They are destroyed when the container is removed. To save generated outputs back to your host machine—like the processed data splits or the pickled model—you must use bind mounts (`-v`/`--volume`).

## Question 4
**Answer:** That the container reproduces the exact same environment as local execution — same Python, same libraries, same numerical results — confirming environment-level reproducibility
**Explanation:** Since the scores match perfectly across Docker and your local host environment, it means Docker successfully isolated and reproduced the precise conditions necessary for identical computations, proving true environment-level reproducibility.

## Question 5
**Answer:** `deploy.sh` never runs — the shell `&&` operator stops on the container's non-zero exit code, preventing deployment of a subpar model
**Explanation:** Just like inside the container, the bash `&&` operator used in the CI pipeline execution (`docker run ... && bash deploy.sh`) acts as a stop-gate condition. Because the model failed validation and exited with code 1, the pipeline short-circuits to avoid deploying bad code.

## Question 6
**Answer:** "Exit code 0 means the model met the minimum R2 threshold we defined — it passed our quality gate, but the threshold itself is a business decision about acceptable risk"
**Explanation:** An exit code 0 simply signals to the outer system that the executable ran correctly and any custom validations inside (like `R2 >= 0.80`) evaluated favorably. It does not speak to whether the model operates flawlessly on untouched prod data or is mathematically perfect.

## Question 7
**Answer:** When the pipeline needs to compile C extensions during the Docker build (e.g., packages requiring `gcc`), which slim images don't include
**Explanation:** `slim` tags drop many OS-level development binaries and headers (like `gcc`, `make`, etc.). If you are installing packages that distribute highly particular source trees without pre-compiled wheels, you'll need the larger full image to allow native compilation against C libraries.

## Question 8
**Answer:** Each script is an independent process with its own exit code; if train.py crashes, the shell reports exactly which step failed and the container's exit code reflects that failure — a Python wrapper requires explicit try/except to achieve the same
**Explanation:** By chaining them natively in the shell, you get process-level tracking. If a step fails, you immediately know which standalone process broke based on the shell trace, without having to inject cumbersome Python exception handling logic just to bubble up an exit code. 

## Question 9
**Answer:** `uv` resolves and installs packages significantly faster than `pip`, which directly reduces Docker build time — especially important when the dependency cache is invalidated
**Explanation:** `uv` is a Rust-based, blazingly fast drop-in replacement for Pip. A pipeline heavily caches the dependency layer, but on the inevitable occasions you add or bump a package, the rebuild will finish in seconds instead of minutes compared to standard `pip install`.

## Question 10
**Answer:** The `&&` chain ensures atomic-like behavior: if any step fails, all subsequent steps are skipped and the container reports failure; success means every step completed — prepare, train, evaluate, and validate all passed
**Explanation:** The `&&` chain gives a clear, sequential safeguard. None of the model outputs will be blessed dynamically with a 0 exit code to continue onward unless the initial sequence up to the current command operates with complete integrity.
