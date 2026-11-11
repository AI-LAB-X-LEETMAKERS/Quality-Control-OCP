from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# from routers.motor import MotorRoute
from app.sps30_service import DustDevice
from routers.dustsensor import DustRouter
from routers.ws import ws

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await DustDevice.stop()

app = FastAPI(lifespan=lifespan)

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


routers = [DustRouter, ws]

for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
