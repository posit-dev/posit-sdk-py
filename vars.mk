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

# Projectc settings
NAME := posit-sdk
CONNECT_BOOTSTRAP_SECRETKEY ?= $(shell head -c 32 /dev/random | base64)

# Docker settings
CONNECT_IMAGE ?= rstudio/rstudio-connect
DOCKER_COMPOSE ?= docker compose
IMAGE_TAG ?= $(NAME):latest

# Python settings
PYTHON ?= $(shell command -v python || command -v python3)
QUARTO ?= quarto
QUARTODOC ?= quartodoc
UV ?= uv

# Netlify settings
ifeq ($(ENV), prod)
    NETLIFY_ARGS := --prod
else
    NETLIFY_ARGS :=
endif
NETLIFY_SITE_ID ?= 5cea1f56-7935-4387-975a-18a7905d15ee
