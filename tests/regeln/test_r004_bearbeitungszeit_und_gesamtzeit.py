"""R-004: Bearbeitungszeit und Gesamtzeit je Auftrag."""

from decimal import Decimal

from app.regeln.zeiten import bearbeitungszeit_stunden, gesamtzeit_stunden


def test_r004_bearbeitungszeit_aus_menge_und_zeit_je_stueck(auftrag):
    # 26-0414: 620 Stk mal 4,0 min/Stk durch 60 = 41,333 h, angezeigt 41,3 h.
    zeile = auftrag("26-0414")
    assert zeile.bearbeitungszeit_h == Decimal("41.3")


def test_r004_gesamtzeit_ist_bearbeitung_plus_ruestzeit(auftrag):
    # 41,333 h + 90 min / 60 = 42,833 h, angezeigt 42,8 h.
    zeile = auftrag("26-0414")
    assert zeile.gesamtzeit_h == Decimal("42.8")


def test_r004_krumme_zeit_wird_erst_am_schluss_gerundet():
    # 26-0391: 400 Stk mal 3,5 min/Stk = 23,3333... h.
    assert bearbeitungszeit_stunden(400, Decimal("3.5")) == Decimal("23.3")
    assert gesamtzeit_stunden(400, Decimal("3.5"), 30) == Decimal("23.8")


def test_r004_ohne_ruestzeit_bleibt_die_bearbeitungszeit():
    assert gesamtzeit_stunden(120, Decimal("4.0"), 0) == Decimal("8.0")


def test_r004_gesamtzeit_ist_nie_float(auftrag):
    zeile = auftrag("26-0405")
    assert isinstance(zeile.gesamtzeit_h, Decimal)
    assert zeile.gesamtzeit_h == Decimal("23.0")
