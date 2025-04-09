import os
import sys
import webbrowser
from flask import Flask, request, jsonify, send_from_directory
import xlwings as xw
from flask_cors import CORS
import threading
import time

app = Flask(__name__, static_folder='frontend')
CORS(app)

# Ensure the Excel file is found in the bundled app
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCEL_PATH = os.path.join(BASE_DIR, "backend", "Bonds Calculator.xlsx")

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Open Excel file using xlwings
        app = xw.App(visible=False)
        wb = app.books.open(EXCEL_PATH, read_only=False)
        sheet = wb.sheets.active

        # Get user input from frontend
        data = request.json
        sheet.range("C7").value = float(data.get("lumpsum", 0))
        sheet.range("G7").value = float(data.get("monthlyPremium", 0))
        sheet.range("G9").value = float(data.get("annualIncrease", 0))
        sheet.range("G11").value = float(data.get("investmentReturn", 0))
        sheet.range("G13").value = float(data.get("term", 0))
        sheet.range("K11").value = float(data.get("actual", 0))

        # Trigger Excel to recalculate
        wb.app.calculate()
        time.sleep(1)

        # Extract results
        results = {
            "property_parameters": {
                "Levies": sheet.range("D21").value,
                "Rental Income": sheet.range("H21").value,
                "Capital Growth": sheet.range("L21").value,
                "Rates & Taxes": sheet.range("D23").value,
                "Rental Management": sheet.range("H23").value,
                "Rental Escalation": sheet.range("L23").value,
                "Rental Insurance": sheet.range("D25").value,
                "Bond Repayment": sheet.range("H25").value,
                "Interest Rate": sheet.range("L25").value,
            },
            "investment_comparison": {
                "igrow": {
                    "Property": "Middle Class - 2 Bed 1 Bath",
                    "1 Year Contribution": sheet.range("F38").value,
                    "1 Year Total Cashflow": sheet.range("F40").value,
                    "Equity through Capital Appreciation": sheet.range("F42").value,
                    "1 Year Financial Position": sheet.range("F44").value,
                    "1 Year Total Contribution": sheet.range("F48").value,
                    "Internal Rate of Return": sheet.range("F50").value,
                    "Total Return": sheet.range("F52").value,
                },
                "traditional": {
                    "Investment Type": "Money Market",
                    "1 Year Premium Monthly": sheet.range("L38").value,
                    "1 Year Value Instrument": sheet.range("L40").value,
                    "1 Year Lumpsum": sheet.range("L42").value,
                    "1 Year Financial Position": sheet.range("L44").value,
                    "1 Year Total Contribution": sheet.range("L48").value,
                    "Internal Rate of Return": sheet.range("L50").value,
                    "Total Return": sheet.range("L52").value,
                }
            },
            "financial_position": {
                "igrow": {
                    "Equity & Cash Reserves": sheet.range("F71").value,
                    "Monthly Income": sheet.range("F73").value,
                    "PV Monthly Income": sheet.range("F75").value,
                },
                "traditional": {
                    "Financial Position": sheet.range("L71").value,
                    "Monthly Income": sheet.range("L73").value,
                    "PV Monthly Income": sheet.range("L75").value,
                }
            },
            "leveraged_strategy": {
                "igrow": {
                    "Properties": sheet.range("F99").value,
                    "Property Portfolio Value": sheet.range("F101").value,
                    "Retirement Income": sheet.range("F103").value,
                    "PV of Retirement Income": sheet.range("F105").value,
                },
                "traditional": {
                    "Financial Position": sheet.range("L101").value,
                    "PV of Retirement Income": sheet.range("L105").value,
                }
            }
        }

        # Clean up Excel
        wb.save(EXCEL_PATH)
        wb.close()
        app.quit()

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e), "results": {}})

def open_browser():
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://127.0.0.1:5001')

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(host="127.0.0.1", port=5001, debug=False) 