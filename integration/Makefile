include ../vars.mk

# pytest settings
PYTEST_ARGS ?= "-s"

.DEFAULT_GOAL := latest

define GET_PORT
$(UV) run -- python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()'
endef

.PHONY: $(CONNECT_VERSIONS) \
	all \
	clean \
	latest \
	print-versions \
	help \
	test-%

# Versions
CONNECT_VERSIONS := \
	2025.12.1 \
	2025.12.0 \
	2025.11.0 \
	2025.10.0 \
	2025.09.1 \
	2025.07.0 \
	2025.06.0 \
	2025.05.0 \
	2025.04.0 \
	2025.03.0 \
	2025.02.0 \
	2025.01.0 \
	2024.12.0 \
	2024.11.0 \
	2024.09.0 \
	2024.08.0 \
	2024.06.0 \
	2024.05.0 \
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

# Run pytest for a specific version (assumes Connect is already running).
test-%:
	@mkdir -p logs reports
	$(UV) run pytest $(PYTEST_ARGS) \
		--junitxml=reports/junit-$*.xml | tee logs/$*.log

# Spin up Connect for a specific version and run tests.
$(CONNECT_VERSIONS): %:
	PORT=$$($(GET_PORT)); \
	uv run --with https://github.com/posit-dev/with-connect.git \
		with-connect --version $* --port $$PORT \
		-- $(MAKE) test-$*

# Run test suite against all Connect versions.
all: $(CONNECT_VERSIONS:%=%)

# Run test suite against latest Connect version.
latest:
	$(MAKE) $(firstword $(CONNECT_VERSIONS))

# Show available versions
print-versions:
	@printf "%s\n" $(strip $(CONNECT_VERSIONS))

# Show help message.
help:
	@echo "Makefile Targets:"
	@echo "  latest (default) Run test suite for latest Connect version."
	@echo "  all              Run test suite for all Connect versions."
	@echo "  <version>        Run test suite for the specified Connect version. (e.g., make 2025.10.0)"
	@echo "  clean            Clean up logs and reports directories."
	@echo "  print-versions   Show the available Connect versions."
	@echo "  help             Show this help message."
	@echo
	@echo "Common Usage:"
	@echo "  make             Run test suite for latest Connect version (default)."
	@echo "  make latest      Run test suite for latest Connect version."
	@echo "  make 2025.10.0   Run test suite for specific Connect version."
	@echo "  make all         Run test suite for all Connect versions."
	@echo "  make -j 4 all    Run test suite in parallel for all Connect versions."
	@echo
	@echo "Environment Variables:"
	@echo "  PYTEST_ARGS      Arguments to pass to pytest. Default: \"-s\""
