"""Darstellung: Zahlen, Daten und Wochen in Schweizer Schreibweise.

Tausendertrennzeichen `'`, Dezimaltrenner `,` in der Anzeige, `.` im Code (Hausregel).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.regeln.typen import Ampel, Kalenderwoche

AMPELWORT = {
    Ampel.ROT: "über Grenze",
    Ampel.GELB: "hoch",
    Ampel.GRUEN: "frei",
    Ampel.NEUTRAL: "normal",
}


def zahl(wert: Decimal | int | float | None, dezimalen: int = 0) -> str:
    """Beispiel: 1329 -> "1'329", Decimal("42.8") mit 1 Dezimale -> "42,8"."""
    if wert is None:
        return ""
    text = f"{Decimal(wert):,.{dezimalen}f}"
    ganz, _, rest = text.partition(".")
    ganz = ganz.replace(",", "'")
    return f"{ganz},{rest}" if rest else ganz


def stunden(wert: Decimal | None) -> str:
    """Beispiel: Decimal("42.8") -> "42,8 h"."""
    return "" if wert is None else f"{zahl(wert, 1)} h"


def menge(wert: Decimal | None) -> str:
    """Beispiel: Decimal("9.4") -> "9,4"."""
    return "" if wert is None else zahl(wert, 1)


def minuten(wert: int | None) -> str:
    """Beispiel: 90 -> "90 min"."""
    return "" if wert is None else f"{zahl(wert)} min"


def prozent(anteil: Decimal | None, dezimalen: int = 1) -> str:
    """Beispiel: Decimal("0.588") -> "58,8 %"."""
    if anteil is None:
        return ""
    return f"{zahl(Decimal(anteil) * 100, dezimalen)} %"


def geld(wert: Decimal | None) -> str:
    """Beispiel: Decimal("910.00") -> "910.00" (Geld mit Punkt, wie auf dem Beleg)."""
    if wert is None:
        return ""
    ganz, _, rest = f"{Decimal(wert):,.2f}".partition(".")
    return f"{ganz.replace(',', chr(39))}.{rest}"


def datum(wert: date | None) -> str:
    """Beispiel: date(2026, 10, 26) -> "26.10.2026"."""
    return "" if wert is None else wert.strftime("%d.%m.%Y")


def kw(wert: Kalenderwoche | None) -> str:
    """Beispiel: Kalenderwoche(2026, 39) -> "2026-KW39"."""
    return "" if wert is None else str(wert)


def kurz(text: str, laenge: int = 60) -> str:
    """Langen Text für die Tabelle kürzen. Der ganze Text steht im Titel der Zeile.

    Beispiel: "Nachtrag zu 26-0416; auf KW44 verschoben" bleibt stehen, ein längerer Text
    endet mit "...".
    """
    if text is None:
        return ""
    return text if len(text) <= laenge else text[: laenge - 1].rstrip() + "…"


def ampelwort(stufe: Ampel) -> str:
    """R-018: das Wort zur Farbe. Beispiel: Ampel.ROT -> "über Grenze"."""
    return AMPELWORT[stufe]


FILTER = {
    "zahl": zahl,
    "stunden": stunden,
    "menge": menge,
    "minuten": minuten,
    "prozent": prozent,
    "geld": geld,
    "datum": datum,
    "kw": kw,
    "ampelwort": ampelwort,
    "kurz": kurz,
}
