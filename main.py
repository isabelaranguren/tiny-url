from fastapi import FastAPI
from kgs.api.routes import router as key_router
from shortener_service.api.routes import router as shortener_router

app = FastAPI()

app.include_router(key_router, prefix="/kgs")
app.include_router(shortener_router)