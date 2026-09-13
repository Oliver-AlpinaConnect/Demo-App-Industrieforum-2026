"""R-005: Liefer-KW aus dem Liefertermin, als Paar (Jahr, ISO-Woche)."""

from datetime import date

from app.regeln.termine import liefer_kw
from app.regeln.typen import Kalenderwoche


def test_r005_liefer_kw_aus_dem_termin():
    # 26-0430: Liefertermin 30.10.2026 ergibt KW 44.
    assert liefer_kw(date(2026, 10, 30)) == Kalenderwoche(2026, 44)
    # 26-0388: 18.09.2026 ergibt KW 38.
    assert liefer_kw(date(2026, 9, 18)) == Kalenderwoche(2026, 38)


def test_r005_die_woche_traegt_ihr_jahr_mit():
    # Der 1. Januar 2027 liegt in der ISO-Woche 53 von 2026, nicht in Woche 1.
    assert liefer_kw(date(2027, 1, 1)) == Kalenderwoche(2026, 53)
    assert str(liefer_kw(date(2027, 1, 1))) == "2026-KW53"


def test_r005_wochendifferenz_stimmt_ueber_den_jahreswechsel():
    # Das Excel rechnet mit nackten Wochennummern: KW 2 minus KW 51 ergibt dort -49.
    # Hier läuft die Rechnung über die Montage, deshalb stimmt sie. 2026 hat 53 Wochen,
    # von 2026-KW51 bis 2027-KW02 sind es also vier Wochen, nicht drei.
    ende = Kalenderwoche(2026, 51)
    anfang = Kalenderwoche(2027, 2)
    assert ende.abstand(anfang) == 4
    assert ende.plus(4) == anfang
    assert anfang.abstand(ende) == -4


def test_r005_ausgabe_immer_mit_jahr_und_zwei_stellen():
    assert str(Kalenderwoche(2026, 39)) == "2026-KW39"
    assert str(Kalenderwoche(2027, 1)) == "2027-KW01"


def test_r005_woche_kennt_ihren_montag():
    assert Kalenderwoche(2026, 39).montag == date(2026, 9, 21)
    assert Kalenderwoche(2026, 44).montag == date(2026, 10, 26)
