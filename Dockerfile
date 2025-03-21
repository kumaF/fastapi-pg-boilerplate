FROM ghcr.io/astral-sh/uv:python3.10-alpine

WORKDIR /code

RUN apk add gcc python3-dev musl-dev linux-headers

COPY pyproject.toml /code/pyproject.toml
COPY uv.lock /code/uv.lock
COPY alembic.ini /code/alembic.ini

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/code/.venv/bin:$PATH"

COPY alembic /code/alembic
COPY app /code/app

CMD [ "uv", "run", "fastapi", "run", "app/main.py", "--port", "80" ]