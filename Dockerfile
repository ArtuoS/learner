FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY . .

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
