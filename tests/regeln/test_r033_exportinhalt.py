"""R-033: Inhalt und Reihenfolge der Exportdatei."""

from datetime import date
from decimal import Decimal

from app.regeln.export import KOPFZEILE, Exportposition, exportzeilen
from app.regeln.typen import Kalenderwoche

AKTUELL = Kalenderwoche(2026, 39)

RM109 = Exportposition(
    rohnummer="RM-109",
    erp_artikelnummer="3090012",
    erp_lieferantennummer="L04001",
    bestellmenge=Decimal("80.0"),
    einheit="Stk",
    bedarfsdatum=date(2026, 10, 26),
    bestell_kw=Kalenderwoche(2026, 38),
)


def test_r033_sieben_felder_in_fester_reihenfolge():
    assert KOPFZEILE == (
        "ARTNR",
        "LIEFNR",
        "MENGE",
        "EINHEIT",
        "BEDARFSDATUM",
        "KOSTENSTELLE",
        "BEMERKUNG",
    )
    zeile = exportzeilen([RM109], AKTUELL, 4100).zeilen[0]
    assert zeile.als_liste() == [
        "3090012",
        "L04001",
        "80",
        "Stk",
        "26.10.2026",
        "4100",
        "Bestellvorschlag KW39 ÜBERFÄLLIG (Bestell-KW 38)",
    ]


def test_r033_erp_nummer_bleibt_text():
    position = Exportposition(
        rohnummer="RM-120",
        erp_artikelnummer="0301500",
        erp_lieferantennummer="L01001",
        bestellmenge=Decimal("10.0"),
        einheit="Stange",
        bedarfsdatum=date(2026, 10, 5),
        bestell_kw=AKTUELL,
    )
    assert exportzeilen([position], AKTUELL, 4100).zeilen[0].artnr == "0301500"


def test_r033_fehlende_erp_nummer_meldet_und_ueberspringt():
    ohne_artikel = Exportposition(
        rohnummer="RM-121",
        erp_artikelnummer="",
        erp_lieferantennummer="L01001",
        bestellmenge=Decimal("10.0"),
        einheit="Stange",
        bedarfsdatum=date(2026, 10, 5),
        bestell_kw=AKTUELL,
    )
    ergebnis = exportzeilen([ohne_artikel, RM109], AKTUELL, 4100)
    assert len(ergebnis.zeilen) == 1
    assert "RM-121" in ergebnis.meldungen[0]


def test_r033_fehlende_lieferantennummer_wird_auch_gemeldet():
    # Im Excel blieb das Feld still leer.
    ohne_lieferant = Exportposition(
        rohnummer="RM-122",
        erp_artikelnummer="3090012",
        erp_lieferantennummer="",
        bestellmenge=Decimal("10.0"),
        einheit="Stk",
        bedarfsdatum=date(2026, 10, 5),
        bestell_kw=AKTUELL,
    )
    ergebnis = exportzeilen([ohne_lieferant], AKTUELL, 4100)
    assert ergebnis.zeilen == []
    assert "RM-122" in ergebnis.meldungen[0]


def test_r033_ganze_mengen_ohne_dezimale():
    assert exportzeilen([RM109], AKTUELL, 4100).zeilen[0].menge == "80"
