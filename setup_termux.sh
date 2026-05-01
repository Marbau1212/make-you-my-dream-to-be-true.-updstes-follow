#!/data/data/com.termux/files/usr/bin/bash
# Elite DNS - Termux Setup Script
# Run once to install all prerequisites.

set -e

echo "[1/5] Termux-Pakete aktualisieren..."
pkg update -y && pkg upgrade -y

echo "[2/5] Systempakete installieren (python, sqlite, gh)..."
pkg install -y python sqlite gh

echo "[3/5] Python-Abhängigkeiten installieren..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/5] GitHub CLI anmelden (falls noch nicht geschehen)..."
if ! gh auth status &>/dev/null; then
    gh auth login
fi

echo "[5/5] Port-Weiterleitung 53 -> 5353 einrichten (kein Root nötig)..."
# Termux kann Port 53 nicht direkt binden (< 1024 ohne Root).
# Passe LISTEN_PORT in elite_DNS_AllInOne.py auf 5353 an und leite auf
# dem Router / in der Android-DNS-Einstellung auf <termux-ip>:5353.
echo ""
echo "======================================================"
echo " Setup abgeschlossen!"
echo " Starten:  python elite_DNS_AllInOne.py"
echo " Dashboard: http://<deine-IP>:8080"
echo ""
echo " Hinweis: Port 53 erfordert Root-Zugriff."
echo " Ohne Root setze LISTEN_PORT = 5353 in der Skript-Konfiguration"
echo " und richte dein Gerät so ein, dass es diesen Port als DNS nutzt."
echo "======================================================"
