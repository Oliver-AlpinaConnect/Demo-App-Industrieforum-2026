"""R-006: Plan-KW aus Liefer-KW und Priorität."""

from app.regeln.termine import plan_kw
from app.regeln.typen import Kalenderwoche, Prioritaet


def test_r006_prio_a_zwei_wochen_vorher(auftrag, parameter):
    # 26-0426: Prio A, Liefer-KW 44 ergibt Plan-KW 42.
    zeile = auftrag("26-0426")
    assert zeile.prioritaet is Prioritaet.A
    assert zeile.liefer_kw == Kalenderwoche(2026, 44)
    assert zeile.plan_kw == Kalenderwoche(2026, 42)


def test_r006_prio_b_eine_woche_vorher(auftrag):
    # 26-0425: Prio B, Liefer-KW 42 ergibt Plan-KW 41.
    zeile = auftrag("26-0425")
    assert zeile.liefer_kw == Kalenderwoche(2026, 42)
    assert zeile.plan_kw == Kalenderwoche(2026, 41)


def test_r006_prio_c_wie_prio_b(auftrag):
    # 26-0406: Prio C, Liefer-KW 40 ergibt Plan-KW 39.
    zeile = auftrag("26-0406")
    assert zeile.prioritaet is Prioritaet.C
    assert zeile.plan_kw == Kalenderwoche(2026, 39)


def test_r006_vorlauf_kommt_aus_den_parametern(parameter):
    # Im Excel steht die 2 fest in der Formel, Parameter!B18 ist nie angeschlossen (F-3).
    assert plan_kw(
        Kalenderwoche(2026, 44), Prioritaet.A, parameter.vorlauf(Prioritaet.A)
    ) == Kalenderwoche(2026, 42)


def test_r006_jahreswechsel_ergibt_die_vorjahreswoche():
    # Liefer-KW 2027-KW01 mit Prio A ergibt 2026-KW52, nicht "Woche -1".
    # 2026 hat 53 Wochen, zwei Wochen vor 2027-KW01 ist 2026-KW52.
    assert plan_kw(Kalenderwoche(2027, 1), Prioritaet.A, 2) == Kalenderwoche(2026, 52)
    # In einem Jahr mit 52 Wochen (2025) landet dieselbe Rechnung in KW 51.
    assert plan_kw(Kalenderwoche(2026, 1), Prioritaet.A, 2) == Kalenderwoche(2025, 51)
