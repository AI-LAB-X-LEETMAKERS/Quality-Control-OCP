from fastapi import APIRouter, HTTPException
from app.state import Motor
from app.serial_handler import serial_lock, serial

# class Motor(BaseModel):
#     name : str | None
#     speed: int | None
#     direction: Direction | None
#     angle: int | None
#     current: float | None

# {
#   "cleaning": {
#     "speed": 50,
#     "forward": true
#   },
#   "vibrator": {
#     "speed": 50,
#     "forward": true
#   },
#   "port": {
#     "angle": 90
#   },
#   "lock": {
#     "angle": 120
#   }
# }
MotorRoute = APIRouter(tags=["motor"])

Internal_error: HTTPException = HTTPException(status_code=500, detail="Motor internal error") 

@MotorRoute.post("/lock", status_code=200)
async def control_lock(data: Motor):
    try:
        is_forward = "true" if data.direction == "RIGHT" else "false"        
        request = (
            f'{{\n'
            f'  "lock": {{\n'
            f'    "speed": {data.speed},\n'
            f'    "forward": {is_forward},\n'
            f'    "angle": {data.angle}\n'
            f'  }}\n'
            f'}}\n'
        )
        
        async with serial_lock:
            await serial.write_async(request.encode())
        return {"current": 30}
    except HTTPException:
        raise
    except Exception as e:
        raise Internal_error

@MotorRoute.post("/port", status_code=200)
async def control_port(data: Motor):
    try:
        is_forward = "true" if data.direction == "RIGHT" else "false"
        
        request = (
            f'{{\n'
            f'  "port": {{\n'
            f'    "speed": {data.speed},\n'
            f'    "forward": {is_forward},\n'
            f'    "angle": {data.angle}\n'
            f'  }}\n'
            f'}}\n'
        )
        
        async with serial_lock:
            await serial.write_async(request.encode())
        return {"current": 30}
    except HTTPException:
        raise Internal_error
    except Exception as e:
        raise Internal_error
    
@MotorRoute.post("/cleaner", status_code=200)
async def control_cleaner(data: Motor):
    try:
        is_forward = "true" if data.direction == "RIGHT" else "false"
        
        request = (
            f'{{\n'
            f'  "cleaning": {{\n'
            f'    "speed": {data.speed},\n'
            f'    "forward": {is_forward}\n'
            f'  }}\n'
            f'}}\n'
        )
        
        async with serial_lock:
            await serial.write_async(request.encode())
        return {"current": 30}
    except HTTPException:
        raise Internal_error
    except Exception as e:
        raise Internal_error
    
@MotorRoute.post("/vibrator", status_code=200)
async def control_vibrator(data: Motor):
    try:
        is_forward = "true" if data.direction == "RIGHT" else "false"
        
        request = (
            f'{{\n'
            f'  "vibrator": {{\n'
            f'    "speed": {data.speed},\n'
            f'    "forward": {is_forward}\n'
            f'  }}\n'
            f'}}\n'
        )
        
        async with serial_lock:
            await serial.write_async(request.encode())
        return {"current": 30}
    except HTTPException:
        raise Internal_error
    except Exception as e:
        raise Internal_error
    
@MotorRoute.post("/vacum", status_code=200)
async def control_vacum(data: Motor):
    try:
        is_forward = "true" if data.direction == "RIGHT" else "false"
        
        request = (
            f'{{\n'
            f'  "vacum": {{\n'
            f'    "speed": {data.speed},\n'
            f'    "forward": {is_forward}\n'
            f'  }}\n'
            f'}}\n'
        )
        
        async with serial_lock:
            await serial.write_async(request.encode())
        return {"current": 30}
    except HTTPException:
        raise Internal_error
    except Exception as e:
        raise Internal_error