"""R-023: Verfügbarer Bestand."""

from decimal import Decimal

from app.regeln.material import verfuegbarer_bestand


def test_r023_lager_plus_offene_bestellungen():
    assert verfuegbarer_bestand(Decimal(6), Decimal(5)) == Decimal("11.0")
    assert verfuegbarer_bestand(Decimal(620), Decimal(200)) == Decimal("820.0")


def test_r023_beispiele_aus_den_testdaten(rohmaterial):
    rm102 = rohmaterial("RM-102")
    assert rm102.lager == Decimal("6.0")
    assert rm102.bestellt_offen == Decimal("5.0")
    assert rm102.verfuegbar == Decimal("11.0")

    rm110 = rohmaterial("RM-110")
    assert rm110.verfuegbar == Decimal("820.0")


def test_r023_ohne_offene_bestellung_zaehlt_nur_das_lager(rohmaterial):
    rm106 = rohmaterial("RM-106")
    assert rm106.bestellt_offen == Decimal("0.0")
    assert rm106.verfuegbar == rm106.lager


def test_r023_offene_bestellung_zaehlt_ohne_ankunftswoche(rohmaterial):
    # Eine Bestellung, die erst in KW 45 eintrifft, zählt schon in KW 39 (offene Frage F-10).
    rm110 = rohmaterial("RM-110")
    assert rm110.verfuegbar == rm110.lager + rm110.bestellt_offen
