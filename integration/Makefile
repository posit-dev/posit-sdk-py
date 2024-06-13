include ../vars.mk

.DEFAULT_GOAL := all

.PHONY: $(CONNECT_VERSIONS) \
		all \
		build \
        down \
        down-% \
        latest \
        test \
        up \
        up-% \
        help

# Versions
CONNECT_VERSIONS := 2024.05.0 \
                    2024.04.1 \
                    2024.04.0 \
                    2024.03.0 \
                    2024.02.0 \
                    2024.01.0 \
                    2023.12.0 \
                    2023.10.0 \
                    2023.09.0 \
                    2023.07.0 \
                    2023.06.0 \
                    2023.05.0 \
                    2023.01.1 \
                    2023.01.0 \
                    2022.12.0 \
                    2022.11.0

clean:
	rm -rf logs reports
	find . -type d -empty -delete

# Run test suite for a specific Connect version.
#
# Matches any version defined in CONNECT_VERSIONS.
#
# Examples:
# ---------
#   make 2024.05.1
#   make 2023.01.0
$(CONNECT_VERSIONS): %: down-% up-%

# Run test suite against all Connect versions.
all: $(CONNECT_VERSIONS:%=%) preview

# Run test suite against latest Connect version.
latest:
	$(MAKE) $(firstword $(CONNECT_VERSIONS))

# Run test suite against preview Connect version.
preview:
	$(MAKE) \
	CONNECT_IMAGE=rstudio/rstudio-connect-preview \
	CONNECT_IMAGE_TAG=dev-jammy-daily \
	down-preview up-preview

# Build Dockerfile
build:
	docker build -t $(IMAGE_TAG) ..

# Tear down resources.
#
# Destroy Docker resources for Connect version.
#
# Examples:
# ---------
#   make down
#   make down-2024.05.0
down: $(CONNECT_VERSIONS:%=down-%)
down-%: CONNECT_IMAGE_TAG=jammy-$*
down-%: CONNECT_VERSION=$*
down-%:
	CONNECT_BOOTSTRAP_SECRETKEY=$(CONNECT_BOOTSTRAP_SECRETKEY) \
	CONNECT_IMAGE=$(CONNECT_IMAGE) \
	CONNECT_IMAGE_TAG=$(CONNECT_IMAGE_TAG) \
	CONNECT_VERSION=$* \
	IMAGE_TAG=$(IMAGE_TAG) \
	$(DOCKER_COMPOSE) -p $(NAME)-$(subst .,-,$(CONNECT_VERSION)) down -v

# Create, start, and run Docker Compose.
#
# Examples:
# ---------
#   make up
#   make up-2024.05.0
up: $(CONNECT_VERSIONS:%=up-%)
up-%: CONNECT_VERSION=$*
up-%: CONNECT_IMAGE_TAG=jammy-$*
up-%: build
	CONNECT_BOOTSTRAP_SECRETKEY=$(CONNECT_BOOTSTRAP_SECRETKEY) \
	CONNECT_IMAGE=$(CONNECT_IMAGE) \
	CONNECT_IMAGE_TAG=$(CONNECT_IMAGE_TAG) \
	CONNECT_VERSION=$* \
	IMAGE_TAG=$(IMAGE_TAG) \
	$(DOCKER_COMPOSE) -p $(NAME)-$(subst .,-,$(CONNECT_VERSION)) up -V --abort-on-container-exit --no-build

# Show help message.
help:
	@echo "Makefile Targets:"
	@echo "  all (default)    Run test suite for all Connect versions."
	@echo "  latest           Run test suite for latest Connect version."
	@echo "  preview          Run test suite for preview Connect version."
	@echo "  <version>        Run test suite for the specified Connect version. (e.g., make 2024.05.0)"
	@echo "  up               Start Docker Compose for all Connect version."
	@echo "  down             Tear down Docker resources for all Connect versions."
	@echo "  clean            Clean up the project directory."
	@echo "  help             Show this help message."
	@echo
	@echo "Common Usage:"
	@echo "  make -j 4        Run test suite in parallel for all Connect versions."
	@echo "  make latest      Run test suite for latest Connect version."
	@echo "  make preview     Run test suite for preview Connect version."
	@echo "  make 2024.05.0   Run test suite for specific Connect version."

# Run tests.
#
# Typically call from docker-compose.yaml. Assumes Connect server is running
# on local network.
test:
	mkdir -p logs
	CONNECT_VERSION=${CONNECT_VERSION} CONNECT_API_KEY="$(shell rsconnect bootstrap -i -s http://connect:3939 --raw)" $(PYTHON) -m pytest -s --junit-xml=./reports/$(CONNECT_VERSION).xml | tee ./logs/$(CONNECT_VERSION).log
