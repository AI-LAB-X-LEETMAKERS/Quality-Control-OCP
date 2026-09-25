const hostname = typeof window !== "undefined" && window.location.hostname ? window.location.hostname : "localhost";

export const API_BASE_URL = `http://${hostname}:8000`;

export const ENDPOINTS = {
  on: "/on",
  off: "/off",
  motor: {
    lock: "/lock",
    port: "/port",
    cleaner: "/cleaner",
    vibrator: "/vibrator",
    vacum: "/vacum",
  },
};
