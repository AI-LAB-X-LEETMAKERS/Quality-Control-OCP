import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from app.serial_handler import serial, serial_lock
from app.sps30_service import sps30_service

ws = APIRouter(tags=["websocket"])


class DustConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)


dust_manager = DustConnectionManager()
sps30_service.register_listener(dust_manager.broadcast)


@ws.websocket("/ws/dust")
async def websocket_dust(websocket: WebSocket):
    await dust_manager.connect(websocket)
    try:
        await websocket.send_json(sps30_service.get_latest_reading())
        while True:
            text = await websocket.receive_text()
            cmd = text.strip().lower()
            if cmd == "start":
                await sps30_service.start_measurement()
            elif cmd == "stop":
                await sps30_service.stop_measurement()
    except WebSocketDisconnect:
        dust_manager.disconnect(websocket)
    except Exception:
        dust_manager.disconnect(websocket)


@ws.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            async with serial_lock:
                line = await serial.readline_async()
            if line:
                await websocket.send_text(line.decode(errors="replace"))
            else:
                await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
