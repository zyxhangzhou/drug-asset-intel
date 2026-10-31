# syntax=docker/dockerfile:1

FROM node:24-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS app
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src/ src/
COPY config/ config/
RUN uv sync --frozen --no-dev
COPY data/processed/intel.db data/processed/intel.db
COPY data/raw/docs/ data/raw/docs/
COPY --from=web /web/dist web/dist
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
# Hosting platforms (e.g. Render) inject PORT; default to 8000 locally.
CMD ["sh", "-c", "intel serve --host 0.0.0.0 --port ${PORT:-8000}"]
