"""Gemeinsame Basis aller Modelle."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from sqlalchemy import Numeric, String
from sqlalchemy.orm import DeclarativeBase, mapped_column

# Mengen und Zeiten immer als Decimal, nie als float (Hausregel).
Betrag = Annotated[Decimal, mapped_column(Numeric(14, 4), nullable=False)]
Kurztext = Annotated[str, mapped_column(String(60), nullable=False)]
Langtext = Annotated[str, mapped_column(String(400), nullable=False, default="")]


class Basis(DeclarativeBase):
    """Basisklasse aller Tabellen."""

    registry_hinweis = "Zeiten in Minuten als int, Stunden und Mengen als Decimal."
