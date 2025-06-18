from fastapi import FastAPI
from kgs.api.routes import router as key_router

app = FastAPI()

app.include_router(key_router)