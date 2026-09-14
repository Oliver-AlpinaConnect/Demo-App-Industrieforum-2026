"""R-019: Planungshorizont, acht Wochen ab der aktuellen KW."""

import pytest

from app.regeln.kapazitaet import horizont
from app.regeln.typen import Kalenderwoche


def test_r019_acht_wochen_ab_der_aktuellen_kw():
    reihe = horizont(Kalenderwoche(2026, 39), 8)
    assert [woche.woche for woche in reihe] == [39, 40, 41, 42, 43, 44, 45, 46]
    assert reihe[0] == Kalenderwoche(2026, 39)
    assert reihe[-1] == Kalenderwoche(2026, 46)


def test_r019_horizont_laeuft_ueber_den_jahreswechsel():
    # 2026 hat 53 Wochen, deshalb 50, 51, 52, 53, dann 2027-KW01 bis 04.
    reihe = horizont(Kalenderwoche(2026, 50), 8)
    assert [str(woche) for woche in reihe] == [
        "2026-KW50",
        "2026-KW51",
        "2026-KW52",
        "2026-KW53",
        "2027-KW01",
        "2027-KW02",
        "2027-KW03",
        "2027-KW04",
    ]


def test_r019_laenge_kommt_aus_den_parametern(stand, parameter):
    assert len(stand.horizont) == parameter.ganzzahl("planungshorizont_wochen")
    assert len(stand.horizont) == 8


def test_r019_horizont_ist_ueberall_gleich_lang(stand):
    # Im Excel stehen vier Kopfzeilen mit je acht eingetippten Wochennummern (F-4).
    for maschine in stand.maschinen:
        assert [zelle.kw for zelle in maschine.zellen] == stand.horizont
    for zeile in stand.material:
        assert len(zeile.bedarf_reihe) == len(stand.horizont)
        assert len(zeile.kumuliert_reihe) == len(stand.horizont)


def test_r019_anderer_horizont_wirkt_sofort():
    assert len(horizont(Kalenderwoche(2026, 39), 12)) == 12
    with pytest.raises(ValueError):
        horizont(Kalenderwoche(2026, 39), 0)
