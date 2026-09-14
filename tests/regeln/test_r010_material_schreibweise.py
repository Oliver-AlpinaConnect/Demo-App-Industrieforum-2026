"""R-010: Die Materialbezeichnung ist exakt."""

import pytest

from app.regeln.stammdaten import (
    MATERIALIEN,
    UnbekanntesMaterial,
    material_ist_bekannt,
    pruefe_material,
)


def test_r010_bekannte_materialien():
    for material in ["Alu", "1.4301", "S235JR", "GG25", "Messing", "42CrMo4"]:
        assert material_ist_bekannt(material)


def test_r010_1_4404_gehoert_dazu_auch_wenn_der_zellkommentar_es_vergisst():
    # Artikel A-1015 hat 1.4404, die Liste im Kommentar auf Artikel!C1 nennt es nicht.
    assert "1.4404" in MATERIALIEN
    assert material_ist_bekannt("1.4404")


def test_r010_abweichende_schreibweise_wird_abgelehnt():
    for falsch in ["ALU", "alu", "Aluminium", "Alu ", "1.4301 "]:
        assert not material_ist_bekannt(falsch)
        with pytest.raises(UnbekanntesMaterial):
            pruefe_material(falsch)


def test_r010_pruefung_korrigiert_nicht_still():
    assert pruefe_material("Alu") == "Alu"


def test_r010_alle_artikel_der_testdaten_haben_ein_bekanntes_material(stand):
    for zeile in stand.auftraege:
        assert material_ist_bekannt(zeile.material), zeile.artikelnummer
