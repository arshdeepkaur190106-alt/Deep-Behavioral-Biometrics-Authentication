// =====================================
// Mouse Behavior Collection Module
// =====================================

let mouseEvents = [];

let lastMoveTime = null;
let lastX = null;
let lastY = null;

let lastSpeed = 0;

let lastClickTime = null;

let totalClicks = 0;
let doubleClicks = 0;

let isDragging = false;
let dragCount = 0;


// ===============================
// Mouse Movement
// ===============================
document.addEventListener("mousemove", (event) => {

    const now = Date.now();

    let speed = 0;
    let acceleration = 0;

    if (lastMoveTime !== null) {

        const dt = (now - lastMoveTime) / 1000;

        const dx = event.clientX - lastX;
        const dy = event.clientY - lastY;

        const distance = Math.sqrt(dx * dx + dy * dy);

        speed = dt > 0 ? distance / dt : 0;

        acceleration = dt > 0 ? (speed - lastSpeed) / dt : 0;
    }

    mouseEvents.push({

        type: "move",

        x: event.clientX,

        y: event.clientY,

        speed: Math.round(speed),

        acceleration: Math.round(acceleration),

        time: now

    });

    lastSpeed = speed;

    lastMoveTime = now;

    lastX = event.clientX;

    lastY = event.clientY;

});


// ===============================
// Mouse Click
// ===============================
document.addEventListener("click", (event) => {

    const now = Date.now();

    let clickInterval = 0;

    if (lastClickTime !== null) {

        clickInterval = now - lastClickTime;

        if (clickInterval < 300) {
            doubleClicks++;
        }

    }

    totalClicks++;

    mouseEvents.push({

        type: "click",

        button: event.button,

        x: event.clientX,

        y: event.clientY,

        clickInterval: clickInterval,

        time: now

    });

    lastClickTime = now;

});


// ===============================
// Drag Detection
// ===============================
document.addEventListener("mousedown", () => {

    isDragging = true;

});

document.addEventListener("mouseup", () => {

    if (isDragging) {
        dragCount++;
    }

    isDragging = false;

});


// ===============================
// Return Mouse Features
// ===============================
function getMouseData() {

    let totalSpeed = 0;
    let totalAcceleration = 0;
    let moveCount = 0;

    mouseEvents.forEach(event => {

        if (event.type === "move") {

            totalSpeed += event.speed;

            totalAcceleration += Math.abs(event.acceleration);

            moveCount++;

        }

    });

    return {

        totalMouseEvents: mouseEvents.length,

        totalClicks: totalClicks,

        doubleClicks: doubleClicks,

        dragCount: dragCount,

        averageSpeed:
            moveCount === 0
                ? 0
                : Math.round(totalSpeed / moveCount),

        averageAcceleration:
            moveCount === 0
                ? 0
                : Math.round(totalAcceleration / moveCount),

        events: mouseEvents

    };

}