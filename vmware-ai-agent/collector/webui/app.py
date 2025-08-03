from flask import Flask, render_template, jsonify
import json
import os
import subprocess
import threading
import time

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, "..", "analysis_report.json")
INSIGHT_SCRIPT_PATH = os.path.join(BASE_DIR, "insights_engine.py")

def run_analysis_loop():
    while True:
        try:
            print("🔁 Running insights_engine.py")
            INSIGHT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "insights_engine.py"))

        except subprocess.CalledProcessError as e:
            print("❌ Error during analysis run:", e)
        time.sleep(60)  # Run every 60 seconds

@app.route("/")
def index():
    try:
        with open(REPORT_PATH) as f:
            data = json.load(f)
    except Exception as e:
        data = []
        print("⚠️ Error reading report file:", e)
    return render_template("index.html", vms=data)

@app.route("/api/data")
def api_data():
    try:
        with open(REPORT_PATH) as f:
            data = json.load(f)
    except Exception as e:
        data = []
        print("⚠️ Error reading report file:", e)
    return jsonify(data)

if __name__ == "__main__":
    # Start background analysis loop
    t = threading.Thread(target=run_analysis_loop, daemon=True)
    t.start()
    app.run(debug=True)

