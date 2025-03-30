# Linux-based commands.
# With WSL on Windows, run 'ubuntu run'
# before executing any make commands.

VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
PYTHON := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip
ENTRY_POINT := main.py
PYTEST := pytest
PYTEST_COV := pytest-cov
BLACK := black
ISORT := isort
FLAKE8 := flake8
PRE_COMMIT := pre-commit

package:
	@echo "==> Building the package..."
	python -m pip install --upgrade pip
	pip install setuptools wheel
	python setup.py sdist bdist_wheel

init:
	@echo "==> Initializing virtualenv..."
	python -m venv $(VENV_DIR)
	@echo "==> Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install $(PYTEST) $(PYTEST_COV) $(BLACK) $(ISORT) $(FLAKE8) $(PRE_COMMIT)
	$(PIP) install -r requirements.txt
	touch $(VENV_DIR)

del-venv:
	@echo "==> Deleting virtualenv..."
	rm -rf $(VENV_DIR)

run:
	@echo "==> Running the application..."
	$(PYTHON) $(ENTRY_POINT) $(ARGS)

clean: clean-build clean-pyc clean-test

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

pre-commit-install:
	@echo "==> Installing pre-commit hooks..."
	$(VENV_BIN)/$(PRE_COMMIT) install

pre-commit:
	@echo "==> Running pre-commit hooks..."
	$(VENV_BIN)/$(PRE_COMMIT) run --all-files

test:
	@echo "==> Running tests with coverage..."
	$(VENV_BIN)/$(PYTEST) --cov src

test-report:
	@echo "==> Running tests with coverage (HTML report)..."
	$(VENV_BIN)/$(PYTEST) --cov src --cov-report=html

codecov-test:
	@echo "==> Running tests with coverage for CI pipeline..."
	$(VENV_BIN)/$(PYTEST) --cov src --cov-report=xml --junitxml=junit.xml -o junit_family=legacy

lint:
	@echo "==> Linting code with flake8..."
	$(VENV_BIN)/$(FLAKE8) --config=.flake8

format:
	@echo "==> Checking code formatting with black and isort..."
	$(VENV_BIN)/$(BLACK) . --check
	$(VENV_BIN)/$(ISORT) . --check-only

check: lint format

full-check: check test
