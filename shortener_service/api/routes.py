from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from shortener_service.services.shortener import URLShortenerService
from kgs.services.key_service import KeyPoolService

router = APIRouter()

TABLE_NAME = "URLMappings"
KEYPOOL_TABLE = "KeyPool"

shortener_service = URLShortenerService(table_name=TABLE_NAME)
key_service = KeyPoolService(table_name=KEYPOOL_TABLE)

class ShortenRequest(BaseModel):
    original_url: str

class ShortenResponse(BaseModel):
    short_url: str

class ResolveResponse(BaseModel):
    original_url: str

@router.post("/shorten", response_model=ShortenResponse)
def shorten_url(request: ShortenRequest):
    short_key = key_service.reserve_available_key() 
    if not short_key:
        raise HTTPException(status_code=500, detail="No available short keys.")

    success = shortener_service.shorten_url(short_key, request.original_url)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to store shortened URL.")

    return {"short_url": f"http://localhost:8000/{short_key}"}

@router.get("/{short_key}", response_model=ResolveResponse)
def resolve_url(short_key: str):
    long_url = shortener_service.get_long_url(short_key)
    if not long_url:
        raise HTTPException(status_code=404, detail="Short URL not found.")
    return {"original_url": long_url}