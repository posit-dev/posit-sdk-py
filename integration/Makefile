.DEFAULT_GOAL := all

.PHONY: down-% down-all test up-% up-all

# Versions
CONNECT_VERSIONS := 2024.05.0 2024.04.1 2024.04.0 2024.03.0 2024.02.0 2024.01.0 2023.12.0 2023.10.0 2023.09.0 2023.07.0 2023.06.0 2023.05.0 2023.01.1 2023.01.0 2022.12.0 2022.11.0

# Environment Variables
NAME = posit-sdk
CONNECT_BOOTSTRAP_SECRETKEY ?= $(shell head -c 32 /dev/random | base64)

# Binaries
DOCKER_COMPOSE ?= docker-compose
PYTHON ?= python3

all: up-all down-all

down-%: CONNECT_VERSION=$*
down-%: CONNECT_IMAGE_TAG=jammy-$*
down-%:
	CONNECT_BOOTSTRAP_SECRETKEY=$(CONNECT_BOOTSTRAP_SECRETKEY) \
	CONNECT_IMAGE_TAG=$(CONNECT_IMAGE_TAG) \
	CONNECT_VERSION=$(CONNECT_VERSION) \
	$(DOCKER_COMPOSE) -p $(NAME)-$(subst .,-,$(CONNECT_VERSION)) down -v

down-all: $(CONNECT_VERSIONS:%=down-%)

up-%: CONNECT_VERSION=$*
up-%: CONNECT_IMAGE_TAG=jammy-$*
up-%: down-%
	CONNECT_BOOTSTRAP_SECRETKEY=$(CONNECT_BOOTSTRAP_SECRETKEY) \
	CONNECT_IMAGE_TAG=$(CONNECT_IMAGE_TAG) \
	CONNECT_VERSION=$* \
	$(DOCKER_COMPOSE) -p $(NAME)-$(subst .,-,$(CONNECT_VERSION)) -f docker-compose.yaml up --abort-on-container-exit --always-recreate-deps --build --remove-orphans

up-all: $(CONNECT_VERSIONS:%=up-%)

test:
	$(PYTHON) -m coverage run --source=src --omit=_version.py -m pytest
