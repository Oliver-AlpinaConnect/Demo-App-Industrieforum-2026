"""Datenbankverbindung und Sitzungen."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import einstellungen
from app.modelle import Basis

_url = einstellungen().datenbank_url
if _url.startswith("sqlite:///"):
    Path(_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)

maschine = create_engine(_url, future=True)
Sitzung = sessionmaker(bind=maschine, expire_on_commit=False, future=True)


def tabellen_anlegen() -> None:
    """Legt fehlende Tabellen an. Änderungen an der Datenbank sind nur additiv."""
    Basis.metadata.create_all(maschine)


def sitzung() -> Iterator[Session]:
    """FastAPI-Abhängigkeit: eine Sitzung je Anfrage."""
    with Sitzung() as offen:
        yield offen
