"""Regeln, die die App nicht übernimmt. Regeln R-039 und R-040.

Beide Regeln stehen im Katalog mit Status `veraltet`. Sie werden hier nicht
nachgebaut, sondern benannt: die Funktionen sagen, warum die Regel entfällt und was an
ihre Stelle tritt. Damit steht jede Regel-ID an genau einer Stelle im Code.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NichtUebernommen:
    """Eine Regel aus dem Excel, die in der App keine Entsprechung hat."""

    regel: str
    grund: str
    ersatz: str


def sicherungskopie_beim_speichern() -> NichtUebernommen:
    """R-039: Sicherungskopie beim Speichern.

    Satz im Excel: Beim Speichern wird eine Kopie der Datei mit Zeitstempel in einem
    fest verdrahteten Backup-Ordner abgelegt.

    Beispiel: Ein Speichern am 13.09.2026 um 15:07 erzeugte
    `Produktionsplanung_20260913_1507.xlsm`.

    In der App gibt es keine Datei, die jemand speichert. Die Sicherung der Datenbank
    macht der Betrieb, siehe `docs/betrieb.md`.
    """
    return NichtUebernommen(
        regel="R-039",
        grund="Es gibt keine Arbeitsmappe mehr, die jemand von Hand speichert.",
        ersatz="Sicherung der Datenbank im Betrieb, siehe docs/betrieb.md.",
    )


def montagserinnerung_und_tastenkuerzel() -> NichtUebernommen:
    """R-040: Montagserinnerung und Tastenkürzel.

    Satz im Excel: Beim Öffnen werden drei Tastenkürzel gesetzt, und montags erscheint
    eine Erinnerung, die aktuelle KW zu prüfen.

    Beispiel: `Ctrl+Shift+W` startete `Wochenplan_aktualisieren`, `Ctrl+Shift+E` den
    Export, `Ctrl+Shift+A` das Abschliessen eines Auftrags.

    In der App entfällt der ganze Montagsablauf: die aktuelle Woche kommt aus dem
    Datum (R-002), der Wochenplan rechnet bei jedem Aufruf neu (R-016), und der Export
    ist ein Knopf auf der Seite Material (R-033).
    """
    return NichtUebernommen(
        regel="R-040",
        grund="Die aktuelle KW wird nicht mehr von Hand gesetzt, es gibt nichts zu erinnern.",
        ersatz="R-002 rechnet die Woche aus dem Datum, die Seiten rechnen bei jedem Aufruf neu.",
    )
