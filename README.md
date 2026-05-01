# 🛡️ Elite DNS Server — Termux Edition

A full-featured, all-in-one DNS server built in Python, designed to run on Android via **Termux**.

## Features

| Feature | Details |
|---|---|
| **DNS Blocking** | Auto-downloads the [StevenBlack hosts list](https://github.com/StevenBlack/hosts) (~200k domains) |
| **DNS Forwarding** | Forwards clean queries to Cloudflare `1.1.1.1` |
| **In-memory Cache** | Caches responses for 60 s to reduce upstream latency |
| **SQLite Logging** | Logs every query (client IP, domain, status) to `dns_history.db` |
| **Web Dashboard** | Dark-mode dashboard with charts at `http://<ip>:8080` |
| **REST API** | `/api/stats` and `/api/recent` JSON endpoints |
| **GitHub Backup** | Dumps the SQLite DB to a private GitHub Gist every 12 hours via `gh` CLI |
| **Auto-install** | Missing pip packages are installed automatically on first run |

## Quick Start (Termux)

```bash
# 1. Clone the repo
git clone https://github.com/Marbau1212/make-you-my-dream-to-be-true.-updstes-follow
cd make-you-my-dream-to-be-true.-updstes-follow

# 2. Run the setup script (installs all dependencies)
bash setup_termux.sh

# 3. Start the DNS server
python elite_DNS_AllInOne.py
```

## Port 53 & Termux

Android restricts binding to ports below 1024 without root.

**Option A – With root (tsu):**
```bash
tsu -c "python elite_DNS_AllInOne.py"
```

**Option B – Without root:**  
Change `LISTEN_PORT = 53` → `LISTEN_PORT = 5353` in `elite_DNS_AllInOne.py`, then point your router or Android private DNS setting to `<termux-ip>:5353`.

## Configuration

Edit the `# --- KONFIGURATION ---` block at the top of `elite_DNS_AllInOne.py`:

| Variable | Default | Description |
|---|---|---|
| `LISTEN_PORT` | `53` | UDP port for DNS |
| `WEB_PORT` | `8080` | Flask dashboard port |
| `FORWARDER_IP` | `1.1.1.1` | Upstream DNS resolver |
| `BLOCKLIST_URL` | StevenBlack hosts | URL of the blocklist |

## Files

```
elite_DNS_AllInOne.py   # Main server script
requirements.txt        # Python dependencies
setup_termux.sh         # One-time Termux setup
dns_history.db          # SQLite query log (auto-created, git-ignored)
dns_system.log          # Text log (auto-created, git-ignored)
```

## Dashboard

Open `http://<your-termux-ip>:8080` in any browser on the same network.

![Dashboard preview — dark mode with stats cards, bar chart, and query table]

## API

```
GET /api/stats   → { "total": N, "blocked": N, "blocklist_size": N, "cache_size": N }
GET /api/recent  → [ { "time": "HH:MM:SS", "client": "ip", "domain": "...", "status": "..." }, … ]
```
