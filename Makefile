.PHONY: install playground run test lint clean

install:
	uv sync

playground:
	uv run adk web app --host 127.0.0.1 --port 18081 --reload_agents

run:
	uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000 --reload

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check app/ tests/
	uv run ruff format --check app/ tests/

clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache .adk *.db
