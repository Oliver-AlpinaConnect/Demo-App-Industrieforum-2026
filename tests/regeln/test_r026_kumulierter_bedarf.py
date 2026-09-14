"""R-026: Kumulierter Bedarf."""

from decimal import Decimal

from app.regeln.material import kumulierter_bedarf


def test_r026_laufende_summe_ueber_den_horizont():
    reihe = [Decimal(wert) for wert in ["0", "0", "23.7", "0", "0", "0", "31.5", "0"]]
    assert [str(wert) for wert in kumulierter_bedarf(reihe)] == [
        "0.0",
        "0.0",
        "23.7",
        "23.7",
        "23.7",
        "23.7",
        "55.2",
        "55.2",
    ]


def test_r026_letzter_wert_ist_die_summe_des_horizonts(stand):
    for zeile in stand.material:
        if zeile.bedarf_reihe:
            assert zeile.kumuliert_reihe[-1] == zeile.summe_horizont


def test_r026_reihe_von_rm107(rohmaterial):
    zeile = rohmaterial("RM-107")
    assert [str(wert) for wert in zeile.kumuliert_reihe] == [
        "14.9",
        "14.9",
        "14.9",
        "24.8",
        "57.8",
        "57.8",
        "62.0",
        "73.6",
    ]


def test_r026_leere_reihe_bleibt_leer():
    assert kumulierter_bedarf([]) == []
