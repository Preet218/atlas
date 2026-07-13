install:
	uv sync

run:
	uvicorn apps.api.main:app --reload

lint:
	ruff check .

format:
	black .

test:
	pytest
