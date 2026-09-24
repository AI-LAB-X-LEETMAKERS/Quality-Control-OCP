# Quality Control OCP - Backend Documentation

Simple overview of the FastAPI backend application for the Quality Control OCP machine interface.

---

## 1. Overview

The backend is built with **FastAPI** and handles asynchronous communication between the Web UI frontend and the ESP32 microcontroller over a serial connection (`aioserial`).

- **Base URL**: `http://localhost:8000`
- **Serial Interface**: `/dev/ttyACM0` at `115200` baud rate.

---

## 2. Project Architecture

```text
Control-Panel/backend/
├── app/
│   ├── main.py            # Main FastAPI application entrypoint & server config
│   ├── serial_handler.py   # Asynchronous serial connection & concurrency lock
│   ├── state.py           # Pydantic data models & state structures
│   └── startup.py         # Calibration and startup utilities
├── routers/
│   ├── motor.py           # Motor control API routes (lock, port, cleaner, vibrator, vacuum)
│   ├── dustsensor.py      # Dust sensor API router
│   └── wb.py              # WebSocket live serial stream router
├── Makefile               # Build & run scripts
└── requirement.txt        # Python package dependencies
```

---

## 3. Key Components

### Serial Communication (`app/serial_handler.py`)
Provides an asynchronous `aioserial.AioSerial` instance linked to `/dev/ttyACM0` (115200 baud). Access is synchronized using an `asyncio.Lock()` (`serial_lock`) to prevent race conditions during serial commands.

### Data Models (`app/state.py`)
Defines Pydantic models used across routes:
- `Motor`: `name`, `speed`, `direction` (`RIGHT` / `LEFT`), `angle`
- `DustSensor`: `value`, `current`
- `WeightSensor`: `value`, `current`
- `StatMachine`: Tracks overall machine state (`IDLE`, `CALIBRATION`, `CLEANING`, `IMAGING`, `SUCCESS`, `FAILED`)

---

## 4. API Endpoints

### Machine Power Controls (`app/main.py`)
| Endpoint | Method | Description | Serial Command Sent |
| :--- | :--- | :--- | :--- |
| `/on` | `GET` | Turn machine ON | `1\n` |
| `/off` | `GET` | Turn machine OFF | `0\n` |

### Motor Control Endpoints (`routers/motor.py`)
Accepts JSON payload adhering to the `Motor` schema and sends corresponding JSON formatted strings over serial.

| Endpoint | Method | Motor | Payload Fields |
| :--- | :--- | :--- | :--- |
| `/port` | `POST` | Port | `speed`, `direction`, `angle` |
| `/vibrator` | `POST` | Vibrator | `speed`, `direction` |
| `/cleaner` | `POST` | Cleaner | `speed`, `direction` |
| `/lock` | `POST` | Lock | `speed`, `direction`, `angle` |
| `/vacum` | `POST` | Vacuum | `speed`, `direction` |

### Telemetry & Sensors
| Endpoint | Protocol | Description |
| :--- | :--- | :--- |
| `/dust` | `POST` | Handles dust sensor reading updates. |
| `/wb` | `WebSocket` | Streams raw incoming serial data from ESP32 in real time. |

---

## 5. How to Run

### Install Dependencies
```bash
make build
# or
pip install -r requirement.txt
```

### Run Server
```bash
make run
# or
python3 -m app.main
```
The server will start on `http://0.0.0.0:8000` with auto-reload enabled.
