"""R-016: Belastung einer Maschine in einer Woche."""

from decimal import Decimal

from app.regeln.kapazitaet import belastung_stunden
from app.regeln.typen import Kalenderwoche

KW39 = Kalenderwoche(2026, 39)


def _zelle(stand, kuerzel, kw):
    for maschine in stand.maschinen:
        if maschine.kuerzel == kuerzel:
            return maschine.zelle(kw)
    raise AssertionError(kuerzel)


def test_r016_belastung_m1_in_kw39(stand):
    # 26-0404 (27,0 h) und 26-0407 (13,0 h) ergeben 40,0 h.
    assert _zelle(stand, "M1", KW39).belastung_h == Decimal("40.0")


def test_r016_belastung_m3_in_kw39(stand):
    # 26-0405 (23,0 h) und 26-0409 (24,8 h) ergeben 47,8 h.
    assert _zelle(stand, "M3", KW39).belastung_h == Decimal("47.8")


def test_r016_erledigter_auftrag_zaehlt_nicht_mit(stand, auftrag):
    # 26-0395 läuft auf M3, ist erledigt und hat KW eff. 38.
    zeile = auftrag("26-0395")
    assert zeile.maschine == "M3"
    assert _zelle(stand, "M3", Kalenderwoche(2026, 38)) is None


def test_r016_nur_auftraege_dieser_maschine_und_woche(stand):
    planauftraege = []
    for zeile in stand.auftraege:
        if zeile.maschine == "M1" and zeile.kw_effektiv == KW39:
            planauftraege.append(zeile)
    summe = sum((zeile.gesamtzeit_h for zeile in planauftraege), Decimal(0))
    assert summe == Decimal("40.0")


def test_r016_leere_woche_ergibt_null(stand):
    zellen = [
        zelle for maschine in stand.maschinen for zelle in maschine.zellen if zelle.belastung_h == 0
    ]
    assert zellen
    assert all(zelle.auslastung == 0 for zelle in zellen)


def test_r016_eine_einzige_funktion_statt_sumifs_und_vba():
    assert belastung_stunden([], "M1", KW39) == Decimal("0.0")
