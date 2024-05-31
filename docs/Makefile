.DEFAULT_GOAL := all

VERSION := $(shell make -C ../ version)
export VERSION

# Command aliases
QUARTO=quarto
QUARTODOC=quartodoc

# Environment variables
CURRENT_YEAR := $(shell date +%Y)
VERSION := $(shell make -C ../ version)
export CURRENT_YEAR VERSION

.PHONY: clean build deps preview

all: deps api build

api: deps
	$(QUARTODOC) build
	$(QUARTODOC) interlinks
	cp -r _extensions/ reference/_extensions	# Required to render footer

build: api
	$(QUARTO) render

clean:
	rm -rf _extensions _inv _site .quarto reference objects.json
	find . -type d -empty -delete

deps:
	$(QUARTO) add --no-prompt posit-dev/product-doc-theme@v4.0.2
	$(QUARTO) add --no-prompt machow/quartodoc

preview: api
	$(QUARTO) preview
