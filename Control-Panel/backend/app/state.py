from pydantic import BaseModel, Field
from enum import Enum

class Direction(Enum):
    RIGHT = "RIGHT"
    LEFT = "LEFT"

class Stats(Enum):
    IDLE = "IDLE"
    CALIBRATION = "CALIBRATION"
    CLEANING = "CLEANING"
    IMAGING = "IMAGING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Motor(BaseModel):
    name: str | None = ""
    speed: int | None = 0
    direction: Direction | None = Direction.RIGHT
    angle: int | None = 0

class WeightSensor(BaseModel):
    value: int | None = 0
    current: float | None = 0.0

class DustSensor(BaseModel):
    pm1_0: float = 0.0
    pm2_5: float = 0.0
    pm4_0: float = 0.0
    pm10_0: float = 0.0
    size: float = 0.0

class RPM(BaseModel):
    value: int | None = 0

class StatMachine(BaseModel):
    stats: Stats = Stats.IDLE
    cleaning: Motor = Field(default_factory=Motor)
    vibrator: Motor = Field(default_factory=Motor)
    port: Motor = Field(default_factory=Motor)
    weight: WeightSensor = Field(default_factory=WeightSensor)
    dust: DustSensor = Field(default_factory=DustSensor)
    rpm: RPM = Field(default_factory=RPM)

status_machine = StatMachine()
