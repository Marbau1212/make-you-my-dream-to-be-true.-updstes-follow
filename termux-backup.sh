#!/data/data/com.termux/files/usr/bin/bash
# termux-backup.sh
# Erstellt ein Backup des Termux Home-Verzeichnisses als tar.gz-Archiv.
# Nutzung: bash termux-backup.sh [ZIEL-VERZEICHNIS]
#
# Standardmässig wird das Backup unter /sdcard/termux-backups/ gespeichert.

set -euo pipefail

BACKUP_DIR="${1:-/sdcard/termux-backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
ARCHIVE_NAME="termux-home-backup_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${BACKUP_DIR}/${ARCHIVE_NAME}"

HOME_DIR="${HOME:-/data/data/com.termux/files/home}"

# Zielverzeichnis anlegen falls nicht vorhanden
mkdir -p "${BACKUP_DIR}"

echo "[*] Starte Backup von: ${HOME_DIR}"
echo "[*] Ziel-Archiv:       ${ARCHIVE_PATH}"

tar \
  --exclude="${HOME_DIR}/.cache" \
  -czf "${ARCHIVE_PATH}" \
  -C "$(dirname "${HOME_DIR}")" \
  "$(basename "${HOME_DIR}")"

SIZE="$(du -sh "${ARCHIVE_PATH}" | cut -f1)"
echo "[✓] Backup abgeschlossen: ${ARCHIVE_PATH} (${SIZE})"
