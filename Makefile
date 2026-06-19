.PHONY: install test lint run coverage docker clean

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	python -m pytest tests/ -v --tb=short

test-full:
	python -m pytest tests/ --cov=src --cov-report=term-missing --tb=short

lint:
	flake8 src/ scripts/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check src/ scripts/ tests/ --diff

format:
	black src/ scripts/ tests/
	isort src/ scripts/ tests/ --profile=black

run:
	python run_pipeline.py

coverage:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing --tb=short

docker:
	docker build -t redrobe:latest .

docker-run:
	docker run --rm -v "$(PWD)/Data:/app/Data:ro" -v "$(PWD)/outputs:/app/outputs" redrobe:latest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage coverage.xml htmlcov
