# SAS Log Scanner

Ein Python-Skript zum automatisierten Durchsuchen von SAS-Logdateien nach konfigurierbaren Fehlerstichwörtern. Alle Einstellungen werden über eine zentrale JSON-Konfigurationsdatei gesteuert.

---

## Features

- **Konfigurierbare Scan-Verzeichnisse** — beliebig viele Pfade in der Config angeben
- **Frei definierbare Stichwörter** — z. B. `ERROR`, `WARNING`, `Invalid data`
- **Case-sensitive Suche** — Groß-/Kleinschreibung wird exakt beachtet
- **Kommentar-Ignorierung** — Treffer innerhalb von `/* ... */` Blöcken (auch mehrzeilig) werden übersprungen
- **Tagesbasierter Filter** — es werden nur Dateien gescannt, deren letzte Änderung zwischen 00:00 Uhr und dem Ausführungszeitpunkt des aktuellen Tages liegt
- **Kontext-Ausgabe** — je Treffer werden die N folgenden Zeilen mit ausgegeben (konfigurierbar)
- **Timestamped Report** — der Bericht wird als `.txt`-Datei mit Zeitstempel im Dateinamen gespeichert

---

## Voraussetzungen

- Python 3.10 oder neuer
- Keine zusätzlichen Bibliotheken erforderlich (nur Python-Standardbibliothek)

---

## Verwendung

```bash
# Standard: config.json im selben Verzeichnis wie das Skript
python logscanner.py

# Alternativ: expliziter Pfad zur Konfigurationsdatei
python logscanner.py C:\Pfad\zur\config.json
```

---

## Konfigurationsdatei (`config.json`)

```json
{
  "scan_directories": [
    "C:\\SAS\\Logs",
    "C:\\Programme\\SAS\\Logs"
  ],
  "output_directory": "C:\\Ausgabe\\Logscanner",
  "keywords": [
    "ERROR",
    "WARNING",
    "Invalid data",
    "Uninitialized"
  ],
  "file_extensions": [".log", ".lst", ".txt"],
  "context_lines_after": 3
}
```

| Parameter | Beschreibung |
|---|---|
| `scan_directories` | Liste der Verzeichnisse, die rekursiv durchsucht werden |
| `output_directory` | Zielordner für den generierten Bericht |
| `keywords` | Stichwörter, nach denen gesucht wird (case-sensitive) |
| `file_extensions` | Dateiendungen, die berücksichtigt werden sollen |
| `context_lines_after` | Anzahl der Zeilen, die nach einem Treffer mit ausgegeben werden |

---

## Ausgabe

Der Bericht wird unter folgendem Namensschema gespeichert:

```
<output_directory>\logscan_YYYYMMDD_HHMMSS.txt
```

**Beispielinhalt:**

```
SAS Log Scanner — Ausführung: 12.06.2026 08:30:00
================================================================================

================================================================================
Datei: C:\SAS\Logs\job_abrechnung.log
================================================================================

  Zeile 142 [ERROR]:
  ERROR: Variable BETRAG not found in dataset.
  NOTE: SAS went to a new line when INPUT statement reached past the end of a line.
  NOTE: Missing values were generated as a result of performing an operation.
  WARNING: Numeric values have been converted to character values.

Gesamt Treffer: 1
```

---

## Kommentar-Ignorierung

Stichwörter, die innerhalb eines SAS-Kommentarblocks stehen, werden **nicht** als Treffer gewertet:

```sas
/* ERROR: Dieser Kommentar wird ignoriert */
ERROR: Diese Zeile wird als Treffer erkannt
```

Mehrzeilige Kommentarblöcke werden vollständig übersprungen. Im Bericht erscheint trotzdem immer die **Originalzeile** aus der Logdatei.

---

## Lizenz

Internes Tool — adesso Group / Rheinenergie
