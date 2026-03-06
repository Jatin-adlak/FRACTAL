
function startSystem() {
    fetch('/start/')
        .then(() => {
            document.getElementById("status").innerText = "Status: Running";

            const img = document.getElementById("cameraFeed");
            const placeholder = document.getElementById("demoPlaceholder");

            placeholder.style.display = "none";
            img.style.display = "block";
            img.src = "/video/";
        });
}

function stopSystem() {
    fetch('/stop/')
        .then(() => {
            document.getElementById("status").innerText = "Status: Stopped";

            const img = document.getElementById("cameraFeed");
            const placeholder = document.getElementById("demoPlaceholder");

            img.src = "";
            img.style.display = "none";
            placeholder.style.display = "flex";
        });
}

// --------------------------------------------------
// SYSTEM USAGE MONITOR
// ------------------------------------

