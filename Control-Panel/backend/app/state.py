from pydantic import BaseModel, Field
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
    name : str | None = ""
    speed: int | None = 0
    direction: Direction | None = Direction.RIGHT
    angle: int | None = 0
    current: float | None = 0

class WeightSensor(BaseModel):
    value: int | None = 0
    current: float | None = 0.0

class DustSensor(BaseModel):
    value : float | None = 0
    current: float | None = 0.0

class RPM(BaseModel):
    value: int | None = 0

class StatMachine(BaseModel):
    stats: Stats = Stats.IDLE
    cleaning: Motor = Field(default_factory=Motor)
    vibrator: Motor = Field(default_factory=Motor)
    port: Motor = Field(default_factory=Motor)
    weight: WeightSensor = Field(default_factory=WeightSensor)
    rpm: RPM = Field(default_factory=RPM)

status_machine = StatMachine()

