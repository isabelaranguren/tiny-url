from fastapi import APIRouter
from shortener_service.services.shortener import URLShortenerService

router = APIRouter()
service = URLShortenerService(table_name="UrlMappings")


@router.post("/shorten")
def shorten(short_key: str, long_url: str):
    if service.shorten_url(short_key, long_url):
        return {"shortKey": short_key}
    return {"error": "Key already exists"}, 409


@router.get("/{short_key}")
def redirect(short_key: str):
    url = service.get_long_url(short_key)
    if url:
        return {"url": url}
    return {"error": "Not found"}, 404