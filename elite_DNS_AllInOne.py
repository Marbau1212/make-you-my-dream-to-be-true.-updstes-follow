import socket
import threading
import time
import sys
import subprocess
import os
import sqlite3
import logging
import json
from datetime import datetime, timedelta


# --- AUTOMATISCHE ABHÄNGIGKEITS-PRÜFUNG ---
def install_dependencies():
    packages = ["dnslib", "flask", "requests"]
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"[SYSTEM] Installiere fehlendes Paket: {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install_dependencies()

import requests
from flask import Flask, render_template_string
from dnslib import DNSRecord, RR, A, QTYPE


# --- KONFIGURATION ---
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 53
WEB_PORT = 8080
FORWARDER_IP = "1.1.1.1"
BLOCKLIST_URL = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
DB_PATH = "dns_history.db"


# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("dns_system.log"), logging.StreamHandler()],
)


# --- DATENBANK KLASSE (LOGGING & CLOUD BACKUP) ---
class DNSDatabase:
    def __init__(self):
        self._setup()

    def _setup(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    client_ip TEXT,
                    domain TEXT,
                    status TEXT
                )
                """
            )

    def log_query(self, client_ip, domain, status):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "INSERT INTO queries (client_ip, domain, status) VALUES (?, ?, ?)",
                    (client_ip, domain, status),
                )
        except Exception as e:
            logging.error(f"DB Log Fehler: {e}")

    def get_stats(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM queries")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM queries WHERE status = 'BLOCKED'")
            blocked = cursor.fetchone()[0]
            return {"total": total, "blocked": blocked}

    def backup_to_github(self):
        dump_file = "dns_backup.sql"
        try:
            with open(dump_file, "w") as f:
                subprocess.run(["sqlite3", DB_PATH, ".dump"], stdout=f, check=True)

            # Nutzt deine bestehende 'gh' Authentifizierung in Termux
            cmd = [
                "gh",
                "gist",
                "create",
                dump_file,
                "-desc",
                f"DNS Backup {datetime.now()}",
                "-p",
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            logging.info("GitHub-Backup erfolgreich.")
            return True
        except Exception as e:
            logging.error(f"GitHub-Backup fehlgeschlagen: {e}")
            return False


# --- GLOBALE VARIABLEN & CACHE ---
db = DNSDatabase()
DYNAMIC_BLOCKLIST: set = set()
DNS_CACHE: dict = {}
recent_queries: list = []
stats_lock = threading.Lock()
cache_lock = threading.Lock()


# --- DNS LOGIK ---
def handle_dns_query(data, addr, server_socket):
    client_ip = addr[0]
    status = "OK"
    qname = "N/A"
    try:
        request = DNSRecord.parse(data)
        qname = str(request.q.qname).lower()

        # 1. Cache Check
        with cache_lock:
            cached = DNS_CACHE.get(qname)
        if cached and cached["expires"] > time.time():
            server_socket.sendto(cached["data"], addr)
            status = "CACHED"
        # 2. Blocklist Check
        elif qname in DYNAMIC_BLOCKLIST:
            status = "BLOCKED"
            reply = request.reply()
            reply.header.rcode = 3  # NXDOMAIN
            server_socket.sendto(reply.pack(), addr)
        else:
            # 3. Forwarding
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as forward_sock:
                forward_sock.settimeout(2.0)
                forward_sock.sendto(data, (FORWARDER_IP, 53))
                resp_data, _ = forward_sock.recvfrom(4096)
                server_socket.sendto(resp_data, addr)
                status = "FORWARDED"
                # Cache the response for 60 seconds
                with cache_lock:
                    DNS_CACHE[qname] = {
                        "data": resp_data,
                        "expires": time.time() + 60,
                    }

    except Exception as e:
        logging.error(f"Query Fehler ({qname}): {e}")
        status = "ERROR"
    finally:
        db.log_query(client_ip, qname, status)
        with stats_lock:
            recent_queries.append(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "client": client_ip,
                    "domain": qname,
                    "status": status,
                }
            )
            if len(recent_queries) > 15:
                recent_queries.pop(0)


def dns_server_loop():
    while True:
        server_socket = None
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((LISTEN_IP, LISTEN_PORT))
            logging.info(f"DNS Server gestartet auf Port {LISTEN_PORT}")
            while True:
                data, addr = server_socket.recvfrom(4096)
                threading.Thread(
                    target=handle_dns_query,
                    args=(data, addr, server_socket),
                    daemon=True,
                ).start()
        except PermissionError:
            logging.error(
                "Port 53 benötigt Root-Rechte. Starte mit: sudo python elite_DNS_AllInOne.py"
            )
            sys.exit(1)
        except Exception as e:
            logging.error(f"DNS Server Crash, Neustart in 5s: {e}")
            time.sleep(5)
        finally:
            if server_socket:
                server_socket.close()


# --- WEB DASHBOARD (FLASK) ---
app = Flask(__name__)

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite DNS Control Center</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; }
        header { background: #161b22; padding: 1rem 2rem; border-bottom: 1px solid #30363d; }
        header h1 { color: #58a6ff; font-size: 1.5rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 1.5rem; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.2rem; text-align: center; }
        .stat-card .value { font-size: 2rem; font-weight: bold; color: #58a6ff; }
        .stat-card .label { color: #8b949e; margin-top: 0.3rem; }
        .stat-card.blocked .value { color: #f85149; }
        .panel { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.2rem; margin-bottom: 1.5rem; }
        .panel h2 { color: #58a6ff; margin-bottom: 1rem; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; }
        table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
        th, td { padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid #21262d; }
        th { color: #8b949e; font-weight: 600; }
        .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
        .badge-ok, .badge-cached, .badge-forwarded { background: #1f4228; color: #3fb950; }
        .badge-blocked { background: #3d1010; color: #f85149; }
        .badge-error { background: #3d2b00; color: #d29922; }
    </style>
</head>
<body>
    <header><h1>🛡️ Elite DNS Control Center</h1></header>
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="value">{{ stats.total }}</div>
                <div class="label">Total Queries</div>
            </div>
            <div class="stat-card blocked">
                <div class="value">{{ stats.blocked }}</div>
                <div class="label">Blocked</div>
            </div>
            <div class="stat-card">
                <div class="value">{{ (stats.blocked / stats.total * 100) | round(1) if stats.total > 0 else 0 }}%</div>
                <div class="label">Block Rate</div>
            </div>
        </div>

        <div class="panel">
            <h2>📊 Queries per Hour</h2>
            <canvas id="chart" height="80"></canvas>
        </div>

        <div class="panel">
            <h2>🕐 Recent Queries</h2>
            <table>
                <thead><tr><th>Time</th><th>Client</th><th>Domain</th><th>Status</th></tr></thead>
                <tbody>
                {% for q in recent %}
                <tr>
                    <td>{{ q.time }}</td>
                    <td>{{ q.client }}</td>
                    <td>{{ q.domain }}</td>
                    <td><span class="badge badge-{{ q.status.lower() }}">{{ q.status }}</span></td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        new Chart(document.getElementById('chart'), {
            type: 'bar',
            data: {
                labels: {{ labels | safe }},
                datasets: [{
                    label: 'Queries',
                    data: {{ values | safe }},
                    backgroundColor: 'rgba(88, 166, 255, 0.5)',
                    borderColor: '#58a6ff',
                    borderWidth: 1
                }]
            },
            options: {
                plugins: { legend: { labels: { color: '#c9d1d9' } } },
                scales: {
                    x: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' } },
                    y: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' } }
                }
            }
        });
    </script>
</body>
</html>
"""


@app.route("/")
def dashboard():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT strftime('%H', timestamp) as h, COUNT(*) FROM queries GROUP BY h ORDER BY h DESC LIMIT 10"
        )
        data = cursor.fetchall()

    labels = json.dumps([f"{r[0]}:00" for r in data][::-1])
    values = json.dumps([r[1] for r in data][::-1])

    return render_template_string(
        DASHBOARD_TEMPLATE,
        stats=db.get_stats(),
        recent=recent_queries[::-1],
        labels=labels,
        values=values,
    )


@app.route("/api/stats")
def api_stats():
    stats = db.get_stats()
    stats["blocklist_size"] = len(DYNAMIC_BLOCKLIST)
    stats["cache_size"] = len(DNS_CACHE)
    return json.dumps(stats), 200, {"Content-Type": "application/json"}


@app.route("/api/recent")
def api_recent():
    with stats_lock:
        data = list(recent_queries[::-1])
    return json.dumps(data), 200, {"Content-Type": "application/json"}


# --- MAINTENANCE THREADS ---
def update_blocklist_loop():
    while True:
        try:
            logging.info("Lade Blocklist...")
            res = requests.get(BLOCKLIST_URL, timeout=30)
            new_list = set()
            for line in res.text.splitlines():
                line = line.strip()
                if line.startswith("0.0.0.0") or line.startswith("127.0.0.1"):
                    parts = line.split()
                    if len(parts) > 1:
                        domain = parts[1].strip().lower() + "."
                        new_list.add(domain)
            global DYNAMIC_BLOCKLIST
            DYNAMIC_BLOCKLIST = new_list
            logging.info(f"Blocklist aktiv: {len(DYNAMIC_BLOCKLIST)} Domains.")
        except Exception as e:
            logging.error(f"Blocklist Update Fehler: {e}")
        time.sleep(86400)  # Alle 24 Stunden


def cache_cleanup_loop():
    """Entfernt abgelaufene Cache-Einträge alle 5 Minuten."""
    while True:
        time.sleep(300)
        now = time.time()
        with cache_lock:
            fresh = {k: v for k, v in DNS_CACHE.items() if v["expires"] > now}
            removed = len(DNS_CACHE) - len(fresh)
            DNS_CACHE.clear()
            DNS_CACHE.update(fresh)
        if removed:
            logging.info(f"Cache-Cleanup: {removed} abgelaufene Einträge entfernt.")


def backup_loop():
    while True:
        time.sleep(43200)  # Alle 12 Stunden
        db.backup_to_github()


# --- MAIN START ---
if __name__ == "__main__":
    logging.info("System startet...")

    # Threads starten
    threading.Thread(target=update_blocklist_loop, daemon=True).start()
    threading.Thread(target=dns_server_loop, daemon=True).start()
    threading.Thread(target=backup_loop, daemon=True).start()
    threading.Thread(target=cache_cleanup_loop, daemon=True).start()

    # Web Dashboard (blockiert als Hauptthread)
    try:
        app.run(host="0.0.0.0", port=WEB_PORT, debug=False)
    except Exception as e:
        logging.error(f"Webserver Fehler: {e}")
