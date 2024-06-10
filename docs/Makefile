.DEFAULT_GOAL := all

# Command aliases
PIP ?= pip3
QUARTO ?= quarto
QUARTODOC ?= quartodoc

# Environment variables
NETLIFY_SITE_ID ?= 5cea1f56-7935-4387-975a-18a7905d15ee
CURRENT_YEAR ?= $(shell date +%Y)
VERSION ?= $(shell make --silent -C ../ version | tail -n 1)

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


netlify:
	NETLIFY_SITE_ID=$(NETLIFY_SITE_ID) npx -y netlify-cli deploy --dir _site --json | jq '.deploy_url'
