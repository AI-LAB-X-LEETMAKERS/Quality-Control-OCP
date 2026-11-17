from fastapi import APIRouter, HTTPException
from app.models import Port, cleaning, vibrator, vaccum
from app.serial_handler import serial_lock_esp
import json

MotorRoute = APIRouter(tags=["motor"])

Internal_error: HTTPException = HTTPException(status_code=500, detail="Motor internal error") 


@MotorRoute.post("/port", status_code=200)
async def control_port(data: Port):
    try:
        request:dict = ({"port":data.angle})
        command:str = json.dumps(request) + '\n'
        async with serial_lock_esp.lock:
            await serial_lock_esp.serial.write_async(command.encode())
        return {"status": "up"}
    except HTTPException:
        raise Internal_error
    except Exception as e:
        raise Internal_error
    
@MotorRoute.post("/cleaner", status_code=200)
async def control_cleaner(data: cleaning):
    try:
        
        request:dict = (
            {"cleaning":
            {"speed": data.speed, "forward": data.forward, "enabled": data.enabled} }
                    )
        commad: str = json.dumps(request) + '\n'
        async with serial_lock_esp.lock:
            await serial_lock_esp.serial.write_async(commad.encode())
            # read from the serial and get the cleaning current and return it
        return {"current": 30}
    except HTTPException:
        raise Internal_error
    except Exception as e:
        raise Internal_error
    
@MotorRoute.post("/vibrator", status_code=200)
async def control_vibrator(data: vibrator):
    try:        
        request:dict = (
            {"vibrator":
             {"speed": data.speed, "forward":data.forward}}
        )
        command:str = json.dumps(request) + '\n'
        async with serial_lock_esp.lock:
            await serial_lock_esp.serial.write_async(command.encode())
            # read from serial and get the current and return it 
        return {"status": "up"}
    except HTTPException:
        raise Internal_error
    except Exception as e:
        raise Internal_error
    
@MotorRoute.post("/vaccum", status_code=200)
async def control_vacum(data: vaccum):
    try:
        
        request:dict = ({"fan":
                    {"throttle": data.throttle, "armed": data.armed}}
                    )
        command: str = json.dumps(request) + '\n'
        async with serial_lock_esp.lock:
            await serial_lock_esp.serial.write_async(command.encode())
            # read from serial and return the current
        return {"current": 30}
    except HTTPException:
        raise Internal_error
    except Exception as e:
        raise Internal_error