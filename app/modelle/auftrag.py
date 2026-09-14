"""Der Auftrag. Kalenderwochen immer als Paar (Jahr, Woche)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelle.basis import Basis, Kurztext, Langtext
from app.modelle.stammdaten import Artikel
from app.regeln.typen import Kalenderwoche


class Auftrag(Basis):
    """Ein Auftrag. Zeiten und Material rechnet die App aus dem Artikel (R-011)."""

    __tablename__ = "auftrag"

    auftragsnummer: Mapped[str] = mapped_column(String(20), primary_key=True)
    kunde: Mapped[Kurztext] = mapped_column(default="")
    prioritaet: Mapped[str] = mapped_column(String(1), nullable=False)
    artikelnummer: Mapped[str] = mapped_column(ForeignKey("artikel.artikelnummer"))
    menge: Mapped[int] = mapped_column(Integer, nullable=False)
    liefertermin: Mapped[date] = mapped_column(Date, nullable=False)

    # R-007: manuell gesetzte Woche, leer = Plan-KW gilt.
    manuell_jahr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manuell_woche: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # R-011: Umplanung auf eine andere als die Standardmaschine (F-7).
    abweichende_maschine: Mapped[str | None] = mapped_column(
        ForeignKey("maschine.kuerzel"), nullable=True
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False)
    bemerkung: Mapped[Langtext] = mapped_column(default="")

    artikel: Mapped[Artikel] = relationship()

    @property
    def manuelle_kw(self) -> Kalenderwoche | None:
        if self.manuell_jahr is None or self.manuell_woche is None:
            return None
        return Kalenderwoche(self.manuell_jahr, self.manuell_woche)

    def setze_manuelle_kw(self, kw: Kalenderwoche | None) -> None:
        self.manuell_jahr = kw.jahr if kw else None
        self.manuell_woche = kw.woche if kw else None
