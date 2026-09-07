FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gateway/ ./gateway/
COPY shared/ ./shared/

ENV PYTHONPATH=/app \
    PORT=8000

EXPOSE 8000

CMD ["uvicorn", "gateway.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
