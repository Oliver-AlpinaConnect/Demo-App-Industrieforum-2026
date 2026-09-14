"""R-008: Status eines Auftrags, exakt geschrieben."""

import pytest

from app.regeln.termine import ist_laufend, status_aus_text
from app.regeln.typen import Status


def test_r008_alles_ausser_erledigt_ist_laufend():
    assert ist_laufend(Status.OFFEN)
    assert ist_laufend(Status.IN_ARBEIT)
    assert not ist_laufend(Status.ERLEDIGT)


def test_r008_status_wird_exakt_gelesen():
    assert status_aus_text("in Arbeit") is Status.IN_ARBEIT
    for falsch in ["Offen", "erledigt ", "ERLEDIGT", "abgeschlossen"]:
        with pytest.raises(ValueError):
            status_aus_text(falsch)


def test_r008_verteilung_in_den_testdaten(stand):
    # 3 erledigt, 2 in Arbeit, 45 offen.
    gezaehlt = {wert: 0 for wert in Status}
    for zeile in stand.auftraege:
        gezaehlt[zeile.status] += 1
    assert gezaehlt[Status.ERLEDIGT] == 3
    assert gezaehlt[Status.IN_ARBEIT] == 2
    assert gezaehlt[Status.OFFEN] == 45


def test_r008_erledigte_auftraege_zaehlen_nicht_in_die_belastung(stand, auftrag):
    # 26-0395 läuft auf M3 in KW 38 und ist erledigt.
    zeile = auftrag("26-0395")
    assert zeile.status is Status.ERLEDIGT
    assert not ist_laufend(zeile.status)
