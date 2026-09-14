"""Gemeinsames für alle Router: Vorlagen, Navigation, Kontext."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import einstellungen
from app.datenbank import sitzung
from app.dienste.anzeige import FILTER
from app.modelle import Aenderungslog

# Eine Datenbanksitzung je Anfrage.
Datenbank = Annotated[Session, Depends(sitzung)]

VORLAGEN = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
VORLAGEN.env.filters.update(FILTER)

NAVIGATION = [
    {"pfad": "/", "titel": "Wochenübersicht"},
    {"pfad": "/auftraege", "titel": "Aufträge"},
    {"pfad": "/wochenplan", "titel": "Wochenplan"},
    {"pfad": "/material", "titel": "Material"},
    {"pfad": "/regeln", "titel": "Regeln"},
]


def seite(request: Request, vorlage: str, aktive_seite: str, **inhalt):
    """Rendert eine Seite mit Navigation und angemeldeter Person."""
    return VORLAGEN.TemplateResponse(
        request=request,
        name=vorlage,
        context={
            "navigation": NAVIGATION,
            "aktive_seite": aktive_seite,
            "benutzer": einstellungen().benutzer,
            **inhalt,
        },
    )


def jetzt() -> datetime:
    """Aktueller Zeitpunkt, Zeitzone Europe/Zurich (Hausregel)."""
    return datetime.now(ZoneInfo(einstellungen().zeitzone))


def protokolliere(
    sitzung: Session, tabelle: str, schluessel: str, feld: str, alt: str, neu: str
) -> None:
    """Schreibt eine Änderung in `aenderungslog` (wer, wann, Feld, alt, neu)."""
    sitzung.add(
        Aenderungslog(
            zeitpunkt=jetzt(),
            benutzer=einstellungen().benutzer,
            tabelle=tabelle,
            schluessel=schluessel,
            feld=feld,
            alt=alt,
            neu=neu,
        )
    )
