"""R-014: Wochenkapazität einer Maschine."""

from decimal import Decimal

from app.regeln.kapazitaet import wochenkapazitaet_stunden


def test_r014_kapazitaet_aus_schichten_stunden_tagen_und_verfuegbarkeit():
    # M1: 2 Schichten mal 8,0 h mal 5 Tage mal 85 % = 68,0 h.
    assert wochenkapazitaet_stunden(2, Decimal("8.0"), 5, Decimal(85)) == Decimal("68.0")
    assert wochenkapazitaet_stunden(2, Decimal("8.0"), 5, Decimal(80)) == Decimal("64.0")
    assert wochenkapazitaet_stunden(2, Decimal("8.0"), 5, Decimal(90)) == Decimal("72.0")


def test_r014_alle_vier_maschinen_der_testdaten(stand):
    erwartet = {
        "M1": Decimal("68.0"),
        "M2": Decimal("68.0"),
        "M3": Decimal("64.0"),
        "M4": Decimal("72.0"),
    }
    for maschine in stand.maschinen:
        assert maschine.grundkapazitaet_h == erwartet[maschine.kuerzel]


def test_r014_alle_maschinen_lesen_dieselben_parameter(stand, parameter):
    # Im Excel hat M3 Schichten, Stunden und Tage fest eingetippt (F-2).
    for maschine in stand.maschinen:
        erwartet = wochenkapazitaet_stunden(
            parameter.ganzzahl("schichten_pro_tag"),
            parameter.zahl("stunden_pro_schicht"),
            parameter.ganzzahl("arbeitstage_pro_woche"),
            maschine.verfuegbarkeit_prozent,
        )
        assert maschine.grundkapazitaet_h == erwartet


def test_r014_dritte_schicht_wirkt_auf_alle_maschinen():
    assert wochenkapazitaet_stunden(3, Decimal("8.0"), 5, Decimal(85)) == Decimal("102.0")
