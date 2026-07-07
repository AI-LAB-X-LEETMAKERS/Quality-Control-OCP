import asyncio
import aioserial


serial = aioserial.AioSerial(port="/dev/ttyACM0", baudrate=115200)

serial_lock = asyncio.Lock()

