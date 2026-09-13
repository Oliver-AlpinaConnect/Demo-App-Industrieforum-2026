"""Stammdaten: Parameter, Lieferanten, Rohmaterial, Artikel, Stückliste, Maschinen."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelle.basis import Basis, Betrag, Kurztext, Langtext


class Parametersatz(Basis):
    """R-001: Eine Stellschraube. Jede Zahl der Fachlogik kommt aus dieser Tabelle."""

    __tablename__ = "parameter"

    name: Mapped[str] = mapped_column(String(60), primary_key=True)
    wert: Mapped[Betrag]
    beschriftung: Mapped[Kurztext]
    einheit: Mapped[str] = mapped_column(String(20), default="")


class Lieferant(Basis):
    """Ein Lieferant. Bewertung C bekommt den Puffer aus R-028."""

    __tablename__ = "lieferant"

    liefnummer: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[Kurztext]
    ort: Mapped[Kurztext] = mapped_column(default="")
    lieferzeit_wochen: Mapped[int] = mapped_column(Integer, nullable=False)
    bewertung: Mapped[str] = mapped_column(String(1), nullable=False)
    erp_nummer: Mapped[str] = mapped_column(String(30), default="")
    bemerkung: Mapped[Langtext] = mapped_column(default="")

    rohmaterialien: Mapped[list[Rohmaterial]] = relationship(back_populates="lieferant")


class Rohmaterial(Basis):
    """Ein Rohmaterial mit Bestand, Gebinde und Preis (R-023, R-025, R-030, R-031)."""

    __tablename__ = "rohmaterial"

    rohnummer: Mapped[str] = mapped_column(String(20), primary_key=True)
    bezeichnung: Mapped[Kurztext]
    einheit: Mapped[str] = mapped_column(String(20), nullable=False)
    liefnummer: Mapped[str] = mapped_column(ForeignKey("lieferant.liefnummer"))
    lager: Mapped[Betrag] = mapped_column(default=Decimal(0))
    bestellt_offen: Mapped[Betrag] = mapped_column(default=Decimal(0))
    gebinde: Mapped[Betrag]
    preis: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    erp_nummer: Mapped[str] = mapped_column(String(30), default="")
    lagerort: Mapped[Kurztext] = mapped_column(default="")

    lieferant: Mapped[Lieferant] = relationship(back_populates="rohmaterialien")


class Maschine(Basis):
    """R-014, R-015: Eine Maschine mit Verfügbarkeit und optionaler Wartungswoche."""

    __tablename__ = "maschine"

    kuerzel: Mapped[str] = mapped_column(String(10), primary_key=True)
    bezeichnung: Mapped[Kurztext]
    verfuegbarkeit_prozent: Mapped[Betrag]
    wartung_jahr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wartung_woche: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bemerkung: Mapped[Langtext] = mapped_column(default="")


class Artikel(Basis):
    """R-011: Ein Artikel. Er bestimmt Material, Maschine und Zeiten seiner Aufträge."""

    __tablename__ = "artikel"

    artikelnummer: Mapped[str] = mapped_column(String(20), primary_key=True)
    bezeichnung: Mapped[Kurztext]
    material: Mapped[str] = mapped_column(String(20), nullable=False)
    standardmaschine: Mapped[str] = mapped_column(ForeignKey("maschine.kuerzel"))
    minuten_je_stueck: Mapped[Betrag]
    ruestzeit_basis_min: Mapped[int] = mapped_column(Integer, nullable=False)
    zeichnung: Mapped[Kurztext] = mapped_column(default="")
    aktiv: Mapped[bool] = mapped_column(default=True)

    positionen: Mapped[list[Stuecklistenposition]] = relationship(
        back_populates="artikel", order_by="Stuecklistenposition.position"
    )


class Stuecklistenposition(Basis):
    """R-012, R-013: Eine Stücklistenzeile. Beliebig viele Positionen je Artikel."""

    __tablename__ = "stuecklistenposition"
    __table_args__ = (UniqueConstraint("artikelnummer", "position"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    artikelnummer: Mapped[str] = mapped_column(ForeignKey("artikel.artikelnummer"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    rohnummer: Mapped[str] = mapped_column(ForeignKey("rohmaterial.rohnummer"))
    menge_je_stueck: Mapped[Betrag]
    verschnitt_prozent: Mapped[Betrag] = mapped_column(default=Decimal(0))
    bemerkung: Mapped[Langtext] = mapped_column(default="")

    artikel: Mapped[Artikel] = relationship(back_populates="positionen")
    rohmaterial: Mapped[Rohmaterial] = relationship()

    @property
    def schluessel(self) -> str:
        return f"{self.artikelnummer}-{self.position}"
