```makefile
.PHONY: install dev run test lint clean

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
```
