"""Das Verzeichnis in `app/regeln/katalog.py` deckt `docs/regeln.md` vollständig ab."""

import importlib
import re

from app.config import WURZEL
from app.regeln.katalog import KATALOG, NACH_ID

KATALOGDATEI = WURZEL / "docs" / "regeln.md"


def _regeln_aus_der_doku() -> dict[str, tuple[str, str]]:
    text = KATALOGDATEI.read_text(encoding="utf-8")
    teile = re.split(r"\n## (R-\d{3}) ", text)
    ergebnis = {}
    for index in range(1, len(teile), 2):
        regel_id = teile[index]
        koerper = teile[index + 1]
        titel = koerper.split("\n", 1)[0].strip()
        status = re.search(r"\*\*Status:\*\* `([^`]+)`", koerper)
        ergebnis[regel_id] = (titel, status.group(1) if status else "")
    return ergebnis


def test_jede_regel_der_doku_steht_im_verzeichnis():
    doku = _regeln_aus_der_doku()
    assert doku, "In docs/regeln.md wurde keine Regel gefunden"
    assert sorted(doku) == sorted(NACH_ID)


def test_titel_und_status_stimmen_mit_der_doku_ueberein():
    doku = _regeln_aus_der_doku()
    for eintrag in KATALOG:
        titel, status = doku[eintrag.id]
        assert eintrag.titel == titel, eintrag.id
        assert eintrag.status == status, eintrag.id


def test_jede_funktion_des_verzeichnisses_gibt_es_wirklich():
    for eintrag in KATALOG:
        modul = importlib.import_module(eintrag.modul)
        for name in eintrag.funktionen:
            assert hasattr(modul, name), f"{eintrag.id}: {eintrag.modul}.{name}"


def test_jede_regel_hat_einen_test():
    dateien = {pfad.name for pfad in (WURZEL / "tests" / "regeln").glob("test_r*.py")}
    for eintrag in KATALOG:
        kennung = eintrag.id.replace("-", "").lower()
        assert any(name.startswith(f"test_{kennung}_") for name in dateien), eintrag.id


def test_jede_funktion_nennt_ihre_regel_im_docstring():
    for eintrag in KATALOG:
        modul = importlib.import_module(eintrag.modul)
        for name in eintrag.funktionen:
            docstring = getattr(modul, name).__doc__ or ""
            assert eintrag.id in docstring, f"{eintrag.id} fehlt in {name}"
