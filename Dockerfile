FROM python:3

RUN apt-get update && apt-get install -y make

WORKDIR /sdk

COPY requirements.txt requirements-dev.txt vars.mk Makefile ./

RUN make deps

COPY .git ./.git
COPY src ./src
COPY pyproject.toml ./

RUN make build

RUN make install
