PIP := "pip3"
PYTHON := "python3"

OPTIONS := if env("DEBUG", "false") == "true" {
        "set -eoux pipefail"
    } else {
        "set -eou pipefail"
    }

default:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    just deps
    just test
    just cov
    just lint
    just build

build:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    {{ PYTHON }} -m build

cov *args="report":
    #!/usr/bin/env bash
    {{ OPTIONS }}

    {{ PYTHON }} -m coverage {{ args }}

clean:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    find . -name "*.egg-info" -exec rm -rf {} +
    find . -name "*.pyc" -exec rm -f {} +
    find . -name "__pycache__" -exec rm -rf {} +
    rm -rf\
        .coverage\
        .mypy_cache\
        .pytest_cache\
        .ruff_cache\
        *.egg-info\
        build\
        dist\
        htmlcov

deps:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    {{ PIP }} install -e '.[test]'

fmt:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    {{ PYTHON }} -m ruff format .

lint:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    {{ PYTHON }} -m mypy --install-types --non-interactive .
    {{ PYTHON }} -m ruff check

test:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    {{ PYTHON }} -m coverage run --source=src --omit=_version.py -m pytest

version:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    {{ PYTHON }} -m setuptools_scm
