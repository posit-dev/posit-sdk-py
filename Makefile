NAME := posit-sdk
PIP := pip3
PYTHON := python3

.PHONY:
	build
	clean
	cov
	default
	deps
	fmt
	install
	lint
	test
	uninstall
	version

default:
	make deps
	make test
	make lint
	make build

build:
	$(PYTHON) -m build

clean:
	find . -name "*.egg-info" -exec rm -rf {} +
	find . -name "*.pyc" -exec rm -f {} +
	find . -name "__pycache__" -exec rm -rf {} +
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache *.egg-info build dist htmlcov

cov:
	$(PYTHON) -m coverage report

cov-html:
	$(PYTHON) -m coverage html

cov-xml:
	$(PYTHON) -m coverage xml

deps:
	$(PIP) install -r requirements.txt -r requirements-dev.txt

fmt:
	$(PYTHON) -m ruff format .

install:
	$(PIP) install -e .

lint:
	$(PYTHON) -m mypy --install-types --non-interactive .
	$(PYTHON) -m ruff check

test:
	$(PYTHON) -m coverage run --source=src --omit=_version.py -m pytest

uninstall:
	$(PIP) uninstall -y $(NAME)

version:
	$(PYTHON) -m setuptools_scm
