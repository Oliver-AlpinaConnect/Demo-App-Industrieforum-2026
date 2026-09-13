"""R-015: Die Wartungswoche kürzt die Kapazität um einen festen Betrag."""

from decimal import Decimal

from app.regeln.kapazitaet import kapazitaet_der_woche
from app.regeln.typen import Kalenderwoche

ABZUG = Decimal(16)


def test_r015_abzug_nur_in_der_wartungswoche():
    kw41 = Kalenderwoche(2026, 41)
    assert kapazitaet_der_woche(Decimal("68.0"), kw41, kw41, ABZUG) == Decimal("52.0")
    assert kapazitaet_der_woche(Decimal("68.0"), kw41, Kalenderwoche(2026, 42), ABZUG) == Decimal(
        "68.0"
    )


def test_r015_ohne_wartungswoche_wird_nie_gekuerzt():
    assert kapazitaet_der_woche(Decimal("64.0"), None, Kalenderwoche(2026, 41), ABZUG) == Decimal(
        "64.0"
    )


def test_r015_wartung_in_den_testdaten(stand):
    # M1 KW 41, M2 KW 44, M4 KW 43, M3 keine.
    erwartet = {
        "M1": Kalenderwoche(2026, 41),
        "M2": Kalenderwoche(2026, 44),
        "M3": None,
        "M4": Kalenderwoche(2026, 43),
    }
    for maschine in stand.maschinen:
        assert maschine.wartungs_kw == erwartet[maschine.kuerzel]


def test_r015_gekuerzte_kapazitaet_im_wochenplan(stand):
    werte = {}
    for maschine in stand.maschinen:
        for zelle in maschine.zellen:
            if zelle.wartung:
                werte[maschine.kuerzel] = zelle.kapazitaet_h
    assert werte == {
        "M1": Decimal("52.0"),
        "M2": Decimal("52.0"),
        "M4": Decimal("56.0"),
    }


def test_r015_kapazitaet_wird_nie_negativ():
    kw = Kalenderwoche(2026, 41)
    assert kapazitaet_der_woche(Decimal("10.0"), kw, kw, ABZUG) == Decimal("0.0")
