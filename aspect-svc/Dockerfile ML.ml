FROM python:3.12-slim

WORKDIR /app

COPY aspect-svc/requirements-ml.txt .
RUN pip install --no-cache-dir -r requirements-ml.txt

COPY aspect-svc/app ./app
COPY aspect-svc/models/model_loader.py ./models/model_loader.py
COPY aspect-svc/training ./training
COPY shared/ ./shared/

ARG HF_TOKEN
ENV PYTHONPATH=/app \
    MODEL_VERSION=aspect-multilabel-v1 \
    MODEL_TYPE=multilabel \
    HF_MODEL_REPO=Jony-0009/isomiddinovs-model \
    MODEL_PATH=/app/models/aspect_model_v1 \
    HF_TOKEN=$HF_TOKEN

# Model fayllarini (model_info.json, pytorch_model.bin, tokenizer) build
# vaqtida Hugging Face Hub'dan tortib, image ichiga "pishirib" qo'yamiz —
# shunda runtime'da internetga chiqish shart bo'lmaydi va cold start tez bo'ladi.
RUN python -c "\
import os; \
from huggingface_hub import snapshot_download; \
snapshot_download(repo_id=os.environ['HF_MODEL_REPO'], local_dir=os.environ['MODEL_PATH'], token=os.environ.get('HF_TOKEN'))"

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
