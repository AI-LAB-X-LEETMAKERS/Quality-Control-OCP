import sys
import asyncio

try:
    import aioserial
except ImportError as e:
    sys.stderr.write(
        f"\n Missing dependency 'aioserial': {e}\n"
        "make build'.\n\n"
    )
    sys.stderr.flush()
    sys.exit(1)

PORT_ESP = "/dev/ttyACM0"
PORT_DUST = "/dev/serial0"
BAUDRATE = 115200


class SerialLock:
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate
        self.lock = asyncio.Lock()
    def open(self):
        try:
            self.serial = aioserial.AioSerial(port=self.port, baudrate=self.baudrate)
        except Exception as err:
            if self.port == PORT_ESP:
                sys.stderr.write(
                    f"\n ESP32 connection failed on {self.port} at {self.baudrate} baud.\n"
                    f"Details: {err}\n"
                )
            else:
                sys.stderr.write(
                    f"\n Dust sensor connection failed on {self.port} at {self.baudrate} baud.\n"
                    f"Details: {err}\n"
                )
            sys.stderr.flush()
            sys.exit(1)

serial_lock_esp: SerialLock = SerialLock(port=PORT_ESP, baudrate=BAUDRATE)
serial_lock_dust: SerialLock = SerialLock(port=PORT_DUST, baudrate=BAUDRATE)
