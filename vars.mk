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

NAME := posit-sdk-py

ifeq ($(ENV), prod)
    NETLIFY_ARGS := --prod
else
    NETLIFY_ARGS :=
endif

NETLIFY_SITE_ID ?= 5cea1f56-7935-4387-975a-18a7905d15ee

PYTHON := python3

ifneq ($(shell command -v uv 2>/dev/null),)
PIP := uv pip
else
PIP := pip3
endif

QUARTO ?= quarto

QUARTODOC ?= quartodoc
