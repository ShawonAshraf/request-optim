FROM python:3.12.8-bookworm

WORKDIR /app

RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync
