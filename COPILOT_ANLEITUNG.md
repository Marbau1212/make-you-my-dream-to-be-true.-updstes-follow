# GitHub Copilot Anleitung

## Voraussetzungen
- [x] GitHub CLI (`gh`) ist bereits installiert
- [x] Sie sind bereits angemeldet

## GitHub Copilot mit gh CLI verwenden

### 1. GitHub Copilot installieren

Zunächst müssen Sie die GitHub Copilot Erweiterung für die GitHub CLI installieren:

```bash
gh extension install github/gh-copilot
```

### 2. GitHub Copilot verwenden

Nach der Installation können Sie GitHub Copilot direkt über die Kommandozeile nutzen:

#### Code-Vorschläge erhalten
```bash
gh copilot suggest "wie erstelle ich eine Python-Funktion zum Sortieren einer Liste?"
```

#### Befehle erklären lassen
```bash
gh copilot explain "git rebase -i HEAD~3"
```

### 3. Häufige Anwendungsfälle

#### Shell-Befehle vorschlagen lassen
```bash
gh copilot suggest -t shell "alle Dateien größer als 100MB finden"
```

#### Git-Befehle vorschlagen lassen
```bash
gh copilot suggest -t git "letzten Commit rückgängig machen"
```

#### GitHub CLI-Befehle vorschlagen lassen
```bash
gh copilot suggest -t gh "alle offenen Pull Requests auflisten"
```

### 4. Interaktiver Modus

Sie können GitHub Copilot auch im interaktiven Modus verwenden:

```bash
gh copilot
```

Dies öffnet eine interaktive Sitzung, in der Sie direkt mit Copilot chatten können.

### 5. Nützliche Tipps

- **Präzise Fragen stellen**: Je genauer Ihre Frage, desto besser die Antwort
- **Kontext angeben**: Geben Sie relevante Details zu Ihrem Problem an
- **Verschiedene Befehle ausprobieren**: Nutzen Sie `suggest` für Vorschläge und `explain` für Erklärungen

### 6. Weitere Informationen

Für weitere Hilfe verwenden Sie:
```bash
gh copilot --help
```

Oder besuchen Sie die offizielle Dokumentation: https://docs.github.com/en/copilot/github-copilot-in-the-cli

## GitHub Copilot in Ihrer IDE

Wenn Sie GitHub Copilot in Ihrer Entwicklungsumgebung (wie VS Code, IntelliJ, etc.) nutzen möchten:

1. Installieren Sie die entsprechende Copilot-Erweiterung aus dem Extension Marketplace
2. Melden Sie sich mit Ihrem GitHub-Konto an
3. Copilot wird automatisch Code-Vorschläge machen, während Sie tippen

### VS Code
```bash
# VS Code Copilot Extension installieren
code --install-extension GitHub.copilot
```

## Fehlerbehebung

Falls Probleme auftreten:

```bash
# Status überprüfen
gh auth status

# Erneut anmelden falls nötig
gh auth login

# Extension aktualisieren
gh extension upgrade gh-copilot
```

## Zusammenfassung

Sie können GitHub Copilot jetzt mit diesen einfachen Befehlen nutzen:
- `gh copilot suggest` - Für Vorschläge
- `gh copilot explain` - Für Erklärungen
- `gh copilot` - Für den interaktiven Modus

Viel Erfolg mit GitHub Copilot! 🚀
