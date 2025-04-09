const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 1000,
    icon: path.join(__dirname, "frontend", "logo.ico"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      enableRemoteModule: false,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, "frontend", "login.html"));
  


  // 🧼 Handle window close
  mainWindow.on("closed", () => {
    shutdownPython();
    mainWindow = null;
  });
}

	app.on("window-all-closed", () => shutdownPython());
	
function startPythonBackend() {
  const pythonExecutable = path.join(__dirname, "app.exe");

  pythonProcess = spawn(pythonExecutable, [], {
    windowsHide: true,
    detached: false,
    stdio: "ignore", // Change to ['pipe', 'pipe', 'pipe'] if you want to see logs
  });

  // Optional debugging output
  // pythonProcess.stdout.on("data", (data) => console.log(`Flask: ${data}`));
  // pythonProcess.stderr.on("data", (data) => console.error(`Flask Error: ${data}`));

  pythonProcess.on("close", (code) =>
    console.log(`Flask backend exited with code ${code}`)
  );
}

const kill = require("tree-kill");

const { exec } = require("child_process");


function shutdownPython() {
  // ✅ Log to Windows Event Viewer using PowerShell
  const logCommand = `powershell -Command "Write-EventLog -LogName Application -Source 'IGrowBondsCalculator' -EntryType Information -EventId 1000 -Message 'Electron requested shutdown of app.exe.'"`;
exec('taskkill /F /T /IM "app.exe"', (err, stdout, stderr) => {
        if (err) {
          console.error("❌ taskkill failed:", err);
        } else {
          console.log("✅ taskkill succeeded.");
        }
        pythonProcess = null;
      });
  exec(logCommand, (err) => {
    if (err) {
      console.error("❌ Failed to write to Event Log:", err);
    } else {
      console.log("📝 Shutdown logged to Event Viewer.");
    }
  });

  // ✅ Try graceful Flask shutdown via API
  fetch("http://127.0.0.1:5001/shutdown", { method: "POST" })
    .then((res) => {
      if (res.ok) {
        console.log("✅ Flask shutdown endpoint called.");
      }
    })
    .catch(() => {
      console.warn("⚠️ Graceful shutdown failed. Forcing taskkill...");

      exec('taskkill /F /T /IM "app.exe"', (err, stdout, stderr) => {
        if (err) {
          console.error("❌ taskkill failed:", err);
        } else {
          console.log("✅ taskkill succeeded.");
        }
        pythonProcess = null;
      });
    });
}

app.whenReady().then(() => {
  startPythonBackend();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  shutdownPython();
  if (process.platform !== "darwin") app.quit();
});

// ✅ IPC Login Logic
ipcMain.on("login", (event, credentials) => {
  fetch("http://127.0.0.1:5001/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  })
    .then((response) => response.json())
    .then((data) => {
      event.reply("login-response", data);
    })
    .catch((error) => {
      console.error("IPC Login Error:", error);
      event.reply("login-response", {
        message: "Login failed. Flask not responding.",
        status: "error",
      });
    });
});
