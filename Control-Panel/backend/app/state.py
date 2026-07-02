from pyndatic import BaseModel
from enum import Enum

class Direction(Enum):
    RIGHT = 1
    LEFT = 2

class Motor(BaseModel):
    name : str
    speed: int | None
    direction: Direction | None
    angle: int | None
    current: float

class WeightSensor(BaseModel):
    value: int 
    current: float

class DustSensor(BaseModel):
    value : float
    current: float

class StatMachine(BaseModel):
    rotator: Motor
    vibrator: Motor
    port: Motor
    dust: DustSensor
    weight: WeightSensor

