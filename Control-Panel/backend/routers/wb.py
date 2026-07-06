from app.serial_handler import serial, serial_lock
from fastapi import WebSocket, APIRouter
from websockets.legacy.protocol import broadcast


wb = APIRouter(tags=["websocket"])


@wb.websocket("/wb")
async def websocket_endpoit(websocket: WebSocket):
    await websocket.accept()
    while True:
        async with serial_lock:
            command= await serial.readline_async()
            await websocket.send_text(command.decode())
