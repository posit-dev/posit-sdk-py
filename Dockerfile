FROM python:3

RUN apt-get update && apt-get install -y make

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip pip install rsconnect

WORKDIR /sdk

COPY Makefile pyproject.toml requirements.txt requirements-dev.txt vars.mk ./
COPY .git .git
COPY src src

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip make deps
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip make dev
