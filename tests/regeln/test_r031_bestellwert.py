"""R-031: Bestellwert einer Position."""

from decimal import Decimal

from app.regeln.material import bestellwert


def test_r031_menge_mal_preis():
    assert bestellwert(Decimal("20.0"), Decimal("45.50")) == Decimal("910.00")


def test_r031_geld_ist_immer_decimal(rohmaterial):
    zeile = rohmaterial("RM-109")
    assert isinstance(zeile.bestellwert, Decimal)
    assert zeile.bestellwert == zeile.bestellmenge * zeile.preis


def test_r031_ohne_bestellmenge_kein_wert(stand):
    for zeile in stand.material:
        if zeile.bestellmenge == 0:
            assert zeile.bestellwert == Decimal("0.00")


def test_r031_wochenwert_ist_die_summe_der_ja_zeilen(stand):
    summe = sum(zeile.bestellwert for zeile in stand.bestellvorschlaege)
    assert stand.kennzahlen.bestellwert == summe
    assert summe > 0
