import logging

from fastapi import FastAPI

from app.model_loader import load_model
from app.routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="sentiment-svc",
    description="Uzbek sentiment analysis — Uzum reviews",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    load_model()


app.include_router(router)
