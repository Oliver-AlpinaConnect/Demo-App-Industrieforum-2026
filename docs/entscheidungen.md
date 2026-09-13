# Entscheidungen

`docs/regeln.md` stellt am Schluss zehn offene Fragen (F-1 bis F-10). Die Hausregeln sagen:
Kann ein Antrag auf zwei Arten umgesetzt werden, die zu unterschiedlichen Ergebnissen
führen, wird nicht gebaut, sondern gefragt.

Der Auftrag lautete, die App direkt zu bauen. Deshalb steht hier zu jeder Frage die
getroffene Annahme, was sie im Code bewirkt und wie viele Datensätze sie heute betrifft.
**Jede Zeile mit "bestätigen" muss ein Mensch abnicken, bevor die App produktiv geht.**
Ändert sich eine Antwort, ändert sich genau eine Funktion in `app/regeln/`.

| Nr | Entscheidung | Wirkung im Code | Heute betroffen | Status |
|----|--------------|-----------------|-----------------|--------|
| F-1 | Der Alu-Zuschlag läuft immer über die Parameter, die Losgrenze gilt als "mehr als 500" | `app/regeln/zeiten.py: ruestzeit_minuten` | 1 Auftrag rechnet anders als das Excel: `26-0430` bekommt 90 statt 50 min, Gesamtzeit 38,2 statt 37,5 h | bestätigen |
| F-2 | M3 liest Schichten, Stunden und Tage wie alle anderen aus den Parametern | `app/regeln/kapazitaet.py: wochenkapazitaet_stunden` | 0 (heute gleiches Ergebnis), wirkt erst bei einer Parameteränderung | bestätigen |
| F-3 | Der Vorlauf steht je Priorität in `parameter`: A = 2, B = 1, C = 1 Wochen | `app/regeln/termine.py: plan_kw`, `Parameter.vorlauf` | alle 50 Aufträge, Ergebnis heute unverändert | bestätigen |
| F-4 | Der Horizont ist ein Parameter, alles andere leitet sich daraus ab | `app/regeln/kapazitaet.py: horizont` | Wochenplan und Material vollständig, Standardwert bleibt 8 | entschieden |
| F-5 | Kalenderwochen sind immer (Jahr, ISO-Woche), Differenzen laufen über echte Datumsrechnung | `app/regeln/typen.py: Kalenderwoche` | heute keiner, ab Dezember alle | entschieden |
| F-6 | Der Export-Pfad ist Konfiguration (`PP_EXPORT_PFAD`), kein Fachdatum | `app/config.py` | jeder Export | entschieden |
| F-7 | Ein Auftrag kann auf eine andere als die Standardmaschine umgeplant werden (neues, leeres Feld) | `app/regeln/stammdaten.py: maschine_des_auftrags` | heute 0 von 50 | bestätigen |
| F-8 | Ein Artikel darf beliebig viele Stücklistenpositionen haben | `app/regeln/stammdaten.py`, `app/dienste/planung.py` | 1 Artikel nutzt heute 2 Positionen | bestätigen |
| F-9 | Ein Artikel mit `Aktiv = N` bekommt keine neuen Aufträge, bestehende rechnen weiter | `app/regeln/stammdaten.py: darf_beauftragt_werden` | 1 Artikel (`A-0998`), 0 Aufträge | bestätigen |
| F-10 | Offene Bestellungen zählen weiter ohne Ankunftswoche, genau wie im Excel | `app/regeln/material.py: verfuegbarer_bestand` | 3 Rohmaterialien mit offener Bestellung | **offen**, siehe unten |

## F-10 ist bewusst nicht entschieden

Ein Ankunftsdatum je offener Bestellung wäre eine neue Spalte und eine neue Fachregel: der
verfügbare Bestand würde dann je Woche verschieden gerechnet, und die Fehl-KW käme früher.
Das ist eine fachliche Änderung, keine Ablösung. Die App rechnet deshalb wie das Excel und
schreibt den Hinweis auf die Seite Material. Wer das ändern will, braucht eine neue Regel
mit eigener ID.

## Weitere Abweichungen vom Excel

Diese Punkte stehen im Katalog als Fehler oder Altlast und sind in der App anders gelöst.
Sie brauchen keine Entscheidung, sollen aber nicht untergehen.

| Thema | Excel | App |
|-------|-------|-----|
| Aktuelle KW (R-002) | jede Woche von Hand in `Parameter!B2` und `B4` | kommt aus dem Datum, Zeitzone Europe/Zurich |
| Belastung (R-016) | zweimal umgesetzt: `SUMIFS` bis Zeile 500 und VBA bis zur letzten belegten Zeile | genau eine Funktion |
| Ampel (R-018) | Wochenplan dreistufig, Übersicht nur rot | überall dieselbe Ampel, Farbe nie ohne Wort |
| Verschiebung (R-021) | Makro ändert die Daten und erkennt seine eigenen Änderungen am Bemerkungstext | die App rechnet nur Vorschläge, übernehmen tut sie ein Mensch, nichts wird über das Horizontende geschoben |
| Ausserhalb Horizont (R-020) | nur eine Zahl, "von Hand prüfen" | die Aufträge werden benannt |
| Unbekannte Artikelnummer (R-011) | halbe Zeile mit `??` und `#NV`, wandert in die Summen | Import lehnt die Zeile ab und meldet sie |
| Export ohne Lieferanten-ERP-Nummer (R-033) | Feld bleibt still leer | Zeile wird gemeldet und übersprungen |
| Exportstempel (R-035) | zwei Zeichen des Windows-Benutzernamens, jeder Lauf überschreibt den vorigen | angemeldete Person, jeder Lauf steht im `aenderungslog` |
| Sicherung (R-039) und Montagsablauf (R-040) | im Makro | entfallen, siehe `docs/betrieb.md` |

## Was die Testdaten sind

`tests/daten/` enthält **keine** Daten aus der echten Arbeitsmappe. Die Arbeitsmappe lag
beim Bau nicht vor, nur `docs/regeln.md`. Die Demodaten sind aus den Beispielen des
Katalogs aufgebaut: 50 Aufträge, 21 Artikel, 22 Stücklistenpositionen, 15 Rohmaterialien,
5 Lieferanten, 4 Maschinen. Alle im Katalog genannten Werte stimmen (Rüstzeiten,
Gesamtzeiten, Bedarfsmengen, Fehl-KW, Bestell-KW, Bestellmengen, Kennzahlen der Übersicht).
Kundennamen sind "Kunde 01" bis "Kunde 12", die Preise sind erfunden; der Katalog lässt
beide bewusst weg.

Sobald die echte Arbeitsmappe vorliegt:

1. `uv run python -m app.import_excel <datei> --trocken` und die Meldungen lesen.
2. Referenzwerte für `tests/abgleich/` aus der Mappe ziehen. Diesen Ordner legt ein Mensch
   an, der Bau-Agent fasst ihn nicht an (Hausregel).
3. Die Zeilen "bestätigen" in der Tabelle oben abarbeiten.
