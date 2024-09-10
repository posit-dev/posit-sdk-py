# Makefile variables file.
#
# Variables shared across project Makefiles via 'include vars.mk'.
#
# - ./Makefile
# - ./docs/Makefile
# - ./integration/Makefile

# Shell settings
SHELL := /bin/bash

# Environment settings
ENV ?= dev

# Project settings
PROJECT_NAME := posit-sdk

# Python settings
PYTHON ?= $(shell command -v python || command -v python3)
UV ?= uv
