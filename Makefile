.PHONY: install run lint fmt clean

install:
	uv venv
	uv pip install -r <(uv pip compile pyproject.toml)

run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	uv run ruff check .

fmt:
	uv run ruff format .

clean:
	rm -rf .venv app.db __pycache__ .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
