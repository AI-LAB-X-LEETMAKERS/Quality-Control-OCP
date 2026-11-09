from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# from app.serial_handler import serial, serial_lock
# # from app.sps30_service import sps30_service
# from routers.motor import MotorRoute
# from routers.dustsensor import DustRouter
# from routers.ws import ws


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     sps30_service.init_hardware()
#     await sps30_service.start_service()
#     yield
#     await sps30_service.stop_service()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status", status_code=200)
def stattus():
    return {"status" : "alive"}

# @app.get("/on", status_code=200)
# async def on():
#     async with serial_lock:
#         await serial.write_async(b"1\n")
#     await sps30_service.start_measurement()
#     return {"status": "on"}


# @app.get("/off", status_code=200)
# async def off():
#     async with serial_lock:
#         await serial.write_async(b"0\n")
#     await sps30_service.stop_measurement()
#     return {"status": "off"}


routers = [DustRouter, MotorRoute, ws]

for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
