# wapimaji-mcp — Dockerfile for Glama sandbox evaluation
FROM python:3.11-slim

LABEL org.opencontainers.image.title="wapimaji-mcp"
LABEL org.opencontainers.image.description="MCP server for Kenya water stress and drought intelligence"
LABEL org.opencontainers.image.source="https://github.com/gabrielmahia/wapimaji-mcp"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Gabriel Mahia <contact@aikungfu.dev>"
LABEL org.opencontainers.image.version="0.1.0"

RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

USER mcpuser

ENV SANDBOX=true
ENV AT_USERNAME="sandbox"
ENV AT_API_KEY=""

ENTRYPOINT ["wapimaji-mcp"]
