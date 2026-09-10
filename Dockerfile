FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gateway/ ./gateway/
COPY shared/ ./shared/

CMD ["sh", "-c", "exec uvicorn gateway.api.app:app --host 0.0.0.0 --port ${GATEWAY_PORT:-${PORT:?GATEWAY_PORT or PORT environment variable must be set}}"]


