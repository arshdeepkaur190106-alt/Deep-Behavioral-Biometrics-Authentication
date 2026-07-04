// =====================================
// Session Tracking Module
// =====================================

const sessionStartTime = Date.now();

const sessionId = "SESSION_" + Date.now();

let sessionEndTime = null;

function endSession() {

    sessionEndTime = Date.now();

}

function getSessionData() {

    const endTime = sessionEndTime || Date.now();

    return {

        sessionId: sessionId,

        sessionStart: sessionStartTime,

        sessionEnd: endTime,

        sessionDuration: endTime - sessionStartTime

    };

}