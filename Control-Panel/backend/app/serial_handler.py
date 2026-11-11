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

PORT = "/dev/ttyACM0"
BAUDRATE = 115200

try:
    serial = aioserial.AioSerial(port=PORT, baudrate=BAUDRATE)
except Exception as err:
    sys.stderr.write(
        f"\n ESP32 connection failed on {PORT} at {BAUDRATE} baud.\n"
        f"Details: {err}\n"
    )
    sys.stderr.flush()
    sys.exit(1)

serial_lock = asyncio.Lock()
