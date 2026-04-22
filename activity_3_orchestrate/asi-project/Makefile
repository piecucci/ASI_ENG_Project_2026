.PHONY: all prepare train evaluate validate promote test clean

all: prepare train evaluate validate promote
	@echo "Pipeline complete."

prepare:
	uv run python src/prepare.py

train: prepare
	uv run python src/train.py

evaluate: train
	uv run python src/evaluate.py

validate: evaluate
	uv run python src/validate.py

promote: validate
	cp models/model.pkl models/production_model.pkl

test:
	uv run python -m pytest tests/ -v

clean:
	rm -f data/processed/*.csv models/*.pkl experiment_log.csv
