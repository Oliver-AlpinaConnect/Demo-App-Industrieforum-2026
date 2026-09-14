"""R-024: Durchschnittlicher Wochenbedarf."""

from decimal import Decimal

import pytest

from app.regeln.material import durchschnittlicher_wochenbedarf


def test_r024_summe_durch_anzahl_wochen():
    # RM-107: 73,6 / 8 = 9,2 Platten je Woche.
    assert durchschnittlicher_wochenbedarf(Decimal("73.6"), 8) == Decimal("9.2")


def test_r024_beispiele_aus_den_testdaten(rohmaterial):
    assert rohmaterial("RM-107").durchschnitt == Decimal("9.2")
    # RM-110: 790,0 / 8 = 98,75 -> 98,8.
    assert rohmaterial("RM-110").durchschnitt == Decimal("98.8")


def test_r024_teiler_ist_die_laenge_des_horizonts(stand, parameter):
    # Im Excel steht dort eine feste 8 (F-4).
    for zeile in stand.material:
        assert zeile.durchschnitt == durchschnittlicher_wochenbedarf(
            zeile.summe_horizont, len(stand.horizont)
        )
    assert len(stand.horizont) == parameter.ganzzahl("planungshorizont_wochen")


def test_r024_horizont_ohne_wochen_wird_abgelehnt():
    with pytest.raises(ValueError):
        durchschnittlicher_wochenbedarf(Decimal("73.6"), 0)
