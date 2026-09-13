"""Verzeichnis aller Regeln aus `docs/regeln.md`.

Eine Zeile je Regel-ID: Titel, Status aus dem Katalog, Modul und Funktion in
`app/regeln/`. Die Seite Regeln zeigt diese Liste neben dem Katalogtext, und der Test
`tests/regeln/test_katalog_vollstaendig.py` vergleicht sie mit `docs/regeln.md`.
"""

from __future__ import annotations

from dataclasses import dataclass

UMSETZUNG_ENTFAELLT = "entfällt"


@dataclass(frozen=True)
class Regeleintrag:
    """Eine Regel und die Stelle im Code, an der sie steht."""

    id: str
    titel: str
    status: str
    modul: str
    funktionen: tuple[str, ...]

    @property
    def umgesetzt(self) -> bool:
        return self.modul != UMSETZUNG_ENTFAELLT


KATALOG: tuple[Regeleintrag, ...] = (
    Regeleintrag(
        "R-001",
        "Alle Stellschrauben stehen im Blatt Parameter",
        "aktiv, uneinheitlich",
        "app.regeln.parameter",
        ("Parameter",),
    ),
    Regeleintrag(
        "R-002",
        "Aktuelle KW und Montagsdatum werden von Hand gesetzt",
        "manuell",
        "app.regeln.parameter",
        ("aktuelle_kalenderwoche", "montag_der_woche"),
    ),
    Regeleintrag(
        "R-003",
        "Rüstzeit je Auftrag, mit Zuschlag für Alu über der Losgrenze",
        "aktiv, uneinheitlich",
        "app.regeln.zeiten",
        ("ruestzeit_minuten",),
    ),
    Regeleintrag(
        "R-004",
        "Bearbeitungszeit und Gesamtzeit je Auftrag",
        "aktiv",
        "app.regeln.zeiten",
        ("bearbeitungszeit_stunden", "gesamtzeit_stunden"),
    ),
    Regeleintrag(
        "R-005",
        "Liefer-KW aus dem Liefertermin, ISO-Woche",
        "aktiv, uneinheitlich",
        "app.regeln.termine",
        ("liefer_kw",),
    ),
    Regeleintrag(
        "R-006",
        "Plan-KW aus Liefer-KW und Priorität",
        "aktiv, uneinheitlich",
        "app.regeln.termine",
        ("plan_kw",),
    ),
    Regeleintrag(
        "R-007",
        "KW eff.: manuelle Woche schlägt Plan-KW",
        "aktiv",
        "app.regeln.termine",
        ("kw_effektiv",),
    ),
    Regeleintrag(
        "R-008",
        "Status eines Auftrags",
        "aktiv",
        "app.regeln.termine",
        ("ist_laufend", "status_aus_text"),
    ),
    Regeleintrag(
        "R-009", "Überfälliger Auftrag", "aktiv", "app.regeln.termine", ("ist_ueberfaellig",)
    ),
    Regeleintrag(
        "R-010",
        "Material-Schreibweise ist exakt",
        "aktiv",
        "app.regeln.stammdaten",
        ("material_ist_bekannt", "pruefe_material"),
    ),
    Regeleintrag(
        "R-011",
        "Artikel bestimmt Bezeichnung, Material, Maschine und Zeiten des Auftrags",
        "aktiv, uneinheitlich",
        "app.regeln.stammdaten",
        ("auftragsstammdaten", "maschine_des_auftrags", "darf_beauftragt_werden"),
    ),
    Regeleintrag(
        "R-012",
        "Stückliste: Schlüssel aus Artikel und Position, maximal zwei Positionen",
        "aktiv",
        "app.regeln.stammdaten",
        ("stueckliste_schluessel",),
    ),
    Regeleintrag(
        "R-013",
        "Rohmaterialbedarf je Auftragsposition",
        "aktiv",
        "app.regeln.stammdaten",
        ("rohmaterialbedarf",),
    ),
    Regeleintrag(
        "R-014",
        "Kapazität einer Maschine pro Woche",
        "aktiv, uneinheitlich",
        "app.regeln.kapazitaet",
        ("wochenkapazitaet_stunden",),
    ),
    Regeleintrag(
        "R-015",
        "Wartungswoche zieht einen festen Betrag ab",
        "aktiv",
        "app.regeln.kapazitaet",
        ("kapazitaet_der_woche",),
    ),
    Regeleintrag(
        "R-016",
        "Belastung einer Maschine in einer Woche",
        "aktiv, uneinheitlich",
        "app.regeln.kapazitaet",
        ("belastung_stunden",),
    ),
    Regeleintrag("R-017", "Auslastung", "aktiv", "app.regeln.kapazitaet", ("auslastung",)),
    Regeleintrag(
        "R-018", "Auslastungsampel", "aktiv, uneinheitlich", "app.regeln.kapazitaet", ("ampel",)
    ),
    Regeleintrag(
        "R-019",
        "Planungshorizont: acht Wochen ab der aktuellen KW",
        "aktiv, uneinheitlich",
        "app.regeln.kapazitaet",
        ("horizont",),
    ),
    Regeleintrag(
        "R-020",
        "Aufträge ausserhalb des Horizonts fallen aus der Planung",
        "aktiv",
        "app.regeln.kapazitaet",
        ("ausserhalb_horizont",),
    ),
    Regeleintrag(
        "R-021",
        "Automatische Verschiebung bei Überlast",
        "aktiv",
        "app.regeln.kapazitaet",
        ("verschiebungen",),
    ),
    Regeleintrag(
        "R-022",
        "Bedarf je Rohmaterial und Woche",
        "aktiv",
        "app.regeln.material",
        ("bedarf_der_woche", "bedarf_je_woche"),
    ),
    Regeleintrag(
        "R-023", "Verfügbarer Bestand", "aktiv", "app.regeln.material", ("verfuegbarer_bestand",)
    ),
    Regeleintrag(
        "R-024",
        "Durchschnittlicher Wochenbedarf",
        "aktiv, uneinheitlich",
        "app.regeln.material",
        ("durchschnittlicher_wochenbedarf",),
    ),
    Regeleintrag(
        "R-025", "Sicherheitsbestand", "aktiv", "app.regeln.material", ("sicherheitsbestand",)
    ),
    Regeleintrag(
        "R-026", "Kumulierter Bedarf", "aktiv", "app.regeln.material", ("kumulierter_bedarf",)
    ),
    Regeleintrag("R-027", "Fehl-KW", "aktiv", "app.regeln.material", ("fehl_kw",)),
    Regeleintrag("R-028", "Bestell-KW", "aktiv", "app.regeln.material", ("bestell_kw",)),
    Regeleintrag(
        "R-029",
        "Bestellen ja oder nein",
        "aktiv",
        "app.regeln.material",
        ("bestellen", "bestellung_ueberfaellig"),
    ),
    Regeleintrag(
        "R-030",
        "Bestellmenge wird auf Gebinde aufgerundet",
        "aktiv",
        "app.regeln.material",
        ("bestellmenge",),
    ),
    Regeleintrag("R-031", "Bestellwert", "aktiv", "app.regeln.material", ("bestellwert",)),
    Regeleintrag(
        "R-032", "Bedarfsdatum", "aktiv, uneinheitlich", "app.regeln.material", ("bedarfsdatum",)
    ),
    Regeleintrag(
        "R-033",
        "Inhalt und Reihenfolge der Exportdatei",
        "aktiv, uneinheitlich",
        "app.regeln.export",
        ("exportzeilen",),
    ),
    Regeleintrag(
        "R-034",
        'Vermerk "überfällig" in der Exportbemerkung',
        "aktiv",
        "app.regeln.export",
        ("export_bemerkung",),
    ),
    Regeleintrag("R-035", "Exportstempel", "aktiv", "app.regeln.export", ("exportstempel",)),
    Regeleintrag(
        "R-036",
        "Exportdatei: Name, Format und Ablage",
        "aktiv, uneinheitlich",
        "app.regeln.export",
        ("csv_text", "csv_bytes", "exportdateiname"),
    ),
    Regeleintrag(
        "R-037", "Auftrag abschliessen", "aktiv", "app.regeln.bedienung", ("auftrag_abschliessen",)
    ),
    Regeleintrag(
        "R-038", "Kennzahlen der Übersicht", "aktiv", "app.regeln.bedienung", ("kennzahlen",)
    ),
    Regeleintrag(
        "R-039",
        "Sicherungskopie beim Speichern",
        "veraltet",
        "app.regeln.veraltet",
        ("sicherungskopie_beim_speichern",),
    ),
    Regeleintrag(
        "R-040",
        "Montagserinnerung und Tastenkürzel",
        "veraltet",
        "app.regeln.veraltet",
        ("montagserinnerung_und_tastenkuerzel",),
    ),
)

NACH_ID: dict[str, Regeleintrag] = {eintrag.id: eintrag for eintrag in KATALOG}


def regel(regel_id: str) -> Regeleintrag:
    """Eine Regel aus dem Verzeichnis holen. Beispiel: regel("R-003")."""
    if regel_id not in NACH_ID:
        raise KeyError(f"Regel {regel_id} steht nicht im Verzeichnis")
    return NACH_ID[regel_id]
