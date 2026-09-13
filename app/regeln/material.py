"""Bedarf, Bestand und Bestellvorschlag. Regeln R-022 bis R-032."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.regeln.termine import ist_laufend
from app.regeln.typen import Bewertung, Kalenderwoche, Status, aufgerundet, geld, menge


@dataclass(frozen=True)
class Materialposition:
    """Eine Auftragsposition, so wie sie der Bedarf sieht (R-022)."""

    auftragsnummer: str
    rohnummer: str
    kw_effektiv: Kalenderwoche
    bedarf: Decimal
    status: Status


def bedarf_der_woche(
    positionen: list[Materialposition], rohnummer: str, kw: Kalenderwoche
) -> Decimal:
    """R-022: Bedarf je Rohmaterial und Woche.

    Satz: Summe der Rohmaterialmengen aller nicht erledigten Auftragspositionen dieses
    Rohmaterials, deren KW eff. diese Woche ist, über alle Stücklistenpositionen.

    Beispiel: RM-107 in 2026-KW43 mit Auftrag 26-0428 (33,0 Platten) -> 33,0.
    Eine Position eines erledigten Auftrags zählt nicht mit.
    """
    return menge(
        sum(
            (
                position.bedarf
                for position in positionen
                if position.rohnummer == rohnummer
                and position.kw_effektiv == kw
                and ist_laufend(position.status)
            ),
            Decimal(0),
        )
    )


def bedarf_je_woche(
    positionen: list[Materialposition],
    rohnummer: str,
    horizont_wochen: list[Kalenderwoche],
) -> list[Decimal]:
    """R-022: Bedarfsreihe eines Rohmaterials über den Horizont.

    Beispiel: RM-107 über 2026-KW39 bis KW46 ->
    14,9 / 0,0 / 0,0 / 9,9 / 33,0 / 0,0 / 4,2 / 11,6.
    """
    return [bedarf_der_woche(positionen, rohnummer, kw) for kw in horizont_wochen]


def summe_horizont(bedarfsreihe: list[Decimal]) -> Decimal:
    """R-022: Summe des Bedarfs über den Horizont.

    Beispiel: 14,9 + 0 + 0 + 9,9 + 33,0 + 0 + 4,2 + 11,6 = 73,6 Platten.
    """
    return menge(sum(bedarfsreihe, Decimal(0)))


def verfuegbarer_bestand(lager: Decimal, bestellt_offen: Decimal) -> Decimal:
    """R-023: Verfügbarer Bestand.

    Satz: Lagerbestand plus offene Bestellungen.

    Beispiel: RM-102 mit 6 Stangen am Lager und 5 offen bestellt -> 11.
    RM-110 mit 620 + 200 -> 820.

    Offene Bestellungen zählen ohne Ankunftswoche, genau wie im Excel; das kann eine
    Fehl-KW zu spät ausweisen (F-10, offen gelassen).
    """
    return menge(Decimal(lager) + Decimal(bestellt_offen))


def durchschnittlicher_wochenbedarf(summe_horizont: Decimal, horizont_wochen: int) -> Decimal:
    """R-024: Durchschnittlicher Wochenbedarf.

    Satz: Summe des Bedarfs über den Horizont geteilt durch die Anzahl Wochen des
    Horizonts.

    Beispiel: RM-107 mit 73,6 über 8 Wochen -> 9,2 Platten je Woche.

    Die Anzahl Wochen kommt aus `parameter`; im Excel steht dort eine feste 8 (F-4).
    """
    if horizont_wochen < 1:
        raise ValueError("Horizont muss mindestens eine Woche umfassen")
    return menge(Decimal(summe_horizont) / Decimal(horizont_wochen))


def sicherheitsbestand(
    durchschnitt_wochenbedarf: Decimal,
    sicherheitsbestand_prozent: Decimal,
    gebinde: Decimal,
) -> Decimal:
    """R-025: Sicherheitsbestand.

    Satz: Der Prozentsatz vom durchschnittlichen Wochenbedarf, aufgerundet auf ganze
    Einheiten, mindestens aber eine Gebindegrösse.

    Beispiel: RM-107 mit Ø 9,2, 10 % -> 0,92 -> aufgerundet 1, Gebinde 4 -> 4.
    RM-110 mit Ø 98,75, 10 % -> 9,875 -> 10, Gebinde 40 -> 40.

    In der Praxis gewinnt fast immer das Gebinde; der Prozentsatz wirkt erst ab einem
    Ø-Wochenbedarf über dem Zehnfachen des Gebindes.
    """
    anteil = aufgerundet(
        Decimal(durchschnitt_wochenbedarf) * Decimal(sicherheitsbestand_prozent) / 100, 0
    )
    return menge(max(anteil, Decimal(gebinde)))


def kumulierter_bedarf(bedarfsreihe: list[Decimal]) -> list[Decimal]:
    """R-026: Kumulierter Bedarf.

    Satz: Summe des Bedarfs von der ersten Horizontwoche bis einschliesslich dieser
    Woche.

    Beispiel: RM-115 mit 0 / 0 / 23,7 / 0 / 0 / 0 / 31,5 / 0 ergibt
    0 / 0 / 23,7 / 23,7 / 23,7 / 23,7 / 55,2 / 55,2.
    """
    laufend = Decimal(0)
    ergebnis: list[Decimal] = []
    for wert in bedarfsreihe:
        laufend += Decimal(wert)
        ergebnis.append(menge(laufend))
    return ergebnis


def fehl_kw(
    horizont_wochen: list[Kalenderwoche],
    kumulierte_reihe: list[Decimal],
    sicherheitsbestand: Decimal,
    verfuegbar: Decimal,
) -> Kalenderwoche | None:
    """R-027: Fehl-KW.

    Satz: Die erste Woche des Horizonts, in der kumulierter Bedarf plus
    Sicherheitsbestand den verfügbaren Bestand übersteigt; reicht der Bestand über den
    ganzen Horizont, gibt es keine Fehl-KW.

    Beispiel: RM-106, verfügbar 5, Sicherheit 5, kumuliert 0 / 13,3 / ...:
    KW 39 mit 0 + 5 > 5 ist falsch, KW 40 mit 13,3 + 5 > 5 ist wahr -> 2026-KW40.

    Der Vergleich ist echt grösser als: bei Gleichstand gilt das Material als
    ausreichend. Die Länge der Reihe kommt aus dem Horizont, nicht aus acht
    verschachtelten IF wie im Excel.
    """
    if len(horizont_wochen) != len(kumulierte_reihe):
        raise ValueError("Horizont und kumulierte Reihe sind unterschiedlich lang")
    for kw, kumuliert in zip(horizont_wochen, kumulierte_reihe, strict=True):
        if Decimal(kumuliert) + Decimal(sicherheitsbestand) > Decimal(verfuegbar):
            return kw
    return None


def bestell_kw(
    fehl_kw: Kalenderwoche | None,
    lieferzeit_wochen: int,
    bewertung: Bewertung,
    puffer_wochen_c: int,
) -> Kalenderwoche | None:
    """R-028: Bestell-KW.

    Satz: Fehl-KW minus Lieferzeit des Lieferanten in Wochen, bei Lieferanten mit
    Bewertung C zusätzlich minus den Puffer; ohne Fehl-KW gibt es keine Bestell-KW.

    Beispiel: RM-109, Fehl-KW 2026-KW44, Lieferzeit 5 Wochen, Bewertung C, Puffer 1
    -> 2026-KW38. RM-101, Fehl-KW 2026-KW42, Lieferzeit 2, Bewertung A -> 2026-KW40.

    Der Puffer hängt an der Bewertung, nicht am einzelnen Lieferanten. Die Bestell-KW
    kann in der Vergangenheit liegen und wird nicht auf die aktuelle Woche begrenzt.
    """
    if fehl_kw is None:
        return None
    puffer = puffer_wochen_c if bewertung is Bewertung.C else 0
    return fehl_kw.minus(lieferzeit_wochen + puffer)


def bestellen(bestell_kw: Kalenderwoche | None, aktuelle_kw: Kalenderwoche) -> bool:
    """R-029: Bestellen ja oder nein.

    Satz: Eine Bestellposition wird vorgeschlagen, wenn eine Bestell-KW vorhanden und
    diese kleiner oder gleich der aktuellen KW ist.

    Beispiel: Bestell-KW 2026-KW39 bei aktueller KW 2026-KW39 -> ja.
    Bestell-KW 2026-KW37 -> ja (und überfällig). Bestell-KW 2026-KW40 -> nein.
    """
    return bestell_kw is not None and bestell_kw <= aktuelle_kw


def bestellung_ueberfaellig(bestell_kw: Kalenderwoche | None, aktuelle_kw: Kalenderwoche) -> bool:
    """R-029: Eine Bestellposition ist überfällig, wenn die Bestell-KW schon vorbei ist.

    Beispiel: Bestell-KW 2026-KW37 bei aktueller KW 2026-KW39 -> überfällig.

    Das ist die zweite Bedeutung von "überfällig" im Excel; der überfällige Auftrag aus
    R-009 ist etwas anderes.
    """
    return bestell_kw is not None and bestell_kw < aktuelle_kw


def bestellmenge(
    summe_horizont: Decimal,
    sicherheitsbestand: Decimal,
    verfuegbar: Decimal,
    gebinde: Decimal,
    fehl_kw: Kalenderwoche | None,
) -> Decimal:
    """R-030: Bestellmenge wird auf Gebinde aufgerundet.

    Satz: Bedarf des Horizonts plus Sicherheitsbestand minus verfügbarer Bestand, nie
    negativ, aufgerundet auf ganze Gebinde; ohne Fehl-KW ist die Bestellmenge 0.

    Beispiel: RM-109 mit 140,0 + 20 - 90 = 70, Gebinde 20 -> 3,5 -> 4 Gebinde -> 80.
    RM-101 mit 32,2 + 10 - 24 = 18,2, Gebinde 10 -> 2 Gebinde -> 20 Stangen.
    """
    if fehl_kw is None:
        return menge(Decimal(0))
    if Decimal(gebinde) <= 0:
        raise ValueError("Gebindegrösse muss grösser als 0 sein")
    offen = max(
        Decimal(0),
        Decimal(summe_horizont) + Decimal(sicherheitsbestand) - Decimal(verfuegbar),
    )
    gebinde_anzahl = aufgerundet(offen / Decimal(gebinde), 0)
    return menge(gebinde_anzahl * Decimal(gebinde))


def bestellwert(bestellmenge: Decimal, preis_je_einheit: Decimal) -> Decimal:
    """R-031: Bestellwert einer Position.

    Satz: Bestellmenge mal Preis je Einheit des Rohmaterials.

    Beispiel: 20 Stangen zu 45.50 -> 910.00. Geld immer als Decimal, nie als float.
    """
    return geld(Decimal(bestellmenge) * Decimal(preis_je_einheit))


def bedarfsdatum(fehl_kw: Kalenderwoche | None) -> date | None:
    """R-032: Bedarfsdatum einer Bestellposition.

    Satz: Der Montag der Fehl-KW; ohne Fehl-KW gibt es kein Bedarfsdatum.

    Beispiel: Fehl-KW 2026-KW44 -> 26.10.2026. Fehl-KW 2027-KW01 -> 04.01.2027.

    Das Excel rechnet "Montag der aktuellen KW plus Differenz der Wochennummern mal 7"
    und liegt über den Jahreswechsel falsch (R-005). Hier kommt der Montag direkt aus
    der Woche, dasselbe Ergebnis innerhalb eines Jahres und richtig darüber hinaus.
    """
    return fehl_kw.montag if fehl_kw is not None else None


@dataclass(frozen=True)
class Bestellvorschlag:
    """Eine gerechnete Zeile des Bestellvorschlags (R-027 bis R-031)."""

    rohnummer: str
    fehl_kw: Kalenderwoche | None
    bestell_kw: Kalenderwoche | None
    bestellen: bool
    ueberfaellig: bool
    bestellmenge: Decimal
    bestellwert: Decimal
