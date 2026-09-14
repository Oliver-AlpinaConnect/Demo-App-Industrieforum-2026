"""R-039: Sicherungskopie beim Speichern. Status `veraltet`, nicht übernommen."""

from app.regeln.katalog import regel
from app.regeln.veraltet import sicherungskopie_beim_speichern


def test_r039_ist_im_katalog_als_veraltet_vermerkt():
    assert regel("R-039").status == "veraltet"


def test_r039_wird_nicht_nachgebaut():
    eintrag = sicherungskopie_beim_speichern()
    assert eintrag.regel == "R-039"
    assert eintrag.grund
    assert "docs/betrieb.md" in eintrag.ersatz


def test_r039_die_app_kennt_keinen_backup_pfad():
    import app.config as konfiguration

    einstellungen = konfiguration.einstellungen()
    assert not hasattr(einstellungen, "backup_pfad")
