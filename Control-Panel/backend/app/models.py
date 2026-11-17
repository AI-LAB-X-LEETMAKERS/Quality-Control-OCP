from pydantic import BaseModel, Field
from enum import Enum

class Stats(Enum):
    IDLE = "IDLE"
    CALIBRATION = "CALIBRATION"
    CLEANING = "CLEANING"
    IMAGING = "IMAGING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Port(BaseModel):
    angle: int

class cleaning(BaseModel):
    speed: int
    forward: bool
    enabled:bool

class vibrator(BaseModel):
    speed:int
    forward:bool

class vaccum(BaseModel):
    throttle: int
    armed: bool    

class WeightSensor(BaseModel):
    value: int | None = 0
    current: float | None = 0.0

class DustSensor(BaseModel):
    pm1_0: int = 0
    pm2_5: int  = 0
    pm4_0: int  = 0
    pm10_0: int = 0
    size: int   = 0

class RPM(BaseModel):
    value: int | None = 0

