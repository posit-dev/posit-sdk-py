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

    just clean
    just deps
    just test
    just cov
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

    find . -name "*.pyc" -exec rm -f {} +
    find . -name "__pycache__" -exec rm -rf {} +
    rm -rf\
        .coverage\
        .pytest_cache\
        *.egg-info\
        build\
        dist\
        htmlcov

deps:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    {{ PIP }} install -e '.[test]'

test:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    {{ PYTHON }} -m coverage run --source=posit --omit=_version.py -m pytest

version:
    #!/usr/bin/env bash
    {{ OPTIONS }}

    {{ PYTHON }} -m setuptools_scm
