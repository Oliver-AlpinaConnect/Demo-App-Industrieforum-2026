"""Termine und Status eines Auftrags. Regeln R-005 bis R-009."""

from __future__ import annotations

from datetime import date

from app.regeln.typen import Kalenderwoche, Prioritaet, Status


def liefer_kw(liefertermin: date) -> Kalenderwoche:
    """R-005: Liefer-KW aus dem Liefertermin, ISO-Woche.

    Satz: Die Liefer-KW eines Auftrags ist die ISO-Kalenderwoche seines Liefertermins,
    geführt als Paar (Jahr, ISO-Woche).

    Beispiel: Auftrag 26-0430, Liefertermin 30.10.2026 -> 2026-KW44.
    Auftrag 26-0388, Liefertermin 18.09.2026 -> 2026-KW38.

    Das Excel rechnet mit `WEEKNUM(...,21)` und führt danach die nackte Wochennummer
    weiter; über den Jahreswechsel bricht das an vier Stellen (R-006, R-019, R-021,
    R-032). Hier trägt jede Woche ihr Jahr mit, deshalb entfällt das Problem.
    """
    return Kalenderwoche.von_datum(liefertermin)


def plan_kw(liefer_kw: Kalenderwoche, prioritaet: Prioritaet, vorlauf_wochen: int) -> Kalenderwoche:
    """R-006: Plan-KW aus Liefer-KW und Priorität.

    Satz: Die Plan-KW ist die Liefer-KW minus dem Vorlauf der Priorität; der Vorlauf
    steht je Priorität in `parameter` (A = 2 Wochen, B und C = 1 Woche).

    Beispiel: Auftrag 26-0426, Prio A, Liefer-KW 2026-KW44 -> 2026-KW42.
    Auftrag 26-0425, Prio B, Liefer-KW 2026-KW42 -> 2026-KW41.
    Über den Jahreswechsel: Prio A mit Liefer-KW 2027-KW01 -> 2026-KW51.

    Prio B und C werden hier gleich behandelt, der Unterschied wirkt erst in R-021.
    Im Excel steht die 2 fest in der Formel und `Parameter!B18` ist nie angeschlossen
    worden (Entscheidung zu F-3).
    """
    if vorlauf_wochen < 0:
        raise ValueError("Vorlauf darf nicht negativ sein")
    del prioritaet  # Die Priorität wählt den Vorlauf, gerechnet wird nur mit ihm.
    return liefer_kw.minus(vorlauf_wochen)


def kw_effektiv(plan_kw: Kalenderwoche, manuelle_kw: Kalenderwoche | None) -> Kalenderwoche:
    """R-007: KW eff. - die manuell gesetzte Woche schlägt die Plan-KW.

    Satz: Die effektive Planwoche ist die manuell gesetzte Woche, wenn eine eingetragen
    ist, sonst die Plan-KW.

    Beispiel: Auftrag 26-0420, Plan-KW 2026-KW41, manuelle KW 2026-KW42 -> 2026-KW42.
    Ohne Eintrag gilt die Plan-KW.

    KW eff. ist der Schlüssel für alles Weitere: Wochenplan (R-016) und Bedarf (R-022)
    rechnen mit dieser Woche, nicht mit Plan-KW und nicht mit Liefer-KW.
    """
    return manuelle_kw if manuelle_kw is not None else plan_kw


def ist_laufend(status: Status) -> bool:
    """R-008: Status eines Auftrags.

    Satz: Ein Auftrag hat genau einen der drei Status `offen`, `in Arbeit` oder
    `erledigt`; alles ausser `erledigt` zählt als laufend und geht in Belastung und
    Bedarf ein.

    Beispiel: 26-0404 hat Status `in Arbeit` und zählt in die Belastung von M1 in
    KW 39. 26-0395 hat Status `erledigt` und fällt aus Belastung und Bedarf.

    Im Excel gibt es keine Datenprüfung, ein Tippfehler wie "Offen" verschwindet still
    aus der Zählung. Hier ist der Status ein Aufzählungstyp, ein unbekannter Wert wird
    beim Import abgelehnt.
    """
    return status is not Status.ERLEDIGT


def status_aus_text(text: str) -> Status:
    """R-008: Statustext exakt einlesen, nicht still korrigieren.

    Beispiel: "offen" -> Status.OFFEN. "Offen" oder "erledigt " werden abgelehnt.
    """
    try:
        return Status(text)
    except ValueError as fehler:
        erlaubt = ", ".join(s.value for s in Status)
        raise ValueError(f"Unbekannter Status {text!r}. Erlaubt: {erlaubt}") from fehler


def ist_ueberfaellig(status: Status, liefer_kw: Kalenderwoche, aktuelle_kw: Kalenderwoche) -> bool:
    """R-009: Überfälliger Auftrag.

    Satz: Ein Auftrag ist überfällig, wenn er nicht `erledigt` ist und seine Liefer-KW
    vor der aktuellen KW liegt.

    Beispiel: Auftrag 26-0402, Liefer-KW 2026-KW38, aktuelle KW 2026-KW39, Status
    `offen` -> überfällig. Ein erledigter Auftrag mit Liefer-KW 2026-KW38 ist es nicht.

    Massgeblich ist die Liefer-KW, nicht die effektive Planwoche: ein Auftrag, den die
    Verschiebung in die Vergangenheit schöbe, wäre sonst plötzlich nicht mehr
    überfällig. Für die Anzeige gilt: Zeile `bg-peach` plus das Wort "überfällig".
    """
    return ist_laufend(status) and liefer_kw < aktuelle_kw
