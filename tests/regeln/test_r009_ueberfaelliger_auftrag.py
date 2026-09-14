"""R-009: Überfälliger Auftrag, gemessen an der Liefer-KW."""

from app.regeln.termine import ist_ueberfaellig
from app.regeln.typen import Kalenderwoche, Status

AKTUELL = Kalenderwoche(2026, 39)


def test_r009_genau_ein_auftrag_ist_ueberfaellig(stand):
    assert [zeile.auftragsnummer for zeile in stand.ueberfaellige] == ["26-0402"]
    assert stand.kennzahlen.davon_ueberfaellig == 1


def test_r009_der_ueberfaellige_auftrag_hat_liefer_kw_38(auftrag):
    zeile = auftrag("26-0402")
    assert zeile.liefer_kw == Kalenderwoche(2026, 38)
    assert zeile.status is Status.OFFEN
    assert zeile.ueberfaellig


def test_r009_erledigt_ist_nie_ueberfaellig():
    assert not ist_ueberfaellig(Status.ERLEDIGT, Kalenderwoche(2026, 30), AKTUELL)


def test_r009_massgeblich_ist_die_liefer_kw_nicht_die_planwoche(auftrag):
    # 26-0395 hat Liefer-KW 39 und KW eff. 38, ist aber erledigt und nicht überfällig.
    zeile = auftrag("26-0395")
    assert zeile.kw_effektiv < AKTUELL
    assert not zeile.ueberfaellig


def test_r009_aktuelle_woche_ist_noch_nicht_ueberfaellig():
    assert not ist_ueberfaellig(Status.OFFEN, AKTUELL, AKTUELL)
    assert ist_ueberfaellig(Status.OFFEN, AKTUELL.minus(1), AKTUELL)
