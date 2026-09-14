# Betrieb

## Umgebungsvariablen

Alle Variablen liest `app/config.py`, sonst nichts. Präfix `PP_`.

| Variable | Standard | Zweck |
|----------|----------|-------|
| `PP_DATENBANK_URL` | `sqlite:///<projekt>/data/app.db` | Datenbank. Produktion später PostgreSQL, gleiche Modelle. |
| `PP_EXPORT_PFAD` | `<projekt>/export` | Ablage der Exportdateien (R-036). Im Excel stand der Pfad in den Fachdaten und war an drei Stellen verschieden beschrieben (F-6). |
| `PP_BENUTZER` | `demo` | Platzhalter, bis `app/auth/` steht. Der Name landet im `aenderungslog`. |
| `PP_ZEITZONE` | `Europe/Zurich` | Zeitzone für Datum und Kalenderwoche (R-002). |
| `PP_STARTDATEN_LADEN` | `true` | Lädt beim Start die Demodaten, wenn die Datenbank leer ist. In Produktion auf `false`. |

## Start und Stop

```
uv sync                            Umgebung aufbauen
uv run fastapi dev app/main.py     lokal starten (http://127.0.0.1:8000)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000    im Betrieb
```

Mit Docker:

```
docker build -t produktionsplanung .
docker run -p 8000:8000 -v $PWD/data:/app/data -e PP_STARTDATEN_LADEN=false produktionsplanung
```

Stop: den Container stoppen. Es läuft kein Hintergrundauftrag, der Wochenplan und der
Bedarf werden bei jedem Aufruf neu gerechnet.

## Schriften

`app/static/fonts/` ist beim Aufsetzen mit den vier Schriftdateien zu füllen, siehe
`app/static/fonts/LIESMICH.md`. Fehlen sie, läuft die App weiter und zeigt die
Systemschrift. Es wird nie ein externer Font-Server aufgerufen.

## Daten laden

Aus der Arbeitsmappe:

```
uv run python -m app.import_excel <pfad>/Produktionsplanung_V7_3.xlsm --trocken
uv run python -m app.import_excel <pfad>/Produktionsplanung_V7_3.xlsm
```

Der Trockenlauf schreibt nichts und zeigt den Bericht: gelesene Sätze und alle Meldungen
(unbekannte Materialschreibweise, unbekannte Artikelnummer, unbekannter Status, fehlende
ERP-Nummer). Der Import korrigiert nichts still.

## Sicherung und Rücksprung

Die Sicherung der Arbeitsmappe beim Speichern (R-039) entfällt. An ihre Stelle tritt die
Sicherung der Datenbank.

SQLite:

```
sqlite3 data/app.db ".backup data/sicherung_$(date +%Y%m%d_%H%M).db"
```

Rücksprung: Dienst stoppen, Sicherungsdatei über `data/app.db` kopieren, Dienst starten.

PostgreSQL: `pg_dump` täglich, Rücksprung mit `pg_restore`. Die Modelle sind dieselben.

Vor jedem Rücksprung prüfen, was im `aenderungslog` nach dem Sicherungszeitpunkt steht;
diese Änderungen gehen verloren.

## Änderungslog

Jede Änderung an einem Auftrag und jeder Export schreiben nach `aenderungslog`
(wer, wann, Tabelle, Schlüssel, Feld, alter Wert, neuer Wert). Die Tabelle wird nie
gelöscht. Abfrage:

```
sqlite3 data/app.db "select zeitpunkt, benutzer, schluessel, feld, alt, neu
                     from aenderungslog order by id desc limit 20;"
```

## Was noch fehlt

- `app/auth/` (Anmeldung und Rollen) ist nicht gebaut. Bis dahin steht in jedem
  Protokolleintrag der Wert aus `PP_BENUTZER`.
- `deploy/compose.yml` fehlt. Der Ordner `deploy/` ist für den Bau-Agenten gesperrt
  (Hausregel), die Datei legt ein Mensch an. Das `Dockerfile` liegt im Projektverzeichnis,
  ist aber noch nie gebaut worden: in der Bauumgebung lief kein Docker. Bitte einmal
  `docker build -t produktionsplanung .` laufen lassen, bevor jemand sich darauf verlässt.
- `tests/abgleich/` (Vergleich gegen die Excel-Referenz) fehlt, weil die Arbeitsmappe nicht
  vorlag. Auch dieser Ordner gehört einem Menschen.
