from app.serial_handler import serial_lock_dust
from app.models import DustSensor
import sys
import asyncio

PORT = "/dev/serial0"
BAUDRATE = 115200

try:
    from sensirion_shdlc_driver import ShdlcSerialPort
    from sensirion_driver_adapters.shdlc_adapter.shdlc_channel import ShdlcChannel
    from sensirion_uart_sps30.device import Sps30Device
    from sensirion_uart_sps30.commands import OutputFormat

except ImportError as e:
    sys.stderr.write(
        f"\nSPS30 driver dependencies not installed: {e}\n"
        "Please run 'make build'.\n\n"
    )
    sys.stderr.flush()
    sys.exit(1)


class Sps30:
    def __init__(self, port: str = PORT, baudrate: int = BAUDRATE):
        self.port_path = port
        self.baudrate = baudrate
        self.port: ShdlcSerialPort | None = None
        self.channel: ShdlcChannel | None = None
        self.device: Sps30Device = None 
        self.is_measuring = False

    async def measure(self) -> DustSensor:
        async with serial_lock_dust.lock:
            if self.device is None:
                try:
                    self.port = ShdlcSerialPort(port=self.port_path, baudrate=self.baudrate)
                    self.channel = ShdlcChannel(self.port)
                    self.device = Sps30Device(self.channel)
                except Exception as err:
                    sys.stderr.write(
                        f"\nSPS30 connection failed on {self.port_path} at {self.baudrate} baud.\n"
                        f"Details: {err}\n"
                    )
                    sys.stderr.flush()
                    sys.exit(1)

            if not self.is_measuring:
                await asyncio.to_thread(
                    self.device.start_measurement, OutputFormat.OUTPUT_FORMAT_FLOAT
                )
                self.is_measuring = True
                await asyncio.sleep(1.0)

            values = await asyncio.to_thread(self.device.read_measurement_values_float)
                
            return DustSensor(
                pm1_0=int(values[0]),
                pm2_5=int(values[1]),
                pm4_0=int(values[2]),
                pm10_0=int(values[3]),
                size=int(values[9]),
            )
    async def stop(self):
        if self.device is not None and self.is_measuring:
            await asyncio.to_thread(self.device.stop_measurement)
            self.is_measuring = False

DustDevice = Sps30(port="/dev/serial0", baudrate=115200)
