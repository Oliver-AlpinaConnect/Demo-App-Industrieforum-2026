"""R-007: Die manuell gesetzte Woche schlägt die Plan-KW."""

from app.regeln.termine import kw_effektiv
from app.regeln.typen import Kalenderwoche


def test_r007_manuelle_woche_gewinnt(auftrag):
    # 26-0420: Plan-KW 41, manuelle KW 42.
    zeile = auftrag("26-0420")
    assert zeile.plan_kw == Kalenderwoche(2026, 41)
    assert zeile.manuelle_kw == Kalenderwoche(2026, 42)
    assert zeile.kw_effektiv == Kalenderwoche(2026, 42)


def test_r007_ohne_eintrag_gilt_die_plan_kw(auftrag):
    zeile = auftrag("26-0414")
    assert zeile.manuelle_kw is None
    assert zeile.kw_effektiv == zeile.plan_kw


def test_r007_nur_wenige_auftraege_haben_eine_manuelle_woche(stand):
    mit_eintrag = [z.auftragsnummer for z in stand.auftraege if z.manuelle_kw]
    assert mit_eintrag == ["26-0420", "26-0449"]


def test_r007_leerer_eintrag_gibt_die_plan_kw_zurueck():
    assert kw_effektiv(Kalenderwoche(2026, 41), None) == Kalenderwoche(2026, 41)
