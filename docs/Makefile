include ../vars.mk

VERSION := $(shell $(MAKE) -C ../ -s version)

.DEFAULT_GOAL := all

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

deploy:
	@NETLIFY_SITE_ID=$(NETLIFY_SITE_ID) npx -y netlify-cli deploy --dir _site --json $(NETLIFY_ARGS)
