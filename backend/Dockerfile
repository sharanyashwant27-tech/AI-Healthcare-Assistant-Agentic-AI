FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential libpq-dev tesseract-ocr ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Build from repo root: docker compose build (context: .)
COPY backend/requirements.txt .
ENV PIP_DEFAULT_TIMEOUT=120
# openai-whisper setup.py needs pkg_resources (setuptools<81) outside build isolation.
# legacy-resolver avoids modern resolver dead-ends across crewai/langchain pins.
RUN pip install --no-cache-dir --upgrade "pip" "setuptools>=70,<81" wheel \
    && grep -v '^openai-whisper' requirements.txt > /tmp/requirements-core.txt \
    && pip install --no-cache-dir --retries 10 --use-deprecated=legacy-resolver -r /tmp/requirements-core.txt \
    && pip install --no-cache-dir --retries 10 --no-build-isolation "openai-whisper==20240930"

COPY backend/ .
COPY README.md /app/README.md
COPY docs /app/docs

RUN mkdir -p /app/uploads /app/logs \
    && printf '%s\n' \
      "AI Healthcare Assistant container image" \
      "Docs: /app/README.md" \
      "API health: http://localhost:8000/health" \
      > /app/IMAGE_INFO.txt

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=10s --retries=5 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
