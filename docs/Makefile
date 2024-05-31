.DEFAULT_GOAL := all

# Command aliases
PIP ?= pip3
QUARTO ?= quarto
QUARTODOC ?= quartodoc

# Environment variables
CURRENT_YEAR ?= $(shell date +%Y)
VERSION ?= $(shell make -C ../ version)

.PHONY: all \
		api \
		build \
		clean \
		deps \
		preview

all: deps api build

api:
	$(QUARTODOC) build
	$(QUARTODOC) interlinks
	cp -r _extensions/ reference/_extensions	# Required to render footer

build:
	CURRENT_YEAR=$(CURRENT_YEAR) \
	VERSION=$(VERSION) \
	$(QUARTO) render

clean:
	rm -rf _extensions _inv _site .quarto reference objects.json
	find . -type d -empty -delete

deps:
	$(PIP) install --upgrade pip -r requirements-site.txt
	$(QUARTO) add --no-prompt posit-dev/product-doc-theme@v4.0.2
	$(QUARTO) add --no-prompt machow/quartodoc

preview:
	CURRENT_YEAR=$(CURRENT_YEAR) \
	VERSION=$(VERSION) \
	$(QUARTO) preview
