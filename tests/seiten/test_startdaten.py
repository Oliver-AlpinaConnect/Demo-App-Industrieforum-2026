"""Die Testdaten sind in sich stimmig und enthalten keine echten Kundendaten."""

from __future__ import annotations

import json
from decimal import Decimal

from app.config import WURZEL
from app.regeln.stammdaten import material_ist_bekannt
from app.regeln.typen import Status
from app.startdaten import BEZUGSWOCHE, verschiebung_auf

DATEN = WURZEL / "tests" / "daten"


def _lies(name: str):
    return json.loads((DATEN / name).read_text(encoding="utf-8"))


def test_fuenfzig_auftraege_mit_eindeutiger_nummer():
    auftraege = _lies("auftraege.json")
    assert len(auftraege) == 50
    assert len({satz["auftragsnummer"] for satz in auftraege}) == 50


def test_kunden_sind_anonymisiert():
    for satz in _lies("auftraege.json"):
        assert satz["kunde"].startswith("Kunde ")


def test_jeder_auftrag_zeigt_auf_einen_vorhandenen_artikel():
    artikel = {satz["artikelnummer"] for satz in _lies("artikel.json")}
    for satz in _lies("auftraege.json"):
        assert satz["artikelnummer"] in artikel
        assert satz["status"] in {wert.value for wert in Status}


def test_jeder_artikel_hat_ein_bekanntes_material_und_eine_stueckliste():
    positionen = _lies("stueckliste.json")
    mit_position = {satz["artikelnummer"] for satz in positionen}
    rohmaterial = {satz["rohnummer"] for satz in _lies("rohmaterial.json")}
    for satz in _lies("artikel.json"):
        assert material_ist_bekannt(satz["material"]), satz["artikelnummer"]
        assert satz["artikelnummer"] in mit_position
    for satz in positionen:
        assert satz["rohnummer"] in rohmaterial


def test_stammdaten_entsprechen_dem_katalog():
    assert len(_lies("artikel.json")) == 21
    assert len(_lies("stueckliste.json")) == 22
    assert len(_lies("rohmaterial.json")) == 15
    assert len(_lies("lieferanten.json")) == 5
    assert len(_lies("maschinen.json")) == 4


def test_materialverteilung_der_artikel():
    verteilung: dict[str, int] = {}
    for satz in _lies("artikel.json"):
        verteilung[satz["material"]] = verteilung.get(satz["material"], 0) + 1
    assert verteilung == {
        "Alu": 7,
        "S235JR": 4,
        "1.4301": 3,
        "GG25": 3,
        "Messing": 2,
        "1.4404": 1,
        "42CrMo4": 1,
    }


def test_jedes_rohmaterial_zeigt_auf_einen_lieferanten():
    lieferanten = {satz["liefnummer"] for satz in _lies("lieferanten.json")}
    for satz in _lies("rohmaterial.json"):
        assert satz["liefnummer"] in lieferanten
        assert Decimal(satz["gebinde"]) > 0


def test_verschiebung_rechnet_von_der_bezugswoche_aus():
    assert verschiebung_auf(BEZUGSWOCHE) == 0
    assert verschiebung_auf(BEZUGSWOCHE.plus(3)) == 3
    assert verschiebung_auf(BEZUGSWOCHE.minus(2)) == -2
