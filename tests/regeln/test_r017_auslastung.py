"""R-017: Auslastung einer Maschine in einer Woche."""

from decimal import Decimal

from app.regeln.kapazitaet import auslastung
from app.regeln.typen import Kalenderwoche

KW39 = Kalenderwoche(2026, 39)


def test_r017_belastung_durch_kapazitaet():
    # M1 in KW 39: 40,0 / 68,0 = 58,8 %.
    assert auslastung(Decimal("40.0"), Decimal("68.0")) == Decimal("0.588")
    # M1 in der Wartungswoche: 44,0 / 52,0 = 84,6 %.
    assert auslastung(Decimal("44.0"), Decimal("52.0")) == Decimal("0.846")


def test_r017_kapazitaet_null_ergibt_auslastung_null():
    assert auslastung(Decimal("12.0"), Decimal(0)) == Decimal(0)


def test_r017_auslastung_der_aktuellen_woche_in_den_testdaten(stand):
    werte = {maschine.kuerzel: maschine.zelle(KW39).auslastung for maschine in stand.maschinen}
    assert werte["M1"] == Decimal("0.588")
    assert werte["M2"] == Decimal("0.375")
    assert werte["M3"] == Decimal("0.747")
    assert werte["M4"] == Decimal("0.292")
