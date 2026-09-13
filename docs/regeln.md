# Regelkatalog Produktionsplanung

Quelle: `Produktionsplanung_V7_3.xlsm` (Version "V7.3 / BH / 03.2024", Stand der Datei
13.09.2026). Der Katalog ist aus dem Excel gelesen: alle 13 Blätter (inkl. dem versteckten
Blatt `Planung_2021_alt`), alle Formeln, alle 23 Zellkommentare, alle bedingten
Formatierungen (auch die, die nur im Roh-XML als x14-Erweiterung stehen) und alle
VBA-Module (`ThisWorkbook`, `Modul_ERP`, `Modul_Planung`, `Modul1`).

Jede Regel hat eine ID. Die ID steht später im Code (`app/regeln/`), im Test
(`tests/regeln/`) und im PR. Änderungen an einer Regel ändern diese Datei mit.

## Wie der Katalog zu lesen ist

Jede Regel hat: **Regel** (ein Satz), **Quelle** (Blatt und Zelle oder VBA-Prozedur),
**Beispiel** (Werte aus der Datei) und **Status**.

| Status | Bedeutung |
|--------|-----------|
| `aktiv` | Regel wird im Excel so gerechnet, überall gleich. |
| `aktiv, uneinheitlich` | Regel wird gerechnet, aber im Excel an mindestens zwei Orten unterschiedlich. Siehe Hinweis bei der Regel. |
| `manuell` | Keine Formel. Ein Mensch pflegt den Wert von Hand. |
| `veraltet` | Steht noch in der Datei, wird aber nicht mehr gerechnet. |
| `offen` | Vor dem Bau ist eine Entscheidung nötig. Siehe Abschnitt "Offene Fragen". |

Die Beispiele nennen Auftragsnummern, Artikelnummern, Rohmaterialnummern, Mengen, Zeiten
und Kalenderwochen aus der Datei. Kundennamen und Preise sind bewusst weggelassen, statt
dessen steht die Zelle (Hausregel: keine echten Kunden- oder Preisdaten in der Doku).

Die Datei kennt in den Blättern nur die nackte Wochennummer. Dieser Katalog schreibt das
Jahr dazu, wo es für das Verständnis nötig ist. Die App führt Kalenderwochen immer als Paar
(Jahr, ISO-Woche), siehe R-005.

## Blätter im Excel

| Blatt | Sichtbar | Inhalt | Zeilen mit Daten |
|-------|----------|--------|------------------|
| `Übersicht` | ja | Kennzahlen, Makroliste, Ablaufbeschreibung | A1:G23 |
| `Parameter` | ja | Alle Stellschrauben, Änderungsprotokoll | A1:C26 |
| `Lieferanten` | ja | 5 Lieferanten | 2-6 |
| `Rohmaterial` | ja | 15 Rohmaterialien | 2-16 |
| `Artikel` | ja | 21 Artikel (20 aktiv, 1 inaktiv) | 2-22 |
| `Stückliste` | ja | 22 Positionen zu 21 Artikeln | 2-23 |
| `Kapazität` | ja | 4 Maschinen | 2-5 |
| `Aufträge` | ja | 50 Aufträge, 22 Spalten | 4-53 |
| `Wochenplan` | ja | Belastung, Kapazität, Auslastung je Maschine und KW | 3-25 |
| `Bedarf` | ja | Bedarf und Bestellvorschlag je Rohmaterial | 3-20 |
| `ERP_Export` | ja | Ergebnis des letzten Exports (5 Positionen) | 1-6 |
| `Planung_2021_alt` | **nein** | Alte Planung von 2021 | 1-8 |
| `Tabelle3` | ja | Testrest, 2 Zellen | 3-4 |

---

# 1. Grundlagen und Parameter

## R-001 Alle Stellschrauben stehen im Blatt Parameter

**Regel:** Sicherheitsbestand, Auslastungsgrenze, Rüstzuschlag, Losgrenze, Horizont,
Wartungsabzug, Puffer und Kostenstelle stehen als einzelne Werte im Blatt `Parameter` und
werden von den Formeln von dort gelesen, nicht als Zahl in die Formel geschrieben.

**Quelle:** `Parameter!A2:B18`

| Zelle | Bezeichnung | Wert |
|-------|-------------|------|
| `B2` | Aktuelle KW | 39 |
| `B3` | Jahr | 2026 |
| `B4` | Montag aktuelle KW | 21.09.2026 |
| `B5` | Sicherheitsbestand % | 10 % |
| `B6` | Auslastungsgrenze | 90 % |
| `B7` | Rüstzuschlag Alu (min) | 40 |
| `B8` | Losgrenze Alu (Stk) | 500 |
| `B9` | Schichten pro Tag | 2 |
| `B10` | Std pro Schicht | 8,0 |
| `B11` | Puffer Lieferant C (Wochen) | 1 |
| `B12` | Arbeitstage pro Woche | 5 |
| `B13` | Export-Pfad | Pfad im Dateisystem |
| `B14` | Kostenstelle Einkauf | 4100 |
| `B15` | Planungshorizont (Wochen) | 8 |
| `B16` | Wartungsabzug (h) | 16 |
| `B17` | Zuschlag Edelstahl (min) | 20 (veraltet, siehe Abschnitt 9) |
| `B18` | Vorlauf Prio A (Wochen) | 2 (nicht verlinkt, siehe R-006) |

**Beispiel:** `Kapazität!C2` liest `=Parameter!$B$9` und ergibt 2 Schichten.

**Status:** `aktiv, uneinheitlich`

**Hinweis:** Der Grundsatz wird im Excel nicht durchgehalten. An diesen Stellen steht eine
feste Zahl statt der Parameterzelle:

- `Aufträge!K24:K53`: `500` und `40` fest statt `Parameter!$B$8` und `$B$7` (R-003).
- `Kapazität!C4:E4` (Maschine M3): `2`, `8`, `5` fest statt `Parameter!$B$9`, `$B$10`, `$B$12` (R-014).
- `Bedarf!P4:P18`: `=L4/8`, die `8` ist der Horizont aus `Parameter!$B$15` (R-024).
- `Aufträge!N4:N53`: `IF(C4="A",2,1)`, die `2` ist der Vorlauf aus `Parameter!$B$18` (R-006).
- `Wochenplan!B3:I3`, `B10:I10`, `B17:I17` und `Bedarf!D3:K3`: die acht Wochennummern
  39 bis 46 sind als Zahl eingetippt, nicht aus `Parameter!$B$2` gerechnet (R-019).

## R-002 Aktuelle KW und Montagsdatum werden von Hand gesetzt

**Regel:** Die aktuelle Kalenderwoche und das Datum des zugehörigen Montags werden jede
Woche von Hand im Blatt `Parameter` nachgetragen; es gibt keine Ableitung aus dem
Systemdatum.

**Quelle:** `Parameter!B2` und `Parameter!B4`, Kommentare dazu, `ThisWorkbook.Workbook_Open`

**Beispiel:** `B2` = 39, `B4` = 21.09.2026. Der 21.09.2026 ist der Montag der ISO-Woche 39
von 2026. Kommentar auf `B2`: "Jeden Montag anpassen!! Sonst stimmt der Export nicht."
Kommentar auf `B4`: "Muss zur KW passen (Montag). Kein Automatismus, weil Jahreswechsel
Probleme macht." `Workbook_Open` zeigt montags eine Meldung mit der eingestellten KW.

**Status:** `manuell`

**Hinweis:** In der App entfällt diese Regel. Die aktuelle Woche ergibt sich aus dem Datum
(Zeitzone Europe/Zurich) als Paar (Jahr, ISO-Woche), das Montagsdatum daraus. Dass es im
Excel manuell ist, erklärt die Jahreswechsel-Probleme in R-005 und R-032.

---

# 2. Auftrag: Zeiten

## R-003 Rüstzeit je Auftrag, mit Zuschlag für Alu über der Losgrenze

**Regel:** Die Rüstzeit eines Auftrags ist die Rüstzeit-Basis des Artikels, plus der
Rüstzuschlag Alu (`Parameter!B7` = 40 min), wenn das Material des Artikels genau `Alu`
heisst **und** die Auftragsmenge grösser als die Losgrenze (`Parameter!B8` = 500 Stk) ist.

**Quelle:** `Aufträge!K4:K53`, Kommentar auf `Aufträge!K3` ("Basis aus Artikel + 40 min
wenn Alu und mehr als 500 Stk (Werkzeugwechsel Spannfutter)"), `Artikel!F`,
`Parameter!B7`, `Parameter!B8`

Formel (Zeilen 4 bis 23):

```
=VLOOKUP($D4,Artikel!$A$2:$H$60,6,0)+IF(AND(H4="Alu",E4>Parameter!$B$8),Parameter!$B$7,0)
```

**Beispiel:** Auftrag `26-0414`, Artikel `A-1005` (Flansch DN50 Alu), Menge 620 Stk.
Rüstzeit-Basis `Artikel!F6` = 50 min, Material = `Alu`, 620 > 500, also
50 + 40 = 90 min (`Aufträge!K18` = 90).
Gegenprobe Auftrag `26-0395`, gleicher Artikel, Menge 120 Stk: 120 ist nicht grösser als
500, also 50 min (`Aufträge!K6` = 50).

Die Grenze ist echt grösser als, nicht grösser gleich. Ein Alu-Auftrag mit genau 500 Stk
bekommt keinen Zuschlag. In der Datei gibt es diesen Fall heute nicht.

**Status:** `aktiv, uneinheitlich`

**Hinweis (wichtig, drei verschiedene Umsetzungen in einer Spalte):**

| Zeilen | Formel | Aufträge |
|--------|--------|----------|
| `K4:K23` | mit `Parameter!$B$8` und `Parameter!$B$7` | 20 |
| `K24:K33`, `K35:K53` | mit fest eingetippten `500` und `40` | 29 |
| `K34` | **ohne** Zuschlagsteil, nur `VLOOKUP(...,6,0)` | 1 |

Heute betroffen sind vier Alu-Aufträge mit Menge über 500:

| Auftrag | Zeile | Artikel | Menge | Rüstzeit im Excel | Rüstzeit nach Regel | Variante |
|---------|-------|---------|-------|-------------------|---------------------|----------|
| `26-0414` | 18 | `A-1005` | 620 | 90 min | 90 min | Parameter |
| `26-0417` | 21 | `A-1016` | 800 | 80 min | 80 min | Parameter |
| `26-0430` | **34** | `A-1005` | 550 | **50 min** | **90 min** | Zuschlag fehlt |
| `26-0441` | 45 | `A-1016` | 700 | 80 min | 80 min | fest 500/40 |

`26-0430` rechnet heute also 40 min zu wenig. Das wirkt bis in `Aufträge!L34` (Gesamt
37,5 h statt 38,2 h) und von dort in die Auslastung von M3 in KW 43. Die feste 500/40 in
den Zeilen 24 bis 53 ergibt heute dasselbe Ergebnis wie die Parametervariante, aber nur
solange niemand `Parameter!B7` oder `B8` ändert. Genau das wurde laut Änderungsprotokoll in
V7.3 (03.2024) eingeführt: "Alu-Zuschlag als Parameter". Die Umstellung wurde in der
Spalte nicht fertig gemacht. Siehe Frage F-1.

## R-004 Bearbeitungszeit und Gesamtzeit je Auftrag

**Regel:** Die Bearbeitungszeit eines Auftrags ist Menge mal Bearbeitungszeit je Stück des
Artikels in Minuten, geteilt durch 60; die Gesamtzeit ist Bearbeitungszeit plus Rüstzeit
durch 60, beides in Stunden.

**Quelle:** `Aufträge!J4:J53` (`=E4*VLOOKUP($D4,Artikel!$A$2:$H$60,5,0)/60`),
`Aufträge!L4:L53` (`=J4+K4/60`), `Artikel!E`

**Beispiel:** Auftrag `26-0414`, Menge 620, `Artikel!E6` = 4,0 min/Stk:
620 × 4,0 / 60 = 41,333 h Bearbeitung. Plus Rüstzeit 90 min / 60 = 1,5 h ergibt
42,833 h Gesamt (`Aufträge!L18`).

Die Gesamtzeit `L` ist der einzige Zeitwert, den der Wochenplan verwendet (R-016).

**Status:** `aktiv`

**Hinweis:** Das Excel rechnet mit `float` und zeigt auf eine Dezimale gerundet an. Der
angezeigte Wert und der gerechnete Wert sind nicht dasselbe. Beispiel `Aufträge!L5` zeigt
24,0 h, gerechnet sind 24,0 h genau; `L7` zeigt 42,5 h, gerechnet 42,5 h; `L4` zeigt
15,5 h. Bei `26-0391` (Menge 400, 3,5 min/Stk) sind es 23,3333... h Bearbeitung. Die App
führt Zeiten in Minuten als `int` und Stunden als `Decimal` mit einer Dezimale
(Hausregel), die Abgleichstests gegen das Excel müssen diese Rundung berücksichtigen.

---

# 3. Auftrag: Termine und Status

## R-005 Liefer-KW aus dem Liefertermin, ISO-Woche

**Regel:** Die Liefer-KW eines Auftrags ist die ISO-Kalenderwoche seines Liefertermins.

**Quelle:** `Aufträge!M4:M53` (`=WEEKNUM(F4,21)`), Kommentar auf `Aufträge!M3`
("KALENDERWOCHE mit Typ 21 = ISO. Jahreswechsel manuell korrigieren!!")

**Beispiel:** Auftrag `26-0430`, Liefertermin 30.10.2026, ergibt Liefer-KW 44
(`Aufträge!M34` = 44). Auftrag `26-0388`, Liefertermin 18.09.2026, ergibt 38.

**Status:** `aktiv, uneinheitlich`

**Hinweis (Jahreswechsel, für die App die wichtigste Regel):** `WEEKNUM(...,21)` liefert
nur die Wochennummer ohne Jahr. Das Excel rechnet danach überall mit dieser nackten Zahl
weiter, und an vier Stellen bricht das über den Jahreswechsel:

1. **R-006 Plan-KW:** `=M4-IF(C4="A",2,1)`. Bei einem Liefertermin in KW 1 ergibt das
   Plan-KW −1 oder 0. Solche Wochen gibt es nicht.
2. **R-019 Horizont:** `Wochenplan!B3:I3` und `Bedarf!D3:K3` sind acht aufsteigende Zahlen.
   Ab KW 49 müsste die Folge 49, 50, 51, 52, 1, 2, 3, 4 lauten. Das kann eine eingetippte
   aufsteigende Zahlenreihe nicht.
3. **R-021 Verschiebung:** Das Makro schreibt `kw + 1` und schleift `For kw = kwStart To
   kwEnde`. Beides bricht über die Jahresgrenze.
4. **R-032 Bedarfsdatum:** `=Parameter!$B$4+(Z4-Parameter!$B$2)*7`. Die Differenz zweier
   nackter Wochennummern ist über den Jahreswechsel falsch (Beispiel: Fehl-KW 2 minus
   aktuelle KW 51 ergibt −49 Wochen statt +3).

Der Kommentar auf `M3` sagt dazu nur "Jahreswechsel manuell korrigieren!!". Es gibt keine
Formel dafür. Die App muss das können: Kalenderwoche immer als Paar (Jahr, ISO-Woche),
Wochendifferenzen über echte Datumsrechnung, Ausgabe als "2026-KW39". Siehe Frage F-5.

## R-006 Plan-KW aus Liefer-KW und Priorität

**Regel:** Die Plan-KW ist die Liefer-KW minus 2 Wochen bei Priorität A, sonst minus
1 Woche.

**Quelle:** `Aufträge!N4:N53` (`=M4-IF(C4="A",2,1)`), Hinweistext `Aufträge!N1`
("Plan-KW: A = 2 Wochen vor Termin, sonst 1 Woche"), `Parameter!B18`

**Beispiel:** Auftrag `26-0426`, Prio A, Liefer-KW 44 ergibt Plan-KW 42
(`Aufträge!N26` = 42). Auftrag `26-0425`, Prio B, Liefer-KW 42 ergibt Plan-KW 41.
Auftrag `26-0406`, Prio C, Liefer-KW 40 ergibt 39.

Prio B und Prio C werden gleich behandelt. Der Unterschied zwischen B und C wirkt erst in
R-021 (Reihenfolge beim Verschieben).

**Status:** `aktiv, uneinheitlich`

**Hinweis:** `Parameter!B18` "Vorlauf Prio A (Wochen)" steht mit dem Wert 2 im
Parameterblatt und trägt den Kommentar "TODO: in Aufträge verlinken". Die Formel benutzt
den Parameter nicht, sie hat die 2 fest eingetippt. Für B und C gibt es überhaupt keinen
Parameter, die 1 steht nur in der Formel. Heute stimmen beide Werte überein, deshalb fällt
es nicht auf. Siehe Frage F-3.

## R-007 KW eff.: manuelle Woche schlägt Plan-KW

**Regel:** Die effektive Planwoche eines Auftrags ist die manuell gesetzte Woche, wenn eine
eingetragen ist, sonst die Plan-KW.

**Quelle:** `Aufträge!P4:P53` (`=IF(O4="",N4,O4)`), Kommentar auf `Aufträge!O3` ("Wird vom
Makro Wochenplan_aktualisieren gesetzt. Kann auch von Hand überschrieben werden. Leer =
Plan-KW gilt."), bedingte Formatierung `Aufträge!O4:O93` (Eintrag in `O` wird blau und fett
dargestellt)

**Beispiel:** Auftrag `26-0420`, Plan-KW 41, Manuell KW 42, ergibt KW eff. 42
(`Aufträge!P24` = 42). Heute haben genau 2 der 50 Aufträge einen Eintrag in `O`:
`26-0420` und `26-0449`, beide vom Makro gesetzt (R-021).

`P` ist der Schlüssel für alles Weitere: Wochenplan (R-016) und Bedarf (R-022) rechnen mit
`P`, nicht mit `N` und nicht mit `M`.

**Status:** `aktiv`

## R-008 Status eines Auftrags

**Regel:** Ein Auftrag hat genau einen der drei Status `offen`, `in Arbeit` oder
`erledigt`, exakt so geschrieben; alles ausser `erledigt` zählt als laufend und geht in
Belastung und Bedarf ein.

**Quelle:** `Aufträge!Q4:Q53`, Kommentar auf `Aufträge!Q3` ("offen / in Arbeit / erledigt.
Genau so schreiben, sonst zählt der Wochenplan falsch."), alle `SUMIFS` und `COUNTIFS` mit
Kriterium `"<>erledigt"`, bedingte Formatierung `Aufträge!A4:V93` (`$Q4="erledigt"` färbt
die Zeile grau)

**Beispiel:** Von den 50 Aufträgen sind heute 3 `erledigt` (`26-0388`, `26-0391`,
`26-0395`), 2 `in Arbeit` (`26-0404`, `26-0405`) und 45 `offen`.
`Übersicht!C5` zählt 47 offene plus laufende, `Übersicht!C6` zählt 2 in Arbeit.

**Status:** `aktiv`

**Hinweis:** Es gibt keine Datenprüfung (kein Dropdown) auf der Spalte. Im ganzen Excel ist
keine einzige Datenprüfung definiert. Ein Tippfehler wie "Offen" oder "erledigt " mit
Leerzeichen verschwindet stillschweigend aus der Zählung, beziehungsweise erscheint in ihr.
Der Unterschied zwischen `offen` und `in Arbeit` wirkt nur in R-021: `in Arbeit` wird nie
verschoben.

## R-009 Überfälliger Auftrag

**Regel:** Ein Auftrag ist überfällig, wenn er nicht `erledigt` ist und seine
**Liefer-KW** kleiner als die aktuelle KW ist.

**Quelle:** bedingte Formatierung `Aufträge!A4:V93`, Regel im Roh-XML als x14-Erweiterung:
`AND($Q4<>"erledigt",$A4<>"",$M4<Parameter!$B$2)`, Hintergrund rot.
Gleiche Bedingung in `Übersicht!C7`
(`=COUNTIFS(Aufträge!$Q$4:$Q$500,"<>erledigt",Aufträge!$A$4:$A$500,"<>",Aufträge!$M$4:$M$500,"<"&Parameter!$B$2)`).

**Beispiel:** Auftrag `26-0402`, Liefer-KW 38, aktuelle KW 39, Status `offen`, Bemerkung
"Kunde hat Termin verschoben, neuer Termin offen!" ist heute der einzige überfällige
Auftrag. `Übersicht!C7` = 1.

**Status:** `aktiv`

**Hinweis:** Massgeblich ist die Liefer-KW `M`, nicht die effektive Planwoche `P`. Ein
Auftrag, den das Makro in die Vergangenheit schieben würde, wäre danach nicht überfällig.
Das Wort "überfällig" steht im Excel für zwei verschiedene Dinge: hier für den Auftrag
(Liefer-KW vergangen), in R-029 und R-034 für eine Bestellposition (Bestell-KW vergangen).
Die App trennt die beiden Begriffe. Für die Darstellung gilt die Hausregel: Zeile `bg-peach`
plus das Wort "überfällig", nie Farbe allein.

---

# 4. Stammdaten

## R-010 Material-Schreibweise ist exakt

**Regel:** Die Materialbezeichnung eines Artikels ist genau eine aus der Liste
`Alu`, `1.4301`, `S235JR`, `GG25`, `Messing`, `42CrMo4`; Abweichungen werden nicht
korrigiert und führen dazu, dass materialabhängige Regeln nicht greifen.

**Quelle:** `Artikel!C2:C22`, Kommentar auf `Artikel!C1` ("Genau so schreiben: Alu /
1.4301 / S235JR / GG25 / Messing / 42CrMo4. Sonst greift der Zuschlag nicht!"),
Auswertung in `Aufträge!H` und `Aufträge!K` (`H4="Alu"`)

**Beispiel:** Die 21 Artikel verteilen sich auf: `Alu` 7, `S235JR` 4, `1.4301` 3
(einer davon inaktiv), `GG25` 3, `Messing` 2, `1.4404` 1, `42CrMo4` 1.
`A-1005` hat Material `Alu`, deshalb greift R-003. Stünde dort "ALU" oder "Aluminium",
wäre `AND(H="Alu",...)` falsch und der Zuschlag fiele still weg.

Achtung: `1.4404` (Artikel `A-1015`) steht **nicht** in der Liste im Kommentar auf `C1`,
kommt in den Stammdaten aber vor. Die Liste im Kommentar ist unvollständig.

**Status:** `aktiv`

**Hinweis:** Es gibt keine Datenprüfung auf `Artikel!C`. Der Vergleich in Excel
(`H4="Alu"`) ist nicht gross-/kleinschreibungssensitiv, "alu" würde also noch greifen,
"Aluminium" nicht. Die Hausregel verlangt, dass der Import die Schreibweise prüft und
meldet, aber nicht still korrigiert.

## R-011 Artikel bestimmt Bezeichnung, Material, Maschine und Zeiten des Auftrags

**Regel:** Bezeichnung, Material, Standardmaschine, Bearbeitungszeit je Stück und
Rüstzeit-Basis eines Auftrags kommen über die Artikelnummer aus dem Blatt `Artikel`; der
Auftrag speichert diese Werte nicht selbst.

**Quelle:** `Aufträge!G4:I53` und die `VLOOKUP` in `J`, `K` auf `Artikel!$A$2:$H$60`,
Kommentar auf `Artikel!D1` ("Standardmaschine. M1 DMG, M2 Mazak, M3 Hermle, M4 Fräsen.
Manuelle Umplanung nur in Aufträge!")

**Beispiel:** Auftrag `26-0413` hat Artikel `A-1009`; daraus ergeben sich Bezeichnung
"Gehäuse G12 GG25", Material `GG25`, Maschine `M4`, 18,0 min/Stk und 120 min Rüstzeit-Basis.

**Status:** `aktiv, uneinheitlich`

**Hinweis:** Die Spalte `Aufträge!G` (Bezeichnung) fängt einen unbekannten Artikel mit
`IFERROR(...,"??")` ab. Die Spalten `H` (Material), `I` (Maschine), `J` und `K` tun das
nicht und liefern dann `#NV`. Ein Tippfehler in der Artikelnummer erzeugt also eine Zeile,
die halb aussieht wie ein Auftrag und halb wie ein Fehler, und `#NV` wandert über `L` in
die Summen des Wochenplans. Die App lehnt eine unbekannte Artikelnummer ab.

Zweiter Punkt: der Auftrag kennt keine eigene Maschine. `Aufträge!I` ist eine Formel, keine
Eingabe. Der Kommentar auf `Artikel!D1` sagt "Manuelle Umplanung nur in Aufträge!", aber
dafür gibt es in `Aufträge` keine Spalte. Umplanen auf eine andere Maschine geht heute nur,
indem man die Formel in `I` überschreibt. Das hat niemand getan, alle 50 Zeilen tragen die
Formel. Siehe Frage F-7.

## R-012 Stückliste: Schlüssel aus Artikel und Position, maximal zwei Positionen

**Regel:** Eine Stücklistenzeile wird über den Schlüssel "ArtNr-Pos" gefunden, und ein
Artikel darf höchstens zwei Positionen haben.

**Quelle:** `Stückliste!A2:A23` (`=B2&"-"&C2`), Kommentar auf `Stückliste!A1` ("NICHT
ÄNDERN. Key wird in Aufträge für SVERWEIS gebraucht (ArtNr-Pos)."), Kommentar auf
`Stückliste!C1` ("Max. 2 Positionen pro Artikel! Mehr geht nicht (siehe Aufträge Spalten
S-V)."), `Aufträge!S`, `T`, `U`, `V`

**Beispiel:** `A-1019` (Lagerbock GG25 kompl.) ist der einzige Artikel mit zwei Positionen:
`A-1019-1` auf `RM-109` (Gehäuse) und `A-1019-2` auf `RM-110` (Deckel). Alle anderen
20 Artikel haben genau eine Position. In den Aufträgen sind das `26-0419` und `26-0439`,
die als einzige eine Menge in `Aufträge!V` haben.

**Status:** `aktiv`

**Hinweis:** Die Grenze von zwei Positionen ist keine Fachregel, sie ist die Breite der
Spalten `S` bis `V` im Auftragsblatt. Ein Artikel mit drei Rohmaterialien würde still
falsch rechnen: Position 3 taucht nirgends auf, weder im Auftrag noch im Bedarf. Das Blatt
`Stückliste` selbst erlaubt sie, geprüft wird nichts. Siehe Frage F-8.
Das Änderungsprotokoll nennt "01.2021 V5.0 Stückliste mit 2 Positionen (BH)", davor gab es
offenbar nur eine.

## R-013 Rohmaterialbedarf je Auftragsposition

**Regel:** Der Rohmaterialbedarf einer Auftragsposition ist Auftragsmenge mal Menge je
Stück aus der Stückliste mal (1 + Verschnitt %), aufgerundet auf eine Dezimale.

**Quelle:** `Aufträge!T4:T53` und `Aufträge!V4:V53`

```
=IF(S4="",0,ROUNDUP(E4*VLOOKUP($D4&"-1",Stückliste!$A$2:$F$50,5,0)*(1+VLOOKUP($D4&"-1",Stückliste!$A$2:$F$50,6,0)),1))
```

Kommentar auf `Aufträge!S3`: "Nicht anfassen. Spalten S bis V braucht das Blatt Bedarf."

**Beispiel:** Auftrag `26-0414`, Menge 620, Stücklistenzeile `A-1005-1`:
`RM-106`, 0,0140 Stangen/Stk, 8 % Verschnitt.
620 × 0,0140 × 1,08 = 9,3744, aufgerundet auf eine Dezimale 9,4 Stangen
(`Aufträge!T18` = 9,4).

Zweites Beispiel mit zwei Positionen: Auftrag `26-0419`, Artikel `A-1019`, Menge 30.
Beide Positionen haben 1,0000 Stk je Stück und 0 % Verschnitt, also
`T23` = 30 (`RM-109`) und `V23` = 30 (`RM-110`).

**Status:** `aktiv`

**Hinweis:** Die Verschnittsätze stehen je Stücklistenzeile, nicht je Material: 5 % bei
Stangenware Stahl und Messing, 8 % bei Alu-Rundmaterial ("Alu: Verschnitt 8% wg.
Planfräsen", Kommentar in `Stückliste!G6`), 10 % bei Alu-Platten, 0 % bei Guss-Rohlingen.
Aufgerundet wird auf eine Dezimale, auch bei Stückgut: `26-0405` braucht 240,0 Stück
`RM-110`, dargestellt mit Dezimale. Die Hausregel führt Rohmaterialmengen als `Decimal`
mit einer Dezimale, das passt.

---

# 5. Kapazität und Wochenplan

## R-014 Kapazität einer Maschine pro Woche

**Regel:** Die Wochenkapazität einer Maschine in Stunden ist Schichten pro Tag mal Stunden
je Schicht mal Arbeitstage pro Woche mal Verfügbarkeit der Maschine.

**Quelle:** `Kapazität!G2:G5` (`=C2*D2*E2*F2`), Eingaben `Kapazität!C:F`

**Beispiel:**

| Maschine | Bezeichnung | Schichten | Std/Schicht | Tage | Verfügbarkeit | Kapazität |
|----------|-------------|-----------|-------------|------|---------------|-----------|
| M1 | DMG CTX beta 800 (Drehen) | 2 | 8,0 | 5 | 85 % | 68,0 h |
| M2 | Mazak QT-250 (Drehen) | 2 | 8,0 | 5 | 85 % | 68,0 h |
| M3 | Hermle C 22 (5-Achs) | 2 | 8,0 | 5 | 80 % | 64,0 h |
| M4 | Fräszentrum Haas VF-3 | 2 | 8,0 | 5 | 90 % | 72,0 h |

M1: 2 × 8,0 × 5 × 0,85 = 68,0 h.

**Status:** `aktiv, uneinheitlich`

**Hinweis:** M1, M2 und M4 lesen Schichten, Stunden und Tage über `=Parameter!$B$9`,
`$B$10`, `$B$12`. **M3 (`Kapazität!C4:E4`) hat die Werte 2, 8 und 5 fest eingetippt.**
Heute kommt dasselbe heraus. Ändert jemand `Parameter!B9` von 2 auf 3 Schichten, ziehen M1,
M2 und M4 nach, M3 nicht, und niemand sieht es. Die Verfügbarkeit `F` ist bewusst je
Maschine unterschiedlich und gehört nicht in die Parameter (Kommentar `Kapazität!I4`:
"Verfügbarkeit tiefer wg. Einfahren neue Aufträge"). Siehe Frage F-2.

## R-015 Wartungswoche zieht einen festen Betrag ab

**Regel:** In der Wartungs-KW einer Maschine wird die Wochenkapazität um den
Wartungsabzug (`Parameter!B16` = 16 h) gekürzt; `0` in der Wartungs-KW bedeutet keine
Wartung im Horizont.

**Quelle:** `Wochenplan!B11:I14` (`=IF(B$10=Kapazität!$H2,Kapazität!$G2-Parameter!$B$16,Kapazität!$G2)`),
`Kapazität!H2:H5`, Kommentar auf `Kapazität!H1` ("0 = keine Wartung im Horizont. Abzug
siehe Parameter (16h).")

**Beispiel:** M1 hat Wartungs-KW 41. Im Wochenplan steht deshalb für KW 41
68,0 − 16 = 52,0 h (`Wochenplan!D11` = 52,0), in allen anderen Wochen 68,0 h.
M2 hat KW 44 (`Wochenplan!G12` = 52,0), M4 hat KW 43 (`Wochenplan!F14` = 56,0),
M3 hat 0 und wird nirgends gekürzt.

**Status:** `aktiv`

**Hinweis:** Jede Maschine kann genau eine Wartungswoche haben und der Abzug ist für alle
Maschinen gleich. Zwei Wartungen im Horizont oder ein maschinenabhängiger Abzug gehen
nicht. Der Vergleich `B$10=Kapazität!$H2` vergleicht nackte Wochennummern (R-005).

## R-016 Belastung einer Maschine in einer Woche

**Regel:** Die Belastung einer Maschine in einer Kalenderwoche ist die Summe der
Gesamtzeiten aller Aufträge, die dieser Maschine zugeordnet sind, deren KW eff. diese
Woche ist und die nicht `erledigt` sind.

**Quelle:** `Wochenplan!B4:I7`

```
=SUMIFS(Aufträge!$L$4:$L$500,Aufträge!$I$4:$I$500,$A4,Aufträge!$P$4:$P$500,B$3,Aufträge!$Q$4:$Q$500,"<>erledigt")
```

Zweite Umsetzung: `Modul_Planung.Belastung(wsA, letzteZeile, m, kw)`, Schleife über die
Auftragszeilen mit derselben Bedingung.

**Beispiel:** M1 in KW 39: Aufträge `26-0404` (27,0 h) und `26-0407` (13,0 h), zusammen
40,0 h (`Wochenplan!B4` = 40,0).
M3 in KW 39: `26-0405` (23,0 h) und `26-0409` (24,833 h), zusammen 47,833 h
(`Wochenplan!B6` = 47,8). `26-0395` läuft auch auf M3, hat aber Status `erledigt` und
KW eff. 38 und fällt doppelt weg.

**Status:** `aktiv, uneinheitlich`

**Hinweis:** Die Regel ist zweimal umgesetzt, einmal als `SUMIFS` im Blatt und einmal als
VBA-Funktion `Belastung`. Sie liefern heute dasselbe, sind aber unabhängig voneinander:
Das `SUMIFS` rechnet bis Zeile 500, die VBA-Funktion nur bis zur letzten belegten Zeile in
Spalte A. Prio A und `in Arbeit` zählen in beiden mit, obwohl sie nach R-021 nicht
verschoben werden dürfen. Die App hat genau eine Funktion dafür.

## R-017 Auslastung

**Regel:** Die Auslastung einer Maschine in einer Woche ist Belastung geteilt durch
Kapazität dieser Woche; bei Kapazität 0 ist die Auslastung 0.

**Quelle:** `Wochenplan!B18:I21` (`=IF(B11=0,0,B4/B11)`)

**Beispiel:** M1 in KW 39: 40,0 / 68,0 = 58,8 % (`Wochenplan!B18`).
M1 in KW 41 mit Wartung: 44,0 / 52,0 = 84,6 % (`Wochenplan!D18`).
Höchster Wert im Horizont heute: M2 in KW 43 mit 58,4 / 68,0 = 85,9 %.

**Status:** `aktiv`

## R-018 Auslastungsampel

**Regel:** Eine Auslastung über der Auslastungsgrenze (`Parameter!B6` = 90 %) wird rot
markiert, zwischen 75 % und der Grenze gelb, unter 40 % grün, dazwischen neutral.

**Quelle:** bedingte Formatierung `Wochenplan!B18:I21`, drei Regeln:

| Priorität | Bedingung | Darstellung |
|-----------|-----------|-------------|
| 2 | `> Parameter!$B$6` | rote Fläche, dunkelroter fetter Text |
| 3 | `between 0.75 and Parameter!$B$6` | gelbe Fläche |
| 4 | `< 0.4` | grüne Fläche |

Hinweistext `Wochenplan!E1`: "Rot = über Auslastungsgrenze, Makro
Wochenplan_aktualisieren verschiebt."

**Beispiel:** M2 in KW 43 mit 85,9 % ist gelb. M1 in KW 40 mit 28,9 % ist grün. Heute ist
keine Zelle rot, weil das Makro bereits gelaufen ist und zwei Aufträge verschoben hat
(R-021).

**Status:** `aktiv, uneinheitlich`

**Hinweis:** Die Übersicht zeigt dieselben vier Auslastungen (`Übersicht!C15:C18`), hat
aber nur die rote Regel (`> Parameter!$B$6`), kein Gelb und kein Grün. Zwei Seiten, zwei
Ampeln. Ausserdem ist die Schwelle 0,75 für Gelb als feste Zahl in der Formatierungsregel
eingetragen, nicht als Parameter. Die Lücke zwischen 40 % und 75 % ist bewusst ohne Farbe.
Für die App gilt die Hausregel: Farbe nie allein, immer mit Wort.

## R-019 Planungshorizont: acht Wochen ab der aktuellen KW

**Regel:** Geplant wird über acht Kalenderwochen, beginnend mit der aktuellen KW.

**Quelle:** `Parameter!B15` (= 8), `Wochenplan!B3:I3`, `B10:I10`, `B17:I17`,
`Bedarf!D3:K3`, Kommentar auf `Bedarf!AF3` ("Deckt den ganzen Horizont (8 Wo) +
Sicherheit, aufgerundet auf Gebinde.")

**Beispiel:** Bei aktueller KW 39 läuft der Horizont über KW 39 bis KW 46. Alle vier
Wochenköpfe im Excel tragen genau diese acht Zahlen.

**Status:** `aktiv, uneinheitlich`

**Hinweis:** Der Horizont ist an fünf Stellen unterschiedlich umgesetzt:

- `Parameter!B15` = 8, als Zahl, ohne dass eine Formel darauf zeigt.
- Vier Kopfzeilen mit acht eingetippten Wochennummern (`Wochenplan!B3:I3`, `B10:I10`,
  `B17:I17`, `Bedarf!D3:K3`). Sie müssen von Hand jede Woche weitergeschoben werden, und
  sie müssen untereinander gleich bleiben, sonst findet das Makro die Kapazität nicht mehr
  (R-021).
- Acht Spalten Bedarf (`Bedarf!D:K`) und acht Spalten kumulierter Bedarf (`Bedarf!R:Y`).
- Acht verschachtelte `IF` in `Bedarf!Z` (R-027).
- `Bedarf!P` teilt durch die feste 8 statt durch `Parameter!$B$15` (R-024).

Eine Änderung des Horizonts ist im Excel praktisch nicht möglich. In der App ist der
Horizont ein Parameter und alles andere leitet sich daraus ab. Siehe Frage F-4.

## R-020 Aufträge ausserhalb des Horizonts fallen aus der Planung

**Regel:** Aufträge, deren KW eff. vor oder nach dem Horizont liegt, erscheinen in keinem
Wochenplan und in keinem Bedarf; sie werden nur gezählt.

**Quelle:** `Wochenplan!B24` (Aufträge im Horizont),
`Wochenplan!B25` (`=COUNTIFS(...)-B24`), Kommentar auf `Wochenplan!A25` ("Aufträge mit KW
vor/nach dem Horizont. Erscheinen nirgends! Von Hand prüfen."), `Übersicht!C9`

**Beispiel:** Heute 45 Aufträge im Horizont, 2 ausserhalb (`Wochenplan!B24` = 45,
`B25` = 2). Das sind `26-0402` mit KW eff. 37 (überfällig, Termin vom Kunden verschoben)
und `26-0446` mit KW eff. 47.

**Status:** `aktiv`

**Hinweis:** Das ist ein stiller Datenverlust. Die Zeiten dieser Aufträge fehlen in der
Auslastung, ihr Rohmaterial fehlt im Bestellvorschlag. Man sieht nur eine Zahl und muss von
Hand nachsehen, welche Aufträge gemeint sind. Die App muss diese Aufträge benennen können,
nicht nur zählen.

## R-021 Automatische Verschiebung bei Überlast

**Regel:** Übersteigt die Belastung einer Maschine in einer Woche die Auslastungsgrenze,
wird so lange je ein Auftrag in die Folgewoche verschoben, bis die Grenze eingehalten ist;
verschoben werden nur Aufträge mit Status `offen`, nie Priorität A, zuerst Priorität C dann
B, und innerhalb einer Priorität der kleinste Auftrag, der die Überlast allein beseitigt,
sonst der grösste.

**Quelle:** `Modul_Planung.Wochenplan_aktualisieren`, Tastenkürzel `Ctrl+Shift+W`,
Auslastungsgrenze `Parameter!B6`

Ablauf im Makro:

1. Alle automatischen Verschiebungen zurücksetzen: Zeilen, deren Bemerkung den Text
   "auto verschoben" enthält, verlieren ihren Eintrag in `Manuell KW` und den Textteil ab
   "; auto verschoben". Von Hand gesetzte Werte in `O` bleiben stehen.
2. Für jede Maschine (M1 bis M4) und jede KW des Horizonts (aufsteigend): solange
   Belastung > Kapazität × Auslastungsgrenze, einen Auftrag auswählen und auf `kw + 1`
   setzen.
3. Auswahl: erst alle `offen`-Aufträge mit Prio C dieser Maschine und Woche, sortiert nach
   Gesamtzeit aufsteigend; der erste, dessen Gesamtzeit die Überlast allein beseitigt;
   sonst der grösste. Gibt es keinen C-Auftrag, dasselbe mit Prio B. Gibt es keinen,
   passiert nichts (Abbruch für diese Woche).
4. Der verschobene Auftrag bekommt `Manuell KW` = `kw + 1` und die Bemerkung
   "auto verschoben KW&lt;alt&gt; -&gt; KW&lt;neu&gt; (Makro TT.MM.)".
5. Notbremse: höchstens 20 Durchläufe je Maschine und Woche.
6. Am Schluss eine Meldung mit der Anzahl und dem Hinweis, rote Felder von Hand zu prüfen.

**Beispiel:** Zwei Aufträge tragen heute den Makrovermerk:

| Auftrag | Prio | Maschine | Plan-KW | Manuell KW | Bemerkung |
|---------|------|----------|---------|------------|-----------|
| `26-0420` | C | M1 | 41 | 42 | "auto verschoben KW41 -> KW42 (Makro 13.09.)" |
| `26-0449` | C | M4 | 43 | 44 | "Nachtrag zu 26-0416; auto verschoben KW43 -> KW44 (Makro 13.09.)" |

Beide sind Prio C und Status `offen`, passend zur Regel. Nach dem Lauf ist keine Zelle im
Wochenplan mehr rot.

**Status:** `aktiv`

**Hinweis:** Vier Punkte, die die App anders lösen muss:

- **Das Rücksetzen hängt am Bemerkungstext.** Löscht jemand die Bemerkung, bleibt die
  Verschiebung für immer stehen und sieht aus wie eine Handeingabe. Es gibt kein Feld, das
  "automatisch" von "manuell" unterscheidet.
- **`kw + 1` kann über das Horizontende hinausgehen.** Ein Auftrag in KW 46, den das Makro
  verschiebt, landet in KW 47 und verschwindet damit nach R-020 aus der Planung.
- **Prio A und `in Arbeit` zählen in die Belastung, können aber nicht verschoben werden.**
  Ist eine Woche allein durch Prio-A-Aufträge überlastet, bricht die Schleife ab und die
  Woche bleibt rot. Das ist gewollt (Meldung: "Prio A wird nie verschoben"), heisst aber,
  dass ein grüner Wochenplan nicht heisst, dass alles passt.
- **Das Makro liest die Kapazität über die Kopfzeile 10 des Wochenplans**
  (`Modul_Planung.Kapazitaet`), die Horizontgrenzen aber über Zeile 3 (`B3` und `I3`).
  Stehen die Zeilen 3, 10 und 17 nicht auf denselben Wochen, liefert `Kapazitaet` 0, das
  Limit wird 0, und das Makro verschiebt alles, was es verschieben darf.

---

# 6. Material und Bestellvorschlag

Das Blatt `Bedarf` hat für jedes Rohmaterial genau eine Zeile: Zeile 4 bis 18 für
`Rohmaterial!2` bis `16`. Stammdaten werden mit direkten Zellbezügen kopiert
(`=Rohmaterial!A2`), nicht über einen Schlüssel gesucht.

## R-022 Bedarf je Rohmaterial und Woche

**Regel:** Der Bedarf eines Rohmaterials in einer Woche ist die Summe der
Rohmaterialmengen aller nicht erledigten Auftragspositionen, deren KW eff. diese Woche ist,
über beide Stücklistenpositionen.

**Quelle:** `Bedarf!D4:K18`

```
=SUMIFS(Aufträge!$T$4:$T$500,Aufträge!$S$4:$S$500,$A4,Aufträge!$P$4:$P$500,D$3,Aufträge!$Q$4:$Q$500,"<>erledigt")
+SUMIFS(Aufträge!$V$4:$V$500,Aufträge!$U$4:$U$500,$A4,Aufträge!$P$4:$P$500,D$3,Aufträge!$Q$4:$Q$500,"<>erledigt")
```

`Bedarf!L` summiert die acht Wochen zur "Summe Horizont".

**Quelle Darstellung:** bedingte Formatierung `Bedarf!D4:K18`, Wert 0 wird hellgrau
dargestellt.

**Beispiel:** `RM-107` (Alu-Platte 20x500x1000) in KW 43: Aufträge `26-0428` (33,0) ergibt
33,0 (`Bedarf!H10` = 33,0). Über den ganzen Horizont: 14,9 + 0 + 0 + 9,9 + 33,0 + 0 + 4,2
+ 11,6 = 73,6 Platten (`Bedarf!L10`).

**Status:** `aktiv`

## R-023 Verfügbarer Bestand

**Regel:** Der verfügbare Bestand eines Rohmaterials ist Lagerbestand plus offene
Bestellungen.

**Quelle:** `Bedarf!O4:O18` (`=M4+N4`), `Rohmaterial!E` (Lager), `Rohmaterial!F`
(Bestellt offen), Kommentar auf `Rohmaterial!E1` ("Lager wird manuell nachgeführt
(Inventur Freitag). Nicht aus ERP!")

**Beispiel:** `RM-102`: Lager 6 Stangen, offen bestellt 5, verfügbar 11
(`Bedarf!O5` = 11). `RM-110`: 620 + 200 = 820 Stück.

**Status:** `aktiv`

**Hinweis:** Offene Bestellungen werden ohne Ankunftswoche gerechnet. Eine Bestellung, die
erst in KW 45 eintrifft, zählt schon in KW 39 als verfügbar. Das kann eine Fehl-KW (R-027)
zu spät ausweisen. Ein Ankunftsdatum gibt es in `Rohmaterial` nicht.
Der Lagerbestand ist eine Handeingabe aus der Freitagsinventur, nicht aus dem ERP.

## R-024 Durchschnittlicher Wochenbedarf

**Regel:** Der durchschnittliche Wochenbedarf eines Rohmaterials ist die Summe des Bedarfs
über den Horizont geteilt durch die Anzahl Wochen des Horizonts.

**Quelle:** `Bedarf!P4:P18` (`=L4/8`)

**Beispiel:** `RM-107`: 73,6 / 8 = 9,2 Platten je Woche (`Bedarf!P10`).

**Status:** `aktiv, uneinheitlich`

**Hinweis:** Die 8 ist fest eingetippt, `Parameter!B15` wird nicht gelesen. Siehe R-019
und Frage F-4.

## R-025 Sicherheitsbestand

**Regel:** Der Sicherheitsbestand eines Rohmaterials ist der Sicherheitsbestand-Prozentsatz
(`Parameter!B5` = 10 %) vom durchschnittlichen Wochenbedarf, aufgerundet auf ganze
Einheiten, mindestens aber eine Gebindegrösse.

**Quelle:** `Bedarf!Q4:Q18` (`=MAX(ROUNDUP(P4*Parameter!$B$5,0),AE4)`), Kommentar auf
`Bedarf!Q3` ("10% vom Ø-Wochenbedarf, mindestens 1 Gebinde. Hat sich bewährt.")

**Beispiel:** `RM-107`: Ø 9,2 je Woche, 10 % davon 0,92, aufgerundet 1. Gebinde 4, also
`MAX(1, 4)` = 4 (`Bedarf!Q10` = 4).
`RM-110`: Ø 98,75, 10 % davon 9,875, aufgerundet 10. Gebinde 40, also 40 (`Bedarf!Q13`).

**Status:** `aktiv`

**Hinweis:** In der Praxis gewinnt fast immer das Gebinde. Bei allen 15 Rohmaterialien ist
der Sicherheitsbestand heute gleich der Gebindegrösse. Der Prozentsatz wirkt erst ab
einem Ø-Wochenbedarf über dem Zehnfachen des Gebindes.

## R-026 Kumulierter Bedarf

**Regel:** Der kumulierte Bedarf eines Rohmaterials bis zu einer Woche ist die Summe des
Bedarfs von der ersten Horizontwoche bis einschliesslich dieser Woche.

**Quelle:** `Bedarf!R4:Y18` (`R4 = D4`, `S4 = R4+E4`, ... `Y4 = X4+K4`), Spalte `R` ist
ausgeblendet

**Beispiel:** `RM-115`: Bedarf 0 / 0 / 23,7 / 0 / 0 / 0 / 31,5 / 0 ergibt kumuliert
0 / 0 / 23,7 / 23,7 / 23,7 / 23,7 / 55,2 / 55,2 (`Bedarf!R18:Y18`).

**Status:** `aktiv`

## R-027 Fehl-KW

**Regel:** Die Fehl-KW eines Rohmaterials ist die erste Woche des Horizonts, in der
kumulierter Bedarf plus Sicherheitsbestand den verfügbaren Bestand übersteigt; reicht der
Bestand über den ganzen Horizont, ist die Fehl-KW leer.

**Quelle:** `Bedarf!Z4:Z18`, acht verschachtelte `IF`:

```
=IF(R4+$Q4>$O4,D$3,IF(S4+$Q4>$O4,E$3,...,IF(Y4+$Q4>$O4,K$3,""))))))))
```

Kommentar auf `Bedarf!Z3`: "Erste KW in der kum. Bedarf + Sicherheit den verfügbaren
Bestand übersteigt. Leer = reicht."

**Beispiel:** `RM-106`: verfügbar 5, Sicherheit 5, kumulierter Bedarf 0 / 13,3 / 13,3 /
13,3 / 21,7 / 21,7 / 26,9 / 31,5.
KW 39: 0 + 5 > 5 ist falsch. KW 40: 13,3 + 5 = 18,3 > 5 ist wahr. Fehl-KW = 40
(`Bedarf!Z9` = 40).
Heute hat jedes der 15 Rohmaterialien eine Fehl-KW, keine Zeile ist leer.

**Status:** `aktiv`

**Hinweis:** Der Vergleich ist echt grösser als. Bei Gleichstand (Bedarf plus Sicherheit
genau gleich verfügbar) gilt das Material als ausreichend. Die Formel ist auf acht Wochen
festverdrahtet (R-019).

## R-028 Bestell-KW

**Regel:** Die Bestell-KW ist die Fehl-KW minus die Lieferzeit des Lieferanten in Wochen,
und bei Lieferanten mit Bewertung `C` zusätzlich minus den Puffer (`Parameter!B11` =
1 Woche).

**Quelle:** `Bedarf!AD4:AD18` (`=IF(Z4="","",Z4-AB4-IF(AC4="C",Parameter!$B$11,0))`),
`Bedarf!AB` (`=VLOOKUP(AA4,Lieferanten!$A$2:$H$20,4,0)`),
`Bedarf!AC` (Bewertung, Spalte 5),
Kommentar auf `Bedarf!AD3` ("Fehl-KW minus Lieferzeit. Lieferant C: 1 Woche extra
(Giesserei!!)."), Kommentar auf `Lieferanten!E1` ("A = zuverlässig, B = ok, C = kritisch
(Puffer!)")

**Beispiel:** `RM-109` (Guss-Rohling Gehäuse), Lieferant `L-04`, Lieferzeit 5 Wochen,
Bewertung `C`. Fehl-KW 44, also 44 − 5 − 1 = 38 (`Bedarf!AD12` = 38).
`RM-101`, Lieferant `L-01`, Lieferzeit 2, Bewertung `A`: Fehl-KW 42, also 42 − 2 = 40.

**Quelle Darstellung:** bedingte Formatierung `Bedarf!AD4:AD18` (x14-Regel im Roh-XML):
`AND(AD4<>"",AD4<Parameter!$B$2)` stellt eine Bestell-KW in der Vergangenheit dunkelrot
und fett dar.

**Status:** `aktiv`

**Hinweis:** Der Puffer hängt an der Bewertung des Lieferanten, nicht am Lieferanten
selbst. `L-04` ist der einzige `C`-Lieferant (Bemerkung im Blatt: "Lieferzeit unzuverlässig,
immer +1 Wo"), betroffen sind `RM-109` und `RM-110`. Die Bestell-KW kann rechnerisch vor
der aktuellen Woche liegen und wird dann nicht auf die aktuelle Woche begrenzt. Genau das
ist heute bei `RM-106` (37) und `RM-109` (38) der Fall.

## R-029 Bestellen ja oder nein

**Regel:** Eine Bestellposition wird zur Bestellung vorgeschlagen, wenn eine Bestell-KW
vorhanden und diese kleiner oder gleich der aktuellen KW ist.

**Quelle:** `Bedarf!AG4:AG18` (`=IF(AD4="","N",IF(AD4<=Parameter!$B$2,"J","N"))`),
Kommentar auf `Bedarf!AG3` ("J = Bestell-KW ist diese Woche oder schon vorbei. Kleiner als
aktuelle KW = ÜBERFÄLLIG."), bedingte Formatierung `Bedarf!AG4:AG18` (`= "J"` wird rot
hinterlegt und fett)

**Beispiel:** Bei aktueller KW 39 stehen fünf Positionen auf `J`:

| RohNr | Fehl-KW | Bestell-KW | J/N |
|-------|---------|------------|-----|
| `RM-106` | 40 | 37 | J (überfällig) |
| `RM-107` | 42 | 39 | J |
| `RM-109` | 44 | 38 | J (überfällig) |
| `RM-110` | 45 | 39 | J |
| `RM-115` | 41 | 39 | J |

`Bedarf!AG20` zählt 5 (`=COUNTIF(AG4:AG18,"J")`), `Übersicht!C10` zeigt dieselbe Zahl.
Davon sind 2 überfällig (Bestell-KW < 39), gezählt in `Übersicht!C12`.

**Status:** `aktiv`

## R-030 Bestellmenge wird auf Gebinde aufgerundet

**Regel:** Die Bestellmenge deckt den gesamten Bedarf des Horizonts plus Sicherheitsbestand
minus verfügbaren Bestand, nie negativ, aufgerundet auf ganze Gebinde; ohne Fehl-KW ist sie
0.

**Quelle:** `Bedarf!AF4:AF18` (`=IF(Z4="",0,ROUNDUP(MAX(0,L4+Q4-O4)/AE4,0)*AE4)`),
`Bedarf!AE` (Gebinde aus `Rohmaterial!G`), Kommentar auf `Bedarf!AF3`

**Beispiel:** `RM-109`: Summe Horizont 140,0, Sicherheit 20, verfügbar 90.
140 + 20 − 90 = 70. Gebinde 20: 70 / 20 = 3,5, aufgerundet 4, mal 20 = 80 Stück
(`Bedarf!AF12` = 80).
`RM-101`: 32,2 + 10 − 24 = 18,2. Gebinde 10: 18,2 / 10 = 1,82, aufgerundet 2, mal 10 = 20
Stangen.

**Status:** `aktiv`

**Hinweis:** Die Bestellmenge wird für alle 15 Rohmaterialien gerechnet, auch für die, die
nach R-029 nicht bestellt werden. Exportiert werden nur die `J`-Zeilen. Der Bedarf ausserhalb
des Horizonts (R-020) fehlt in `L` und damit in der Bestellmenge.

## R-031 Bestellwert

**Regel:** Der Bestellwert einer Position ist Bestellmenge mal Preis je Einheit des
Rohmaterials.

**Quelle:** `Bedarf!AH4:AH18` (`=AF4*Rohmaterial!H2`), `Bedarf!AH20`
(`=SUMIF(AG4:AG18,"J",AH4:AH18)`), `Übersicht!C11`

**Beispiel:** `RM-109`: `Bedarf!AF12` (80 Stück) mal `Rohmaterial!H10` ergibt
`Bedarf!AH12`. Der Wochenwert ist die Summe über die `J`-Zeilen in `Bedarf!AH20` und steht
so auch in `Übersicht!C11`. (Preise sind hier bewusst nicht ausgeschrieben.)

**Status:** `aktiv`

**Hinweis:** Der Preis ist ein einziger Wert je Rohmaterial, ohne Datum, Währung, Staffel
oder Mindestmenge. Die App führt Geld als `Decimal`, nie als `float`.

## R-032 Bedarfsdatum

**Regel:** Das Bedarfsdatum einer Bestellposition ist der Montag der aktuellen KW plus die
Anzahl Wochen zwischen aktueller KW und Fehl-KW, mal sieben Tage.

**Quelle:** `Bedarf!AI4:AI18` (`=IF(Z4="","",Parameter!$B$4+(Z4-Parameter!$B$2)*7)`)

**Beispiel:** `RM-109`: Fehl-KW 44, aktuelle KW 39, Montag 21.09.2026.
21.09.2026 + (44 − 39) × 7 = 21.09.2026 + 35 Tage = 26.10.2026 (`Bedarf!AI12`).
Dieses Datum geht so in den Export (R-033).

**Status:** `aktiv, uneinheitlich`

**Hinweis:** Die Formel rechnet mit der Differenz zweier nackter Wochennummern und ist über
den Jahreswechsel falsch (R-005). Ausserdem ist das Bedarfsdatum immer der Montag der
Fehl-KW, nie ein Tag innerhalb der Woche.

---

# 7. Export nach Abacus

## R-033 Inhalt und Reihenfolge der Exportdatei

**Regel:** Der Export enthält je Bestellposition mit `Bestellen? = J` genau sieben Felder
in fester Reihenfolge: ERP-Artikelnummer, ERP-Lieferantennummer, Bestellmenge, Einheit,
Bedarfsdatum, Kostenstelle Einkauf, Bemerkung.

**Quelle:** `Modul_ERP.Export_ERP`, Blatt `ERP_Export` Zeile 1, Kommentar auf
`ERP_Export!A1` ("Kopfzeile NICHT ÄNDERN. Reihenfolge muss mit Abacus Import-Definition
PLAN_BESTELL übereinstimmen.")

| Feld | Herkunft |
|------|----------|
| `ARTNR` | `Rohmaterial!I` über die RohNr, als Text (führende Null bzw. führende 3 muss bleiben) |
| `LIEFNR` | `Lieferanten!F` über die LiefNr |
| `MENGE` | `Bedarf!AF` (R-030) |
| `EINHEIT` | `Bedarf!C` (aus `Rohmaterial!C`) |
| `BEDARFSDATUM` | `Bedarf!AI`, formatiert `TT.MM.JJJJ` (R-032) |
| `KOSTENSTELLE` | `Parameter!B14` (= 4100) |
| `BEMERKUNG` | siehe R-034 |

**Beispiel:** Der letzte Export (Stempel 13.09.2026 15:07) hat fünf Zeilen, passend zu den
fünf `J`-Positionen aus R-029:

| ARTNR | MENGE | EINHEIT | BEDARFSDATUM | KOSTENSTELLE |
|-------|-------|---------|--------------|--------------|
| 3050800 (`RM-106`) | 35 | Stange | 28.09.2026 | 4100 |
| 3052000 (`RM-107`) | 60 | Platte | 12.10.2026 | 4100 |
| 3090012 (`RM-109`) | 80 | Stk | 26.10.2026 | 4100 |
| 3090112 (`RM-110`) | 40 | Stk | 02.11.2026 | 4100 |
| 3010160 (`RM-115`) | 50 | Stange | 05.10.2026 | 4100 |

**Status:** `aktiv, uneinheitlich`

**Hinweis:** Die Kopfzeile steht an zwei Stellen: einmal in `ERP_Export!A1:G1` und einmal
als Textliteral im VBA (`Print #ff, "ARTNR;LIEFNR;..."`). Die CSV bekommt immer die
VBA-Version, die Blattzeile ist nur Anzeige. Wer die Blattzeile ändert (was der Kommentar
verbietet), merkt nichts.
Fehlt die ERP-Nummer eines Rohmaterials, meldet das Makro das und überspringt die Zeile,
der Export läuft weiter. Fehlt die ERP-Nummer des Lieferanten, wird das nicht geprüft, das
Feld bleibt leer.

## R-034 Vermerk "überfällig" in der Exportbemerkung

**Regel:** Die Bemerkung jeder Exportzeile lautet "Excel Bestellvorschlag KW&lt;aktuelle
KW&gt;" und wird um " ÜBERFÄLLIG (Bestell-KW &lt;n&gt;)" ergänzt, wenn die Bestell-KW der
Position kleiner als die aktuelle KW ist.

**Quelle:** `Modul_ERP.Export_ERP`
(`If bestellKw < kwAkt Then bem = bem & " ÜBERFÄLLIG (Bestell-KW " & bestellKw & ")"`)

**Beispiel:** `ERP_Export!G2` (`RM-106`, Bestell-KW 37): "Excel Bestellvorschlag KW39
ÜBERFÄLLIG (Bestell-KW 37)". `ERP_Export!G3` (`RM-107`, Bestell-KW 39): "Excel
Bestellvorschlag KW39".

**Status:** `aktiv`

**Hinweis:** Das ist die zweite Bedeutung von "überfällig" im Excel, siehe R-009. Die
Bemerkung geht als Freitext nach Abacus.

## R-035 Exportstempel

**Regel:** Nach jedem erfolgreichen Export werden Zeitpunkt und Kürzel der ausführenden
Person auf dem Blatt festgehalten.

**Quelle:** `Modul_ERP.Export_ERP` (`wsE.Range("J1").Value = Now`,
`wsE.Range("J2").Value = LCase(Left(Application.UserName, 2))`)

**Beispiel:** `ERP_Export!J1` = 13.09.2026 15:07, `ERP_Export!J2` = "he".

**Status:** `aktiv`

**Hinweis:** Das Kürzel sind die ersten zwei Zeichen des Windows-Benutzernamens,
kleingeschrieben. Es gibt keine Anmeldung und keine Historie, jeder Export überschreibt den
vorigen Stempel. Die App hat eine Anmeldung (`app/auth/`) und schreibt Änderungen in
`aenderungslog` (Hausregel).

## R-036 Exportdatei: Name, Format und Ablage

**Regel:** Der Export wird als CSV mit Semikolon als Trennzeichen, ANSI-Kodierung und
Datumsformat `TT.MM.JJJJ` unter dem Namen `PLAN_BESTELL_JJJJMMTT_KW<n>.csv` im Export-Pfad
abgelegt.

**Quelle:** `Modul_ERP.Export_ERP`, `Parameter!B13` (Export-Pfad), Kopfkommentar in
`Modul_ERP` ("Semikolon getrennt, ANSI, Datum TT.MM.JJJJ. Freitag ausführen, vorher
Wochenplan_aktualisieren!!"), `Übersicht!G7` ("Ctrl+Shift+E Schreibt Bestellvorschlag als
CSV (Freitag!)")

Ablauf: Export-Pfad aus `Parameter!B13` lesen, fehlenden Ordner anlegen (Kommentar im Code:
"Sandra hatte den Ordner nicht, 05.2023"), Rückfrage "Wochenplan wurde aktualisiert? Lager
ist nachgeführt?", neu rechnen, `ERP_Export!A2:G500` leeren, Zeilen schreiben, CSV
schreiben, Stempel setzen. Gibt es nichts zu bestellen, kommt eine Meldung und es wird
keine Datei geschrieben.

**Beispiel:** Bei aktueller KW 39 und Ausführung am 13.09.2026 entsteht
`PLAN_BESTELL_20260913_KW39.csv` mit 5 Datenzeilen plus Kopfzeile.

**Status:** `aktiv, uneinheitlich`

**Hinweis:** Der Ablageort ist an drei Stellen verschieden beschrieben:
`Parameter!B13` zeigt auf einen lokalen Ordner auf dem Rechner einer Person,
`Übersicht!E19` sagt "CSV liegt im Ordner ERP_Import, Sandra importiert in Abacus", und der
Kommentar auf `Parameter!B13` sagt "Abacus Import-Ordner wird von Sandra sync't". Welcher
Ordner am Ende gilt, steht nirgends eindeutig. Für die App ist der Pfad Konfiguration über
eine Umgebungsvariable (`app/config.py`), nicht ein Wert in den Fachdaten. Siehe Frage F-6.

---

# 8. Bedienung und Kennzahlen

## R-037 Auftrag abschliessen

**Regel:** Ein Auftrag wird auf `erledigt` gesetzt und bekommt den Vermerk "erledigt
TT.MM." in der Bemerkung; die vorhandene Bemerkung bleibt erhalten und wird mit "; "
ergänzt.

**Quelle:** `Modul_Planung.Auftrag_abschliessen`, Tastenkürzel `Ctrl+Shift+A`,
`Übersicht!G9`

Das Makro arbeitet auf der markierten Zeile im Blatt `Aufträge`, prüft, dass die Zeile eine
Auftragsnummer hat, und fragt nach.

**Beispiel:** `26-0388` trägt heute die Bemerkung "ausgeliefert 17.09." und den Status
`erledigt`. Diese Bemerkung ist von Hand geschrieben, nicht vom Makro (das Makro würde
"erledigt 17.09." schreiben).

**Status:** `aktiv`

**Hinweis:** Es gibt keinen Weg zurück von `erledigt` und keinen Eintrag, wer wann
abgeschlossen hat. Die App schreibt jede Änderung an einem Auftrag nach `aenderungslog`
(wer, wann, Feld, alt, neu).

## R-038 Kennzahlen der Übersicht

**Regel:** Die Übersicht zeigt sieben Kennzahlen und die Auslastung der vier Maschinen in
der aktuellen Woche.

**Quelle:** `Übersicht!A5:C18`

| Kennzahl | Zelle | Formel/Quelle | Wert heute |
|----------|-------|---------------|------------|
| Offene Aufträge (offen + in Arbeit) | `C5` | `COUNTIFS` Status `<>erledigt`, AufNr nicht leer | 47 |
| davon in Arbeit | `C6` | `COUNTIF` Status `= "in Arbeit"` | 2 |
| davon überfällig | `C7` | R-009 | 1 |
| Aufträge in aktueller KW | `C8` | `COUNTIFS` Status `<>erledigt`, KW eff. `= Parameter!B2` | 7 |
| Aufträge ausserhalb Horizont | `C9` | `=Wochenplan!B25`, R-020 | 2 |
| Bestellpositionen diese Woche | `C10` | `=Bedarf!AG20`, R-029 | 5 |
| Bestellwert diese Woche | `C11` | `=Bedarf!AH20`, R-031 | siehe Zelle |
| davon überfällig | `C12` | `COUNTIFS` Bestell-KW `< Parameter!B2` und `AG = "J"` | 2 |
| Auslastung M1 bis M4 | `C15:C18` | `INDEX/MATCH` auf `Wochenplan!B17:I21` | 58,8 / 37,5 / 74,7 / 29,2 % |

**Status:** `aktiv`

**Hinweis:** `C6` zählt ohne die Bedingung "AufNr nicht leer", die anderen Zählungen haben
sie. Bei den heutigen Daten macht das keinen Unterschied. Die Auslastungszellen suchen die
aktuelle KW mit `MATCH` in `Wochenplan!B17:I17`; steht die aktuelle KW nicht im Horizont,
liefern alle vier `#NV`.

## R-039 Sicherungskopie beim Speichern

**Regel:** Beim Speichern über den normalen Speichern-Befehl wird eine Kopie der Datei mit
Zeitstempel in einem Backup-Ordner abgelegt.

**Quelle:** `ThisWorkbook.Workbook_BeforeSave`
(`ThisWorkbook.SaveCopyAs "P:\Produktion\Planung\Backup\Produktionsplanung_" &
Format(Now, "yyyymmdd_hhnn") & ".xlsm"`), Kommentar im Code ("Sicherung, weil schon zweimal
was kaputt gegangen ist")

**Beispiel:** Ein Speichern am 13.09.2026 um 15:07 erzeugt
`Produktionsplanung_20260913_1507.xlsm`.

**Status:** `veraltet`

**Hinweis:** Der Pfad ist im Code festgeschrieben und nicht derselbe wie der Export-Pfad in
`Parameter!B13`. Bei "Speichern unter" (`SaveAsUI = True`) wird keine Kopie gemacht.
Fehler werden mit `On Error Resume Next` verschluckt, ein fehlgeschlagenes Backup meldet
sich nicht. In der App übernimmt das der Betrieb, siehe `docs/betrieb.md`.
`Übersicht!E20` beschreibt daneben noch ein zweites, manuelles Verfahren: "Datei speichern
unter P:\Produktion\Planung\ (Kopie mit Datum!)".

## R-040 Montagserinnerung und Tastenkürzel

**Regel:** Beim Öffnen der Datei werden die drei Tastenkürzel gesetzt, und montags erscheint
eine Erinnerung, die aktuelle KW zu prüfen.

**Quelle:** `ThisWorkbook.Workbook_Open`, `Workbook_BeforeClose`, `Übersicht!E5:G9`

| Kürzel | Makro | Zweck |
|--------|-------|-------|
| `Ctrl+Shift+W` | `Wochenplan_aktualisieren` | R-021 |
| `Ctrl+Shift+E` | `Export_ERP` | R-033, R-036 |
| `Ctrl+Shift+A` | `Auftrag_abschliessen` | R-037 |

Ablauf jeden Montag laut `Übersicht!E14:E20`: 1. Aktuelle KW und Montag in `Parameter`
setzen. 2. Neue Aufträge unten anfügen, keine Zeilen einfügen. 3. Lager nach Inventur
nachführen. 4. Makro Wochenplan aktualisieren, rote Felder prüfen. 5. Freitag Export ERP.
6. Datei speichern.

**Status:** `veraltet`

**Hinweis:** Die Meldung beim Öffnen und die Meldungen in `Export_ERP` sagen, das Blatt
`Parameter` sei ausgeblendet ("Rechtsklick auf Register > Einblenden"). Das stimmt nicht:
`Parameter` ist sichtbar. Ausgeblendet ist nur `Planung_2021_alt`. Ebenso steht in
`Export_ERP` die Zeile `Set wsP = ThisWorkbook.Sheets(1)` mit dem Kommentar "Parameter ist
immer das erste Blatt (ausgeblendet)", direkt danach wird sie durch
`Set wsP = ThisWorkbook.Sheets("Parameter")` korrigiert, mit dem Kommentar "seit V7 ist
Parameter nicht mehr Blatt 1". Die erste Zuweisung ist wirkungslos, die Texte sind
Altlasten aus einer früheren Version. In der App entfällt der ganze Montagsablauf.

---

# 9. Veraltet und ungenutzt

Alles in diesem Abschnitt steht in der Datei, wird aber nicht mehr gerechnet oder gebraucht.
Nichts davon wird in die App übernommen.

## Blätter

| Blatt | Zustand | Inhalt | Was damit passiert |
|-------|---------|--------|--------------------|
| `Planung_2021_alt` | versteckt | 7 Aufträge aus März und April 2021, Spalten AufNr, Kunde, Artikel, Menge, Termin, KW, Std, erledigt. Bemerkung in `J2`: "alte Version vor Umstellung auf Stückliste, nur zur Sicherheit behalten" | Nicht übernehmen. Keine Formel und kein Makro zeigt darauf. Struktur passt nicht mehr (eine Zeit statt Rüst- und Bearbeitungszeit, keine Stückliste, keine Maschine). |
| `Tabelle3` | sichtbar | `B3` = "test", `B4` = `=Aufträge!L4*2` (ergibt 31) | Nicht übernehmen. Testrest. Das Blatt ist sichtbar und rechnet auf einer echten Auftragszeile. |

## Parameter

| Zelle | Bezeichnung | Zustand |
|-------|-------------|---------|
| `Parameter!B17` | Zuschlag Edelstahl (min) = 20 | Kommentar in `C17`: "alt, wird nicht mehr verwendet (seit V5)". Keine Formel liest ihn. Es gibt keinen Edelstahl-Zuschlag mehr, nur den Alu-Zuschlag aus R-003. |
| `Parameter!B18` | Vorlauf Prio A (Wochen) = 2 | Kommentar in `C18`: "TODO: in Aufträge verlinken". Keine Formel liest ihn, R-006 hat die 2 fest eingetippt. Der Parameter ist nicht veraltet, er ist nie angeschlossen worden. Siehe Frage F-3. |

## Stammdaten

| Ort | Zustand |
|-----|---------|
| `Artikel!A22` (`A-0998`, "Welle Ø20x180 1.4301 (alt)") | Einziger Artikel mit `Aktiv = N`. Kein Auftrag verwendet ihn. Er hat trotzdem eine Stücklistenzeile (`Stückliste!A23`, Bemerkung "alt"). |
| `Artikel!H` (Aktiv) | Wird von keiner Formel gelesen. Der Flag ist reine Anzeige, ein Auftrag auf `A-0998` würde ganz normal durchrechnen. Siehe Frage F-9. |
| `Artikel!G` (Zeichnung) | Wird von keiner Formel gelesen. Reine Information. |
| `Lieferanten!C` (Ort), `G` (Kontakt), `H` (Bemerkung) | Werden von keiner Formel und keinem Makro gelesen. Reine Information. |
| `Rohmaterial!J` (Lagerort) | Wird von keiner Formel gelesen. Reine Information. |
| `Kapazität!I` (Bemerkung) | Reine Information. |

## Makros in `Modul1`

Das Modul trägt selbst den Kommentar "aufgezeichnete Makros, teilweise nicht mehr in
Gebrauch".

| Makro | Zustand |
|-------|---------|
| `Makro3` | Aufgezeichnet, formatiert die Kopfzeile `A3:V3` fett und grau. An kein Kürzel gebunden. Nicht übernehmen. |
| `Sortieren_Termin` | Sortiert `Aufträge!A4:V500` nach Liefertermin. Eigener Kommentar: "ACHTUNG: danach stimmen die Zeilennummern in Bemerkungen nicht mehr". Gefährlich, weil die Zeilen Formeln mit relativen Bezügen enthalten. An kein Kürzel gebunden. Nicht übernehmen, die App sortiert in der Ansicht. |
| `Makro5` | Leer, enthält nur den Kommentar "test". Nicht übernehmen. |

## Makro in `Modul_ERP`

| Makro | Zustand |
|-------|---------|
| `Export_ERP_alt` | Vollständig auskommentiert. Alter Export als Tabulator-Textdatei nach `C:\Temp\bestell.txt`, mit fest verdrahtetem Blattindex `Sheets(4)` und den Spalten 20 und 19, die im heutigen Blatt `Bedarf` etwas anderes bedeuten. Kommentar: "wird nicht mehr gebraucht seit Abacus Update". Nicht übernehmen. |

## Sonstiges

- **Kein einziges Dropdown.** Im ganzen Excel ist keine Datenprüfung definiert, obwohl
  mehrere Kommentare exakte Schreibweisen verlangen (R-008, R-010).
- **Drei verschiedene Tabellenenden im Blatt `Aufträge`:** Formeln bis Zeile 53, bedingte
  Formatierung bis Zeile 93, `SUMIFS` und `COUNTIFS` bis Zeile 500, Autofilter bis Zeile 53.
  Ein Auftrag in Zeile 54 hätte keine Formeln, würde aber in den Summen mitgezählt, sobald
  jemand die Werte von Hand einträgt.
- **Feste Obergrenzen in den Nachschlagebereichen:** `Artikel!$A$2:$H$60` (21 Artikel
  vorhanden), `Stückliste!$A$2:$F$50` (22 Positionen), `Lieferanten!$A$2:$H$20`
  (5 Lieferanten), `Bedarf` Zeile 4 bis 18 fest auf `Rohmaterial` Zeile 2 bis 16
  (15 Rohmaterialien). **Ein 16. Rohmaterial erscheint nicht im Blatt `Bedarf`** und damit
  nicht im Bestellvorschlag, ohne jede Meldung. Die Exportschleife läuft `For r = 4 To 60`
  und bricht beim ersten leeren Feld ab.
- **`Bedarf!R` ist ausgeblendet**, wird aber gebraucht (`S4 = R4+E4`, R-026). Nicht
  veraltet, nur unsichtbar.
- **Änderungsprotokoll** in `Parameter!A21:A26`: 03.2024 V7.3 Alu-Zuschlag als Parameter,
  11.2023 V7.2 Wartungswochen in Kapazität, 06.2022 V6.0 Export auf Abacus-Format
  umgestellt, 01.2021 V5.0 Stückliste mit 2 Positionen, 2019 V1 erste Version. Alle
  Einträge tragen dasselbe Kürzel.

---

# 10. Offene Fragen

Diese Punkte lassen sich aus der Datei nicht eindeutig beantworten. Sie sind vor dem Bau
der betroffenen Regel zu klären, weil es je nach Antwort ein anderes Ergebnis gibt.

| Nr | Betrifft | Frage | Heute betroffen |
|----|----------|-------|-----------------|
| F-1 | R-003 | Der Alu-Zuschlag ist in `Aufträge!K` dreifach umgesetzt (Parameter, feste 500/40, gar nicht). Welche Variante ist die richtige? Und gilt die Losgrenze als "mehr als 500" oder "ab 500"? | 1 Auftrag rechnet falsch (`26-0430`, 40 min zu wenig), 29 von 50 Zeilen hängen nicht am Parameter |
| F-2 | R-014 | `Kapazität` M3 hat Schichten, Stunden und Tage fest eingetippt, M1/M2/M4 lesen sie aus `Parameter`. Ist M3 bewusst anders oder ist das ein Versehen? | 1 von 4 Maschinen, heute gleiches Ergebnis |
| F-3 | R-006 | `Parameter!B18` "Vorlauf Prio A" = 2 ist nie angeschlossen. Soll der Vorlauf je Priorität ein Parameter werden (A, B, C getrennt), oder bleibt es bei fest 2 und 1? | alle 50 Aufträge |
| F-4 | R-019, R-024 | Der Horizont steht als Parameter (8) da, wird aber nirgends gelesen. Soll er in der App wirklich einstellbar sein, oder fest bei 8 Wochen bleiben? | Wochenplan und Bedarf komplett |
| F-5 | R-005, R-032 | Wie soll sich die Plan-KW über den Jahreswechsel verhalten? Beispiel: Liefertermin in KW 1, Prio A. Ergebnis soll KW 51 des Vorjahres sein, richtig? Und der Horizont läuft dann von KW 50 über KW 52 in KW 1 bis 4? | heute keiner, ab Dezember alle |
| F-6 | R-036 | Wohin geht die CSV wirklich? `Parameter!B13` zeigt auf einen lokalen Ordner, `Übersicht!E19` spricht von "ERP_Import". Welcher Pfad gilt für die App? | jeder Export |
| F-7 | R-011 | Soll ein Auftrag auf eine andere als die Standardmaschine des Artikels umgeplant werden können? Der Kommentar auf `Artikel!D1` sagt ja, im Blatt `Aufträge` gibt es dafür kein Feld. | heute 0 von 50, aber laut Kommentar vorgesehen |
| F-8 | R-012 | Bleibt die Grenze von zwei Stücklistenpositionen je Artikel, oder soll die App beliebig viele können? Die Grenze kommt nur von der Spaltenbreite im Excel. | 1 Artikel nutzt heute 2 Positionen (`A-1019`) |
| F-9 | R-011 | Soll ein Artikel mit `Aktiv = N` in neuen Aufträgen gesperrt sein? Im Excel hat der Flag keine Wirkung. | 1 Artikel (`A-0998`), 0 Aufträge |
| F-10 | R-023 | Sollen offene Bestellungen mit einem erwarteten Ankunftsdatum geführt werden? Heute zählen sie ab sofort als verfügbar, was die Fehl-KW zu spät ausweisen kann. | 3 Rohmaterialien mit offener Bestellung (`RM-102`, `RM-105`, `RM-110`) |
