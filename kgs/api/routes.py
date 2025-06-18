from fastapi import APIRouter, HTTPException
from services import key_service

router = APIRouter()

@router.post("/generate-keys")
async def generate_keys_endpoint(count: int = 1000):
    try:
        key_service.insert_keys(count)
        return {"message": f"Successfully inserted {count} keys."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-key")
async def get_key():
    key = key_service.fetch_and_reserve_key()
    if not key:
        raise HTTPException(status_code=404, detail="No unused keys available.")
    return {"shortKey": key}