"""R-036: Name, Format und Kodierung der Exportdatei."""

from datetime import date
from decimal import Decimal

from app.regeln.export import (
    KODIERUNG,
    TRENNZEICHEN,
    Exportposition,
    csv_bytes,
    csv_text,
    exportdateiname,
    exportzeilen,
)
from app.regeln.typen import Kalenderwoche

AKTUELL = Kalenderwoche(2026, 39)

POSITION = Exportposition(
    rohnummer="RM-106",
    erp_artikelnummer="3050800",
    erp_lieferantennummer="L02001",
    bestellmenge=Decimal("35.0"),
    einheit="Stange",
    bedarfsdatum=date(2026, 9, 28),
    bestell_kw=Kalenderwoche(2026, 37),
)


def test_r036_dateiname():
    assert exportdateiname(date(2026, 9, 13), AKTUELL) == "PLAN_BESTELL_20260913_KW39.csv"


def test_r036_semikolon_und_kopfzeile():
    zeilen = exportzeilen([POSITION], AKTUELL, 4100).zeilen
    text = csv_text(zeilen)
    assert TRENNZEICHEN == ";"
    assert text.splitlines()[0] == "ARTNR;LIEFNR;MENGE;EINHEIT;BEDARFSDATUM;KOSTENSTELLE;BEMERKUNG"
    assert text.splitlines()[1].startswith("3050800;L02001;35;Stange;28.09.2026;4100;")


def test_r036_ansi_kodierung():
    zeilen = exportzeilen([POSITION], AKTUELL, 4100).zeilen
    roh = csv_bytes(zeilen)
    assert KODIERUNG == "cp1252"
    assert "ÜBERFÄLLIG".encode("cp1252") in roh
    assert "ÜBERFÄLLIG".encode() not in roh


def test_r036_ohne_positionen_bleibt_die_kopfzeile_allein():
    assert csv_text([]).strip() == "ARTNR;LIEFNR;MENGE;EINHEIT;BEDARFSDATUM;KOSTENSTELLE;BEMERKUNG"


def test_r036_datum_immer_tt_mm_jjjj():
    zeile = exportzeilen([POSITION], AKTUELL, 4100).zeilen[0]
    assert zeile.bedarfsdatum == "28.09.2026"
