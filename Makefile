include vars.mk

.DEFAULT_GOAL := all

.PHONY: build clean cov default deps dev docs fmt fix install it lint test uninstall version

all: deps dev test lint build

build:
	$(PYTHON) -m build

clean:
	$(MAKE) -C ./docs $@
	$(MAKE) -C ./integration $@
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache *.egg-info build coverage.xml dist htmlcov coverage.xml
	find . -name "*.egg-info" -exec rm -rf {} +
	find . -name "*.pyc" -exec rm -f {} +
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "_version.py" -exec rm -rf {} +
	find . -type d -empty -delete

cov:
	$(PYTHON) -m coverage report

cov-html:
	$(PYTHON) -m coverage html

cov-xml:
	$(PYTHON) -m coverage xml

deps:
	$(PIP) install --upgrade pip setuptools wheel -r requirements.txt -r requirements-dev.txt

dev:
	$(PIP) install -e .

docs:
	$(MAKE) -C ./docs

fix:
	$(PYTHON) -m ruff check --fix

fmt:
	$(PYTHON) -m ruff format .

install:
	$(PIP) install dist/*.whl

it:
	$(MAKE) -C ./integration

lint:
	$(PYTHON) -m mypy --install-types --non-interactive .
	$(PYTHON) -m ruff check

test:
	$(PYTHON) -m coverage run --source=src --omit=_version.py -m pytest tests

uninstall:
	$(PIP) uninstall $(NAME)

version:
	@$(PYTHON) -m setuptools_scm
