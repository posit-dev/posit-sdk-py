FROM python:3

RUN apt-get update && apt-get install -y make

WORKDIR /sdk

COPY Makefile pyproject.toml vars.mk uv.lock ./

# Run before `COPY src src` to cache dependencies for faster iterative builds
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip make docker-deps

COPY .git .git
COPY src src

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip make dev
