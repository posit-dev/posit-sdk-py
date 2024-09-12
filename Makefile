include vars.mk

.DEFAULT_GOAL := all

.PHONY: build clean cov default deps dev docs ensure-uv fmt fix install it lint test uninstall version help

all: deps dev test lint build

build:
	$(UV) build

clean:
	$(MAKE) -C ./docs $@
	$(MAKE) -C ./integration $@
	rm -rf .coverage .pytest_cache .ruff_cache *.egg-info build coverage.xml dist htmlcov coverage.xml
	find src -name "_version.py" -exec rm -rf {} +
	find . -name "*.egg-info" -exec rm -rf {} +
	find . -name "*.pyc" -exec rm -f {} +
	find . -name "__pycache__" -exec rm -rf {} +
	find . -type d -empty -delete

cov:
	$(PYTHON) -m coverage report

cov-html:
	$(PYTHON) -m coverage html
	open htmlcov/index.html

cov-xml:
	$(PYTHON) -m coverage xml

deps: ensure-uv
	$(UV) pip install --upgrade pip setuptools wheel -r requirements.txt -r requirements-dev.txt

dev: ensure-uv
	$(UV) pip install -e .

docs:
	$(MAKE) -C ./docs

ensure-uv:
	@if ! command -v $(UV) >/dev/null; then \
		$(PYTHON) -m ensurepip && $(PYTHON) -m pip install uv; \
	fi

fmt:
	$(PYTHON) -m ruff check --fix
	$(PYTHON) -m ruff format

install: ensure-uv
	$(UV) pip install dist/*.whl

it:
	$(MAKE) -C ./integration

lint:
	$(PYTHON) -m pyright
	$(PYTHON) -m ruff check

test:
	$(PYTHON) -m coverage run --source=src -m pytest tests

uninstall: ensure-uv
	$(UV) pip uninstall $(PROJECT_NAME)

version:
	@$(PYTHON) -m setuptools_scm

help:
	@echo "Makefile Targets"
	@echo "  all            Run deps, dev, test, lint, and build"
	@echo "  build          Build the project"
	@echo "  clean          Clean up project artifacts"
	@echo "  cov            Generate a coverage report"
	@echo "  cov-html       Generate an HTML coverage report and open it"
	@echo "  cov-xml        Generate an XML coverage report"
	@echo "  deps           Install dependencies"
	@echo "  dev            Install the project in editable mode"
	@echo "  docs           Build the documentation"
	@echo "  ensure-uv      Ensure 'uv' is installed"
	@echo "  fmt            Format the code"
	@echo "  install        Install the built project"
	@echo "  it             Run integration tests"
	@echo "  lint           Lint the code"
	@echo "  test           Run unit tests with coverage"
	@echo "  uninstall      Uninstall the project"
	@echo "  version        Display the project version"
