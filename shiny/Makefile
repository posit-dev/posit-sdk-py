include ../vars.mk

.DEFAULT_GOAL := all

.PHONY: deploy assistant assistant-update-prompt assistant-test-chat help

all: assistant-update-prompt

SHINY_DIRS:=$(subst .,,$(subst /,,$(dir $(wildcard ./*/app.py))))
deploy:
	$(foreach dir,$(SHINY_DIRS),$(MAKE) deploy-$(dir);)
deploy-%:
	cd "$*" && \
		$(UV) run rsconnect deploy shiny . -v

assistant:
	$(MAKE) assistant-update-prompt
assistant-update-prompt:
	cd assistant && \
		$(UV) run python _update_prompt.py
assistant-test-chat:
	cd assistant && \
		$(UV) run python _test_chat.py

help:
	@echo "Makefile Targets"
	@echo "  all                      Run assistant-update-prompt"
	@echo "  assistant                Run assistant-update-prmopt"
	@echo "  assistant-update-prompt  Update the assistant prompt"
	@echo "  assistant-test-chat      Test the assistant chat"
	@echo "  deploy                   Deploys each Shiny app"
	@echo "  deploy-<APPDIR>          Deploys the <APPDIR> Shiny app"
