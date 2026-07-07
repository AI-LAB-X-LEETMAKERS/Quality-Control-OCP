import { turnOn, turnOff, sendMotorCommand } from "./api.js";
import { API_BASE_URL } from "./config.js";

const backendStatus = document.getElementById("backend-status") || {};
const apiBase = document.getElementById("api-base");
const dashboardStatus = document.getElementById("dashboard-status");
const dashboardRpm = document.getElementById("dashboard-rpm");
const dashboardDust = document.getElementById("dashboard-dust");
const dashboardElapsed = document.getElementById("dashboard-elapsed");
const startMachineButton = document.getElementById("start-machine");
const log = document.getElementById("log");
const clearLog = document.getElementById("clear-log");
const powerButtons = document.querySelectorAll("[data-action]");
const sectionTabs = document.querySelectorAll("[data-section-target]");
const sections = document.querySelectorAll(".section-view");

let totalCommands = 0;
let currentPowerState = "Off";
let machineRunning = false;
let machineStartTime = null;
let elapsedTimer = null;

const dashboardState = {
  rpm: "--",
  dust: "--",
};

if (apiBase) {
  apiBase.textContent = API_BASE_URL;
}

function formatElapsed(ms) {
  const totalSeconds = Math.floor(ms / 1000);
  const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
  const minutes = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

function updateElapsed() {
  if (!machineRunning || machineStartTime === null) {
    dashboardElapsed.textContent = "00:00:00";
    return;
  }

  dashboardElapsed.textContent = formatElapsed(Date.now() - machineStartTime);
}

function startElapsedTimer() {
  if (elapsedTimer) {
    clearInterval(elapsedTimer);
  }

  machineRunning = true;
  machineStartTime = Date.now();
  dashboardStatus.textContent = "RUNNING";
  updateElapsed();
  elapsedTimer = setInterval(updateElapsed, 1000);
}

function stopElapsedTimer() {
  machineRunning = false;
  machineStartTime = null;
  if (elapsedTimer) {
    clearInterval(elapsedTimer);
    elapsedTimer = null;
  }
  updateElapsed();
}

function syncDashboard() {
  dashboardStatus.textContent = machineRunning ? "RUNNING" : currentPowerState === "On" ? "READY" : "IDLE";
  dashboardRpm.textContent = String(dashboardState.rpm);
  dashboardDust.textContent = String(dashboardState.dust);
  updateElapsed();
}

function setPowerButtonState(action) {
  powerButtons.forEach((button) => {
    const isActive = button.dataset.action === action;
    button.classList.toggle("power-button-active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });
}

function writeLog(title, value) {
  const stamp = new Date().toLocaleTimeString();
  const body = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  log.textContent = `[${stamp}] ${title}\n${body}\n\n${log.textContent === "Waiting for a command..." ? "" : log.textContent}`.trim();
}

function getMotorData(formElement) {
  return {
    name: String(formElement.querySelector('[name="name"]')?.value ?? ""),
    speed: Number(formElement.querySelector('[name="speed"]')?.value ?? 0),
    direction: formElement.querySelector('[name="direction"]')?.value || "RIGHT",
    angle: Number(formElement.querySelector('[name="angle"]')?.value ?? 0),
  };
}

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

async function handlePower(action) {
  backendStatus.textContent = "Sending...";
  try {
    const result = action === "on" ? await turnOn() : await turnOff();
    backendStatus.textContent = "Ready";
    currentPowerState = action === "on" ? "On" : "Off";
    totalCommands += 1;
    setPowerButtonState(action);
    if (action === "on") {
      startElapsedTimer();
    } else {
      stopElapsedTimer();
      dashboardStatus.textContent = "IDLE";
    }
    syncDashboard();
    writeLog(action.toUpperCase(), result);
  } catch (error) {
    backendStatus.textContent = "Error";
    writeLog("ERROR", error.message);
  }
}

async function handleMotorAction(action) {
  backendStatus.textContent = "Sending...";
  const btn = document.querySelector(`.component-action[data-motor="${action}"]`);
  const originalText = btn.textContent;
  btn.textContent = "Applying...";
  btn.disabled = true;

  try {
    const result = await sendMotorCommand(action, getMotorData(getMotorActionForm(action)));
    backendStatus.textContent = "Ready";
    totalCommands += 1;
    syncDashboard();
    writeLog(action.toUpperCase(), result);
    
    btn.textContent = "Applied!";
    btn.style.backgroundColor = "#2e8b57"; // Darker green for success
  } catch (error) {
    backendStatus.textContent = "Error";
    writeLog("ERROR", error.message);
    
    btn.textContent = "Failed!";
    btn.style.backgroundColor = "#d9534f"; // Red for error
  } finally {
    setTimeout(() => {
      btn.textContent = originalText;
      btn.disabled = false;
      btn.style.backgroundColor = "";
    }, 2000);
  }
}

function getMotorActionForm(action) {
  const card = document.querySelector(`.component-form[data-motor="${action}"]`);
  if (!card) {
    throw new Error(`Missing form for motor action: ${action}`);
  }

  return card;
}

sectionTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    setSection(tab.dataset.sectionTarget);
  });
});

powerButtons.forEach((button) => {
  button.addEventListener("click", () => handlePower(button.dataset.action));
});

document.querySelectorAll(".component-action[data-motor]").forEach((button) => {
  button.addEventListener("click", () => {
    handleMotorAction(button.dataset.motor);
  });
});

clearLog.addEventListener("click", () => {
  log.textContent = "Waiting for a command...";
});

startMachineButton.addEventListener("click", () => {
  handlePower("on");
});

document.querySelectorAll(".component-form").forEach((form) => {
  form.addEventListener("input", () => {
    syncDashboard();
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    syncDashboard();
  });
});

syncDashboard();
setPowerButtonState("off");
sections.forEach((section) => {
  section.hidden = section.id !== "dashboard-section";
});
setSection("dashboard-section");
