"""R-025: Sicherheitsbestand."""

from decimal import Decimal

from app.regeln.material import sicherheitsbestand

PROZENT = Decimal(10)


def test_r025_prozent_vom_durchschnitt_aufgerundet_mindestens_ein_gebinde():
    # RM-107: Ø 9,2, 10 % davon 0,92, aufgerundet 1, Gebinde 4 -> 4.
    assert sicherheitsbestand(Decimal("9.2"), PROZENT, Decimal(4)) == Decimal("4.0")
    # RM-110: Ø 98,75, 10 % davon 9,875, aufgerundet 10, Gebinde 40 -> 40.
    assert sicherheitsbestand(Decimal("98.75"), PROZENT, Decimal(40)) == Decimal("40.0")


def test_r025_der_prozentsatz_gewinnt_bei_grossem_bedarf():
    # Erst ab dem Zehnfachen des Gebindes wirkt der Prozentsatz.
    assert sicherheitsbestand(Decimal("500.0"), PROZENT, Decimal(40)) == Decimal("50.0")


def test_r025_heute_ist_der_sicherheitsbestand_immer_das_gebinde(stand):
    for zeile in stand.material:
        assert zeile.sicherheitsbestand == zeile.gebinde


def test_r025_wird_aufgerundet_nicht_kaufmaennisch():
    assert sicherheitsbestand(Decimal("41.0"), PROZENT, Decimal(1)) == Decimal("5.0")
