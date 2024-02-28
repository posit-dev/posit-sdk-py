# Contributing

## Overview

The `posit-sdk` is a software development kit (SDK) designed to facilitate the development of projects using the Posit framework. This document provides instructions on how to use the provided `Makefile` to perform various tasks such as building, testing, linting, and installing the SDK.

## Prerequisites

Before contributing to the `posit-sdk`, ensure that the following prerequisites are met:

- Python 3.x is installed on your system.
- `pip3` is installed to manage Python packages.
- `make` utility is installed (commonly available on Unix-like systems).

## Project Structure

The the following files are commonly used during development.

- `Makefile`: Contains various commands to build, test, lint, and install the SDK.
- `requirements.txt`: Lists the required Python dependencies for the SDK.
- `requirements-dev.txt`: Lists additional dependencies required for development and testing purposes.
- `src/`: Contains the source code of the SDK.

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

Once complete the action has completed, the release will be available on the [Releases page](https://github.com/posit-dev/posit-sdk-py/releases).

### Pre-Releases

Any tags denoted as a pre-release as defined by the [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html) specification will be marked as such in GitHub. For example, the `v0.0.dev0` is a pre-release. Tag `v0.0.0` is a standard-release. Please consult the specification for additional information.

[PEP-440](https://peps.python.org/pep-0440/#summary-of-permitted-suffixes-and-relative-ordering) provides a good example of common pre-release tag combinations.

For additional definitions see https://en.wikipedia.org/wiki/Software_release_life_cycle.

Currently, the following suffix lineage is in use:

### Release Lifecycle

- `X`: The major version.
- `Y`: The minor version.
- `Z`: The patch version.
- `N`: A variable representing the incremental version value.

**`X.Y.devN`**

A development pre-release. Created to test changes to the release procces. `N` starts at **0** and increments by 1 (`X.Y.dev0`, `X.Y.dev1`, ..., `X.Y.devN`).

*https://peps.python.org/pep-0440/#implicit-development-release-number*

**`X.Y.aN`**

An alpha pre-release. Created to support internal user testing. `N` starts at **1** and increments by 1 (`X.Y.a1`, `X.Y.a2`, ..., `X.Y.aN`).

*https://peps.python.org/pep-0440/#pre-releases*

**`X.Y.bN`**

An beta pre-release. Created to support closed external user testing. `N` starts at **1** and increments by 1 (`X.Y.b1`, `X.Y.b2`, ..., `X.Y.bN`).

*https://peps.python.org/pep-0440/#pre-releases*


**`X.Y.rcN`**

An release-candidate pre-release. Created to support open external user testing. `N` starts at **1** and increments by 1 (`X.Y.rc1`, `X.Y.rc2`, ..., `X.Y.rcN`).

*https://peps.python.org/pep-0440/#pre-releases*

**`X.Y.N`**

A stable patch release. Created for backward compatible bug fixes. `N` starts at **0** and increments by 1 (`X.Y.0`, `X.Y.1`, ..., `X.Y.N`).

*https://semver.org*

**`X.N.Z`**

A stable minor release. Created for added functionality in a backward compatible manner. `N` starts at **0** and increments by 1 (`X.0.Z`, `X.1.Z`, ..., `X.N.Z`).

*https://semver.org*

**`N.Y.Z`**

A stable major release. Created for incompatbile API changes. `N` starts at **0** and increments by 1 (`0.Y.Z`, `1.Y.Z`, ..., `N.Y.Z`).

*https://semver.org*
