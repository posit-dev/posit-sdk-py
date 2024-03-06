# Contributing

## Overview

The `posit-sdk` is a software development kit (SDK) for working with Posit's professional products.

## Prerequisites

Before contributing to the `posit-sdk`, ensure that the following prerequisites are met:

- Python >=3.8

## Instructions

1. Fork the repository and clone it to your local machine.
1. Create a new branch for your feature or bug fix.
1. Run `make` to run the default development workflow.
1. Make your changes and test them thoroughly using `make test`
1. Commit your changes and push them to your forked repository.
1. Submit a pull request to the main repository.

Please ensure that your code follows the project's coding conventions and style guidelines using the configured pre-commit hooks. Run `pre-commit install` install to configure this functionality on your machine.

Also, make sure to include tests for any new functionality or bug fixes.

## Tooling

Use the default make target to execute the full build pipeline. For details on specific targets, refer to the [Makefile](./Makefile).

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
