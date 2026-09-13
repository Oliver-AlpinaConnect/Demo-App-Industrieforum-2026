"""R-018: Auslastungsampel."""

from decimal import Decimal

from app.regeln.kapazitaet import ampel
from app.regeln.typen import Ampel

GRENZE = Decimal("0.90")


def test_r018_ueber_der_grenze_ist_rot():
    assert ampel(Decimal("0.947"), GRENZE) is Ampel.ROT
    assert ampel(Decimal("0.901"), GRENZE) is Ampel.ROT


def test_r018_genau_auf_der_grenze_ist_noch_nicht_rot():
    assert ampel(GRENZE, GRENZE) is Ampel.GELB


def test_r018_zwischen_75_prozent_und_grenze_ist_gelb():
    assert ampel(Decimal("0.859"), GRENZE) is Ampel.GELB
    assert ampel(Decimal("0.750"), GRENZE) is Ampel.GELB


def test_r018_unter_40_prozent_ist_gruen():
    assert ampel(Decimal("0.289"), GRENZE) is Ampel.GRUEN
    assert ampel(Decimal("0.000"), GRENZE) is Ampel.GRUEN


def test_r018_die_luecke_dazwischen_bleibt_ohne_farbe():
    assert ampel(Decimal("0.588"), GRENZE) is Ampel.NEUTRAL
    assert ampel(Decimal("0.400"), GRENZE) is Ampel.NEUTRAL


def test_r018_dieselbe_ampel_auf_jeder_seite(stand):
    # Im Excel hat die Übersicht nur die rote Stufe, der Wochenplan drei.
    for maschine in stand.maschinen:
        for zelle in maschine.zellen:
            assert zelle.ampel is ampel(
                zelle.auslastung, stand.parameter.anteil("auslastungsgrenze_prozent")
            )
