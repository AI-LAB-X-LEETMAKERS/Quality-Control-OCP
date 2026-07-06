import { turnOn, turnOff, sendMotorCommand } from "./api.js";
import { API_BASE_URL } from "./config.js";

const backendStatus = document.getElementById("backend-status");
const apiBase = document.getElementById("api-base");
const log = document.getElementById("log");
const clearLog = document.getElementById("clear-log");
const motorForm = document.getElementById("motor-form");
const motorActions = document.getElementById("motor-actions");

apiBase.textContent = API_BASE_URL;

function writeLog(title, value) {
  const stamp = new Date().toLocaleTimeString();
  const body = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  log.textContent = `[${stamp}] ${title}\n${body}\n\n${log.textContent === "Waiting for a command..." ? "" : log.textContent}`.trim();
}

function getMotorData() {
  const formData = new FormData(motorForm);
  return {
    name: String(formData.get("name") ?? ""),
    speed: Number(formData.get("speed") ?? 0),
    direction: formData.get("direction") || "RIGHT",
    angle: Number(formData.get("angle") ?? 0),
    current: Number(formData.get("current") ?? 0),
  };
}

async function handlePower(action) {
  backendStatus.textContent = "Sending...";
  try {
    const result = action === "on" ? await turnOn() : await turnOff();
    backendStatus.textContent = "Ready";
    writeLog(action.toUpperCase(), result);
  } catch (error) {
    backendStatus.textContent = "Error";
    writeLog("ERROR", error.message);
  }
}

async function handleMotorAction(action) {
  backendStatus.textContent = "Sending...";
  try {
    const result = await sendMotorCommand(action, getMotorData());
    backendStatus.textContent = "Ready";
    writeLog(action.toUpperCase(), result);
  } catch (error) {
    backendStatus.textContent = "Error";
    writeLog("ERROR", error.message);
  }
}

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => handlePower(button.dataset.action));
});

motorActions.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-motor]");
  if (!button) {
    return;
  }

  handleMotorAction(button.dataset.motor);
});

clearLog.addEventListener("click", () => {
  log.textContent = "Waiting for a command...";
});
