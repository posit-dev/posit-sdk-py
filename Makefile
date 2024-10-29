include vars.mk

.DEFAULT_GOAL := all

.PHONY: build clean cov default dev docs ensure-uv fmt fix install it lint test uninstall version help

all: dev test lint build

build: dev
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

cov: dev
	$(UV) run coverage report

cov-html: dev
	$(UV) run coverage html
	open htmlcov/index.html

cov-xml: dev
	$(UV) run coverage xml

dev: ensure-uv
	$(UV) pip install -e .

docs: ensure-uv
	$(MAKE) -C ./docs

$(VIRTUAL_ENV):
	$(UV) venv $(VIRTUAL_ENV)
ensure-uv: $(VIRTUAL_ENV)
	@if ! command -v $(UV) >/dev/null; then \
		$(PYTHON) -m ensurepip && $(PYTHON) -m pip install "uv >= 0.4.27"; \
	fi
	@# Be sure latest pip is installed
	@$(UV) pip install "uv >= 0.4.27" --quiet
	@# Install virtual environment
	@$(MAKE) $(VIRTUAL_ENV) 1>/dev/null

fmt: dev
	$(UV) run ruff check --fix
	$(UV) run ruff format

install: build
	$(UV) pip install dist/*.whl

it:
	$(MAKE) -C ./integration

lint: dev
	$(UV) run pyright
	$(UV) run ruff check

test: dev
	$(UV) run coverage run --source=src -m pytest tests

uninstall: ensure-uv
	$(UV) pip uninstall $(PROJECT_NAME)

version:
	@$(MAKE) ensure-uv &>/dev/null
	@$(UV) run --quiet python -m setuptools_scm

help:
	@echo "Makefile Targets"
	@echo "  all            Run dev, test, lint, and build"
	@echo "  build          Build the project"
	@echo "  clean          Clean up project artifacts"
	@echo "  cov            Generate a coverage report"
	@echo "  cov-html       Generate an HTML coverage report and open it"
	@echo "  cov-xml        Generate an XML coverage report"
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
