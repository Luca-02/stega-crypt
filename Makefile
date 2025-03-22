PYTHON := python
PIP := $(PYTHON) -m pip
PYTEST := pytest
PYTEST_COV := pytest-cov
BLACK := black
ISORT := isort
FLAKE8 := flake8
PRE_COMMIT := pre-commit
COV_REPORT := --cov --junitxml=junit.xml

# Install dependencies
install:
	$(PIP) install --upgrade pip
	$(PIP) install $(DOC) $(PYTEST) $(PYTEST_COV) $(BLACK) $(ISORT) $(FLAKE8) $(PRE_COMMIT)
	$(PIP) install -r requirements.txt

# Run pre-commit hooks
pre-commit:
	$(PRE_COMMIT) run --all-files

# Run tests with coverage
test:
	$(PYTEST) $(COV_REPORT)

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
