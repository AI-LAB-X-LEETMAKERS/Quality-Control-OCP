from fastapi import APIRouter, HTTPException
from app.state import DustSensor
from app.sps30_service import sps30_service

DustRouter = APIRouter(tags=["dust"])

Internal_error: HTTPException = HTTPException(status_code=500, detail="Dust internal error")


@DustRouter.post("/dust", status_code=200)
async def update_dust(data: DustSensor):
    """Legacy endpoint for dust updates."""
    try:
        return {"status": "up"}
    except HTTPException:
        raise
    except Exception:
        raise Internal_error


@DustRouter.api_route("/dust/start", methods=["GET", "POST"], status_code=200)
async def start_dust_measurement():
    """Start SPS30 particle measurement (fan and laser on). Accepts both GET and POST."""
    try:
        await sps30_service.start_measurement()
        return {
            "status": "measuring",
            "message": "SPS30 measurement started. Fan is spinning up.",
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@DustRouter.api_route("/dust/stop", methods=["GET", "POST"], status_code=200)
async def stop_dust_measurement():
    """Stop SPS30 particle measurement (fan and laser off). Accepts both GET and POST."""
    try:
        await sps30_service.stop_measurement()
        return {
            "status": "idle",
            "message": "SPS30 measurement stopped.",
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@DustRouter.get("/dust/latest", status_code=200)
async def get_latest_dust_reading():
    """Retrieve the most recent SPS30 measurement snapshot."""
    return sps30_service.get_latest_reading()


@DustRouter.get("/dust/status", status_code=200)
async def get_dust_status():
    """Retrieve operational status of the SPS30 sensor."""
    return sps30_service.get_status()
