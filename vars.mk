# Makefile variables file.
#
# Variables shared across project Makefiles via 'include vars.mk'.
#
# - ./Makefile
# - ./docs/Makefile
# - ./integration/Makefile

CONNECT_BOOTSTRAP_SECRETKEY ?= $(shell head -c 32 /dev/random | base64)

CONNECT_IMAGE ?= rstudio/rstudio-connect

CURRENT_YEAR ?= $(shell date +%Y)

DOCKER_COMPOSE ?= docker compose

ENV ?= dev

IMAGE_TAG ?= $(NAME):latest

NAME := posit-sdk

ifeq ($(ENV), prod)
    NETLIFY_ARGS := --prod
else
    NETLIFY_ARGS :=
endif

NETLIFY_SITE_ID ?= 5cea1f56-7935-4387-975a-18a7905d15ee

PYTHON := $(shell command -v python3 2>/dev/null || command -v python)
PIP = uv pip

SHELL := /bin/bash

QUARTO ?= quarto

QUARTODOC ?= quartodoc
