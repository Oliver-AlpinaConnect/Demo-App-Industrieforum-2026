"""R-027: Fehl-KW."""

from decimal import Decimal

import pytest

from app.regeln.kapazitaet import horizont
from app.regeln.material import fehl_kw, kumulierter_bedarf
from app.regeln.typen import Kalenderwoche

HORIZONT = horizont(Kalenderwoche(2026, 39), 8)


def test_r027_erste_woche_in_der_bedarf_plus_sicherheit_den_bestand_uebersteigt():
    # RM-106: verfügbar 5, Sicherheit 5, kumuliert 0 / 13,3 / ... -> Fehl-KW 40.
    kumuliert = [
        Decimal(wert) for wert in ["0", "13.3", "13.3", "13.3", "21.7", "21.7", "26.9", "31.5"]
    ]
    assert fehl_kw(HORIZONT, kumuliert, Decimal(5), Decimal(5)) == Kalenderwoche(2026, 40)


def test_r027_reicht_der_bestand_gibt_es_keine_fehl_kw():
    kumuliert = kumulierter_bedarf([Decimal("1.0")] * 8)
    assert fehl_kw(HORIZONT, kumuliert, Decimal(0), Decimal(1000)) is None


def test_r027_bei_gleichstand_reicht_der_bestand():
    # Der Vergleich ist echt grösser als.
    kumuliert = [Decimal("10.0")] * 8
    assert fehl_kw(HORIZONT, kumuliert, Decimal(5), Decimal(15)) is None
    assert fehl_kw(HORIZONT, kumuliert, Decimal(5), Decimal("14.9")) == HORIZONT[0]


def test_r027_fehl_kw_der_bestellpositionen(stand, rohmaterial):
    erwartet = {
        "RM-106": Kalenderwoche(2026, 40),
        "RM-107": Kalenderwoche(2026, 42),
        "RM-109": Kalenderwoche(2026, 44),
        "RM-110": Kalenderwoche(2026, 45),
        "RM-115": Kalenderwoche(2026, 41),
    }
    for nummer, woche in erwartet.items():
        assert rohmaterial(nummer).fehl_kw == woche


def test_r027_reihe_und_horizont_muessen_gleich_lang_sein():
    with pytest.raises(ValueError):
        fehl_kw(HORIZONT, [Decimal(1)], Decimal(0), Decimal(0))
