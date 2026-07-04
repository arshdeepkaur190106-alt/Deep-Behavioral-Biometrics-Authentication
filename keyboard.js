// ===============================
// Keyboard Behavior Collection
// ===============================

let keyboardData = [];

let keyDownTimes = {};
let lastKeyRelease = null;

let totalKeys = 0;
let backspaceCount = 0;

let totalHoldTime = 0;
let totalFlightTime = 0;

const sessionStart = Date.now();

// Key Press
document.addEventListener("keydown", (event) => {

    const now = Date.now();

    if (!keyDownTimes[event.code]) {
        keyDownTimes[event.code] = now;
    }

    totalKeys++;

    if (event.key === "Backspace") {
        backspaceCount++;
    }

    if (lastKeyRelease !== null) {
        totalFlightTime += (now - lastKeyRelease);
    }

});

// Key Release
document.addEventListener("keyup", (event) => {

    const now = Date.now();

    if (keyDownTimes[event.code]) {

        const holdTime = now - keyDownTimes[event.code];

        totalHoldTime += holdTime;

        keyboardData.push({
            key: event.key,
            holdTime: holdTime,
            time: now
        });

        delete keyDownTimes[event.code];
    }

    lastKeyRelease = now;

});

// Return Keyboard Features
function getKeyboardData() {

    const minutes = (Date.now() - sessionStart) / 60000;

    const typingSpeed = Math.round(
        totalKeys / Math.max(minutes, 0.01)
    );

    return {

        totalKeys: totalKeys,

        typingSpeed: typingSpeed,

        averageHoldTime:
            keyboardData.length === 0
                ? 0
                : Math.round(totalHoldTime / keyboardData.length),

        averageFlightTime:
            keyboardData.length <= 1
                ? 0
                : Math.round(totalFlightTime / (keyboardData.length - 1)),

        backspaceCount: backspaceCount,

        errorRate:
            totalKeys === 0
                ? 0
                : Number((backspaceCount / totalKeys).toFixed(2)),

        events: keyboardData

    };

}