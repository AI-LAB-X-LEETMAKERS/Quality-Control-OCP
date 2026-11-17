# Quality Control OCP - Backend Documentation

Overview of the FastAPI backend application for the Quality Control OCP machine interface, designed to run on a Raspberry Pi alongside the frontend daemon.

---

## 1. Overview

The backend is built with **FastAPI** and orchestrates asynchronous communication between:
- **Web UI & Clients** (via REST and WebSockets, running as a separate frontend daemon on the Raspberry Pi)
- **ESP32 Microcontroller** over USB Serial (e.g., `/dev/ttyACM0` or auto-detected port at `115200` baud; supports `MOCK_ESP32=1` before firmware is ready)
- **Sensirion SPS30 Dust Sensor** over UART/SHDLC (`/dev/serial0` at `115200` baud)

---

## 2. Project Architecture

```text
Control-Panel/backend/
├── app/
│   ├── main.py             # FastAPI entrypoint, lifespan events & router registration
│   ├── serial_handler.py   # Serial connections (ESP32 and SPS30) & concurrency locks
│   ├── sps30_service.py    # Sensirion SPS30 UART driver & shared measurement broadcaster
│   ├── esp32_protocol.py   # (Planned) ESP32 command defaults, telemetry parser & mock mode
│   ├── workflow_service.py # (Planned) Automated machine workflow state machine
│   ├── models.py           # Pydantic data models & workflow state structures
│   └── startup.py          # Calibration and workflow sequence notes
├── routers/
│   ├── dustsensor.py       # Dust sensor API router (/dust snapshot with auto-shutdown)
│   ├── motors.py           # Motor control API routes (/port, /cleaner, /vibrator, /vaccum)
│   ├── esp32.py            # (Planned) ESP32 presence & port detection (/esp32/status)
│   ├── workflow.py         # (Planned) Workflow control routes (/workflow/calibrate, /start, /stop, /status)
│   └── ws.py               # WebSocket routers (/ws/dust live dust stream, /ws/machine telemetry)
├── Makefile                # Build & run scripts (make build / make run)
└── requirement.txt         # Python package dependencies
```

---

## 3. Key Components

### Serial Handler (`app/serial_handler.py`)
Manages asynchronous serial locks using `asyncio.Lock()` to prevent concurrent read/write collisions:
- `serial_lock_esp`: Serial port lock for ESP32 (`PORT_ESP = "/dev/ttyACM0"` default, `115200` baud, non-fatal startup if unplugged and dynamically updatable when `GET /esp32/status` detects the active port).
- `serial_lock_dust`: Serial port lock for Sensirion SPS30 on `PORT_DUST = "/dev/serial0"` at `115200` baud.

### Sensirion SPS30 Dust Sensor Service (`app/sps30_service.py`)
Communicates directly with the Sensirion SPS30 particulate matter sensor over UART via SHDLC protocol on `/dev/serial0` at `115200` baud (`sensirion-uart-sps30`).
- **Format:** Measures values using `OutputFormat.OUTPUT_FORMAT_UINT16` (integer readings).
- **Concurrency & Threading:** Synchronous sensor driver operations run in non-blocking threads via `asyncio.to_thread` protected by `serial_lock_dust.lock`.
- **Shared Broadcaster *(Planned)*:** A single 1 Hz reader feeds all `/ws/dust` subscribers and the workflow loop without lock contention.
- **Auto-Shutdown Lifecycle:** Stops measurement (`DustDevice.stop()`) to preserve fan/laser lifespan on:
  - Completion of a single measurement query (`GET /dust`).
  - All `/ws/dust` clients disconnecting and no active workflow needing dust readings.
  - Immediately when `PM10 <= 12 µg/m³` during the automated cleaning workflow.
  - FastAPI server shutdown via lifespan context manager in `app/main.py`.

### Data Models (`app/models.py`)
- `Stats` (Enum): `IDLE`, `CALIBRATION`, `READY` *(planned)*, `CLEANING`, `IMAGING`, `SUCCESS`, `FAILED`.
- `Port`: `angle` (`int`)
- `cleaning`: `speed` (`int`), `forward` (`bool`), `enabled` (`bool`)
- `vibrator`: `speed` (`int`), `forward` (`bool`)
- `vaccum`: `throttle` (`int`), `armed` (`bool`)
- `WeightSensor`: `value` (`int | None = 0`), `current` (`float | None = 0.0`)
- `DustSensor`:
  - `pm1_0`: `int` (PM1.0 concentration in µg/m³)
  - `pm2_5`: `int` (PM2.5 concentration in µg/m³)
  - `pm4_0`: `int` (PM4.0 concentration in µg/m³)
  - `pm10_0`: `int` (PM10.0 concentration in µg/m³)
  - `size`: `int` (typical particle size)
- `RPM`: `value` (`int | None = 0`)
- `WorkflowStatus` *(planned)*: Live state snapshot (`state`, `calibrated`, `rpm`, `cleaning_current`, `weight`, `dust_pm10`, `message`, `elapsed_ms`, `esp32_connected`, `esp32_port`).

---

## 4. Automated Machine Workflow *(Planned)*

```text
IDLE ──(Calibrate)──▶ CALIBRATION ──(ESP32 OK + 3s Dust Stabilized)──▶ READY
                                                                         │
                                                                  (Start Machine)
                                                                         ▼
SUCCESS ◀──(Weight > 0 Stable 3s)── IMAGING ◀──(PM10 <= 12 µg/m³)── CLEANING
```

1. **Calibration (`IDLE` -> `CALIBRATION` -> `READY`):**
   - Frontend disables **Start Machine** until calibration succeeds.
   - User clicks **Calibrate** (`POST /workflow/calibrate`); backend sends the calibration command to the ESP32 for the cleaning motor and runs the SPS30 dust sensor for **3 seconds** to stabilize on a baseline value.
   - Once both finish, the workflow enters `READY` and enables **Start Machine**.
2. **Active Cleaning & Live Dashboard (`READY` -> `CLEANING`):**
   - User clicks **Start Machine** (`POST /workflow/start`).
   - Backend starts cleaning + vacuum (and closes the port) using configurable default presets in `app/esp32_protocol.py`.
   - Live Dashboard receives real-time updates: **Status**, **Cleaning Current**, **RPM**, **Dust Level (`PM10`)** (via `/ws/dust`), and **Time Elapsed**.
3. **Dust Threshold Transition (`CLEANING` -> `IMAGING`):**
   - As soon as `PM10 <= 12 µg/m³`, backend immediately:
     1. Stops the **cleaning motor** and **vacuum**.
     2. **Opens the port**.
     3. **Shuts down the dust sensor** (`DustDevice.stop()`).
     4. Starts the **vibrator motor**.
     5. Sets status message to **`"imaging in process"`** on the Dashboard.
4. **Weight Stabilization & Completion (`IMAGING` -> `SUCCESS`):**
   - Backend continuously reads the **weight sensor** from the ESP32 serial stream.
   - Once weight is **`> 0`** and stays stable within a small tolerance over a **3-second** interval, backend stops the **vibrator motor** and transitions to `SUCCESS`.

---

## 5. API Endpoints

### System & Hardware Status Endpoints
| Endpoint | Method | Description | Response |
| :--- | :--- | :--- | :--- |
| `/status` | `GET` | Server health check | `{"status": "alive"}` |
| `/esp32/status` *(planned)* | `GET` | Runs `arduino-cli` / `lsusb` to check ESP32 presence and extract its active port | `{"connected": bool, "port": str \| null, ...}` |

### Workflow Endpoints *(Planned)*
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/workflow/status` | `GET` | Returns current `WorkflowStatus` snapshot |
| `/workflow/calibrate` | `POST` | Starts ESP32 cleaning-motor calibration + 3s SPS30 stabilization |
| `/workflow/start` | `POST` | Starts cleaning workflow (requires `READY` / calibrated state) |
| `/workflow/stop` | `POST` | Stops motors and dust sensor, resets workflow to `IDLE` |

### Dust Sensor Endpoints (`routers/dustsensor.py`)
| Endpoint | Method | Description | Actions & Response |
| :--- | :--- | :--- | :--- |
| `/dust` | `GET` | Single dust measurement snapshot | Triggers measurement, turns off sensor in `finally`, returns `DustSensor` JSON |

#### `/dust` Response Example
```json
{
  "pm1_0": 12,
  "pm2_5": 24,
  "pm4_0": 29,
  "pm10_0": 31,
  "size": 0
}
```

### Real-Time WebSocket Streams (`routers/ws.py`)
| Endpoint | Protocol | Description | Payload Format |
| :--- | :--- | :--- | :--- |
| `/ws/dust` | `WebSocket` | Real-time SPS30 particulate matter stream (1 Hz) | `DustSensor` JSON |
| `/ws/machine` *(planned)* | `WebSocket` | Live workflow state, RPM, cleaning current, weight & messages | `WorkflowStatus` JSON |

### Motor Control Endpoints (`routers/motors.py`)
| Endpoint | Method | Motor | Request Body Fields | Serial JSON Payload |
| :--- | :--- | :--- | :--- | :--- |
| `/port` | `POST` | Port | `angle` | `{"port": <angle>}` |
| `/cleaner` | `POST` | Cleaner | `speed`, `forward`, `enabled` | `{"cleaning": {"speed", "forward", "enabled"}}` |
| `/vibrator` | `POST` | Vibrator | `speed`, `forward` | `{"vibrator": {"speed", "forward"}}` |
| `/vaccum` | `POST` | Vacuum / Fan | `throttle`, `armed` | `{"fan": {"throttle", "armed"}}` |

---

## 6. Testing & Verification

### Running the Backend
```bash
cd Control-Panel/backend
make build   # installs dependencies from requirement.txt
make run     # starts python3 -m app.main on port 8000 (0.0.0.0:8000)

# Optional mock mode before ESP32 firmware is ready:
MOCK_ESP32=1 make run
```

### REST Verification
```bash
curl http://localhost:8000/status
curl http://localhost:8000/dust
curl http://localhost:8000/esp32/status
```

### WebSocket Verification
1. Ensure the Sensirion SPS30 is connected to `/dev/serial0`.
2. Connect to `ws://localhost:8000/ws/dust` (and `ws://localhost:8000/ws/machine` once implemented) via a WebSocket client or `wscat`:
   ```bash
   wscat -c ws://localhost:8000/ws/dust
   ```
3. Observe live JSON packets streaming at 1 Hz.
4. Close the connection: the backend stops `DustDevice` once no active subscribers or workflows remain.
