# Contributing

## Overview

The `posit-sdk` is a software development kit (SDK) for working with Posit's professional products.

## Prerequisites

Before contributing to the `posit-sdk`, ensure that the following prerequisites are met:

- Python >=3.9

> [!INFO]
> We require using virtual environments to maintain a clean and consistent development environment.
> Any Python virtual environment will do.

## Instructions

> [!WARNING]
> Executing `make` will install third-party packages in your `.venv` virtual Python environment. Please review the [`Makefile`](./Makefile) to verify behavior before executing any commands.

1. Fork the repository and open it in your development environment.
2. Activate your Python environment (e.g., `source .venv/bin/activate`)
3. Run `make` to run the default development workflow.
4. Make your changes and test them thoroughly using `make test`
5. Run `make fmt` and `make lint` to verify adherence to the project style guide.
6. Commit your changes and push them to your forked repository.
7. Submit a pull request to the main repository.

## Tooling

Use the default make target to execute the full build pipeline. For details on specific targets, run `make help`, or review the [Makefile](./Makefile) itself.

## Style Guide

We use [Ruff](https://docs.astral.sh/ruff/) for linting and code formatting.

All proposed changes must successfully pass the `make lint` rules prior to merging.

Utilize `make fmt lint` to format and lint your changes.

### (Optional) pre-commit

This project is configured for [pre-commit](https://pre-commit.com). Once enabled, a `git commit` hook is created, which invokes `make fmt lint`.

To enable pre-commit on your machine, run `pre-commit install`.

## Release

### Instructions

To start a release create a semver compatible tag.

_For this example, we will use the tag `v0.1.0`. This tag already exists, so you will not be able run the following commands verbatim._

**Step 1**

Create a proper SemVer compatible tag. Consult the [SemVer specification](https://semver.org/spec/v2.0.0.html) if you are unsure what this means.

`git tag v0.1.0`

**Step 2**

Push the tag GitHub.

`git push origin v0.1.0`

This command will trigger the [Release GitHub Action](https://github.com/posit-dev/posit-sdk-py/actions/workflows/release.yaml).

**Step 3**

Once complete, the release will be available on [PyPI](https://pypi.org/project/posit-sdk).

### Pre-Releases

Any tags denoted as a pre-release as defined by the [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html) specification will be marked as such in GitHub. For example, the `v0.1.rc1` is a pre-release. Tag `v0.1.0` is a standard-release. Please consult the specification for additional information.
