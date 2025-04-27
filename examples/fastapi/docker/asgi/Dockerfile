# -----------------------------------------------------------
# Pre base image
# Installs base dependencies and sets up python
# -----------------------------------------------------------
FROM python:3.11 AS pre-base

WORKDIR /

RUN pip install pip==25.0.1 && \
    pip install poetry==2.1.1

ENV PYTHONUNBUFFERED 1 \
    PYTHONDONTWRITEBYTECODE=1

RUN poetry config virtualenvs.in-project true && \
    poetry config virtualenvs.create true && \
    poetry config cache-dir /tmp/poetry_cache

COPY ./src/poetry.lock ./src/pyproject.toml ./


# -----------------------------------------------------------
# Pre base image with dependencies
# Installs python dependencies with poetry
# -----------------------------------------------------------
FROM pre-base AS pre-base-dependencies

RUN poetry install --no-interaction && \
    # clear poetry cache
    rm -rf /tmp/poetry_cache

# -----------------------------------------------------------
# Base image
# Copies python devendencies from pre base image and sets up python
# -----------------------------------------------------------
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED 1 \
    PYTHONDONTWRITEBYTECODE=1

RUN mkdir /apps/
WORKDIR /apps/

ENV VIRTUAL_ENV=/.venv \
    PATH="/.venv/bin:$PATH"

COPY --from=pre-base-dependencies ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY ./src/ ./


# ***********************************************************
# Ready to use images from now on
# ***********************************************************

# -----------------------------------------------------------
# ASGI started with uvicorn
# -----------------------------------------------------------
FROM base AS uvicorn-asgi

WORKDIR /apps/

COPY ./docker/asgi/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["bash", "/entrypoint.sh"]
