include ../vars.mk

# pytest settings
PYTEST_ARGS ?= "-s"
# Connect and Workbench each need their own server, so each target runs only its own subtree.
PYTEST_TARGET ?= tests/posit/connect

# Posit Connect license file
LICENSE ?= ./license.lic

.DEFAULT_GOAL := latest

# Versions
CONNECT_VERSIONS := \
	2026.09.0 \
	2026.08.0 \
	2026.07.0 \
	2026.06.1 \
	2026.05.1 \
	2026.04.1 \
	2026.03.1 \
	2026.02.0 \
	2026.01.1 \
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

# Workbench versions (newest first). Requires the Workbench API (Bearer tokens) and
# `rstudio-server generate-api-token --token-env`; older versions are added as they're verified.
WORKBENCH_VERSIONS := \
	2026.10.0

# with-workbench with --api-token support, pinned to the fork's integration branch until
# posit-dev/with-workbench#4 (license deactivation) and #5 (--api-token) land upstream.
WITH_WORKBENCH ?= git+https://github.com/michaelmayer2/with-workbench.git@2e2ce269f528fd9eca2384f22fbfe3b8410cd267

define GET_PORT
$(UV) run -- python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()'
endef

.PHONY: $(CONNECT_VERSIONS) \
	all \
	clean \
	latest \
	print-versions \
	help \
	test-% \
	$(WORKBENCH_VERSIONS:%=workbench-%) \
	workbench-all \
	workbench-latest \
	print-workbench-versions \
	workbench-test-%

clean:
	rm -rf logs reports
	find . -type d -empty -delete

# Run the test suite against a specific Connect version.
test-%:
	@mkdir -p logs reports
	CONNECT_VERSION=$* LICENSE=$(LICENSE) $(UV) run pytest $(PYTEST_TARGET) $(PYTEST_ARGS) \
		--junitxml=reports/junit-$*.xml 2>&1 | tee logs/$*.log; \
	exit $${PIPESTATUS[0]}

$(CONNECT_VERSIONS): %: test-%

# Run test suite against all Connect versions.
all: $(CONNECT_VERSIONS)

# Run test suite against latest Connect version.
latest:
	$(MAKE) $(firstword $(CONNECT_VERSIONS))

# Show available versions
print-versions:
	@printf "%s\n" $(strip $(CONNECT_VERSIONS))

# Run the Workbench test suite for a specific version (assumes Workbench is already running and
# WORKBENCH_SERVER/WORKBENCH_API_KEY point at it).
workbench-test-%:
	@mkdir -p logs reports
	$(UV) run pytest tests/posit/workbench $(PYTEST_ARGS) \
		--junitxml=reports/junit-workbench-$*.xml 2>&1 | tee logs/workbench-$*.log; \
	exit $${PIPESTATUS[0]}

# Spin up Workbench for a specific version and run tests. Requires a license key in
# RSW_LICENSE or PWB_LICENSE. with-workbench runs `-- COMMAND` inside the container, so start it
# in start-only mode and stop it (which also deactivates the license) when done.
$(WORKBENCH_VERSIONS:%=workbench-%): workbench-%:
	set -euo pipefail; \
	export RSW_LICENSE="$${RSW_LICENSE:-$${PWB_LICENSE:?Set RSW_LICENSE or PWB_LICENSE}}"; \
	PORT=$$($(GET_PORT)); \
	CREDENTIALS=$$($(UV) run --with "$(WITH_WORKBENCH)" with-workbench \
		--version $* --port $$PORT --api-token admin --quiet); \
	eval "$$(sed 's/^/export /' <<< "$$CREDENTIALS")"; \
	trap '$(UV) run --with "$(WITH_WORKBENCH)" with-workbench --stop "$$CONTAINER_ID"' EXIT; \
	WORKBENCH_SERVER="$$WORKBENCH_URL" $(MAKE) workbench-test-$*

# Run test suite against all Workbench versions.
workbench-all: $(WORKBENCH_VERSIONS:%=workbench-%)

# Run test suite against latest Workbench version.
workbench-latest:
	$(MAKE) workbench-$(firstword $(WORKBENCH_VERSIONS))

# Show available Workbench versions
print-workbench-versions:
	@printf "%s\n" $(strip $(WORKBENCH_VERSIONS))

# Show help message.
help:
	@echo "Makefile Targets:"
	@echo "  latest (default) Run test suite for latest Connect version."
	@echo "  all              Run test suite for all Connect versions."
	@echo "  <version>        Run test suite for the specified Connect version. (e.g., make 2025.10.0)"
	@echo "  clean            Clean up logs and reports directories."
	@echo "  print-versions   Show the available Connect versions."
	@echo "  workbench-latest Run Workbench test suite for latest Workbench version."
	@echo "  workbench-all    Run Workbench test suite for all Workbench versions."
	@echo "  workbench-<ver>  Run Workbench test suite for the specified version. (e.g., make workbench-2026.10.0)"
	@echo "  print-workbench-versions  Show the available Workbench versions."
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
	@echo "  PYTEST_TARGET    Connect test path/node-ID selection. Default: tests/posit/connect"
	@echo "  LICENSE          Path to the Connect license file. Default: ./license.lic"
	@echo "  RSW_LICENSE      Workbench license key (falls back to PWB_LICENSE)."
	@echo "  WITH_WORKBENCH   with-workbench package spec. Default: $(WITH_WORKBENCH)"
