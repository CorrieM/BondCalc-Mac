const { app, BrowserWindow } = require("electron");
const { execFile } = require("child_process");
const path = require("path");

let mainWindow;
let flaskProcess;

app.whenReady().then(() => {
    // Start Flask server from EXE inside the bundled app
    let flaskPath;
    if (process.platform === "win32") {
        flaskPath = path.join(process.resourcesPath, "backend", "app.exe"); // Ensure `app.exe` is bundled
    } else {
        flaskPath = path.join(__dirname, "backend", "app.py");
    }

    console.log("Starting Flask at:", flaskPath);
    flaskProcess = execFile(flaskPath, (error, stdout, stderr) => {
        if (error) {
            console.error("Flask error:", error);
        }
        console.log(stdout);
        console.error(stderr);
    });

    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        }
    });

    mainWindow.loadFile("index.html");

    mainWindow.on("closed", () => {
        mainWindow = null;
        if (flaskProcess) flaskProcess.kill();
    });
});

app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
        if (flaskProcess) flaskProcess.kill();
        app.quit();
    }
});
