"""Export nach Abacus. Regeln R-033 bis R-036."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from app.regeln.typen import Kalenderwoche

KOPFZEILE: tuple[str, ...] = (
    "ARTNR",
    "LIEFNR",
    "MENGE",
    "EINHEIT",
    "BEDARFSDATUM",
    "KOSTENSTELLE",
    "BEMERKUNG",
)
TRENNZEICHEN = ";"
KODIERUNG = "cp1252"  # ANSI, wie die Abacus-Import-Definition PLAN_BESTELL es erwartet
DATUMSFORMAT = "%d.%m.%Y"


@dataclass(frozen=True)
class Exportposition:
    """Eine Bestellposition, so wie der Export sie braucht (R-033)."""

    rohnummer: str
    erp_artikelnummer: str
    erp_lieferantennummer: str
    bestellmenge: Decimal
    einheit: str
    bedarfsdatum: date | None
    bestell_kw: Kalenderwoche | None


@dataclass(frozen=True)
class Exportzeile:
    """Eine fertige Zeile der CSV (R-033)."""

    artnr: str
    liefnr: str
    menge: str
    einheit: str
    bedarfsdatum: str
    kostenstelle: str
    bemerkung: str

    def als_liste(self) -> list[str]:
        return [
            self.artnr,
            self.liefnr,
            self.menge,
            self.einheit,
            self.bedarfsdatum,
            self.kostenstelle,
            self.bemerkung,
        ]


@dataclass(frozen=True)
class Exportergebnis:
    """Zeilen und Meldungen eines Exportlaufs."""

    zeilen: list[Exportzeile]
    meldungen: list[str]


def _menge_als_text(wert: Decimal) -> str:
    if wert == wert.to_integral_value():
        return str(int(wert))
    return f"{wert:.1f}"


def export_bemerkung(aktuelle_kw: Kalenderwoche, bestell_kw: Kalenderwoche | None) -> str:
    """R-034: Vermerk "überfällig" in der Exportbemerkung.

    Satz: Die Bemerkung lautet "Bestellvorschlag KW<aktuelle KW>" und wird um
    " ÜBERFÄLLIG (Bestell-KW <n>)" ergänzt, wenn die Bestell-KW vor der aktuellen
    Woche liegt.

    Beispiel: aktuelle KW 2026-KW39, Bestell-KW 2026-KW37 ->
    "Bestellvorschlag KW39 ÜBERFÄLLIG (Bestell-KW 37)".
    Bestell-KW 2026-KW39 -> "Bestellvorschlag KW39".

    Der Text sagt "Bestellvorschlag" statt "Excel Bestellvorschlag", weil er nicht mehr
    aus dem Excel kommt. Die Wochennummern bleiben nackt, weil das Feld so nach Abacus
    geht.
    """
    bemerkung = f"Bestellvorschlag KW{aktuelle_kw.woche}"
    if bestell_kw is not None and bestell_kw < aktuelle_kw:
        bemerkung += f" ÜBERFÄLLIG (Bestell-KW {bestell_kw.woche})"
    return bemerkung


def exportzeilen(
    positionen: list[Exportposition], aktuelle_kw: Kalenderwoche, kostenstelle: int
) -> Exportergebnis:
    """R-033: Inhalt und Reihenfolge der Exportdatei.

    Satz: Der Export enthält je Bestellposition mit "Bestellen? = ja" genau sieben
    Felder in fester Reihenfolge: ERP-Artikelnummer, ERP-Lieferantennummer,
    Bestellmenge, Einheit, Bedarfsdatum, Kostenstelle Einkauf, Bemerkung.

    Beispiel: RM-109 mit ERP-Nummer 3090012, 80 Stk, Bedarfsdatum 26.10.2026,
    Kostenstelle 4100 ergibt
    "3090012;L04711;80;Stk;26.10.2026;4100;Bestellvorschlag KW39".

    Die ERP-Artikelnummer bleibt Text, führende Nullen gehen nicht verloren. Fehlt die
    ERP-Nummer des Artikels oder des Lieferanten, wird die Zeile gemeldet und
    übersprungen; im Excel blieb die Lieferantennummer still leer.
    """
    zeilen: list[Exportzeile] = []
    meldungen: list[str] = []
    for position in positionen:
        if not position.erp_artikelnummer:
            meldungen.append(f"{position.rohnummer}: keine ERP-Artikelnummer, Zeile übersprungen")
            continue
        if not position.erp_lieferantennummer:
            meldungen.append(
                f"{position.rohnummer}: keine ERP-Lieferantennummer, Zeile übersprungen"
            )
            continue
        if position.bedarfsdatum is None:
            meldungen.append(f"{position.rohnummer}: kein Bedarfsdatum, Zeile übersprungen")
            continue
        zeilen.append(
            Exportzeile(
                artnr=position.erp_artikelnummer,
                liefnr=position.erp_lieferantennummer,
                menge=_menge_als_text(position.bestellmenge),
                einheit=position.einheit,
                bedarfsdatum=position.bedarfsdatum.strftime(DATUMSFORMAT),
                kostenstelle=str(kostenstelle),
                bemerkung=export_bemerkung(aktuelle_kw, position.bestell_kw),
            )
        )
    return Exportergebnis(zeilen=zeilen, meldungen=meldungen)


def csv_text(zeilen: list[Exportzeile]) -> str:
    """R-036: Die CSV als Text, Semikolon getrennt, mit Kopfzeile.

    Satz: Der Export ist eine CSV mit Semikolon als Trennzeichen und der festen
    Kopfzeile aus R-033.

    Beispiel: eine Position ergibt zwei Zeilen, Kopfzeile plus Datenzeile.

    Die Kopfzeile steht nur hier, nicht zusätzlich als Text im Code und im Blatt wie
    im Excel.
    """
    ausgabe = [TRENNZEICHEN.join(KOPFZEILE)]
    ausgabe += [TRENNZEICHEN.join(zeile.als_liste()) for zeile in zeilen]
    return "\r\n".join(ausgabe) + "\r\n"


def csv_bytes(zeilen: list[Exportzeile]) -> bytes:
    """R-036: Die CSV in ANSI-Kodierung (cp1252), wie Abacus sie liest.

    Beispiel: "ÜBERFÄLLIG" wird als cp1252 kodiert, nicht als UTF-8.
    """
    return csv_text(zeilen).encode(KODIERUNG, errors="replace")


def exportdateiname(tag: date, aktuelle_kw: Kalenderwoche) -> str:
    """R-036: Name der Exportdatei.

    Satz: `PLAN_BESTELL_JJJJMMTT_KW<n>.csv` mit dem Tag der Ausführung und der
    aktuellen Kalenderwoche.

    Beispiel: Ausführung am 13.09.2026 in KW 39 -> `PLAN_BESTELL_20260913_KW39.csv`.
    """
    return f"PLAN_BESTELL_{tag.strftime('%Y%m%d')}_KW{aktuelle_kw.woche}.csv"


@dataclass(frozen=True)
class Exportstempel:
    """Zeitpunkt und Person eines Exportlaufs (R-035)."""

    zeitpunkt: datetime
    benutzer: str


def exportstempel(zeitpunkt: datetime, benutzer: str) -> Exportstempel:
    """R-035: Exportstempel.

    Satz: Nach jedem Export werden Zeitpunkt und die ausführende Person festgehalten.

    Beispiel: 13.09.2026 15:07 und "sandra.meier" ergeben einen Stempel, der als
    Eintrag im `aenderungslog` stehen bleibt.

    Im Excel sind es die ersten zwei Zeichen des Windows-Benutzernamens, und jeder
    Export überschreibt den vorigen Stempel. Hier bleibt jeder Lauf erhalten
    (Hausregel: wer, wann, Feld, alt, neu).
    """
    if zeitpunkt.tzinfo is None:
        raise ValueError("Zeitpunkt muss zeitzonenbehaftet sein (Europe/Zurich)")
    if not benutzer:
        raise ValueError("Ohne angemeldete Person kein Export")
    return Exportstempel(zeitpunkt=zeitpunkt, benutzer=benutzer)
