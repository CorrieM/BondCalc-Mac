const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let loginWindow;
let mainWindow;
let backendProcess;

// User credentials (Replace with secure authentication logic if needed)
const VALID_USERNAME = "strat";
const VALID_PASSWORD = "Strat@IGrow";

app.whenReady().then(() => {
    console.log("Launching Login Window...");

    loginWindow = new BrowserWindow({
        width: 800,
        height: 600,
        resizable: false,
        icon: path.join(__dirname, 'logo.ico'),
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false // Needed for IPC communication
        }
    });

    loginWindow.loadFile('login.html');
});

// Handle login authentication
ipcMain.on('login-attempt', (event, credentials) => {
    const { username, password } = credentials;

    if (username === VALID_USERNAME && password === VALID_PASSWORD) {
        loginWindow.close();
        openMainApp();
    } else {
        event.reply('login-failed', 'Invalid username or password.');
    }
});

function openMainApp() {
    console.log("Launching Main App...");

    let exePath = path.join(app.getAppPath(), 'ExcelUpdater.exe');
    backendProcess = spawn(exePath, { windowsHide: true });

    backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`Backend Error: ${data}`);
    });

    backendProcess.on('error', (err) => {
        console.error(`Failed to start backend process: ${err}`);
    });

    backendProcess.on('close', (code) => {
        console.log(`Backend exited with code ${code}`);
    });

    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        show: false,
        icon: path.join(__dirname, 'logo.ico'),
        webPreferences: {
            nodeIntegration: true
        }
    });

    mainWindow.loadFile('index.html');

    mainWindow.once('ready-to-show', () => {
        console.log("Showing Main App...");
        mainWindow.show();
    });

    mainWindow.on('closed', () => {
        if (backendProcess) backendProcess.kill();
    });
}

app.on('window-all-closed', () => {
    if (backendProcess) backendProcess.kill();
    if (process.platform !== 'darwin') app.quit();
});
