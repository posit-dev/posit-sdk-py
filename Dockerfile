FROM python:3

ENV UV_SYSTEM_PYTHON=true

RUN apt-get update && apt-get install -y make

WORKDIR /sdk

COPY Makefile pyproject.toml vars.mk ./

COPY .git .git
COPY src src

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip make dev
