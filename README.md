# Produktionsplanung

Web-App der Meier Präzisionstechnik AG für Produktionsplanung und Materialdisposition nach
Kalenderwoche. Sie ersetzt die Arbeitsmappe `Produktionsplanung_V7_3.xlsm`.

Die Fachregeln stehen in [`docs/regeln.md`](docs/regeln.md). Jede Regel hat eine ID
(R-001 bis R-040) und steht mit dieser ID im Code (`app/regeln/`) und im Test
(`tests/regeln/`). Die Seite **Regeln** zeigt den Katalog in der App.

## Start

```
uv sync
uv run fastapi dev app/main.py
```

Die App läuft auf http://127.0.0.1:8000. Beim ersten Start füllt sie eine leere Datenbank
mit den Demodaten aus `tests/daten/` und schiebt sie auf die aktuelle Woche, damit der
Planungshorizont voll ist.

## Bedienung

### Wochenübersicht (`/`)

Die Kennzahlen des Blattes `Übersicht` (R-038): offene Aufträge, davon in Arbeit, davon
überfällig, Aufträge in der aktuellen KW, Aufträge ausserhalb des Horizonts,
Bestellpositionen und Bestellwert dieser Woche, davon überfällig. Dazu die Auslastung
jeder Maschine in der aktuellen Woche und drei Listen: überfällige Aufträge (R-009),
Aufträge ausserhalb des Horizonts (R-020) und der Bestellvorschlag (R-029).

Anders als im Excel werden die Aufträge ausserhalb des Horizonts benannt, nicht nur gezählt.

### Aufträge (`/auftraege`)

Alle Aufträge mit Rüstzeit (R-003), Bearbeitungs- und Gesamtzeit (R-004), Liefer-KW
(R-005), Plan-KW (R-006) und KW eff. (R-007). Filter nach Status, Maschine, Woche und
Suche über Auftrag, Artikel und Kunde. Überfällige Aufträge stehen auf `bg-peach` und
tragen das Wort "überfällig".

Zwei Änderungen sind möglich:

- **erledigt**: setzt den Status und ergänzt die Bemerkung um "erledigt TT.MM." (R-037).
- **Woche von Hand setzen**: trägt eine manuelle KW im Format `2026-KW39` ein. Ein leeres
  Feld heisst, die Plan-KW gilt wieder (R-007).

Beides schreibt nach `aenderungslog` (wer, wann, Feld, alt, neu).

### Wochenplan (`/wochenplan`)

Belastung, Kapazität und Auslastung je Maschine über den Horizont (R-014 bis R-019).
Die Wartungswoche ist gekennzeichnet und um den Wartungsabzug gekürzt (R-015). Eine Zelle
über der Auslastungsgrenze ist `bg-peach` und trägt das Wort "über Grenze".

Darunter die Verschiebevorschläge (R-021): welcher Auftrag aus einer überlasteten Woche in
die Folgewoche gehört. Die App verschiebt nie von selbst. Der Knopf "Vorschläge als
manuelle KW übernehmen" setzt sie als manuelle Woche und schreibt Bemerkung und
Änderungslog. Priorität A und Aufträge in Arbeit werden nie verschoben, und nichts wird
über das Horizontende hinausgeschoben.

Ganz unten stehen die Aufträge je Maschine und Woche.

### Material (`/material`)

Bedarf je Rohmaterial und Woche (R-022), Summe und Durchschnitt über den Horizont (R-024),
Bestand und verfügbarer Bestand (R-023), Sicherheitsbestand (R-025), Fehl-KW (R-027),
Bestell-KW mit Lieferantenpuffer (R-028), Bestellmenge auf Gebinde (R-030), Bestellwert
(R-031) und Bedarfsdatum (R-032).

Der Knopf **CSV herunterladen** schreibt den Bestellvorschlag für Abacus: Semikolon
getrennt, ANSI, Datum TT.MM.JJJJ, Dateiname `PLAN_BESTELL_JJJJMMTT_KW<n>.csv`
(R-033 bis R-036). Positionen ohne ERP-Nummer werden gemeldet und übersprungen.

### Regeln (`/regeln`)

Der Regelkatalog: je Regel die ID, der Titel, der Status aus dem Excel und die Stelle im
Code. Darunter `docs/regeln.md` im Volltext.

### Galerie (`/galerie`)

Ein Beispiel je Baustein der Oberfläche, siehe [`docs/design.md`](docs/design.md).

## Aufbau

```
app/
  main.py            FastAPI-App, bindet die Router ein
  config.py          liest als einzige Stelle die Umgebungsvariablen
  datenbank.py       Verbindung und Sitzungen
  startdaten.py      lädt tests/daten/ in eine leere Datenbank
  import_excel.py    liest die Arbeitsmappe, anonymisiert Kunden, meldet Abweichungen
  regeln/            Fachlogik als reine Funktionen, kein Datenbankzugriff
  modelle/           SQLAlchemy-Modelle
  dienste/           Brücke: Daten laden, Regeln aufrufen, Sichten liefern
  routen/            ein Router pro Seite
  templates/         basis.html, komponenten/, seiten/
tests/
  regeln/            ein Test je Regel, Regel-ID im Dateinamen
  seiten/            Seiten und Export
  daten/             anonymisierte Demodaten
docs/                regeln.md, design.md, entscheidungen.md, betrieb.md
```

Die Schicht `app/dienste/` steht nicht in der Ordnerliste der Hausregeln. Sie ist nötig,
weil `app/regeln/` keine Datenbank kennen darf: die Dienste laden Zeilen, bauen Werttypen
und rufen die Regeln in der richtigen Reihenfolge auf.

## Befehle

```
uv sync                          Umgebung
uv run fastapi dev app/main.py   lokal starten
uv run pytest                    alle Tests
uv run ruff check . && uv run ruff format .
uv run python -m app.import_excel <datei>.xlsm [--trocken]
```

## Offene Punkte

`docs/regeln.md` stellt zehn Fragen, die vor dem Bau zu klären wären. Sie sind mit
festgehaltenen Annahmen umgesetzt; jede Annahme steht mit ihrer Wirkung in
[`docs/entscheidungen.md`](docs/entscheidungen.md). Die dort mit "bestätigen" markierten
Zeilen braucht es, bevor die App produktiv geht. Betrieb, Sicherung und Rücksprung stehen
in [`docs/betrieb.md`](docs/betrieb.md).
