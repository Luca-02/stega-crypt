ROOT_DIR := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))
PYTHON := python
PIP := $(PYTHON) -m pip
PYTEST := pytest
PYTEST_COV := pytest-cov
BLACK := black
ISORT := isort
FLAKE8 := flake8
PRE_COMMIT := pre-commit

# Install dependencies
install:
	$(PIP) install --upgrade pip
	$(PIP) install $(PYTEST) $(PYTEST_COV) $(BLACK) $(ISORT) $(FLAKE8) $(PRE_COMMIT)
	$(PIP) install -r requirements.txt

# Run pre-commit hooks
pre-commit:
	$(PRE_COMMIT) run --all-files

# Run tests with coverage, html output file
test:
	$(PYTEST) --cov

# Run tests with coverage, html output file
test-report:
	$(PYTEST) --cov --cov-report=html
	@echo Report saved at file:///$(CURDIR)/htmlcov/index.html

# Run tests with coverage for codecov for CI pipeline
codecov-test:
	$(PYTEST) --cov --cov-report=xml --junitxml=junit.xml -o junit_family=legacy

# Format code with Black and isort
format:
	$(BLACK) . --check
	$(ISORT) . --check-only

# Lint code with flake8
lint:
	$(FLAKE8) --config=.flake8

# Run all checks (lint and format)
check: lint format

# Run all checks including tests
full-check: check test
