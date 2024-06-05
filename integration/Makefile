.DEFAULT_GOAL := all

.PHONY: clean all down-% down-all latest test up-% up-all

# Versions
CONNECT_VERSIONS := 2024.05.0 2024.04.1 2024.04.0 2024.03.0 2024.02.0 2024.01.0 2023.12.0 2023.10.0 2023.09.0 2023.07.0 2023.06.0 2023.05.0 2023.01.1 2023.01.0 2022.12.0 2022.11.0

# Environment Variables
NAME = posit-sdk
CONNECT_BOOTSTRAP_SECRETKEY ?= $(shell head -c 32 /dev/random | base64)

# Binaries
DOCKER_COMPOSE ?= docker-compose
PYTHON ?= python3

# Run for each Connect version.
all: $(CONNECT_VERSIONS:%=up-%)

# Run latest Connect version.
latest:
	$(MAKE) $(firstword $(CONNECT_VERSIONS))

# Run against a specific Connect version.
#
# Matches any version defined in CONNECT_VERSIONS.
#
# Examples:
# ---------
# 	make 2024.05.1
#	make 2023.01.0
# 	make 2024.05.0 CONNECT_IMAGE_TAG=jammy  # override image tag to 'latest'
$(CONNECT_VERSIONS):
	$(MAKE) up-$@

# Tear down resources.
#
# Destory Docker resources for Connect version.
#
# Examples:
# ---------
#	make down-all
# 	make down-2024.05.0
down-all: $(CONNECT_VERSIONS:%=down-%)
down-%: CONNECT_VERSION=$*
down-%: CONNECT_IMAGE_TAG=jammy-$*
down-%:
	CONNECT_BOOTSTRAP_SECRETKEY=$(CONNECT_BOOTSTRAP_SECRETKEY) \
	CONNECT_IMAGE_TAG=$(CONNECT_IMAGE_TAG) \
	CONNECT_VERSION=$* \
	$(DOCKER_COMPOSE) -p $(NAME)-$(subst .,-,$(CONNECT_VERSION)) down -v

# Create, start, and run Docker compose.
#
# Examples:
# ---------
#	make up-all
# 	make up-2024.05.0
up-all: $(CONNECT_VERSIONS:%=up-%)
up-%: CONNECT_VERSION=$*
up-%: CONNECT_IMAGE_TAG=jammy-$*
up-%: down-%
	CONNECT_BOOTSTRAP_SECRETKEY=$(CONNECT_BOOTSTRAP_SECRETKEY) \
	CONNECT_IMAGE_TAG=$(CONNECT_IMAGE_TAG) \
	CONNECT_VERSION=$* \
	$(DOCKER_COMPOSE) -p $(NAME)-$(subst .,-,$(CONNECT_VERSION)) -f docker-compose.yaml up --abort-on-container-exit --always-recreate-deps --build --remove-orphans

# Show help message.
help:
	@echo "Makefile Targets:"
	@echo "  all              Run test suite for each Connect version."
	@echo "  latest           Run test suite for latest Connect version."
	@echo "  <version>        Run test suite for the specified Connect version. (e.g., make 2024.05.0)"
	@echo "  down-all         Tear down Docker resources for all Connect versions."
	@echo "  down-<version>   Tear down Docker resources for specific Connect version (e.g., make down-2024.05.0)."
	@echo "  up-all           Start Docker Compose for each Connect version."
	@echo "  up-<version>     Start Docker Compose for specific Connect version (e.g., make up-2024.05.0)."
	@echo "  help             Show this help message."
	@echo
	@echo "Common Usage:"
	@echo "  make -j 4        Run test suite in parallel for all Connect versions."
	@echo "  make latest      Run test suite for latest Connect version."
	@echo "  make 2024.05.0   Run test suite for specific Connect version."

# Run tests.
#
# Typically call from docker-compose.yaml. Assumes Connect server is running
# on local network.
_test:
	CONNECT_API_KEY="$(shell rsconnect bootstrap -i -s http://connect:3939 --raw)" $(PYTHON) -m pytest
