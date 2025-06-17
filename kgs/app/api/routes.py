from fastapi import APIRouter, HTTPException
from app.services.key_service import get_available_key

router = APIRouter()

@router.get("/get-key")
def get_key():
    key = get_available_key()
    if key:
        return {"shortKey": key}
    else:
        raise HTTPException(status_code=404, detail="No keys available")