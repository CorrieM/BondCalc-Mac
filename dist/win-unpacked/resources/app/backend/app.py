import subprocess
import sys
import math
import logging
import logging.handlers
import ctypes
import signal
import atexit

# def is_admin():
    # try:
        # return ctypes.windll.shell32.IsUserAnAdmin()
    # except:
        # return False

# if not is_admin():
    # # Re-run the script with admin rights
    # ctypes.windll.shell32.ShellExecuteW(
        # None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    # sys.exit()

# -----------------------------------
# Set up logging to Windows Event Viewer
# -----------------------------------
def setup_windows_event_log():
    try:
        handler = logging.handlers.NTEventLogHandler("IGrowBondCalculator")
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        logger.info("Starting IGrow Investment Calculator.")
        return logger
    except Exception as e:
        print(f"Failed to initialize Windows Event Log: {e}")
        sys.exit(1)

logger = setup_windows_event_log()

# -----------------------------------
# Install required packages if not present
# -----------------------------------
required_packages = ['Flask-Cors', 'xlwings', 'openpyxl']

for package in required_packages:
    try:
        __import__(package.lower().replace('-', '_'))
    except ImportError:
        try:
            logger.warning(f"{package} not found. Installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            logger.info(f"Installed {package} successfully.")
        except Exception as install_error:
            logger.error(f"Failed to install {package}: {install_error}")
            sys.exit(1)

# -----------------------------------
# Imports after dependency check
# -----------------------------------
from flask import Flask, request, jsonify
import xlwings as xw
import openpyxl
import os
import time
from flask_cors import CORS

# -----------------------------------
# Flask App Setup
# -----------------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
EXCEL_PATH = os.path.join(BASE_DIR, "Bonds Calculator.xlsx")

# -----------------------------------
# Gracefully  Shutdown
# -----------------------------------

def shutdown_handler(*args):
    logger.info("Shutting down IGrow Bonds Calculator.")
    try:
        # Clean up any open Excel apps just in case
        for app in xw.apps:
            if not app.api.Workbooks.Count:  # if app has no workbooks open
                app.quit()
    except Exception as e:
        logger.warning(f"Error during Excel cleanup: {e}")
    sys.exit(0)

# Handle common termination signals
signal.signal(signal.SIGINT, shutdown_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, shutdown_handler)  # kill command or system shutdown
atexit.register(shutdown_handler)                # Normal Python exit

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        logger.info("Received calculation request.")
        excel = xw.App(visible=False)
        wb = excel.books.open(EXCEL_PATH, read_only=False)
        sheet = wb.sheets[0]         # First tab (active calculations)
        sheet2 = wb.sheets[1]        # Second tab by index (0-based)

        data = request.json
        #Set excel cell data for calculation
        rate = float(data.get("rate", 2))
        logger.info(f"1st Rate: {rate}")
        rate = rate/100
        logger.info(f"2nd Rate: {rate}")
        rate = sheet2.range("H7").value = rate
        #Set excel cell in the second tab data for calculation
        prop1 = sheet2.range("H9").value = float(data.get("PropValue1", 0))
        prop2 = sheet2.range("H11").value = float(data.get("PropValue2", 0))
        prop3 = sheet2.range("H13").value = float(data.get("PropValue3", 0))
        prop4 = sheet2.range("H15").value = float(data.get("PropValue4", 0))
        prop5 = sheet2.range("H17").value = float(data.get("PropValue5", 0))

        logger.info("Excel path: "+EXCEL_PATH)


        wb.app.calculate()
        #Send calculated data back
        results = {
    "parameters": [
        ("TransferIncentive", round(sheet.range("H17").value, 2)),
        ("TotalComm", round(sheet.range("H20").value, 2)),
        ("RevenueRate", round(sheet.range("H23").value, 2))
    ]
}
        logger.info("Excel path: "+EXCEL_PATH)
        wb.save(EXCEL_PATH)
        wb.close()
        excel.quit()

        logger.info("Calculation completed successfully.")
        return jsonify({"results": results})

    except Exception as e:
        logger.error(f"Error during calculation: {str(e)}")
        return jsonify({"error": str(e), "results": {}})
        excel.quit()

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if username == "admin" and password == "IGrow@1":
            logger.info("Admin login successful.")
            return jsonify({"message": "Login successful", "status": "success"})
        else:
            logger.warning("Login failed with invalid credentials.")
            return jsonify({"message": "Invalid credentials", "status": "error"})

    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": str(e), "status": "error"})

if __name__ == '__main__':
    try:
        app.run(host="127.0.0.1", port=5001, debug=False)
        logger.info("Flask server started successfully.")
    except Exception as e:
        logger.error(f"Failed to start Flask server: {e}")