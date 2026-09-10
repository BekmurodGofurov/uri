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


if __name__ == "__main__":
    import os
    import uvicorn

    port_val = os.getenv("ASPECT_PORT") or os.getenv("PORT")
    if not port_val:
        raise RuntimeError("ASPECT_PORT yoki PORT muhit o'zgaruvchisi .env faylida ko'rsatilishi shart")
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(port_val))


