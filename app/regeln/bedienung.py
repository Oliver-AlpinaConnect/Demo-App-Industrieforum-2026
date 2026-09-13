"""Bedienung und Kennzahlen. Regeln R-037 und R-038."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.regeln.kapazitaet import Planauftrag, ausserhalb_horizont
from app.regeln.material import Bestellvorschlag
from app.regeln.termine import ist_laufend, ist_ueberfaellig
from app.regeln.typen import Kalenderwoche, Status, geld


def auftrag_abschliessen(status: Status, bemerkung: str, tag: date) -> tuple[Status, str]:
    """R-037: Auftrag abschliessen.

    Satz: Ein Auftrag wird auf `erledigt` gesetzt und bekommt den Vermerk
    "erledigt TT.MM." in der Bemerkung; eine vorhandene Bemerkung bleibt erhalten und
    wird mit "; " ergänzt.

    Beispiel: Status `offen`, Bemerkung "Nachtrag zu 26-0416", Tag 13.09.2026 ->
    (`erledigt`, "Nachtrag zu 26-0416; erledigt 13.09."). Ohne vorhandene Bemerkung
    steht dort nur "erledigt 13.09.".

    Ein bereits erledigter Auftrag wird nicht zweimal abgeschlossen. Wer wann
    abgeschlossen hat, steht im `aenderungslog` (Hausregel); im Excel gab es dazu
    nichts und keinen Weg zurück.
    """
    if status is Status.ERLEDIGT:
        raise ValueError("Auftrag ist bereits erledigt")
    vermerk = f"erledigt {tag.strftime('%d.%m.')}"
    neue_bemerkung = f"{bemerkung}; {vermerk}" if bemerkung else vermerk
    return Status.ERLEDIGT, neue_bemerkung


@dataclass(frozen=True)
class Kennzahlen:
    """Die Kennzahlen der Wochenübersicht (R-038)."""

    offene_auftraege: int
    davon_in_arbeit: int
    davon_ueberfaellig: int
    auftraege_aktuelle_kw: int
    ausserhalb_horizont: int
    bestellpositionen: int
    bestellwert: Decimal
    bestellpositionen_ueberfaellig: int


def kennzahlen(
    auftraege: list[Planauftrag],
    horizont_wochen: list[Kalenderwoche],
    aktuelle_kw: Kalenderwoche,
    vorschlaege: list[Bestellvorschlag],
) -> Kennzahlen:
    """R-038: Kennzahlen der Übersicht.

    Satz: Die Übersicht zeigt offene Aufträge, davon in Arbeit, davon überfällig,
    Aufträge in der aktuellen KW, Aufträge ausserhalb des Horizonts,
    Bestellpositionen dieser Woche, Bestellwert dieser Woche und davon überfällige
    Positionen.

    Beispiel: 50 Aufträge mit 3 erledigten ergeben 47 offene; davon 2 in Arbeit,
    1 überfällig, 7 in der aktuellen KW, 2 ausserhalb des Horizonts. Dazu
    5 Bestellpositionen, davon 2 überfällig.

    "Offene Aufträge" zählt offen und in Arbeit zusammen, also alles ausser
    `erledigt`. Alle Zählungen benutzen dieselbe Auftragsliste; im Excel zählte
    `C6` mit einer anderen Bedingung als der Rest.
    """
    laufende = [auftrag for auftrag in auftraege if ist_laufend(auftrag.status)]
    return Kennzahlen(
        offene_auftraege=len(laufende),
        davon_in_arbeit=sum(1 for auftrag in laufende if auftrag.status is Status.IN_ARBEIT),
        davon_ueberfaellig=sum(
            1
            for auftrag in laufende
            if ist_ueberfaellig(auftrag.status, auftrag.liefer_kw, aktuelle_kw)
        ),
        auftraege_aktuelle_kw=sum(1 for auftrag in laufende if auftrag.kw_effektiv == aktuelle_kw),
        ausserhalb_horizont=len(ausserhalb_horizont(auftraege, horizont_wochen)),
        bestellpositionen=sum(1 for vorschlag in vorschlaege if vorschlag.bestellen),
        bestellwert=geld(
            sum(
                (vorschlag.bestellwert for vorschlag in vorschlaege if vorschlag.bestellen),
                Decimal(0),
            )
        ),
        bestellpositionen_ueberfaellig=sum(
            1 for vorschlag in vorschlaege if vorschlag.bestellen and vorschlag.ueberfaellig
        ),
    )
