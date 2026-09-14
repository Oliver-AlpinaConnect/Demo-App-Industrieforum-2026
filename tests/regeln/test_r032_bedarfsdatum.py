"""R-032: Bedarfsdatum einer Bestellposition."""

from datetime import date

from app.regeln.material import bedarfsdatum
from app.regeln.typen import Kalenderwoche


def test_r032_montag_der_fehl_kw():
    # RM-109: Fehl-KW 44 -> 26.10.2026.
    assert bedarfsdatum(Kalenderwoche(2026, 44)) == date(2026, 10, 26)
    # RM-106: Fehl-KW 40 -> 28.09.2026.
    assert bedarfsdatum(Kalenderwoche(2026, 40)) == date(2026, 9, 28)


def test_r032_ohne_fehl_kw_kein_datum():
    assert bedarfsdatum(None) is None


def test_r032_stimmt_auch_ueber_den_jahreswechsel():
    # Das Excel rechnet Montag der aktuellen KW plus Wochendifferenz mal 7 und
    # liegt über den Jahreswechsel falsch.
    assert bedarfsdatum(Kalenderwoche(2027, 1)) == date(2027, 1, 4)


def test_r032_daten_der_testdaten(rohmaterial):
    erwartet = {
        "RM-106": date(2026, 9, 28),
        "RM-107": date(2026, 10, 12),
        "RM-109": date(2026, 10, 26),
        "RM-110": date(2026, 11, 2),
        "RM-115": date(2026, 10, 5),
    }
    for nummer, tag in erwartet.items():
        assert rohmaterial(nummer).bedarfsdatum == tag
        assert tag.weekday() == 0
