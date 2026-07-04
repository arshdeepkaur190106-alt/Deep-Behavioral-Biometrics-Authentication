// ===============================
// Device Information Module
// ===============================

function getDeviceData() {

    return {

        platform: navigator.platform,

        userAgent: navigator.userAgent,

        language: navigator.language,

        screenWidth: window.screen.width,

        screenHeight: window.screen.height,

        windowWidth: window.innerWidth,

        windowHeight: window.innerHeight,

        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,

        deviceMemory: navigator.deviceMemory || "unknown",

        hardwareConcurrency: navigator.hardwareConcurrency || "unknown"

    };

}