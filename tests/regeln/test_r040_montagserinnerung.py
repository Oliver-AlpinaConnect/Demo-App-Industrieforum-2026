"""R-040: Montagserinnerung und Tastenkürzel. Status `veraltet`, nicht übernommen."""

from app.regeln.katalog import regel
from app.regeln.veraltet import montagserinnerung_und_tastenkuerzel


def test_r040_ist_im_katalog_als_veraltet_vermerkt():
    assert regel("R-040").status == "veraltet"


def test_r040_wird_nicht_nachgebaut():
    eintrag = montagserinnerung_und_tastenkuerzel()
    assert eintrag.regel == "R-040"
    assert "R-002" in eintrag.ersatz


def test_r040_die_aktuelle_woche_wird_nicht_mehr_von_hand_gesetzt(parameter):
    # Es gibt keinen Parameter "aktuelle KW" und kein Montagsdatum mehr.
    assert "aktuelle_kw" not in parameter.werte
    assert "montag_aktuelle_kw" not in parameter.werte
