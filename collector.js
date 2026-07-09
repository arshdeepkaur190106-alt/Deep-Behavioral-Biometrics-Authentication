// ===============================
// Collector Module
// ===============================

function collectBehaviorData() {
    const features = extractFeatures();

    fetch(CONFIG.API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(features)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Server response:", data);
    })
    .catch(error => {
        console.error("Error sending behavior data:", error);
    });
}