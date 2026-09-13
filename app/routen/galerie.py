"""Seite Galerie. Ein Beispiel je Makro aus `templates/komponenten/` (siehe docs/design.md)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.dienste.planung import stand_laden
from app.routen.gemeinsam import Datenbank, seite

router = APIRouter(prefix="/galerie")


@router.get("")
def galerie(request: Request, db: Datenbank):
    """Zeigt jedes Makro einmal, damit Änderungen am Design sichtbar werden."""
    stand = stand_laden(db)
    return seite(request, "seiten/galerie.html", "/galerie", stand=stand)
