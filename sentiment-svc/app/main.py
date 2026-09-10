import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.model_loader import load_model
from app.routes import router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


app = FastAPI(
    title="sentiment-svc",
    description="Uzbek sentiment analysis — Uzum reviews",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


if __name__ == "__main__":
    import os
    import uvicorn

    port_val = os.getenv("SENTIMENT_PORT") or os.getenv("PORT")
    if not port_val:
        raise RuntimeError("SENTIMENT_PORT yoki PORT muhit o'zgaruvchisi .env faylida ko'rsatilishi shart")
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(port_val))


