# Linux-based commands.
# With WSL on Windows, run 'ubuntu run'
# before executing any make commands.

ENTRY_POINT := main.py
PYTEST := pytest
PYTEST_COV := pytest-cov
BLACK := black
ISORT := isort
FLAKE8 := flake8
PRE_COMMIT := pre-commit
SETUPTOOLS := setuptools
WHEEL := wheel

help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "- package: Build the package"
	@echo "- init: Install dependencies"
	@echo "- run: Run the application"
	@echo "- clean: Remove all build and cache files"
	@echo "- test: Run tests with coverage"
	@echo "- test-report: Generate HTML coverage report"
	@echo "- codecov-test: Run tests with CI coverage output"
	@echo "- lint: Lint the code"
	@echo "- format: Check code formatting"
	@echo "- check: Run lint and format checks"
	@echo "- full-check: Run all checks and tests"
	@echo "- pre-commit-install: Install pre-commit hooks"
	@echo "- pre-commit: Run pre-commit hooks"

package:
	@echo "==> Building the package..."
	python -m pip install --upgrade pip
	pip install $(SETUPTOOLS) $(WHEEL)
	python setup.py sdist bdist_wheel

init:
	@echo "==> Installing dependencies..."
	python -m pip install --upgrade pip
	pip install $(PYTEST) $(PYTEST_COV) $(BLACK) $(ISORT) $(FLAKE8) $(PRE_COMMIT)
	pip install -r requirements.txt

run:
	@echo "==> Running the application..."
	python $(ENTRY_POINT) $(ARGS)

clean-build:
	@echo "==> Removing build artifacts..."
	rm -rf build/ dist/ .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +

clean-pyc:
	@echo "==> Removing Python cache files..."
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:
	@echo "==> Removing test and coverage artifacts..."
	rm -f .coverage
	rm -rf .tox/ htmlcov/ .pytest_cache

clean: clean-build clean-pyc clean-test

test:
	@echo "==> Running tests with coverage..."
	$(PYTEST) --cov src

test-report:
	@echo "==> Running tests with coverage (HTML report)..."
	$(PYTEST) --cov src --cov-report=html

codecov-test:
	@echo "==> Running tests with coverage for CI pipeline..."
	$(PYTEST) --cov src --cov-report=xml --junitxml=junit.xml -o junit_family=legacy

lint:
	@echo "==> Linting code with flake8..."
	$(FLAKE8) --config=.flake8

format:
	@echo "==> Checking code formatting with black and isort..."
	$(BLACK) . --check
	$(ISORT) . --check-only

check: lint format

full-check: check test

pre-commit-install:
	@echo "==> Installing pre-commit hooks..."
	$(PRE_COMMIT) install

pre-commit:
	@echo "==> Running pre-commit hooks..."
	$(PRE_COMMIT) run --all-files
