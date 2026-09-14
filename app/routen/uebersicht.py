"""Seite Wochenübersicht. Kennzahlen wie im Blatt `Übersicht` (R-038)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.dienste.planung import stand_laden
from app.routen.gemeinsam import Datenbank, seite

router = APIRouter()


@router.get("/")
def uebersicht(request: Request, db: Datenbank):
    """R-038: sieben Kennzahlen und die Auslastung der Maschinen in der aktuellen Woche."""
    stand = stand_laden(db)
    auslastung = [(maschine, maschine.zelle(stand.aktuelle_kw)) for maschine in stand.maschinen]
    return seite(
        request,
        "seiten/uebersicht.html",
        "/",
        stand=stand,
        auslastung=auslastung,
    )
