# make-you-my-dream-to-be-true.-updstes-follow
Dreams for job who refreers my skills. i hope my long study in not wast... smile read and enjoy

---

## extract_ips.py – IP-Adressen aus /proc/\<pid\>/net/tcp extrahieren

`extract_ips.py` liest alle lokalen und remote IPv4- sowie IPv6-Adressen
aus den Kernel-Dateien `/proc/<pid>/net/tcp` (IPv4) und
`/proc/<pid>/net/tcp6` (IPv6) eines laufenden Prozesses aus.

### Voraussetzungen

- Python 3.6 oder neuer  
- Linux (die `/proc`-Dateien existieren nur dort)

### Verwendung

```bash
# Alle eindeutigen IP-Adressen (ohne 0.0.0.0 / ::) für PID 1234 anzeigen
python3 extract_ips.py 1234

# Auch unspezifizierte Adressen (0.0.0.0, ::) einschließen
python3 extract_ips.py 1234 --include-unspecified
```

Die Ausgabe enthält deduplizierte, sortierte Adressen – IPv4 vor IPv6.

### Optionen

| Option | Beschreibung |
|---|---|
| `pid` | Prozess-ID, deren Netzwerkverbindungen ausgewertet werden sollen |
| `--include-unspecified` | Gibt auch `0.0.0.0` und `::` aus (werden standardmäßig herausgefiltert) |

### Hinweise

- Die IPv4-Hex-Darstellung in `/proc/.../net/tcp` ist little-endian; das Skript berücksichtigt dies korrekt.
- Die IPv6-Darstellung in `/proc/.../net/tcp6` besteht aus vier aufeinanderfolgenden 32-Bit-Little-Endian-Wörtern; auch das wird korrekt geparst.
- Falls `/proc/<pid>/net/tcp` oder `/proc/<pid>/net/tcp6` nicht vorhanden ist (z. B. kein IPv6-Stack oder PID nicht existent), wird die jeweilige Datei stillschweigend übersprungen.
