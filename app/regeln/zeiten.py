"""Zeiten eines Auftrags. Regeln R-003 und R-004."""

from __future__ import annotations

from decimal import Decimal

from app.regeln.typen import stunden

MATERIAL_MIT_ZUSCHLAG = "Alu"


def ruestzeit_minuten(
    ruestzeit_basis_min: int,
    material: str,
    menge_stk: int,
    losgrenze_stk: int,
    ruestzuschlag_min: int,
) -> int:
    """R-003: Rüstzeit je Auftrag, mit Zuschlag für Alu über der Losgrenze.

    Satz: Die Rüstzeit ist die Rüstzeit-Basis des Artikels, plus der Rüstzuschlag Alu,
    wenn das Material des Artikels genau `Alu` heisst und die Auftragsmenge grösser als
    die Losgrenze ist. Die Grenze ist echt grösser als, nicht grösser gleich.

    Beispiel: Auftrag 26-0414, Artikel A-1005 (Alu), Menge 620, Basis 50 min,
    Losgrenze 500, Zuschlag 40 min -> 90 min. Gegenprobe 26-0395, gleicher Artikel,
    Menge 120 -> 50 min. Menge genau 500 -> kein Zuschlag.

    Losgrenze und Zuschlag kommen immer aus `parameter` (R-001, Entscheidung zu F-1).
    """
    if material == MATERIAL_MIT_ZUSCHLAG and menge_stk > losgrenze_stk:
        return ruestzeit_basis_min + ruestzuschlag_min
    return ruestzeit_basis_min


def bearbeitungszeit_stunden(menge_stk: int, minuten_je_stueck: Decimal) -> Decimal:
    """R-004: Bearbeitungszeit eines Auftrags in Stunden.

    Satz: Menge mal Bearbeitungszeit je Stück in Minuten, geteilt durch 60.

    Beispiel: Auftrag 26-0414, Menge 620, 4,0 min/Stk -> 620 * 4,0 / 60 = 41,3 h.
    """
    return stunden(Decimal(menge_stk) * Decimal(minuten_je_stueck) / Decimal(60))


def gesamtzeit_stunden(menge_stk: int, minuten_je_stueck: Decimal, ruestzeit_min: int) -> Decimal:
    """R-004: Gesamtzeit eines Auftrags in Stunden.

    Satz: Bearbeitungszeit plus Rüstzeit durch 60, in Stunden auf eine Dezimale.

    Beispiel: Auftrag 26-0414, 620 Stk, 4,0 min/Stk, Rüstzeit 90 min ->
    41,333 h + 1,5 h = 42,8 h. Die Gesamtzeit ist der einzige Zeitwert, den der
    Wochenplan verwendet (R-016).

    Gerundet wird erst am Schluss, nicht auf der Bearbeitungszeit.
    """
    roh = Decimal(menge_stk) * Decimal(minuten_je_stueck) / Decimal(60) + Decimal(
        ruestzeit_min
    ) / Decimal(60)
    return stunden(roh)
