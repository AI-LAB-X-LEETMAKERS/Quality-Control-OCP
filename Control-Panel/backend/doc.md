# Quality Control OCP - Backend Documentation

Overview of the FastAPI backend application for the Quality Control OCP machine interface.

---

## 1. Overview

The backend is built with **FastAPI** and orchestrates asynchronous communication between:
- **Web UI & Clients** (via REST and WebSockets)
- **ESP32 Microcontroller** over USB Serial (`/dev/ttyACM0` at `115200` baud)
- **Sensirion SPS30 Dust Sensor** over UART/SHDLC (`/dev/serial0` at `115200` baud)

---

## 2. Project Architecture

```text
Control-Panel/backend/
├── app/
│   ├── main.py            # FastAPI entrypoint, lifespan events & server config
│   ├── serial_handler.py   # ESP32 serial connection & concurrency lock
│   ├── sps30_service.py    # Sensirion SPS30 UART driver & async worker
│   ├── state.py           # Pydantic data models & state structures
│   └── startup.py         # Calibration and startup utilities
├── routers/
│   ├── motor.py           # Motor control API routes (lock, port, cleaner, vibrator, vacuum)
│   ├── dustsensor.py      # Dust sensor API router (start, stop, latest, status)
│   └── ws.py              # WebSocket routers (/ws serial log, /ws/dust live telemetry)
├── Makefile               # Build & run scripts
└── requirement.txt        # Python package dependencies
```

---

## 3. Key Components

### ESP32 Serial (`app/serial_handler.py`)
Provides an asynchronous `aioserial.AioSerial` connection on `/dev/ttyACM0` at `115200` baud. Synchronized with `asyncio.Lock()` (`serial_lock`).
*Note: If the ESP32 is not connected, the application terminates immediately with an error.*

### Sensirion SPS30 Dust Sensor (`app/sps30_service.py`)
Communicates directly with the Sensirion SPS30 particulate matter sensor over UART via SHDLC protocol on `/dev/serial0` at `115200` baud (`sensirion-uart-sps30`).
- Runs synchronous sensor queries in a non-blocking background thread.
- Automatically begins acquiring data when the machine is turned on (`/on`).
- Stops laser/fan when machine is turned off (`/off`).
- Broadcasts real-time JSON frames at 1 Hz to all active `/ws/dust` WebSocket connections.
*Note: If the physical SPS30 is not connected, the application terminates immediately with an error.*

### Data Models (`app/state.py`)
- `Motor`: `name`, `speed`, `direction` (`RIGHT` / `LEFT`), `angle`
- `DustSensor`: `pm1_0`, `pm2_5`, `pm4_0`, `pm10_0`, `nc0_5`, `nc1_0`, `nc2_5`, `nc4_0`, `nc10_0`, `typical_particle_size`, `status`
- `WeightSensor`: `value`, `current`
- `StatMachine`: Tracks system state and sensor telemetry.

---

## 4. API Endpoints

### Machine Power Controls (`app/main.py`)
| Endpoint | Method | Description | Actions Performed |
| :--- | :--- | :--- | :--- |
| `/on` | `GET` | Turn machine ON | Sends `1\n` to ESP32 & starts SPS30 sensor acquisition |
| `/off` | `GET` | Turn machine OFF | Sends `0\n` to ESP32 & stops SPS30 sensor acquisition |

### Motor Control Endpoints (`routers/motor.py`)
| Endpoint | Method | Motor | Payload Fields |
| :--- | :--- | :--- | :--- |
| `/port` | `POST` | Port | `speed`, `direction`, `angle` |
| `/vibrator` | `POST` | Vibrator | `speed`, `direction` |
| `/cleaner` | `POST` | Cleaner | `speed`, `direction` |
| `/lock` | `POST` | Lock | `speed`, `direction`, `angle` |
| `/vacum` | `POST` | Vacuum | `speed`, `direction` |

### Dust Sensor Controls (`routers/dustsensor.py`)
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/dust/start` | `POST` | Starts SPS30 measurement (fan and laser on) |
| `/dust/stop` | `POST` | Stops SPS30 measurement (fan and laser off) |
| `/dust/latest` | `GET` | Returns most recent telemetry snapshot |
| `/dust/status` | `GET` | Returns operational status of the sensor |

### Real-Time WebSocket Streams (`routers/ws.py`)
| Endpoint | Protocol | Description | Payload Format |
| :--- | :--- | :--- | :--- |
| `/ws/dust` | `WebSocket` | Real-time SPS30 particulate matter stream (1 Hz) | JSON (see below) |
| `/ws` | `WebSocket` | Raw serial incoming text stream from ESP32 | Plain text |

#### `/ws/dust` Message Format
```json
{
  "pm1_0": 12.35,
  "pm2_5": 24.81,
  "pm4_0": 29.40,
  "pm10_0": 31.62,
  "nc0_5": 145.20,
  "nc1_0": 168.04,
  "nc2_5": 172.41,
  "nc4_0": 173.12,
  "nc10_0": 173.55,
  "typical_particle_size": 0.82,
  "status": "MEASURING",
  "timestamp": 1731157200.15
}
```

---

## 5. Testing with Postman

### Step-by-Step WebSocket Testing:
1. Ensure both the **ESP32** (`/dev/ttyACM0`) and **SPS30** (`/dev/ttyUSB0`) are plugged into the Raspberry Pi.
2. Start the backend:
   ```bash
   cd backend
   python3 -m app.main
   ```
3. Open **Postman**:
   - Click **New** -> **WebSocket Request**.
   - Set URL: `ws://localhost:8000/ws/dust`.
   - Click **Connect**.
4. In another tab or via browser, trigger `GET http://localhost:8000/on` or `POST http://localhost:8000/dust/start`.
5. Observe continuous live JSON packets streaming in Postman every 1 second.
6. Trigger `GET http://localhost:8000/off` or `POST http://localhost:8000/dust/stop` to stop measurements.
