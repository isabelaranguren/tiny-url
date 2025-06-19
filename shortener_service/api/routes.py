from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from shortener_service.services.shortener import URLShortenerService
from kgs.services.key_service import fetch_and_reserve_key

router = APIRouter()

TABLE_NAME = "URLMappings"

shortener_service = URLShortenerService(table_name=TABLE_NAME)

class ShortenRequest(BaseModel):
    original_url: str

class ShortenResponse(BaseModel):
    short_url: str

class ResolveResponse(BaseModel):
    original_url: str

@router.post("/shorten", response_model=ShortenResponse)
def shorten_url(request: ShortenRequest):
    short_key = fetch_and_reserve_key()
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