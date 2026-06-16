#!/data/data/com.termux/files/usr/bin/bash
# termux-backup.sh
# Erstellt ein vollständiges Backup des Termux-Home-Verzeichnisses
# Nutzung: bash termux-backup.sh [ziel-verzeichnis]
# Beispiel: bash termux-backup.sh /sdcard/termux-backups

set -euo pipefail

# --- Konfiguration ---
BACKUP_DIR="${1:-/sdcard/termux-backups}"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
BACKUP_FILE="${BACKUP_DIR}/termux-home_${TIMESTAMP}.tar.gz"
PREFIX_BACKUP="${BACKUP_DIR}/termux-prefix_${TIMESTAMP}.tar.gz"

# --- Farben ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()    { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# --- Speicherzugriff prüfen ---
if [ ! -d "/sdcard" ]; then
    warn "Kein Zugriff auf /sdcard. Bitte 'termux-setup-storage' ausführen."
    warn "Alternativ ein anderes Zielverzeichnis angeben: bash termux-backup.sh /data/data/com.termux/files/home/backup"
fi

# --- Zielverzeichnis erstellen ---
mkdir -p "${BACKUP_DIR}" || { error "Zielverzeichnis konnte nicht erstellt werden: ${BACKUP_DIR}"; exit 1; }

info "Starte Termux-Backup..."
info "Zielverzeichnis: ${BACKUP_DIR}"
echo ""

# --- Home-Verzeichnis sichern (~) ---
info "Sichere Home-Verzeichnis (~) ..."
tar \
    --exclude="${HOME}/backup" \
    --exclude="${HOME}/.cache" \
    -czf "${BACKUP_FILE}" \
    -C "$(dirname "$HOME")" \
    "$(basename "$HOME")" \
    2>/dev/null || { error "Backup des Home-Verzeichnisses fehlgeschlagen."; exit 1; }

BACKUP_SIZE="$(du -sh "${BACKUP_FILE}" | cut -f1)"
info "Home-Backup erstellt: ${BACKUP_FILE} (${BACKUP_SIZE})"

# --- Prefix sichern ($PREFIX) ---
PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
if [ -d "${PREFIX}" ]; then
    info "Sichere Termux-Prefix (installierte Pakete) ..."
    tar \
        --exclude="${PREFIX}/tmp" \
        -czf "${PREFIX_BACKUP}" \
        -C "$(dirname "$PREFIX")" \
        "$(basename "$PREFIX")" \
        2>/dev/null || { warn "Prefix-Backup fehlgeschlagen (ggf. fehlende Berechtigungen)."; }

    if [ -f "${PREFIX_BACKUP}" ]; then
        PREFIX_SIZE="$(du -sh "${PREFIX_BACKUP}" | cut -f1)"
        info "Prefix-Backup erstellt: ${PREFIX_BACKUP} (${PREFIX_SIZE})"
    fi
else
    warn "Termux-Prefix nicht gefunden unter: ${PREFIX}"
fi

echo ""
info "Backup abgeschlossen."
info "Dateien:"
echo "  Home    : ${BACKUP_FILE}"
[ -f "${PREFIX_BACKUP}" ] && echo "  Prefix  : ${PREFIX_BACKUP}"

# --- Wiederherstellung ---
echo ""
echo "-----------------------------------------------------------"
echo "Wiederherstellung (Restore):"
echo "  Home   : tar -xzf ${BACKUP_FILE} -C \$(dirname \"\$HOME\")"
echo "  Prefix : tar -xzf ${PREFIX_BACKUP} -C \$(dirname \"\$PREFIX\")"
echo "-----------------------------------------------------------"
