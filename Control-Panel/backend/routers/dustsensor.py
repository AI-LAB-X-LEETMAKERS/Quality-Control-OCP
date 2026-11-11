from fastapi import APIRouter, HTTPException
from app.models import DustSensor
from app.sps30_service import DustDevice

DustRouter = APIRouter(tags=["dust"])

Internal_error: HTTPException = HTTPException(status_code=500, detail="Dust internal error")


@DustRouter.get("/dust", status_code=200, response_model=DustSensor)
async def update_dust():
    try:
        dust: DustSensor = await DustDevice.measure()
        return dust
    except HTTPException as e:
        print(f"HTTP error occurred: {e}")
        raise e
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        raise Internal_error
    finally:
        await DustDevice.stop()

