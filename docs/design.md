# Design

Quelle der Farben und Schriften ist die Alpina Connect Vorlage, festgehalten in `CLAUDE.md`.
Die Tokens stehen als Tailwind-Konfiguration in `app/templates/basis.html`. Jedes Beispiel
dieser Seite ist unter `/galerie` zu sehen.

## Tokens

| Token | Hex | Verwendung |
|-------|-----|------------|
| `navy` | `#030E4F` | Kopfleiste, Primärknopf |
| `navy-700` | `#0C1A5E` | Karten auf dunklem Grund |
| `navy-600` | `#2A3670` | Rahmen und Trennlinien auf dunklem Grund |
| `ink` | `#2B3350` | Fliesstext und Überschriften auf hellem Grund |
| `accent` | `#F49F1C` | ein Akzent pro Seite: Kicker, aktiver Tab |
| `cream` | `#F6F5EC` | Karten, Tabellenkopf, Hinweis (info) |
| `peach` | `#FAEDE6` | hervorgehobene Zeile, Hinweis (warnung) |
| `mist` | `#C9CEE0` | Sekundärtext auf dunklem Grund, Rahmen auf hellem Grund |
| `white` | `#FFFFFF` | Seitenhintergrund |

Schrift: Überschriften `Barlow Condensed` (600/700), Text `Inter` (400/600). Beide liegen
lokal in `app/static/fonts/`, es wird kein externer Font-Server aufgerufen. Fehlen die
Dateien, greift `system-ui, sans-serif` (siehe `app/static/fonts/LIESMICH.md`).

Regeln: keine Hex-Farben in den Seiten, nur Token-Klassen. Orange ist ein Akzent, keine
Fläche. Keine Schatten, keine Verläufe. Radius `rounded-md`. Abstände `gap-4` innerhalb,
`gap-8` zwischen Blöcken, Seitenrand `px-8 py-6`.

## Farbe steht nie allein

Status wird immer mit einem Wort gezeigt, nicht nur mit einer Farbe:

- Überfälliger Auftrag: Zeile `bg-peach`, Text `text-ink`, dazu das Wort "überfällig".
- Auslastung über der Grenze: Zelle `bg-peach`, Wert fett, dazu das Wort "über Grenze".
- Bestellposition: "ja", "ja, überfällig" oder "nein" als Text.

Die Ampelwörter stehen in `app/dienste/anzeige.py`: `über Grenze`, `hoch`, `frei`, `normal`.

## Makros

Alle in `app/templates/komponenten/makros.html`. Tailwind-Klassen stehen nur dort; in den
Seiten nur Layout (`grid`, `flex`, `gap-*`, `p-*`, `m-*`, `w-*`).

| Makro | Aufruf | Zweck |
|-------|--------|-------|
| `kennzahl` | `k.kennzahl(wert, beschriftung, hinweis="")` | eine Zahl mit Beschriftung |
| `karte` | `{% call k.karte("Titel") %}…{% endcall %}` | Abschnitt mit Titelleiste |
| `tabelle` | `k.tabelle(spalten, zeilen, leertext)` | Datentabelle mit Zeilenstatus |
| `knopf` | `k.knopf(text, art, ziel, typ, name, wert)` | primär (navy) oder sekundär (cream) |
| `hinweis` | `k.hinweis(text, art)` | `info` (cream) oder `warnung` (peach) |
| `leer` | `k.leer(text)` | Text, wenn nichts da ist |
| `formular` | `{% call k.formular(aktion, verfahren) %}…{% endcall %}` | Formularrahmen |
| `feld` | `k.feld(name, beschriftung, wert, auswahl, typ)` | Eingabe oder Auswahlliste |
| `tabs` | `k.tabs(eintraege, aktiv)` | Reiter innerhalb einer Seite |
| `ampelzelle` | `k.ampelzelle(wert_text, stufe, wort)` | Auslastung mit Wort (R-018) |

### tabelle

`spalten` ist eine Liste von Beschriftungen oder von `{titel, rechts, umbruch}`:

- `rechts: true` für Zahlenspalten (rechtsbündig),
- `umbruch: true` für lange Texte; ohne das bleibt eine Zelle einzeilig, damit die Zeilen
  in breiten Planungstabellen gleich hoch bleiben.

`zeilen` ist eine Liste von `{zellen: [...], status: "", titel: ""}`. `status`
`"ueberfaellig"` oder `"ausgewaehlt"` färbt die Zeile `bg-peach`; das Wort gehört in eine
Zelle, die Farbe allein sagt nichts.

## Ein neues Makro

1. Makro in `app/templates/komponenten/makros.html` ergänzen.
2. Abschnitt in dieser Datei ergänzen.
3. Beispiel in `app/templates/seiten/galerie.html` eintragen.
4. Im PR beschreiben, Label `design-erweiterung`.
