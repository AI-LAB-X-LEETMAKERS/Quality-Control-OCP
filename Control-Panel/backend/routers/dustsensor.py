from fastapi import APIRouter, HTTPException
from app.state import DustSensor
from app.sps30_service import DustDevice
from app.serial_handler import serial_lock
from app.state import DustSensor

DustRouter = APIRouter(tags=["dust"])

Internal_error: HTTPException = HTTPException(status_code=500, detail="Dust internal error")


@DustRouter.get("/dust", status_code=200, response_model=DustSensor)
async def update_dust():
    try:
        dust: DustSensor = await DustDevice.measure()
        return dust
    except HTTPException:
        raise
    except Exception:
        raise Internal_error

