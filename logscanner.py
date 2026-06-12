#!/usr/bin/env python3
"""SAS Log Scanner — scannt Log-Dateien nach konfigurierbaren Stichworten."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def remove_comments(lines: list[str]) -> list[str]:
    """Ersetzt den Inhalt von /* ... */ Kommentaren durch Leerzeichen.
    Mehrzeilige Kommentare werden vollständig bereinigt.
    Die Zeilennummern bleiben dabei erhalten (keine Zeilen werden entfernt).
    """
    result = []
    in_comment = False
    for line in lines:
        cleaned = []
        i = 0
        while i < len(line):
            if not in_comment:
                if line[i:i+2] == "/*":
                    in_comment = True
                    cleaned.append("  ")  # Platzhalter, damit Zeilenlänge grob stimmt
                    i += 2
                else:
                    cleaned.append(line[i])
                    i += 1
            else:
                if line[i:i+2] == "*/":
                    in_comment = False
                    i += 2
                else:
                    # Kommentarinhalt unsichtbar machen, Zeilenumbruch behalten
                    if line[i] == "\n":
                        cleaned.append("\n")
                    i += 1
        result.append("".join(cleaned))
    return result


def scan_file(filepath: Path, keywords: list[str], context_lines: int) -> list[dict]:
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        return [{"error": str(e), "filepath": str(filepath)}]

    # Kommentarblöcke aus der Suchkopie entfernen; Originalzeilen bleiben für die Ausgabe
    search_lines = remove_comments(lines)

    for i, search_line in enumerate(search_lines):
        for keyword in keywords:
            if keyword in search_line:
                after = lines[i + 1 : i + 1 + context_lines]
                findings.append({
                    "filepath": str(filepath),
                    "line_number": i + 1,
                    "keyword": keyword,
                    "match_line": lines[i].rstrip("\n"),   # Originalzeile ausgeben
                    "context": [l.rstrip("\n") for l in after],
                })
                break  # nur ein Treffer pro Zeile
    return findings


def scan_directories(
    directories: list[str],
    extensions: list[str],
    keywords: list[str],
    context_lines: int,
    run_time: datetime,
) -> list[dict]:
    all_findings = []
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"  [WARNUNG] Verzeichnis nicht gefunden: {directory}", file=sys.stderr)
            continue
        for ext in extensions:
            for filepath in dir_path.rglob(f"*{ext}"):
                try:
                    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                except OSError:
                    continue
                # nur Dateien die heute (ab 0 Uhr) bis zum Ausführungszeitpunkt geändert wurden
                start_of_day = run_time.replace(hour=0, minute=0, second=0, microsecond=0)
                if start_of_day <= mtime <= run_time:
                    findings = scan_file(filepath, keywords, context_lines)
                    all_findings.extend(findings)
    return all_findings


def write_report(findings: list[dict], output_dir: str, run_time: datetime) -> str:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    timestamp = run_time.strftime("%Y%m%d_%H%M%S")
    report_file = out_path / f"logscan_{timestamp}.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"SAS Log Scanner — Ausführung: {run_time.strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        if not findings:
            f.write("Keine Treffer gefunden.\n")
        else:
            current_file = None
            for entry in findings:
                if "error" in entry:
                    f.write(f"[LESEFEHLER] {entry['filepath']}: {entry['error']}\n\n")
                    continue

                if entry["filepath"] != current_file:
                    current_file = entry["filepath"]
                    f.write(f"\n{'='*80}\n")
                    f.write(f"Datei: {current_file}\n")
                    f.write(f"{'='*80}\n")

                f.write(f"\n  Zeile {entry['line_number']} [{entry['keyword']}]:\n")
                f.write(f"  {entry['match_line']}\n")
                for ctx_line in entry["context"]:
                    f.write(f"  {ctx_line}\n")

        f.write(f"\n\n{'='*80}\n")
        f.write(f"Gesamt Treffer: {sum(1 for e in findings if 'error' not in e)}\n")

    return str(report_file)


def main():
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.json"

    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])

    if not config_path.exists():
        print(f"Konfigurationsdatei nicht gefunden: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)
    run_time = datetime.now()

    print(f"SAS Log Scanner gestartet: {run_time.strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"Suche nach: {', '.join(config['keywords'])}")
    print(f"Verzeichnisse: {len(config['scan_directories'])}")

    findings = scan_directories(
        directories=config["scan_directories"],
        extensions=config.get("file_extensions", [".log"]),
        keywords=config["keywords"],
        context_lines=config.get("context_lines_after", 3),
        run_time=run_time,
    )

    report_path = write_report(findings, config["output_directory"], run_time)
    hit_count = sum(1 for e in findings if "error" not in e)
    print(f"\nFertig. {hit_count} Treffer gefunden.")
    print(f"Bericht: {report_path}")


if __name__ == "__main__":
    main()
