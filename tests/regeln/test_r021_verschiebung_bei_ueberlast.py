"""R-021: Automatische Verschiebung bei Überlast."""

from decimal import Decimal

from app.regeln.kapazitaet import Planauftrag, verschiebungen
from app.regeln.typen import Kalenderwoche, Prioritaet, Status

KW40 = Kalenderwoche(2026, 40)
KW41 = Kalenderwoche(2026, 41)
HORIZONT = [KW40, KW41]
KAPAZITAET = {("M1", KW40): Decimal("68.0"), ("M1", KW41): Decimal("68.0")}
GRENZE = Decimal("0.9")


def _auftrag(nummer, stunden, prioritaet=Prioritaet.C, status=Status.OFFEN, kw=KW40):
    return Planauftrag(
        auftragsnummer=nummer,
        maschine="M1",
        kw_effektiv=kw,
        liefer_kw=kw.plus(1),
        gesamtzeit_h=Decimal(stunden),
        status=status,
        prioritaet=prioritaet,
    )


def test_r021_ohne_ueberlast_wird_nichts_verschoben():
    auftraege = [_auftrag("A", "40.0"), _auftrag("B", "20.0")]
    assert verschiebungen(auftraege, ["M1"], HORIZONT, KAPAZITAET, GRENZE) == []


def test_r021_kleinster_auftrag_der_die_ueberlast_allein_beseitigt():
    # Kapazität 68,0 h, Grenze 90 %, Limit 61,2 h.
    # Belastung 70,0 h, Überlast 8,8 h. Der kleinste Auftrag, der sie allein
    # beseitigt, ist der mit 10,0 h, nicht der grösste.
    auftraege = [
        _auftrag("gross", "40.0"),
        _auftrag("mittel", "20.0"),
        _auftrag("passend", "10.0"),
    ]
    ergebnis = verschiebungen(auftraege, ["M1"], HORIZONT, KAPAZITAET, GRENZE)
    assert [schritt.auftragsnummer for schritt in ergebnis] == ["passend"]
    assert ergebnis[0].von_kw == KW40
    assert ergebnis[0].nach_kw == KW41


def test_r021_reicht_keiner_allein_kommt_der_groesste_dran():
    # 60,0 h Prio A sind nicht verschiebbar, Überlast 8,8 h. Weder 4,0 noch 6,0
    # beseitigen sie allein, deshalb geht zuerst der grösste der beiden.
    auftraege = [
        _auftrag("eil", "60.0", prioritaet=Prioritaet.A),
        _auftrag("klein", "4.0"),
        _auftrag("groesser", "6.0"),
    ]
    ergebnis = verschiebungen(auftraege, ["M1"], HORIZONT, KAPAZITAET, GRENZE)
    assert ergebnis[0].auftragsnummer == "groesser"


def test_r021_prio_c_kommt_vor_prio_b():
    auftraege = [
        _auftrag("b-auftrag", "20.0", prioritaet=Prioritaet.B),
        _auftrag("c-auftrag", "20.0", prioritaet=Prioritaet.C),
        _auftrag("rest", "30.0", prioritaet=Prioritaet.B),
    ]
    ergebnis = verschiebungen(auftraege, ["M1"], HORIZONT, KAPAZITAET, GRENZE)
    assert ergebnis[0].auftragsnummer == "c-auftrag"


def test_r021_prio_a_und_in_arbeit_werden_nie_verschoben():
    auftraege = [
        _auftrag("eil", "40.0", prioritaet=Prioritaet.A),
        _auftrag("laufend", "30.0", status=Status.IN_ARBEIT),
    ]
    assert verschiebungen(auftraege, ["M1"], HORIZONT, KAPAZITAET, GRENZE) == []


def test_r021_nichts_wird_ueber_das_horizontende_hinaus_geschoben():
    # Im Excel schreibt das Makro kw + 1 und schiebt den Auftrag aus der Planung.
    auftraege = [_auftrag("a", "40.0", kw=KW41), _auftrag("b", "30.0", kw=KW41)]
    assert verschiebungen(auftraege, ["M1"], HORIZONT, KAPAZITAET, GRENZE) == []


def test_r021_die_funktion_aendert_die_eingabe_nicht():
    auftraege = [_auftrag("gross", "40.0"), _auftrag("passend", "25.0")]
    verschiebungen(auftraege, ["M1"], HORIZONT, KAPAZITAET, GRENZE)
    assert all(eintrag.kw_effektiv == KW40 for eintrag in auftraege)


def test_r021_vorschlaege_in_den_testdaten(stand):
    # M3 liegt in KW 40 mit 94,7 % über der Grenze von 90 %.
    assert stand.verschiebungen
    erster = stand.verschiebungen[0]
    assert erster.maschine == "M3"
    assert erster.von_kw == Kalenderwoche(2026, 40)
    assert erster.nach_kw == Kalenderwoche(2026, 41)
    for schritt in stand.verschiebungen:
        zeile = next(
            eintrag
            for eintrag in stand.auftraege
            if eintrag.auftragsnummer == schritt.auftragsnummer
        )
        assert zeile.status is Status.OFFEN
        assert zeile.prioritaet is not Prioritaet.A
