import logging

from app.routes import router
from fastapi import FastAPI
from models.model_loader import load_model

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="aspect-svc",
    description="Aspect-based sentiment analysis — Uzum reviews",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    load_model()


app.include_router(router)
