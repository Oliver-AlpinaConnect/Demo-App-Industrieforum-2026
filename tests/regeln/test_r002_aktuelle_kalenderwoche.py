"""R-002: Die aktuelle KW kommt aus dem Datum, nicht aus einer Handeingabe."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from app.regeln.parameter import aktuelle_kalenderwoche, montag_der_woche
from app.regeln.typen import Kalenderwoche

ZUERICH = ZoneInfo("Europe/Zurich")


def test_r002_woche_aus_dem_datum():
    # 21.09.2026 ist der Montag der ISO-Woche 39, so steht es in Parameter!B4.
    jetzt = datetime(2026, 9, 21, 8, 0, tzinfo=ZUERICH)
    assert aktuelle_kalenderwoche(jetzt) == Kalenderwoche(2026, 39)


def test_r002_montag_der_woche():
    assert montag_der_woche(Kalenderwoche(2026, 39)) == date(2026, 9, 21)


def test_r002_jahreswechsel_ohne_handarbeit():
    # Der 1. Januar 2027 liegt noch in der ISO-Woche 53 von 2026.
    assert aktuelle_kalenderwoche(datetime(2027, 1, 1, 9, 0, tzinfo=ZUERICH)) == Kalenderwoche(
        2026, 53
    )
    assert aktuelle_kalenderwoche(datetime(2027, 1, 4, 9, 0, tzinfo=ZUERICH)) == Kalenderwoche(
        2027, 1
    )


def test_r002_zeitpunkt_ohne_zeitzone_wird_abgelehnt():
    with pytest.raises(ValueError):
        aktuelle_kalenderwoche(datetime(2026, 9, 21, 8, 0))
