.PHONY: all prepare train evaluate validate promote test clean

all: prepare train evaluate validate promote
	@echo "Pipeline complete."

prepare:
	# TODO: Run the data preparation script
	# Hint: uv run python src/prepare.py

train: prepare
	# TODO: Run the training script
	# Hint: uv run python src/train.py

evaluate: train
	# TODO: Run the evaluation script
	# Hint: uv run python src/evaluate.py

validate: evaluate
	# TODO: Run the validation script (quality gate)
	# Hint: uv run python src/validate.py

promote: validate
	# TODO: Copy the trained model to production
	# Hint: cp models/model.pkl models/production_model.pkl

test:
	# TODO: Run the smoke test
	# Hint: uv run python -m pytest tests/ -v

clean:
	# TODO: Remove processed data, models, and experiment log
	# Hint: rm -f data/processed/*.csv models/*.pkl experiment_log.csv
