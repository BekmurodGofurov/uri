FROM python:3.12-slim

WORKDIR /app

COPY aspect-svc/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY aspect-svc/app ./app
COPY aspect-svc/models ./models
COPY aspect-svc/training ./training
COPY shared/ ./shared/

# Standart: yengil keyword-stub xizmatda (tez build, torch/transformers kerak emas).
# Haqiqiy o'qitilgan modelni ishga tushirish uchun:
#   1. `pip install -r aspect-svc/requirements-ml.txt` ni ham qo'shing (ushbu Dockerfile'da
#      RUN qatoriga qo'shimcha qiling yoki alohida ml-Dockerfile yarating)
#   2. `models/aspect_model_v1/` papkasini (pytorch_model.bin, tokenizer, model_info.json)
#      shu image ichiga COPY qiling (Git LFS orqali repo'dan yoki tashqi manbadan)
#   3. Quyidagi ENV larni almashtiring: MODEL_TYPE=multilabel, MODEL_VERSION=aspect-multilabel-v1
ENV PYTHONPATH=/app \
    MODEL_VERSION=aspect-stub-v0.1 \
    MODEL_TYPE=keyword_stub

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]