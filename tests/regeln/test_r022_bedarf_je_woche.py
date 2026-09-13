"""R-022: Bedarf je Rohmaterial und Woche."""

from decimal import Decimal

from app.regeln.material import Materialposition, bedarf_der_woche
from app.regeln.typen import Kalenderwoche, Status

KW43 = Kalenderwoche(2026, 43)


def test_r022_bedarfsreihe_von_rm107(rohmaterial):
    # 14,9 / 0 / 0 / 9,9 / 33,0 / 0 / 4,2 / 11,6 über den Horizont.
    zeile = rohmaterial("RM-107")
    assert [str(wert) for wert in zeile.bedarf_reihe] == [
        "14.9",
        "0.0",
        "0.0",
        "9.9",
        "33.0",
        "0.0",
        "4.2",
        "11.6",
    ]


def test_r022_summe_ueber_den_horizont(rohmaterial):
    assert rohmaterial("RM-107").summe_horizont == Decimal("73.6")


def test_r022_beide_stuecklistenpositionen_zaehlen(rohmaterial, auftrag):
    # 26-0419 liefert 30,0 auf RM-109 (Position 1) und 30,0 auf RM-110 (Position 2).
    zeile = auftrag("26-0419")
    assert zeile.kw_effektiv == Kalenderwoche(2026, 41)
    index = 41 - 39
    assert rohmaterial("RM-109").bedarf_reihe[index] >= Decimal("30.0")
    assert rohmaterial("RM-110").bedarf_reihe[index] >= Decimal("30.0")


def test_r022_erledigte_auftraege_zaehlen_nicht_mit():
    positionen = [
        Materialposition("26-0001", "RM-106", KW43, Decimal("5.0"), Status.OFFEN),
        Materialposition("26-0002", "RM-106", KW43, Decimal("7.0"), Status.ERLEDIGT),
        Materialposition("26-0003", "RM-106", KW43, Decimal("1.0"), Status.IN_ARBEIT),
    ]
    assert bedarf_der_woche(positionen, "RM-106", KW43) == Decimal("6.0")


def test_r022_andere_woche_und_anderes_material_zaehlen_nicht():
    positionen = [
        Materialposition("26-0001", "RM-106", KW43, Decimal("5.0"), Status.OFFEN),
        Materialposition("26-0002", "RM-107", KW43, Decimal("7.0"), Status.OFFEN),
        Materialposition("26-0003", "RM-106", KW43.plus(1), Decimal("9.0"), Status.OFFEN),
    ]
    assert bedarf_der_woche(positionen, "RM-106", KW43) == Decimal("5.0")
