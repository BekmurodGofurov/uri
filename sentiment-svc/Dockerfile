FROM python:3.11-slim

WORKDIR /workspace

# Install dependencies first (layer-cached)
COPY sentiment-svc/requirements.txt sentiment-svc/requirements.txt
RUN pip install --no-cache-dir -r sentiment-svc/requirements.txt

# Copy the monorepo root so shared/ is importable
COPY shared/ shared/
COPY sentiment-svc/ sentiment-svc/

WORKDIR /workspace/sentiment-svc

# Expose the monorepo root so `import shared` works without a try/except
ENV PYTHONPATH=/workspace \
    MODEL_PATH=models/tfidf_v1.joblib \
    MODEL_VERSION=sentiment-v1 \
    MODEL_TYPE=tfidf

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${SENTIMENT_PORT:-${PORT:?SENTIMENT_PORT or PORT environment variable must be set}}"]