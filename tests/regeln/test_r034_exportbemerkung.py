"""R-034: Vermerk "überfällig" in der Exportbemerkung."""

from app.regeln.export import export_bemerkung
from app.regeln.typen import Kalenderwoche

AKTUELL = Kalenderwoche(2026, 39)


def test_r034_bemerkung_ohne_ueberfaelligkeit():
    assert export_bemerkung(AKTUELL, AKTUELL) == "Bestellvorschlag KW39"


def test_r034_bemerkung_mit_ueberfaelligkeit():
    assert (
        export_bemerkung(AKTUELL, Kalenderwoche(2026, 37))
        == "Bestellvorschlag KW39 ÜBERFÄLLIG (Bestell-KW 37)"
    )


def test_r034_ohne_bestell_kw_bleibt_der_grundtext():
    assert export_bemerkung(AKTUELL, None) == "Bestellvorschlag KW39"


def test_r034_bestell_kw_in_der_zukunft_ist_nicht_ueberfaellig():
    assert export_bemerkung(AKTUELL, Kalenderwoche(2026, 41)) == "Bestellvorschlag KW39"
