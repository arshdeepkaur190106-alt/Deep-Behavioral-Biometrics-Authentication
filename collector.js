// ===============================
// Collector Module
// ===============================

function collectBehaviorData() {

    const features = extractFeatures();

    console.clear();

    console.log("====================================");
    console.log("Behavior Authentication Report");
    console.log("====================================");

    console.table(features);

    console.log("AI Ready JSON");

    console.log(JSON.stringify(features, null, 4));

}