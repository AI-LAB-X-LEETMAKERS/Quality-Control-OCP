from pyndatic import BaseModel
from enum import Enum

class Direction(Enum):
    RIGHT = 1
    LEFT = 2

class Stats(Enum):
    IDLE = "IDLE"
    CALIBRATION = "CALIBRATION"
    CLEANING = "CLEANING"
    IMAGING = "IMAGING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Motor(BaseModel):
    name : str | None
    speed: int | None
    direction: Direction | None
    angle: int | None
    current: float | None

class WeightSensor(BaseModel):
    value: int | None
    current: float | None

class DustSensor(BaseModel):
    value : float | None
    current: float | None

class RPM(BaseModel):
    value: int | None

class StatMachine(BaseModel):
    stats: Stats
    cleaning: Motor
    vibrator: Motor
    port: Motor
    weight: WeightSensor
    rpm: RPM

status_machine = StatMachine()

