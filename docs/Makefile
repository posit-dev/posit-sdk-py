.DEFAULT_GOAL := all

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
	quarto add --no-prompt machow/quartodoc

preview:
	$(QUARTODOC) build
	$(QUARTODOC) interlinks
	$(QUARTO) preview
