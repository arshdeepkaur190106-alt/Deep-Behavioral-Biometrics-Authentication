// ===============================
// Feature Extraction Module
// ===============================

function extractFeatures() {

    // Get data from all behavior modules
    const keyboardData = getKeyboardData();
    const mouseData = getMouseData();
    const scrollData = getScrollData();
    const sessionData = getSessionData();

    return {

        // ===============================
        // Session Features
        // ===============================
        sessionId: sessionData.sessionId,
        sessionStart: sessionData.sessionStart,
        sessionEnd: sessionData.sessionEnd,
        sessionDuration: sessionData.sessionDuration,

        // ===============================
        // Keyboard Features
        // ===============================
        totalKeyEvents: keyboardData.totalKeys,
        typingSpeed: keyboardData.typingSpeed,
        averageHoldTime: keyboardData.averageHoldTime,
        averageFlightTime: keyboardData.averageFlightTime,
        backspaceCount: keyboardData.backspaceCount,
        errorRate: keyboardData.errorRate,

        // ===============================
        // Mouse Features
        // ===============================
        totalMouseEvents: mouseData.totalMouseEvents,
        mouseClicks: mouseData.totalClicks,
        doubleClicks: mouseData.doubleClicks,
        dragCount: mouseData.dragCount,
        averageMouseSpeed: mouseData.averageSpeed,
        averageMouseAcceleration: mouseData.averageAcceleration,

        // ===============================
        // Scroll Features
        // ===============================
        totalScrollEvents: scrollData.totalScrollEvents,
        totalScrollDistance: scrollData.totalScrollDistance,
        averageScrollSpeed: scrollData.averageScrollSpeed,
        maxScrollSpeed: scrollData.maxScrollSpeed,
        minScrollSpeed: scrollData.minScrollSpeed,
        scrollUpCount: scrollData.scrollUpCount,
        scrollDownCount: scrollData.scrollDownCount,

        // ===============================
        // Timestamp
        // ===============================
        timestamp: Date.now()

    };

}