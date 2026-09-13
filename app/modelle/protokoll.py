"""Änderungslog. Jede Änderung an einem Auftrag steht hier (Hausregel)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modelle.basis import Basis, Kurztext, Langtext


class Aenderungslog(Basis):
    """Wer, wann, welches Feld, alter Wert, neuer Wert."""

    __tablename__ = "aenderungslog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zeitpunkt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    benutzer: Mapped[Kurztext]
    tabelle: Mapped[str] = mapped_column(String(40), nullable=False)
    schluessel: Mapped[Kurztext]
    feld: Mapped[Kurztext]
    alt: Mapped[Langtext] = mapped_column(default="")
    neu: Mapped[Langtext] = mapped_column(default="")
