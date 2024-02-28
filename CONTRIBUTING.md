# Contributing

## Overview

The `posit-sdk` is a software development kit (SDK) for working with Posit's professional products.

## Prerequisites

Before contributing to the `posit-sdk`, ensure that the following prerequisites are met:

- Python >=3.8

## Tooling

The `Makefile` provides the following commands:

- `build`: Build the SDK.
- `clean`: Remove generated files and directories.
- `cov`: Generate coverage report.
- `cov-html`: Generate HTML coverage report.
- `cov-xml`: Generate XML coverage report.
- `deps`: Install required dependencies.
- `fmt`: Format the source code.
- `install`: Install the SDK locally.
- `lint`: Perform linting using `mypy` and `ruff`.
- `test`: Run tests with coverage.
- `uninstall`: Uninstall the SDK.
- `version`: Display the current version of the SDK.

## Release

### Instructions

To start a release create a semver compatible tag.

_For this example, we will use the tag `v0.0.dev0`. This tag already exists, so you will not be able run the following commands verbatim._

**Step 1**

Create a proper SemVer compatible tag. Consult the [SemVer specification](https://semver.org/spec/v2.0.0.html) if you are unsure what this means.

`git tag v0.0.dev0`

**Step 2**

Push the tag GitHub.

`git push origin v0.0.dev0`

This command will trigger the [Release GitHub Action](https://github.com/posit-dev/posit-sdk-py/actions/workflows/release.yaml).

**Step 3**

Once complete, the release will be available on [PyPI](https://pypi.org/project/posit-sdk).

### Pre-Releases

Any tags denoted as a pre-release as defined by the [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html) specification will be marked as such in GitHub. For example, the `v0.0.dev0` is a pre-release. Tag `v0.0.0` is a standard-release. Please consult the specification for additional information.
