// API Configuration
// Automatically detects if running locally or on PythonAnywhere
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : window.location.origin;

export { API_BASE_URL };
