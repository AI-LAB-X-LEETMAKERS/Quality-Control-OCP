import sys
import traceback

from pypylon import pylon

try:
    factory = pylon.TlFactory.GetInstance()
    devices = factory.EnumerateDevices()
    print(f"Python: {sys.executable}")
    print(f"Detected cameras: {len(devices)}")
    for device in devices:
        print(f"- {device.GetFriendlyName()}")
except Exception:
    traceback.print_exc()

if __name__ == "__main__":
    pass