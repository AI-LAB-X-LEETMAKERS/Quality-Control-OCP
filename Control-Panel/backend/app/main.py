from fastapi import FastAPI
import uvicorn
from app.serial_handler import serial , serial_lock
from app.state import status_machine
from routers.motor import MotorRoute
from routers.dustsensor import DustRouter
from routers.wb import wb


app = FastAPI()

@app.get("/on")
async def on():
    async with serial_lock:
        await serial.write_async(b"1\n")
        return {
            "status": "on"}

@app.get("/off")
async def off():
    async with serial_lock:
        await serial.write_async(b"0\n")
        return {
            "status": "off"}

#context manager for startup and wait for the response to display it and allow the user to start the machine
routers = [DustRouter, MotorRoute, wb]

for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)