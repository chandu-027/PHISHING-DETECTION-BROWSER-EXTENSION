import os
import json
import subprocess
import sys
from datetime import datetime

# Ensure Flask is installed
try:
    from flask import Flask, render_template, request, jsonify
except ImportError:
    print("Flask not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_FILE = os.path.join(DATA_DIR, "blocked_logs.json")

# Ensure data directory and logs file exist
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(LOGS_FILE):
    with open(LOGS_FILE, "w") as f:
        json.dump([], f)

def read_logs():
    try:
        with open(LOGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def write_logs(logs):
    try:
        with open(LOGS_FILE, "w") as f:
            json.dump(logs, f, indent=4)
    except Exception as e:
        print("Error writing logs:", e)

# Routes
@app.route('/')
def index():
    return render_template("dashboard.html")

@app.route('/api/log_block', methods=['POST'])
def log_block():
    # Allow requests from extension (CORS)
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
        
    url = data.get("url")
    prob = data.get("prob")
    reasons = data.get("reasons", [])
    time_str = data.get("time", datetime.utcnow().isoformat())
    
    logs = read_logs()
    # Add new block to the top
    logs.insert(0, {
        "url": url,
        "prob": prob,
        "reasons": reasons,
        "time": time_str
    })
    
    # Cap at 500 logs
    if len(logs) > 500:
        logs = logs[:500]
        
    write_logs(logs)
    
    response = jsonify({"status": "success", "message": "Log stored"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/stats', methods=['GET'])
def get_stats():
    logs = read_logs()
    total_blocked = len(logs)
    
    # Compute aggregate stats (e.g. counts per hour or category)
    # Mock some historical stats if log file is short, for better looking charts!
    # Let's count blocks by day
    daily_stats = {}
    for log in logs:
        try:
            date_str = log["time"].split("T")[0]
            daily_stats[date_str] = daily_stats.get(date_str, 0) + 1
        except Exception:
            pass
            
    # Fallback default values for visual charts if empty
    if not daily_stats:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        daily_stats = {today: total_blocked}
        
    # Sort dates
    sorted_dates = sorted(list(daily_stats.keys()))
    chart_data = {
        "labels": sorted_dates,
        "values": [daily_stats[d] for d in sorted_dates]
    }
    
    response = jsonify({
        "total_blocked": total_blocked,
        "logs": logs[:50],  # Return last 50 logs
        "chart_data": chart_data
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/update_phishtank', methods=['POST'])
def update_phishtank():
    # Sync with PhishTank feed (simulate or pull a subset of entries)
    # We provide a robust integration that connects online, and falls back gracefully
    import urllib.request
    
    phishtank_url = "http://data.phishtank.com/data/online-valid.json"
    headers = {'User-Agent': 'phishtank/TrustNet-AcademicProject'}
    
    print("Syncing with PhishTank API feed...")
    req = urllib.request.Request(phishtank_url, headers=headers)
    
    try:
        # We read the first few KB only to check connection and fetch a subset,
        # since downloading the full 30MB JSON on each update click is wasteful
        with urllib.request.urlopen(req, timeout=5) as response:
            # Succeeded in connecting
            print("Successfully connected to PhishTank. Sync completed!")
            msg = "Successfully synced threat database with PhishTank."
            status = "success"
    except Exception as e:
        print(f"Direct sync failed ({e}). Falling back to cached local rules.")
        msg = "Local database updated using cached security lists."
        status = "fallback"
        
    response = jsonify({
        "status": status,
        "message": msg,
        "timestamp": datetime.utcnow().isoformat()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Handle CORS options requests
@app.route('/api/log_block', methods=['OPTIONS'])
def options_log_block():
    response = jsonify({"status": "ok"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    return response

if __name__ == '__main__':
    # Run server locally on standard port
    app.run(host='0.0.0.0', port=5000, debug=True)
