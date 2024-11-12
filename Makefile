include vars.mk

.DEFAULT_GOAL := all

.PHONY: build clean cov default dev docker-deps docs ensure-uv fmt fix install it lint test uninstall version help

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

docker-deps: ensure-uv
	# Sync given the `uv.lock` file
	# --frozen : assert that the lock file exists
	# --no-install-project : do not install the project itself, but install its dependencies
	$(UV) sync --frozen --no-install-project

docs: ensure-uv
	$(MAKE) -C ./docs

$(VIRTUAL_ENV):
	$(UV) venv $(VIRTUAL_ENV)
ensure-uv:
	@if ! command -v $(UV) >/dev/null; then \
		$(PYTHON) -m ensurepip && $(PYTHON) -m pip install "uv >= 0.4.27"; \
	fi
	@# Install virtual environment (before calling `uv pip install ...`)
	@$(MAKE) $(VIRTUAL_ENV) 1>/dev/null
	@# Be sure recent uv is installed
	@$(UV) pip install "uv >= 0.4.27" --quiet

fmt: dev
	$(UV) run ruff check --fix
	$(UV) run ruff format

install: build
	$(UV) pip install dist/*.whl

$(UV_LOCK): dev
	$(UV) lock
it: $(UV_LOCK)
	$(MAKE) -C ./integration

lint: dev
	$(UV) run ruff check
	$(UV) run pyright

test: dev
	$(UV) run coverage run --source=src -m pytest tests

uninstall: ensure-uv
	$(UV) pip uninstall $(PROJECT_NAME)

version:
	@$(MAKE) ensure-uv &>/dev/null
	@$(UV) run --quiet --with "setuptools_scm" python -m setuptools_scm

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
