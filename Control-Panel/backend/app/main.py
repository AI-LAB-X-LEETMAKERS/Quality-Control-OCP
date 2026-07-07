from fastapi import FastAPI
import uvicorn
from app.serial_handler import serial , serial_lock
from app.state import status_machine
from routers.motor import MotorRoute
from routers.dustsensor import DustRouter
from routers.wb import wb
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           
    allow_credentials=False,
    allow_methods=["*"],             
    allow_headers=["*"], 
)

@app.get("/on", status_code = 200)
async def on():
    async with serial_lock:
        await serial.write_async(b"1\n")
        return {
            "status": "on"}

@app.get("/off", status_code = 200)
async def off():
    async with serial_lock:
        await serial.write_async(b"0\n")
        return {
            "status": "off"}

routers = [DustRouter, MotorRoute, wb]

for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)