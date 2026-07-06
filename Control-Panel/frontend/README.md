# Frontend

This folder contains a framework-free control panel for the FastAPI backend.

## Structure

- `index.html` - main entry point
- `css/styles.css` - visual styling
- `js/config.js` - backend URL and route map
- `js/api.js` - fetch wrapper for API calls
- `js/app.js` - DOM wiring and event handlers

## Run

Serve this folder with any static file server, then open `index.html` in the browser.

Example using Python:

```bash
python -m http.server 5500
```

If the frontend is hosted on a different origin from the backend, enable CORS in FastAPI.
