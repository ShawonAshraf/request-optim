FROM python:3.12-alpine3.21

WORKDIR /app

RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync
