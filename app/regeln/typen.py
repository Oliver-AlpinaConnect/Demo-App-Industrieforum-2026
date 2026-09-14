"""Werttypen der Fachlogik.

Reine Werte, keine Datenbank. Der wichtigste Typ ist `Kalenderwoche`: das Excel kennt
nur die nackte Wochennummer, die App führt immer das Paar (Jahr, ISO-Woche) und rechnet
Wochendifferenzen über echte Datumsrechnung (R-005).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal
from enum import StrEnum

ZEITZONE = "Europe/Zurich"


@dataclass(frozen=True, order=True)
class Kalenderwoche:
    """Eine Kalenderwoche als Paar (Jahr, ISO-Woche).

    Ausgabe "2026-KW39". Vergleiche und Differenzen laufen über den Montag der Woche,
    deshalb stimmen sie auch über den Jahreswechsel (R-005).
    """

    jahr: int
    woche: int

    def __post_init__(self) -> None:
        if not 1 <= self.woche <= 53:
            raise ValueError(f"ISO-Woche ausserhalb 1..53: {self.woche}")
        # Wirft ValueError, wenn das Jahr die Woche nicht hat (z.B. 2026-KW53).
        date.fromisocalendar(self.jahr, self.woche, 1)

    @classmethod
    def von_datum(cls, tag: date) -> Kalenderwoche:
        jahr, woche, _ = tag.isocalendar()
        return cls(jahr, woche)

    @property
    def montag(self) -> date:
        return date.fromisocalendar(self.jahr, self.woche, 1)

    @property
    def sonntag(self) -> date:
        return self.montag + timedelta(days=6)

    def plus(self, wochen: int) -> Kalenderwoche:
        return Kalenderwoche.von_datum(self.montag + timedelta(weeks=wochen))

    def minus(self, wochen: int) -> Kalenderwoche:
        return self.plus(-wochen)

    def abstand(self, andere: Kalenderwoche) -> int:
        """Anzahl Wochen von dieser Woche bis `andere`, negativ wenn `andere` früher liegt."""
        return (andere.montag - self.montag).days // 7

    def __str__(self) -> str:
        return f"{self.jahr}-KW{self.woche:02d}"


class Status(StrEnum):
    """Auftragsstatus, exakt wie im Excel geschrieben (R-008)."""

    OFFEN = "offen"
    IN_ARBEIT = "in Arbeit"
    ERLEDIGT = "erledigt"


class Prioritaet(StrEnum):
    """Priorität eines Auftrags (R-006, R-021)."""

    A = "A"
    B = "B"
    C = "C"


class Bewertung(StrEnum):
    """Bewertung eines Lieferanten (R-028). A = zuverlässig, B = ok, C = kritisch."""

    A = "A"
    B = "B"
    C = "C"


class Ampel(StrEnum):
    """Ampelstufe der Auslastung (R-018). Farbe nie allein, immer mit Wort."""

    ROT = "rot"
    GELB = "gelb"
    GRUEN = "gruen"
    NEUTRAL = "neutral"


def stunden(wert: Decimal | int | str) -> Decimal:
    """Stunden auf eine Dezimale, kaufmännisch gerundet (Hausregel)."""
    return Decimal(wert).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def menge(wert: Decimal | int | str) -> Decimal:
    """Rohmaterialmenge auf eine Dezimale, kaufmännisch gerundet (Hausregel)."""
    return Decimal(wert).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def aufgerundet(wert: Decimal, stellen: int = 1) -> Decimal:
    """Aufrunden wie ROUNDUP in Excel (R-013, R-025, R-030)."""
    faktor = Decimal(1).scaleb(-stellen)
    return Decimal(wert).quantize(faktor, rounding=ROUND_CEILING)


def geld(wert: Decimal | int | str) -> Decimal:
    """Geldbetrag auf zwei Dezimalen (Hausregel: nie float)."""
    return Decimal(wert).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
