"""Seite Regeln. Zeigt `docs/regeln.md` und das Verzeichnis aus `app/regeln/katalog.py`."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Request
from markdown_it import MarkdownIt

from app.config import WURZEL
from app.dienste.planung import stand_laden
from app.regeln.katalog import KATALOG
from app.routen.gemeinsam import Datenbank, seite

router = APIRouter(prefix="/regeln")

KATALOGDATEI = WURZEL / "docs" / "regeln.md"


@lru_cache
def _katalogtext(datei: Path, stand_ns: int) -> str:
    """Wandelt den Regelkatalog in HTML. Der Zeitstempel hält den Zwischenspeicher aktuell."""
    del stand_ns
    markdown = MarkdownIt("commonmark", {"html": False}).enable("table")
    return markdown.render(datei.read_text(encoding="utf-8"))


@router.get("")
def regeln(request: Request, db: Datenbank):
    """Der Regelkatalog als Seite, mit der Stelle im Code je Regel."""
    stand = stand_laden(db)
    vorhanden = KATALOGDATEI.exists()
    return seite(
        request,
        "seiten/regeln.html",
        "/regeln",
        stand=stand,
        katalog=KATALOG,
        katalogtext=_katalogtext(KATALOGDATEI, KATALOGDATEI.stat().st_mtime_ns)
        if vorhanden
        else "",
        katalogdatei=str(KATALOGDATEI.relative_to(WURZEL)),
    )
