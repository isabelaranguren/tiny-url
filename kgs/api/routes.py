from fastapi import APIRouter, HTTPException
from botocore.exceptions import ClientError
from kgs.services import key_service

router = APIRouter()

@router.post("/generate-keys")
async def generate_keys_endpoint(count: int = 1000):
    """
    Generate a batch of keys.
    """
    try:
        key_service.batch_generate_keys(count)
        return {"message": f"Successfully inserted {count} keys."}
    except ClientError as e:
        # AWS-specific errors
        raise HTTPException(status_code=502, detail=f"AWS Client error: {e.response['Error']['Message']}")
    except Exception as e:
        # General errors
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-key")
async def get_key_endpoint():
    """
    Fetch and reserve one unused key.
    """
    try:
        key = key_service.fetch_and_reserve_key()
        if key is None:
            raise HTTPException(status_code=404, detail="No available keys")
        return {"key": key}
    except ClientError as e:
        raise HTTPException(status_code=502, detail=f"AWS Client error: {e.response['Error']['Message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/metrics")
def metrics():
    return key_service.get_metrics()