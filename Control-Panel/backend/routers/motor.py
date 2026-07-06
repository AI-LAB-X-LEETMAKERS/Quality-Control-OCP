from fastapi import APIRouter, HTTPException
from app.state import Motor
from app.serial_handler import serial_lock, serial

# class Motor(BaseModel):
#     name : str | None
#     speed: int | None
#     direction: Direction | None
#     angle: int | None
#     current: float | None

MotorRoute = APIRouter(tags=["motor"])

Internal_error: HTTPException = HTTPException(status_code = 500, detail="Motor internal error") 

@MotorRoute.post("/lock", status_code = 200)
async def control_lock(data: Motor):
    try:
        request = f"name:{data.name},\
            speed:{data.speed},direction:{data.direction},angle:{data.angle},current:0\n"
        async with serial_lock:
            await serial.write_async(request.encode()) # always encode data to utf-8 before writing to the serial same for reading from the serial always decode
        return {"status": "up"}
    except HTTPException:
        raise
    except Exception as e:
        raise Internal_error

@MotorRoute.post("/port", status_code = 200)
async def control_port(data: Motor):
    try:
        request = f"name:{data.name},\
            speed:{data.speed},direction:{data.direction},angle:{data.angle},current:0\n"
        async with serial_lock:
            await serial.write_async(request.encode()) #always encode data to utf-8 before writing to the serial same for reading from the serial always decode
        return {"status": "up"}
    except HTTPException:
        raise Internal_error
    
@MotorRoute.post("/cleaner", status_code = 200)
async def control_cleaner(data: Motor):
    try:
        request = f"name:{data.name},\
            speed:{data.speed},direction:{data.direction},angle:{data.angle},current:0\n"
        async with serial_lock:
            await serial.write_async(request.encode()) #always encode data to utf-8 before writing to the serial same for reading from the serial always decode
        return {"status": "up"}
    except HTTPException:
        raise Internal_error
    
@MotorRoute.post("/vibrator", status_code = 200)
async def control_vibrator(data: Motor):
    try:
        request = f"name:{data.name},\
            speed:{data.speed},direction:{data.direction},angle:{data.angle},current:0\n"
        async with serial_lock:
            await serial.write_async(request.encode()) #always encode data to utf-8 before writing to the serial same for reading from the serial always decode
        return {"status": "up"}
    except HTTPException:
        raise Internal_error
    
@MotorRoute.post("/vacum", status_code = 200)
async def control_vacum(data: Motor):
    try:
        request = f"name:{data.name},\
            speed:{data.speed},direction:{data.direction},angle:{data.angle},current:0\n"
        async with serial_lock:
            await serial.write_async(request.encode()) #always encode data to utf-8 before writing to the serial same for reading from the serial always decode
        return {"status": "up"}
    except HTTPException:
        raise Internal_error