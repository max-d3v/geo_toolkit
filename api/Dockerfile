FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install -e .

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1


CMD if [ "$RELOAD" = "true" ]; then \
    python -m uvicorn api:app --host 0.0.0.0 --reload; \
else \
    python -m uvicorn api:app --host 0.0.0.0; \
fi
