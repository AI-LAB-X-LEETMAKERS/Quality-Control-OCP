from fastapi import APIRouter, HTTPException
from app.state import DustSensor

# class Motor(BaseModel):
#     name : str | None
#     speed: int | None
#     direction: Direction | None
#     angle: int | None
#     current: float | None

DustRouter = APIRouter(tags=["dust"])

Internal_error: HTTPException = HTTPException(status_code = 500, detail = "Dust Internal error")

@DustRouter.post("/dust", status_code = 200)
async def control_motor(data: DustSensor):
    try:
        return {"status": "up"}
    except HTTPException:
        raise