// =====================================
// Scroll Behavior Collection Module
// =====================================

let scrollEvents = [];

let lastScrollTime = null;
let lastScrollPosition = window.scrollY;

let totalScrollDistance = 0;
let totalScrollSpeed = 0;

let maxScrollSpeed = 0;
let minScrollSpeed = Infinity;

let scrollUpCount = 0;
let scrollDownCount = 0;

window.addEventListener("scroll", () => {

    const now = Date.now();

    const currentPosition = window.scrollY;

    const distance = Math.abs(currentPosition - lastScrollPosition);

    let speed = 0;

    if (lastScrollTime !== null) {

        const timeDiff = (now - lastScrollTime) / 1000;

        speed = timeDiff > 0 ? distance / timeDiff : 0;

    }

    if (currentPosition > lastScrollPosition) {
        scrollDownCount++;
    } else if (currentPosition < lastScrollPosition) {
        scrollUpCount++;
    }

    totalScrollDistance += distance;

    totalScrollSpeed += speed;

    if (speed > maxScrollSpeed)
        maxScrollSpeed = speed;

    if (speed > 0 && speed < minScrollSpeed)
        minScrollSpeed = speed;

    scrollEvents.push({

        position: currentPosition,

        direction:
            currentPosition > lastScrollPosition
                ? "Down"
                : "Up",

        speed: Math.round(speed),

        distance: distance,

        time: now

    });

    lastScrollPosition = currentPosition;

    lastScrollTime = now;

});


function getScrollData() {

    const averageSpeed =
        scrollEvents.length === 0
            ? 0
            : Math.round(totalScrollSpeed / scrollEvents.length);

    return {

        totalScrollEvents: scrollEvents.length,

        totalScrollDistance,

        averageScrollSpeed: averageSpeed,

        maxScrollSpeed: Math.round(maxScrollSpeed),

        minScrollSpeed:
            minScrollSpeed === Infinity
                ? 0
                : Math.round(minScrollSpeed),

        scrollUpCount,

        scrollDownCount,

        events: scrollEvents

    };

}