// ===============================
// Configuration Module
// ===============================

const CONFIG = {

    // Session Settings
    SESSION_TIMEOUT: 300000, // 5 minutes

    MIN_SESSION_TIME: 2000, // 2 sec

    // Mouse Settings
    DOUBLE_CLICK_THRESHOLD: 300,
    MAX_CLICK_INTERVAL: 800,

    // Keyboard Settings
    MAX_TYPING_SPEED: 120, // keys per min threshold
    MAX_BACKSPACE_RATIO: 0.4,

    // Scroll Settings
    SCROLL_SENSITIVITY: 1,

    // Risk Scoring
    RISK_THRESHOLD: 70,
    HIGH_RISK_THRESHOLD: 85,

    // System Flags
    ENABLE_ALERTS: true,
    ENABLE_AI_PREDICTION: true,

    // API (backend integration)
    API_URL: "http://localhost:8000/api/behavior",

    // Debug mode
    DEBUG: true

};