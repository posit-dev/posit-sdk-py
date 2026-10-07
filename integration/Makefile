include ../vars.mk

# pytest settings
PYTEST_ARGS ?= "-s"
PYTEST_TARGET ?= tests

# Posit Connect license file
LICENSE ?= ./license.lic

.DEFAULT_GOAL := latest

# Versions
CONNECT_VERSIONS := \
	2026.08.1 \
	2026.07.0 \
	2026.06.1 \
	2026.05.1 \
	2026.04.1 \
	2026.03.1 \
	2026.02.0 \
	2026.01.1 \
	2025.12.1 \
	2025.11.0 \
	2025.10.0 \
	2025.09.1 \
	2025.07.0 \
	2025.06.0 \
	2025.05.0 \
	2025.04.0 \
	2025.03.0

.PHONY: $(CONNECT_VERSIONS) \
	all \
	clean \
	latest \
	print-versions \
	help \
	test-%

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
	@echo "  PYTEST_TARGET    Test path/node-ID selection. Default: tests"
	@echo "  LICENSE          Path to the Connect license file. Default: ./license.lic"
