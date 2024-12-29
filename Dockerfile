FROM python:3.12-alpine3.21 AS base

ENV POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/.poetry

WORKDIR /app

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3

RUN apk add --no-cache gcc libffi-dev musl-dev postgresql-dev
RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin

COPY . .
RUN poetry build && /venv/bin/pip install dist/*.whl

FROM base as final

RUN apk add --no-cache libffi libpq
COPY --from=builder /venv /venv
COPY docker-entrypoint.sh wsgi.py ./

RUN ["chmod", "+x", "./docker-entrypoint.sh"]

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
#
## OLD
#
#RUN apt-get update && \
#    apt-get install --no-install-suggests --no-install-recommends --yes pipx
#ENV PATH="/root/.local/bin:${PATH}"
#
#RUN pipx install poetry==${POETRY_VERSION}
#RUN pipx inject poetry poetry-plugin-bundle
#
#WORKDIR /app
#COPY . .
#RUN poetry bundle venv --python=/usr/bin/python3 --only=main /venv
#
#FROM gcr.io/distroless/python3-debian12
#COPY --from=builder /venv /venv
#COPY docker-entrypoint.sh wsgi.py ./
#CMD ["./docker-entrypoint.sh"]
