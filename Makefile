# Linux based commands.
# With wsl on windows run 'ubuntu run'
# before running any make commands.

VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
PIP := $(VENV_BIN)/pip
ENTRY_POINT := main.py
PYTEST := pytest
PYTEST_COV := pytest-cov
BLACK := black
ISORT := isort
FLAKE8 := flake8
PRE_COMMIT := pre-commit

run:
	@echo "==> Running the application..."
	$(VENV_BIN)/python $(ENTRY_POINT) $(ARGS)

init:
	@echo "==> Initialize virtualenv..."
	python -m venv $(VENV_DIR)
	@echo "==> Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install $(PYTEST) $(PYTEST_COV) $(BLACK) $(ISORT) $(FLAKE8) $(PRE_COMMIT)
	$(PIP) install -r requirements.txt
	touch $(VENV_DIR)

del-venv:
	@echo "==> Delete the virtualenv."
	rm -fr $(VENV_DIR)

clean-build:
	@echo "==> Remove build artifacts."
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/

clean-pyc:
	@echo "==> Remove python file artifacts."
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	@echo "==> Remove test and coverage artifacts."
	rm -f .coverage
	rm -fr .tox/
	rm -fr htmlcov/
	rm -fr .pytest_cache

clean: clean-build clean-pyc clean-test

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
	@echo "==> Running tests with coverage html output file..."
	$(VENV_BIN)/$(PYTEST) --cov src --cov-report=html

codecov-test:
	@echo "==> Run tests with coverage for codecov for CI pipeline..."
	$(VENV_BIN)/$(PYTEST) --cov src --cov-report=xml --junitxml=junit.xml -o junit_family=legacy

lint:
	@echo "==> Lint code with flake8..."
	$(VENV_BIN)/$(FLAKE8) --config=.flake8

format:
	@echo "==> Check code with black and isort..."
	$(VENV_BIN)/$(BLACK) . --check
	$(VENV_BIN)/$(ISORT) . --check-only

check: lint format

full-check: check test
