"""R-030: Bestellmenge wird auf ganze Gebinde aufgerundet."""

from decimal import Decimal

import pytest

from app.regeln.material import bestellmenge
from app.regeln.typen import Kalenderwoche

FEHL = Kalenderwoche(2026, 44)


def test_r030_bedarf_plus_sicherheit_minus_bestand_auf_gebinde():
    # RM-109: 140,0 + 20 - 90 = 70, Gebinde 20 -> 3,5 -> 4 Gebinde -> 80.
    assert bestellmenge(Decimal("140.0"), Decimal(20), Decimal(90), Decimal(20), FEHL) == Decimal(
        "80.0"
    )
    # RM-101: 32,2 + 10 - 24 = 18,2, Gebinde 10 -> 2 Gebinde -> 20.
    assert bestellmenge(Decimal("32.2"), Decimal(10), Decimal(24), Decimal(10), FEHL) == Decimal(
        "20.0"
    )


def test_r030_ohne_fehl_kw_ist_die_menge_null():
    assert bestellmenge(Decimal("140.0"), Decimal(20), Decimal(90), Decimal(20), None) == Decimal(
        "0.0"
    )


def test_r030_nie_negativ():
    assert bestellmenge(Decimal("10.0"), Decimal(5), Decimal(1000), Decimal(20), FEHL) == Decimal(
        "0.0"
    )


def test_r030_mengen_der_testdaten(rohmaterial):
    erwartet = {
        "RM-106": Decimal("35.0"),
        "RM-107": Decimal("60.0"),
        "RM-109": Decimal("80.0"),
        "RM-110": Decimal("40.0"),
        "RM-115": Decimal("50.0"),
    }
    for nummer, menge in erwartet.items():
        assert rohmaterial(nummer).bestellmenge == menge


def test_r030_menge_ist_immer_ein_vielfaches_des_gebindes(stand):
    for zeile in stand.material:
        if zeile.bestellmenge:
            assert zeile.bestellmenge % zeile.gebinde == 0


def test_r030_gebinde_null_wird_abgelehnt():
    with pytest.raises(ValueError):
        bestellmenge(Decimal("10.0"), Decimal(5), Decimal(0), Decimal(0), FEHL)
