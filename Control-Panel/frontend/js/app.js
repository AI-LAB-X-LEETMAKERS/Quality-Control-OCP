import { turnOn, turnOff, sendMotorCommand, runMachineTest } from "./api.js";

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

let machineRunning = false;
let machineStartTime = null;
let elapsedTimer = null;
let dustPollTimer = null;

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

// Event Listeners
if (startMachineButton) {
  startMachineButton.addEventListener("click", toggleMachineState);
}

if (btnMachineTest) {
  btnMachineTest.addEventListener("click", handleMachineTest);
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
