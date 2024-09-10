include ../vars.mk

# Site settings
PROJECT_VERSION ?= $(shell $(MAKE) -C ../ -s version)
CURRENT_YEAR ?= $(shell date +%Y)

# Quarto settings
QUARTO ?= quarto
QUARTODOC ?= quartodoc

# Netlify settings
NETLIFY_SITE_ID ?= 5cea1f56-7935-4387-975a-18a7905d15ee
NETLIFY_ARGS :=
ifeq ($(ENV), prod)
    NETLIFY_ARGS = --prod
endif

.DEFAULT_GOAL := all

.PHONY: all api build clean deps preview deploy

all: deps api build

api:
	$(QUARTODOC) build
	$(QUARTODOC) interlinks
	cp -r _extensions/ reference/_extensions  # Required to render footer

build:
	CURRENT_YEAR=$(CURRENT_YEAR) \
	PROJECT_VERSION=$(PROJECT_VERSION) \
	$(QUARTO) render

clean:
	rm -rf _extensions _inv _site .quarto reference objects.json
	find . -type d -empty -delete

deps:
	$(UV) pip install --upgrade pip -r requirements-site.txt
	$(QUARTO) add --no-prompt posit-dev/product-doc-theme@v4.0.2
	$(QUARTO) add --no-prompt machow/quartodoc

preview:
	CURRENT_YEAR=$(CURRENT_YEAR) \
	PROJECT_VERSION=$(PROJECT_VERSION) \
	$(QUARTO) preview

deploy:
	@NETLIFY_SITE_ID=$(NETLIFY_SITE_ID) npx -y netlify-cli deploy --dir _site --json $(NETLIFY_ARGS)
