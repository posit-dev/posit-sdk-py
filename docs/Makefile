.DEFAULT_GOAL := all

VERSION := $(shell make -C ../ version)
export VERSION

# Command aliases
QUARTO=quarto
QUARTODOC=quartodoc

# Targets
.PHONY: clean build deps preview

all: deps build

build:
	$(QUARTODOC) build
	$(QUARTODOC) interlinks
	$(QUARTO) render

clean:
	rm -rf _extensions _inv _site .quarto reference objects.json
	find . -type d -empty -delete

deps:
	$(QUARTO) add --no-prompt posit-dev/product-doc-theme@v4.0.2
	$(QUARTO) add --no-prompt machow/quartodoc

preview:
	$(QUARTODOC) build
	$(QUARTODOC) interlinks
	$(QUARTO) preview
