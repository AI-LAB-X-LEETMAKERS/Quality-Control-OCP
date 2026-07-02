from fastapi import FastAPI
import uvicorn
from serial_handler import serial
from state import status_machine
# uvicorn app.main:app --host 0.0.0.0 --port 8000

app = FastAPI()

@app.get("/health")
def check_health():
    serial
    return {
        "status": "up",
        "dust": status_machine.dust}

#context manager for startup and wait for the response to display it and allow the user to start the machine


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)