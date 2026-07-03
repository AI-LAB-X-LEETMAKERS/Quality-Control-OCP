from fastapi import APIRouter, HTTPException
from app.state import Motor

# class Motor(BaseModel):
#     name : str | None
#     speed: int | None
#     direction: Direction | None
#     angle: int | None
#     current: float | None

MotorRoute = APIRouter(tags=["motor"])


@MotorRoute.post("/motor", status_code = 200)
async def control_motor(data: Motor):
    try:
        request = f"name:{data.name},\
            speed:{data.speed},direction:{data.direction},angle:{data.angle},current:0\n"
        
        return {"status": "up"}
    except HTTPException:
        raise