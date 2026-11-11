import { API_BASE_URL, WS_BASE_URL, ENDPOINTS } from "./config.js?v=2";

async function request(path, options = {}) {
  const hasBody = options.body !== undefined && options.body !== null;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      ...(hasBody ? { "Content-Type": "application/json" } : {}),
      ...(options.headers ?? {}),
    },
    ...options,
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message = payload?.detail ?? `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return payload;
}

export function turnOn() {
  return request(ENDPOINTS.on, { method: "GET" });
}

export function turnOff() {
  return request(ENDPOINTS.off, { method: "GET" });
}

export function sendMotorCommand(action, motor) {
  const path = ENDPOINTS.motor[action];
  if (!path) {
    throw new Error(`Unknown motor action: ${action}`);
  }

  return request(path, {
    method: "POST",
    body: JSON.stringify(motor),
  });
}

export function runMachineTest() {
  return request(ENDPOINTS.on, { method: "GET" });
}

export function fetchDustReading() {
  return request(ENDPOINTS.dust, { method: "GET" });
}

export function createDustWebSocket() {
  return new WebSocket(`${WS_BASE_URL}${ENDPOINTS.wsDust}`);
}
