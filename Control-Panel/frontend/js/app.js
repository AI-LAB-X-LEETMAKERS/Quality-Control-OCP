import { turnOn, turnOff, sendMotorCommand, runMachineTest, createDustWebSocket } from "./api.js";

// DOM References
const backendStatus = document.getElementById("backend-status");
const dashboardSummary = document.getElementById("dashboard-summary");
const dashboardStatus = document.getElementById("dashboard-status");
const dashboardRpm = document.getElementById("dashboard-rpm");
const dashboardDust = document.getElementById("dashboard-dust");
const dustMeterFill = document.getElementById("dust-meter-fill");
const dashboardElapsed = document.getElementById("dashboard-elapsed");
const startMachineButton = document.getElementById("start-machine");
const btnMachineTest = document.getElementById("btn-machine-test");
const machineTestOutput = document.getElementById("machine-test-output");
const log = document.getElementById("log");
const clearLog = document.getElementById("clear-log");
const sectionTabs = document.querySelectorAll("[data-section-target]");
const sections = document.querySelectorAll(".section-view");

// Dust Sensor Control Panel References
const dustSensorBadge = document.getElementById("dust-sensor-badge");
const dustGaugeFill = document.getElementById("dust-gauge-fill");
const dustGaugeNeedle = document.getElementById("dust-gauge-needle");
const dustPm10Value = document.getElementById("dust-pm10-value");
const dustPm1_0 = document.getElementById("dust-pm1-0");
const dustPm2_5 = document.getElementById("dust-pm2-5");
const dustPm4_0 = document.getElementById("dust-pm4-0");
const dustPm10_0 = document.getElementById("dust-pm10-0");
const dustSize = document.getElementById("dust-size");
const btnDustSensor = document.getElementById("btn-dust-sensor");

const DUST_GAUGE_MIN = 1;
const DUST_GAUGE_MAX = 1000;
const DUST_GAUGE_ARC_LENGTH = 251.33;

let machineRunning = false;
let machineStartTime = null;
let elapsedTimer = null;
let dustPollTimer = null;

let dustSocket = null;
let dustSensorRunning = false;
let userStoppedDustSensor = false;

const state = {
  rpm: 1200,
  dust: 45, // default reading in µg/m³
};

// Status Badge Helper
function setBackendStatus(text, statusClass = "ready") {
  if (!backendStatus) return;
  backendStatus.textContent = text;
  backendStatus.className = `status-badge ${statusClass}`;
}

// Format Elapsed Time
function formatElapsed(ms) {
  const totalSeconds = Math.floor(ms / 1000);
  const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
  const minutes = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

function updateElapsed() {
  if (!machineRunning || machineStartTime === null) {
    if (dashboardElapsed) dashboardElapsed.textContent = "00:00:00";
    return;
  }
  if (dashboardElapsed) {
    dashboardElapsed.textContent = formatElapsed(Date.now() - machineStartTime);
  }
}

// Dust Level Meter Update (Range 0 - 500 µg/m³)
function updateDustMeter(value) {
  state.dust = value;
  if (dashboardDust) {
    dashboardDust.textContent = String(value);
  }
  if (dustMeterFill) {
    const maxVal = 500;
    const percentage = Math.min(100, Math.max(0, (value / maxVal) * 100));
    dustMeterFill.style.width = `${percentage}%`;
  }
}

function startTimers() {
  if (elapsedTimer) clearInterval(elapsedTimer);
  if (dustPollTimer) clearInterval(dustPollTimer);

  machineStartTime = Date.now();
  updateElapsed();
  elapsedTimer = setInterval(updateElapsed, 1000);

  // Poll / update simulated telemetry reading
  dustPollTimer = setInterval(() => {
    if (machineRunning) {
      // Fluctuate reading realistically around 35-65 µg/m³
      const variation = Math.floor(Math.random() * 11) - 5;
      const newDust = Math.max(10, Math.min(450, state.dust + variation));
      updateDustMeter(newDust);
    }
  }, 3000);
}

function stopTimers() {
  if (elapsedTimer) {
    clearInterval(elapsedTimer);
    elapsedTimer = null;
  }
  if (dustPollTimer) {
    clearInterval(dustPollTimer);
    dustPollTimer = null;
  }
  machineStartTime = null;
  updateElapsed();
}

function syncDashboard() {
  if (dashboardStatus) {
    dashboardStatus.textContent = machineRunning ? "RUNNING" : "IDLE";
  }
  if (dashboardRpm) {
    dashboardRpm.textContent = machineRunning ? String(state.rpm) : "0";
  }
  updateDustMeter(machineRunning ? state.dust : 0);
  updateElapsed();
}

// System Logger
function writeLog(title, value) {
  if (!log) return;
  const stamp = new Date().toLocaleTimeString();
  const body = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  const entry = `[${stamp}] ${title}\n${body}`;

  if (log.textContent === "Waiting for a command...") {
    log.textContent = entry;
  } else {
    log.textContent = `${entry}\n\n${log.textContent}`;
  }
}

// Get Form Data for Motor Action
function getMotorData(formElement) {
  return {
    name: String(formElement.querySelector('[name="name"]')?.value ?? ""),
    speed: Number(formElement.querySelector('[name="speed"]')?.value ?? 0),
    direction: formElement.querySelector('[name="direction"]')?.value || "RIGHT",
    angle: Number(formElement.querySelector('[name="angle"]')?.value ?? 0),
  };
}

function getMotorActionForm(action) {
  const card = document.querySelector(`.component-form[data-motor="${action}"]`);
  if (!card) {
    throw new Error(`Missing form for motor action: ${action}`);
  }
  return card;
}

// Tab Switching Handler
function setSection(sectionId) {
  sections.forEach((section) => {
    const isActive = section.id === sectionId;
    section.hidden = !isActive;
    section.classList.toggle("active-view", isActive);
  });

  sectionTabs.forEach((tab) => {
    const isActive = tab.dataset.sectionTarget === sectionId;
    tab.classList.toggle("active", isActive);
    tab.setAttribute("aria-pressed", String(isActive));
  });
}

// Start Machine Toggle Handler
async function toggleMachineState() {
  setBackendStatus("Sending...", "sending");

  if (!machineRunning) {
    // Start Machine
    try {
      const result = await turnOn();
      machineRunning = true;
      setBackendStatus("Ready", "ready");

      // Show Dashboard Summary
      if (dashboardSummary) {
        dashboardSummary.classList.remove("hidden");
      }

      // Update Start Hero Button
      if (startMachineButton) {
        startMachineButton.classList.add("running");
        startMachineButton.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="6" y="6" width="12" height="12" rx="2"></rect>
          </svg>
          <span>Stop Machine</span>
        `;
      }

      startTimers();
      syncDashboard();
      writeLog("START MACHINE (ON)", result);
    } catch (error) {
      setBackendStatus("Error", "error");
      writeLog("START MACHINE ERROR", error.message);
    }
  } else {
    // Stop Machine
    try {
      const result = await turnOff();
      machineRunning = false;
      setBackendStatus("Ready", "ready");

      // Hide Dashboard Summary
      if (dashboardSummary) {
        dashboardSummary.classList.add("hidden");
      }

      // Reset Start Hero Button
      if (startMachineButton) {
        startMachineButton.classList.remove("running");
        startMachineButton.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          <span>Start Machine</span>
        `;
      }

      stopTimers();
      syncDashboard();
      writeLog("STOP MACHINE (OFF)", result);
    } catch (error) {
      setBackendStatus("Error", "error");
      writeLog("STOP MACHINE ERROR", error.message);
    }
  }
}

// Machine Test Response Handler
async function handleMachineTest() {
  if (!btnMachineTest || !machineTestOutput) return;

  const originalText = btnMachineTest.textContent;
  btnMachineTest.textContent = "Testing...";
  btnMachineTest.disabled = true;
  setBackendStatus("Testing...", "sending");

  try {
    const response = await runMachineTest();
    setBackendStatus("Ready", "ready");
    machineTestOutput.textContent = JSON.stringify(
      {
        timestamp: new Date().toISOString(),
        testStatus: "SUCCESS",
        responsePayload: response,
      },
      null,
      2
    );
    writeLog("MACHINE TEST RESPONSE", response);
  } catch (error) {
    setBackendStatus("Error", "error");
    machineTestOutput.textContent = JSON.stringify(
      {
        timestamp: new Date().toISOString(),
        testStatus: "FAILED",
        error: error.message,
      },
      null,
      2
    );
    writeLog("MACHINE TEST ERROR", error.message);
  } finally {
    btnMachineTest.textContent = originalText;
    btnMachineTest.disabled = false;
  }
}

// Motor Action Command Handler
async function handleMotorAction(action) {
  setBackendStatus("Sending...", "sending");
  const btn = document.querySelector(`.component-action[data-motor="${action}"]`);
  if (!btn) return;

  const originalText = btn.textContent;
  btn.textContent = "Applying...";
  btn.disabled = true;

  try {
    const motorData = getMotorData(getMotorActionForm(action));
    const result = await sendMotorCommand(action, motorData);
    setBackendStatus("Ready", "ready");
    writeLog(`MOTOR ACTION [${action.toUpperCase()}]`, result);

    btn.textContent = "Applied!";
    btn.style.backgroundColor = "#059669";
  } catch (error) {
    setBackendStatus("Error", "error");
    writeLog(`MOTOR ACTION ERROR [${action.toUpperCase()}]`, error.message);

    btn.textContent = "Failed!";
    btn.style.backgroundColor = "#ef4444";
  } finally {
    setTimeout(() => {
      btn.textContent = originalText;
      btn.disabled = false;
      btn.style.backgroundColor = "";
    }, 2000);
  }
}

// Dust Sensor Gauge & Readings Helpers
function setDustSensorBadge(text, statusClass = "") {
  if (!dustSensorBadge) return;
  dustSensorBadge.textContent = text;
  dustSensorBadge.className = statusClass ? `status-badge ${statusClass}` : "status-badge";
}

function updateDustGauge(pm10Value) {
  if (pm10Value === null || pm10Value === undefined) {
    if (dustPm10Value) dustPm10Value.textContent = "0";
    if (dustGaugeFill) dustGaugeFill.style.strokeDashoffset = String(DUST_GAUGE_ARC_LENGTH);
    if (dustGaugeNeedle) dustGaugeNeedle.style.transform = "rotate(-90deg)";
    return;
  }

  const numericVal = Number(pm10Value) || 0;
  if (dustPm10Value) {
    dustPm10Value.textContent = String(numericVal);
  }

  const clamped = Math.min(DUST_GAUGE_MAX, Math.max(DUST_GAUGE_MIN, numericVal));
  const ratio = numericVal <= 0 ? 0 : (clamped - DUST_GAUGE_MIN) / (DUST_GAUGE_MAX - DUST_GAUGE_MIN);
  const dashOffset = DUST_GAUGE_ARC_LENGTH * (1 - ratio);
  const needleAngle = -90 + ratio * 180;

  if (dustGaugeFill) {
    dustGaugeFill.style.strokeDashoffset = String(dashOffset);
  }
  if (dustGaugeNeedle) {
    dustGaugeNeedle.style.transform = `rotate(${needleAngle}deg)`;
  }
}

function updateDustReadings(data) {
  if (!data) {
    if (dustPm1_0) dustPm1_0.textContent = "--";
    if (dustPm2_5) dustPm2_5.textContent = "--";
    if (dustPm4_0) dustPm4_0.textContent = "--";
    if (dustPm10_0) dustPm10_0.textContent = "--";
    if (dustSize) dustSize.textContent = "--";
    updateDustGauge(null);
    return;
  }

  if (dustPm1_0) dustPm1_0.textContent = String(data.pm1_0 ?? "--");
  if (dustPm2_5) dustPm2_5.textContent = String(data.pm2_5 ?? "--");
  if (dustPm4_0) dustPm4_0.textContent = String(data.pm4_0 ?? "--");
  if (dustPm10_0) dustPm10_0.textContent = String(data.pm10_0 ?? "--");
  if (dustSize) dustSize.textContent = String(data.size ?? "--");

  const pm10 = Number(data.pm10_0 ?? 0);
  updateDustGauge(pm10);
  updateDustMeter(pm10);
}

function toggleDustSensor() {
  if (!btnDustSensor) return;

  if (!dustSensorRunning && !dustSocket) {
    userStoppedDustSensor = false;
    btnDustSensor.disabled = true;
    btnDustSensor.textContent = "Starting...";
    setDustSensorBadge("STARTING", "sending");

    try {
      const ws = createDustWebSocket();
      dustSocket = ws;

      ws.onopen = () => {
        dustSensorRunning = true;
        btnDustSensor.disabled = false;
        btnDustSensor.textContent = "Shutdown Sensor";
        btnDustSensor.classList.add("running");
        setDustSensorBadge("ACTIVE", "ready");
        writeLog("DUST SENSOR", "Connected to /ws/dust - sensor started.");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          updateDustReadings(data);
        } catch (err) {
          writeLog("DUST SENSOR PARSE ERROR", err.message);
        }
      };

      ws.onerror = () => {
        setDustSensorBadge("ERROR", "error");
        writeLog("DUST SENSOR ERROR", "WebSocket error on /ws/dust");
      };

      ws.onclose = (event) => {
        dustSocket = null;
        dustSensorRunning = false;
        btnDustSensor.disabled = false;
        btnDustSensor.textContent = "Start Sensor";
        btnDustSensor.classList.remove("running");

        if (userStoppedDustSensor) {
          setDustSensorBadge("OFF", "");
          updateDustReadings(null);
          writeLog("DUST SENSOR", "Sensor shutdown completed.");
        } else {
          setDustSensorBadge("ERROR", "error");
          writeLog(
            "DUST SENSOR DISCONNECTED",
            event.reason || `Connection closed (code ${event.code})`
          );
        }
      };
    } catch (error) {
      dustSocket = null;
      dustSensorRunning = false;
      btnDustSensor.disabled = false;
      btnDustSensor.textContent = "Start Sensor";
      btnDustSensor.classList.remove("running");
      setDustSensorBadge("ERROR", "error");
      writeLog("DUST SENSOR ERROR", error.message);
    }
  } else if (dustSocket) {
    userStoppedDustSensor = true;
    btnDustSensor.disabled = true;
    btnDustSensor.textContent = "Shutting down...";
    dustSocket.close();
  }
}

// Event Listeners
if (startMachineButton) {
  startMachineButton.addEventListener("click", toggleMachineState);
}

if (btnMachineTest) {
  btnMachineTest.addEventListener("click", handleMachineTest);
}

if (btnDustSensor) {
  btnDustSensor.addEventListener("click", toggleDustSensor);
}

sectionTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    setSection(tab.dataset.sectionTarget);
  });
});

document.querySelectorAll(".component-action[data-motor]").forEach((button) => {
  button.addEventListener("click", () => {
    handleMotorAction(button.dataset.motor);
  });
});

if (clearLog && log) {
  clearLog.addEventListener("click", () => {
    log.textContent = "Waiting for a command...";
  });
}

// Initial state setup
syncDashboard();
setBackendStatus("Ready", "ready");
setSection("dashboard-section");
