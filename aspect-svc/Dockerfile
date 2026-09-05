FROM python:3.12-slim

WORKDIR /app

COPY aspect-svc/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY aspect-svc/app ./app
COPY shared/ ./shared/

ENV PYTHONPATH=/app \
    MODEL_VERSION=aspect-stub-v0.1 \
    MODEL_TYPE=keyword_stub

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
