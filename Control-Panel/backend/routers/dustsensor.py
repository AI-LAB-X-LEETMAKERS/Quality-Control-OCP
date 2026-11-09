from fastapi import APIRouter, HTTPException
from app.state import DustSensor
from app.sps30_service import sps30_service

DustRouter = APIRouter(tags=["dust"])

Internal_error: HTTPException = HTTPException(status_code=500, detail="Dust internal error")


@DustRouter.post("/dust", status_code=200)
async def update_dust(data: DustSensor):
    try:
        return {"status": "up"}
    except HTTPException:
        raise
    except Exception:
        raise Internal_error


@DustRouter.post("/dust/start", status_code=200)
async def start_dust_measurement():
    try:
        await sps30_service.start_measurement()
        return {"status": "measuring"}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@DustRouter.post("/dust/stop", status_code=200)
async def stop_dust_measurement():
    try:
        await sps30_service.stop_measurement()
        return {"status": "idle"}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@DustRouter.get("/dust/latest", status_code=200)
async def get_latest_dust_reading():
    return sps30_service.get_latest_reading()


@DustRouter.get("/dust/status", status_code=200)
async def get_dust_status():
    return sps30_service.get_status()
