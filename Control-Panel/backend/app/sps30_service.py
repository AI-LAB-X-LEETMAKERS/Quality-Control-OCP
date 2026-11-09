import sys
import time
import asyncio
from typing import Callable, Coroutine, Any
from app.state import status_machine

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

try:
    from sensirion_shdlc_driver import ShdlcSerialPort
    from sensirion_driver_adapters.shdlc_adapter.shdlc_channel import ShdlcChannel
    from sensirion_uart_sps30.device import Sps30Device
except ImportError as e:
    sys.stderr.write(
        f"\n[FATAL ERROR] Sensirion SPS30 driver dependencies not installed: {e}\n"
        "Please run 'pip install -r requirement.txt'.\n\n"
    )
    sys.stderr.flush()
    sys.exit(1)


class SPS30Service:
    def __init__(self, port: str = PORT, baudrate: int = BAUDRATE):
        self.port_path = port
        self.baudrate = baudrate
        self.port: ShdlcSerialPort | None = None
        self.channel: ShdlcChannel | None = None
        self.device: Sps30Device | None = None
        self.is_measuring = False
        self._worker_task: asyncio.Task | None = None
        self._listeners: list[Callable[[dict], Coroutine[Any, Any, None]]] = []
        self._lock = asyncio.Lock()

        self.latest_data: dict = {
            "pm1_0": 0.0,
            "pm2_5": 0.0,
            "pm4_0": 0.0,
            "pm10_0": 0.0,
            "nc0_5": 0.0,
            "nc1_0": 0.0,
            "nc2_5": 0.0,
            "nc4_0": 0.0,
            "nc10_0": 0.0,
            "typical_particle_size": 0.0,
            "status": "IDLE",
            "timestamp": time.time(),
        }

    def init_hardware(self):
        """Initialize connection to physical SPS30 sensor via SHDLC channel. Exits on failure."""
        try:
            self.port = ShdlcSerialPort(port=self.port_path, baudrate=self.baudrate)
            self.channel = ShdlcChannel(self.port)
            self.device = Sps30Device(self.channel)
            serial_num = self.device.get_serial_number()
            product_type = self.device.get_product_type()
            sys.stdout.write(
                f"[SPS30] Connected on {self.port_path} | Product: {product_type} | Serial: {serial_num}\n"
            )
            sys.stdout.flush()
        except Exception as err:
            sys.stderr.write(
                f"\n[FATAL ERROR] SPS30 connection failed on {self.port_path} at {self.baudrate} baud.\n"
                f"Details: {err}\n"
                f"Exiting because physical SPS30 sensor is required.\n\n"
            )
            sys.stderr.flush()
            sys.exit(1)

    def register_listener(self, callback: Callable[[dict], Coroutine[Any, Any, None]]):
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unregister_listener(self, callback: Callable[[dict], Coroutine[Any, Any, None]]):
        if callback in self._listeners:
            self._listeners.remove(callback)

    async def start_service(self):
        """Start SPS30 background polling task."""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._poll_loop())

    async def stop_service(self):
        """Stop measurement and cancel background polling task."""
        await self.stop_measurement()
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        self._close_hardware()

    async def start_measurement(self):
        """Start sensor laser/fan and enable data acquisition."""
        async with self._lock:
            if not self.is_measuring:
                if self.device:
                    await asyncio.to_thread(self.device.start_measurement)
                self.is_measuring = True
                self.latest_data["status"] = "MEASURING"
                status_machine.dust.status = "MEASURING"

    async def stop_measurement(self):
        """Stop sensor laser/fan and pause data acquisition."""
        async with self._lock:
            if self.is_measuring:
                if self.device:
                    try:
                        await asyncio.to_thread(self.device.stop_measurement)
                    except Exception as err:
                        sys.stderr.write(f"[WARN] Error stopping SPS30 measurement: {err}\n")
                self.is_measuring = False
                self.latest_data["status"] = "IDLE"
                status_machine.dust.status = "IDLE"

    def _close_hardware(self):
        """Close serial port handle and adapters."""
        if self.port:
            try:
                self.port.close()
            except Exception:
                pass
            self.port = None
            self.channel = None
            self.device = None

    def _read_sensor_blocking(self) -> dict | None:
        """Synchronously query the SPS30 for measurement data."""
        if not self.device or not self.is_measuring:
            return None
        try:
            # Check data ready flag if supported
            if hasattr(self.device, "get_data_ready_flag") and not self.device.get_data_ready_flag():
                return None

            raw = self.device.read_measured_values()

            # Handle unpacked tuple/list or object format
            if isinstance(raw, (list, tuple)) and len(raw) >= 10:
                pm1_0, pm2_5, pm4_0, pm10_0, nc0_5, nc1_0, nc2_5, nc4_0, nc10_0, typical_size = raw[:10]
            elif hasattr(raw, "pm1p0"):
                pm1_0 = raw.pm1p0.value
                pm2_5 = raw.pm2p5.value
                pm4_0 = raw.pm4p0.value
                pm10_0 = raw.pm10p0.value
                nc0_5 = raw.nc0p5.value
                nc1_0 = raw.nc1p0.value
                nc2_5 = raw.nc2p5.value
                nc4_0 = raw.nc4p0.value
                nc10_0 = raw.nc10p0.value
                typical_size = raw.typical_particle_size.value
            else:
                pm1_0, pm2_5, pm4_0, pm10_0 = raw[0], raw[1], raw[2], raw[3]
                nc0_5, nc1_0, nc2_5, nc4_0, nc10_0 = raw[4], raw[5], raw[6], raw[7], raw[8]
                typical_size = raw[9]

            return {
                "pm1_0": round(float(pm1_0), 2),
                "pm2_5": round(float(pm2_5), 2),
                "pm4_0": round(float(pm4_0), 2),
                "pm10_0": round(float(pm10_0), 2),
                "nc0_5": round(float(nc0_5), 2),
                "nc1_0": round(float(nc1_0), 2),
                "nc2_5": round(float(nc2_5), 2),
                "nc4_0": round(float(nc4_0), 2),
                "nc10_0": round(float(nc10_0), 2),
                "typical_particle_size": round(float(typical_size), 2),
                "status": "MEASURING",
                "timestamp": round(time.time(), 2),
            }
        except Exception as err:
            sys.stderr.write(f"[ERROR] Error reading SPS30 values: {err}\n")
            return None

    async def _poll_loop(self):
        """Background loop reading SPS30 at 1 Hz when measuring."""
        while True:
            try:
                if self.is_measuring:
                    reading = await asyncio.to_thread(self._read_sensor_blocking)
                    if reading:
                        self.latest_data = reading
                        # Update shared state machine
                        status_machine.dust.pm1_0 = reading["pm1_0"]
                        status_machine.dust.pm2_5 = reading["pm2_5"]
                        status_machine.dust.pm4_0 = reading["pm4_0"]
                        status_machine.dust.pm10_0 = reading["pm10_0"]
                        status_machine.dust.nc0_5 = reading["nc0_5"]
                        status_machine.dust.nc1_0 = reading["nc1_0"]
                        status_machine.dust.nc2_5 = reading["nc2_5"]
                        status_machine.dust.nc4_0 = reading["nc4_0"]
                        status_machine.dust.nc10_0 = reading["nc10_0"]
                        status_machine.dust.typical_particle_size = reading["typical_particle_size"]
                        status_machine.dust.value = reading["pm2_5"]
                        status_machine.dust.status = "MEASURING"

                        # Broadcast to all registered WebSocket listeners
                        for listener in list(self._listeners):
                            try:
                                await listener(reading)
                            except Exception:
                                pass
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                sys.stderr.write(f"[ERROR] Uncaught in SPS30 loop: {e}\n")
                await asyncio.sleep(1.0)

    def get_latest_reading(self) -> dict:
        return self.latest_data

    def get_status(self) -> dict:
        return {
            "status": "MEASURING" if self.is_measuring else "IDLE",
            "is_measuring": self.is_measuring,
            "port": self.port_path,
            "baudrate": self.baudrate,
        }


sps30_service = SPS30Service()
