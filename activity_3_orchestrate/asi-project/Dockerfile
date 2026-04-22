FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv && uv sync --frozen

COPY . .

CMD uv run python src/prepare.py && uv run python src/train.py && uv run python src/evaluate.py && uv run python src/validate.py
