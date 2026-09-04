FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MODEL_PATH=models/tfidf_v1.joblib \
    MODEL_VERSION=sentiment-v1 \
    MODEL_TYPE=tfidf

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]