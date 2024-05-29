.DEFAULT_GOAL := all

# Command aliases
QUARTO=quarto
QUARTODOC=quartodoc

# Targets
.PHONY: clean build preview

all: build

build:
	$(QUARTODOC) build
	$(QUARTO) render

clean:
	rm -rf _site reference objects.json
	find . -type d -empty -delete

preview:
	$(QUARTODOC) build
	$(QUARTO) preview
