FROM python:3

ENV UV_SYSTEM_PYTHON=true

RUN apt-get update && apt-get install -y make

WORKDIR /sdk

COPY Makefile pyproject.toml requirements.txt requirements-dev.txt vars.mk ./

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip make deps

COPY .git .git
COPY src src

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip make dev
