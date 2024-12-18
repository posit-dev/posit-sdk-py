include ../vars.mk

# Site settings
PROJECT_VERSION ?= $(shell $(MAKE) -C ../ -s version)
CURRENT_YEAR ?= $(shell date +%Y)

# Quarto settings
QUARTO ?= quarto
# quartodoc doesn't like py3.8; Run using `--with` as it can conflict with the project's dependencies
QUARTODOC ?= --no-cache --with "quartodoc==0.8.1" quartodoc

# Netlify settings
NETLIFY_SITE_ID ?= 5cea1f56-7935-4387-975a-18a7905d15ee
NETLIFY_ARGS :=
ifeq ($(ENV), prod)
    NETLIFY_ARGS = --prod
endif

.DEFAULT_GOAL := all

.PHONY: all api build clean deps preview deploy

all: deps api build

ensure-dev:
	$(MAKE) -C .. dev

api: ensure-dev
	@echo "::group::quartodoc interlinks"
	$(UV) tool run --with ../ $(QUARTODOC) interlinks
	@echo "::endgroup::"
	@echo "::group::quartodoc build"
	$(UV) tool run --with ../ $(QUARTODOC) build --verbose
	@echo "::endgroup::"
	cp -r _extensions/ reference/_extensions  # Required to render footer

build: ensure-dev
	CURRENT_YEAR=$(CURRENT_YEAR) \
	PROJECT_VERSION=$(PROJECT_VERSION) \
	$(UV) tool run --with ../ \
	$(QUARTO) render

clean:
	rm -rf _extensions _inv _site .quarto reference objects.json
	find . -type d -empty -delete

_extensions/posit-dev/posit-docs/_extension.yml:
	$(QUARTO) add --no-prompt posit-dev/product-doc-theme@v4.0.2
_extensions/machow/interlinks/_extension.yml:
	$(QUARTO) add --no-prompt machow/quartodoc
deps: ensure-dev _extensions/posit-dev/posit-docs/_extension.yml _extensions/machow/interlinks/_extension.yml

preview: ensure-dev
	CURRENT_YEAR=$(CURRENT_YEAR) \
	PROJECT_VERSION=$(PROJECT_VERSION) \
	$(UV) tool run --with ../ \
	$(QUARTO) preview

deploy:
	@NETLIFY_SITE_ID=$(NETLIFY_SITE_ID) npx -y netlify-cli deploy --dir _site --json $(NETLIFY_ARGS)
