"""R-029: Bestellen ja oder nein."""

from app.regeln.material import bestellen, bestellung_ueberfaellig
from app.regeln.typen import Kalenderwoche

AKTUELL = Kalenderwoche(2026, 39)


def test_r029_bestell_kw_diese_woche_oder_frueher():
    assert bestellen(AKTUELL, AKTUELL)
    assert bestellen(AKTUELL.minus(2), AKTUELL)
    assert not bestellen(AKTUELL.plus(1), AKTUELL)


def test_r029_ohne_bestell_kw_wird_nicht_bestellt():
    assert not bestellen(None, AKTUELL)
    assert not bestellung_ueberfaellig(None, AKTUELL)


def test_r029_ueberfaellig_heisst_bestell_kw_schon_vorbei():
    assert bestellung_ueberfaellig(AKTUELL.minus(1), AKTUELL)
    assert not bestellung_ueberfaellig(AKTUELL, AKTUELL)


def test_r029_fuenf_positionen_stehen_auf_ja(stand):
    nummern = [zeile.rohnummer for zeile in stand.bestellvorschlaege]
    assert nummern == ["RM-106", "RM-107", "RM-109", "RM-110", "RM-115"]
    assert stand.kennzahlen.bestellpositionen == 5


def test_r029_zwei_davon_sind_ueberfaellig(stand):
    ueberfaellig = [zeile.rohnummer for zeile in stand.bestellvorschlaege if zeile.ueberfaellig]
    assert ueberfaellig == ["RM-106", "RM-109"]
    assert stand.kennzahlen.bestellpositionen_ueberfaellig == 2
