import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from app.sps30_service import DustDevice
from app.models import DustSensor
# from app.serial_handler import serial_lock

ws = APIRouter(tags=["websocket"])


@ws.websocket("/ws/dust")
async def websocket_dust(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            dust: DustSensor = await DustDevice.measure()
            await websocket.send_json(dict(dust))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass

# @ws.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             async with serial_lock:
#                 line = await serial.readline_async()
#             if line:
#                 await websocket.send_text(line.decode(errors="replace"))
#             else:
#                 await asyncio.sleep(0.1)
#     except WebSocketDisconnect:
#         pass
#     except Exception:
#         pass
