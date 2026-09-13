# Hausregeln Produktionsplanung

Du bist der Bau-Agent für die Web-App "Produktionsplanung" der Meier Präzisionstechnik AG.
Die App ersetzt das Excel `Produktionsplanung_V7_3.xlsm`.

Du arbeitest immer in einem Branch `agent/<issue-nummer>-<kurzname>` und öffnest einen
Pull Request. Du mergst nie. Du deployst nie. Du änderst diese Datei nie.

## Was diese App ist

Produktionsplanung und Materialdisposition nach Kalenderwoche. Aufträge, Artikel, Stückliste,
Rohmaterial, Lieferanten, Kapazität pro Maschine, Bedarf und Bestellvorschlag.
Die Fachregeln stehen in `docs/regeln.md`. Jede Regel hat eine ID (R-001, R-002, ...).
Wenn du eine Regel umsetzt oder änderst, steht die ID im Code, im Test und im PR.

## Rückfragen (Pflicht)

Bevor du baust, prüfst du den Antrag gegen den bestehenden Code und `docs/regeln.md`.
Kann der Antrag auf zwei Arten umgesetzt werden, die zu unterschiedlichen Ergebnissen führen,
baust du nicht. Du schreibst die Varianten als Kommentar ins Issue, mit Regel-ID und, wenn
möglich, mit der Anzahl Datensätze, die jede Variante heute betrifft. Dann wartest du.
Du baust erst, wenn die antragstellende Person geantwortet hat.

Eine Rückfrage ist kein Scheitern. Ein PR mit einer falschen Annahme ist eines.

## Stack (nichts anderes)

- Python 3.12, Paketverwaltung mit `uv` (`pyproject.toml`, `uv run`, `uv add`)
- FastAPI, SQLAlchemy 2, Pydantic 2
- SQLite in `data/app.db` (Produktion später PostgreSQL, gleiche Modelle)
- Jinja2-Templates, HTMX, Alpine.js für kleine Interaktionen
- Tailwind CSS über CDN mit Inline-Konfiguration in `templates/basis.html`
- Tests: pytest, openpyxl für den Abgleich mit dem Excel
- Betrieb: ein `Dockerfile`, ein `deploy/compose.yml`

Verboten: React, Vue, Svelte, jedes andere JS-Framework, npm, node_modules, ein Build-Schritt.
Neue Python-Pakete nur mit Begründung im PR und Label `neue-abhaengigkeit`.

## Ordner

```
app/
  main.py            FastAPI-App, Router einbinden, sonst nichts
  config.py          Einzige Stelle, die Umgebungsvariablen liest
  auth/              Login, Rollen. Nicht anfassen.
  regeln/            Fachlogik, reine Funktionen, kein DB-Zugriff, eine Datei pro Regelgruppe
  modelle/           SQLAlchemy-Modelle
  routen/            Ein Router pro Seite
  import_excel.py    Liest das Excel in die Datenbank, anonymisiert Kunden
  templates/
    basis.html       Layout, Tailwind-Konfiguration, Design-Tokens
    komponenten/     Jinja-Makros, siehe Abschnitt Oberfläche
    seiten/          Eine Datei pro Seite
  static/
tests/
  regeln/            Ein Test pro Regel, Regel-ID im Dateinamen
  abgleich/          Vergleich gegen die Excel-Referenz. Nie ändern.
  daten/             Anonymisiertes Excel, Referenzwerte als JSON
docs/
  regeln.md          Regelkatalog
  betrieb.md         Start, Stop, Backup, Rollback
deploy/              Nicht anfassen.
```

Du änderst nur Dateien unter `app/`, `tests/regeln/`, `tests/daten/` (nur neue Testfälle),
`docs/`. Du fasst nie an: `deploy/`, `.github/`, `CLAUDE.md`, `app/auth/`, `tests/abgleich/`.
Verlangt eine Aufgabe das, schreibst du es in den PR und stoppst.

## Fachlogik

- Jede Regel ist eine Funktion in `app/regeln/` mit Docstring: Regel-ID, Satz, Beispiel.
- Zeit in Minuten als `int`. Stunden als `Decimal` mit einer Dezimale. Mengen als `int`,
  Rohmaterialmengen als `Decimal` mit einer Dezimale. Geld als `Decimal`. Nie `float`.
- Kalenderwochen immer als Paar (Jahr, ISO-Woche), nie als nackte Zahl. Ausgabe "2026-KW39".
  Das Excel kennt nur die Wochennummer, die App muss den Jahreswechsel richtig machen (R-005).
- Parameter (Rüstzuschlag, Losgrenze, Auslastungsgrenze, Sicherheitsbestand, Horizont) liest
  der Code immer aus der Tabelle `parameter`. Keine festen Zahlen in Formeln.
- Material-Schreibweise ist exakt (R-010). Der Import prüft und meldet Abweichungen, er
  korrigiert nicht still.
- Datum und Zeit als timezone-aware `datetime`, Zeitzone Europe/Zurich.

## Tests (Pflicht)

- Jede Änderung in `app/regeln/` braucht einen Test in `tests/regeln/`. Name enthält die
  Regel-ID: `test_r003_ruestzeit_alu_ueber_500`.
- Testwerte kommen aus `tests/daten/auftraege.json` (anonymisierte echte Aufträge). Erfinde
  keine Zahlen, wenn ein echter Auftrag den Fall abdeckt.
- Ein Test ohne `assert` ist kein Test.
- Ein roter Test, den du nicht geschrieben hast: nicht löschen, nicht skippen, nicht anpassen.
  Im PR beschreiben und stoppen.
- Der Abgleich in `tests/abgleich/` muss grün bleiben. Bei bewusster Regeländerung: PR beschreibt,
  welche Referenzwerte sich ändern und warum. Die Referenz ändert ein Mensch.

## Oberfläche

### Farben und Schrift (Design-Tokens, Quelle: Alpina Connect Vorlage)

In `templates/basis.html` als Tailwind-Konfiguration definiert. Nur diese Namen verwenden.

| Token | Hex | Verwendung |
|-------|-----|------------|
| `navy` | `#030E4F` | Kopfleiste, Seitentitel auf dunklem Grund, Primärknopf |
| `navy-700` | `#0C1A5E` | Karten und Hover auf dunklem Grund |
| `navy-600` | `#2A3670` | Rahmen und Trennlinien auf dunklem Grund |
| `ink` | `#2B3350` | Fliesstext und Überschriften auf hellem Grund |
| `accent` | `#F49F1C` | Genau ein Akzent pro Seite: Kicker über dem Titel, aktiver Tab, Warnung, Primäraktion |
| `cream` | `#F6F5EC` | Karten und Tabellenkopf auf hellem Grund |
| `peach` | `#FAEDE6` | Hervorgehobene Zeile (zum Beispiel überfällig, ausgewählt) |
| `mist` | `#C9CEE0` | Sekundärtext auf dunklem Grund, Rahmen auf hellem Grund |
| `white` | `#FFFFFF` | Seitenhintergrund |

Schrift: Überschriften `Barlow Condensed` (600/700), Text `Inter` (400/600).
Beide liegen lokal in `app/static/fonts/`, kein Aufruf externer Font-Server.
Fallback: `system-ui, sans-serif`.

Regeln:
- Seitenhintergrund weiss, Kopfleiste navy mit weissem Text, Kicker in accent in Grossbuchstaben.
- Keine Hex-Farben in Templates. Nur Token-Klassen (`bg-navy`, `text-ink`, `border-mist`).
- Orange ist ein Akzent, keine Fläche. Nie grosse orange Flächen, nie oranger Fliesstext.
- Status: überfällig = Zeile `bg-peach` mit Text `text-ink`, plus Wort "überfällig". Nie Farbe allein.
- Keine Schatten, keine Verläufe, keine Icons ausser den drei in `static/icons/` (Pfeil, Warnung, Haken).
- Radius: `rounded-md` für Karten und Knöpfe, sonst nichts.
- Abstände: `gap-4` innerhalb, `gap-8` zwischen Blöcken. Seitenrand `px-8 py-6`.

### Komponenten

Jede Seite erbt von `templates/basis.html`. Nutze nur Makros aus `templates/komponenten/`:

`kennzahl` (Wert, Beschriftung, optional Hinweis) · `tabelle` (Spalten, Zeilen, optional Zeilenstatus) ·
`karte` (Titel, Inhalt) · `formular` und `feld` · `knopf` (primär navy, sekundär cream) ·
`hinweis` (info cream, warnung peach) · `leer` (Text, wenn nichts da ist) · `tabs`

Brauchst du ein neues Makro: im PR beschreiben, Label `design-erweiterung`, Abschnitt in
`docs/design.md` ergänzen, Beispiel auf der Seite `/galerie` eintragen.
Keine Tailwind-Klassen ausserhalb der Makros, ausser Layout (`grid`, `flex`, `gap-*`, `p-*`, `m-*`, `w-*`).

### Sprache

Deutsch, Schweizer Schreibweise (ss, nie ß). Fachbegriffe aus dem Excel übernehmen:
Auftrag, Rüstzeit, Bearbeitungszeit, Plan-KW, Liefer-KW, Rohmaterial, Fehl-KW, Bestell-KW,
Gebinde, Auslastung. Keine Anglizismen, wenn es das deutsche Wort gibt. Zahlen mit
Tausendertrennzeichen `'` (1'329), Dezimaltrenner `,` in der Anzeige, `.` im Code.

## Daten

- Keine echten Kunden- oder Preisdaten in Tests, Doku, Commits oder Issue-Kommentaren.
  `tests/daten/` ist anonymisiert. Siehst du echte Daten in einem Issue, verwendest du sie
  nicht und weist im PR darauf hin.
- Konfiguration nur über Umgebungsvariablen, gelesen in `app/config.py`. Keine Secrets im Code.
- Datenbankänderungen nur additiv (neue Tabelle, neue Spalte). Spalte löschen nur mit
  Label `datenverlust` und Hinweis im PR.
- Jede Änderung an einem Auftrag durch einen Benutzer schreibt in `aenderungslog`
  (wer, wann, Feld, alt, neu).

## Doku (Pflicht)

- Neue oder geänderte Regel: `docs/regeln.md` anpassen, gleiche ID wie im Code.
- Neue Seite: `README.md`, Abschnitt Bedienung.
- Neue Umgebungsvariable oder neuer Container: `docs/betrieb.md`.
- PR-Text nach `.github/pull_request_template.md`. Alle Felder füllen. Screenshot bei jeder
  sichtbaren Änderung.

## Befehle

```
uv sync                          Umgebung
uv run fastapi dev app/main.py   lokal starten
uv run pytest                    alle Tests
uv run pytest tests/abgleich     nur Abgleich gegen Excel
uv run ruff check . && uv run ruff format .
uv run python -m app.import_excel tests/daten/Produktionsplanung_demo.xlsm
```

## Wenn du unsicher bist

Stopp. Frage im Issue oder im PR und warte. Lieber ein halber PR mit einer Frage als ein
ganzer PR mit einer Annahme.

## Verboten, immer

- `git push --force`
- Tests löschen oder skippen
- Dateien in `deploy/`, `.github/`, `app/auth/`, `tests/abgleich/` ändern
- Externe Dienste aufrufen, die nicht in `app/config.py` stehen
- Pakete ausserhalb von `pyproject.toml` installieren
- Hex-Farben, externe Fonts, JS-Frameworks
