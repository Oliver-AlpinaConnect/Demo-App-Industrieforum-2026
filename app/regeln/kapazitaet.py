"""Kapazität, Belastung und Wochenplan. Regeln R-014 bis R-021."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal

from app.regeln.termine import ist_laufend
from app.regeln.typen import Ampel, Kalenderwoche, Prioritaet, Status, stunden

KEINE_WARTUNG = None


@dataclass(frozen=True)
class Planauftrag:
    """Ein Auftrag, so wie ihn der Wochenplan sieht (R-016)."""

    auftragsnummer: str
    maschine: str
    kw_effektiv: Kalenderwoche
    liefer_kw: Kalenderwoche
    gesamtzeit_h: Decimal
    status: Status
    prioritaet: Prioritaet


@dataclass(frozen=True)
class Verschiebung:
    """Eine Verschiebung, die R-021 vorschlägt."""

    auftragsnummer: str
    maschine: str
    von_kw: Kalenderwoche
    nach_kw: Kalenderwoche
    grund: str


def wochenkapazitaet_stunden(
    schichten_pro_tag: int,
    stunden_pro_schicht: Decimal,
    arbeitstage_pro_woche: int,
    verfuegbarkeit_prozent: Decimal,
) -> Decimal:
    """R-014: Kapazität einer Maschine pro Woche.

    Satz: Schichten pro Tag mal Stunden je Schicht mal Arbeitstage pro Woche mal
    Verfügbarkeit der Maschine, in Stunden.

    Beispiel: M1 mit 2 Schichten, 8,0 h, 5 Tagen und 85 % -> 68,0 h.
    M3 mit 80 % -> 64,0 h, M4 mit 90 % -> 72,0 h.

    Schichten, Stunden und Tage kommen für jede Maschine aus `parameter`; im Excel hat
    M3 sie fest eingetippt (Entscheidung zu F-2). Die Verfügbarkeit steht bewusst je
    Maschine.
    """
    roh = (
        Decimal(schichten_pro_tag)
        * Decimal(stunden_pro_schicht)
        * Decimal(arbeitstage_pro_woche)
        * Decimal(verfuegbarkeit_prozent)
        / Decimal(100)
    )
    return stunden(roh)


def kapazitaet_der_woche(
    grundkapazitaet_h: Decimal,
    wartungs_kw: Kalenderwoche | None,
    kw: Kalenderwoche,
    wartungsabzug_h: Decimal,
) -> Decimal:
    """R-015: Wartungswoche zieht einen festen Betrag ab.

    Satz: In der Wartungs-KW einer Maschine wird die Wochenkapazität um den
    Wartungsabzug gekürzt; ohne Wartungs-KW wird nie gekürzt.

    Beispiel: M1 hat 68,0 h und Wartung in 2026-KW41: in KW 41 stehen 52,0 h, in allen
    anderen Wochen 68,0 h. M3 hat keine Wartung und wird nie gekürzt.

    Die Kapazität wird nie negativ.
    """
    if wartungs_kw is not None and wartungs_kw == kw:
        return stunden(max(Decimal(0), grundkapazitaet_h - Decimal(wartungsabzug_h)))
    return stunden(grundkapazitaet_h)


def belastung_stunden(auftraege: list[Planauftrag], maschine: str, kw: Kalenderwoche) -> Decimal:
    """R-016: Belastung einer Maschine in einer Woche.

    Satz: Summe der Gesamtzeiten aller Aufträge dieser Maschine, deren KW eff. diese
    Woche ist und die nicht `erledigt` sind.

    Beispiel: M1 in 2026-KW39 mit 26-0404 (27,0 h) und 26-0407 (13,0 h) -> 40,0 h.
    Ein erledigter Auftrag derselben Woche zählt nicht mit.

    Im Excel ist die Regel zweimal umgesetzt (SUMIFS im Blatt, VBA-Funktion
    `Belastung`) mit unterschiedlichen Zeilengrenzen. Hier gibt es genau eine Funktion.
    """
    return stunden(
        sum(
            (
                auftrag.gesamtzeit_h
                for auftrag in auftraege
                if auftrag.maschine == maschine
                and auftrag.kw_effektiv == kw
                and ist_laufend(auftrag.status)
            ),
            Decimal(0),
        )
    )


def auslastung(belastung_h: Decimal, kapazitaet_h: Decimal) -> Decimal:
    """R-017: Auslastung einer Maschine in einer Woche.

    Satz: Belastung geteilt durch Kapazität dieser Woche; bei Kapazität 0 ist die
    Auslastung 0.

    Beispiel: M1 in KW 39 mit 40,0 h auf 68,0 h -> 0,588 (58,8 %).
    M1 in der Wartungswoche KW 41 mit 44,0 h auf 52,0 h -> 0,846 (84,6 %).
    """
    if kapazitaet_h == 0:
        return Decimal(0)
    return (Decimal(belastung_h) / Decimal(kapazitaet_h)).quantize(Decimal("0.001"))


def ampel(
    auslastung_anteil: Decimal,
    auslastungsgrenze: Decimal,
    gelb_ab: Decimal = Decimal("0.75"),
    gruen_bis: Decimal = Decimal("0.40"),
) -> Ampel:
    """R-018: Auslastungsampel.

    Satz: Eine Auslastung über der Auslastungsgrenze ist rot, von 75 % bis zur Grenze
    gelb, unter 40 % grün, dazwischen neutral.

    Beispiel: 0,859 bei Grenze 0,90 -> gelb. 0,289 -> grün. 0,912 -> rot.
    0,50 -> neutral (die Lücke zwischen 40 % und 75 % ist bewusst ohne Farbe).

    Im Excel hat der Wochenplan drei Stufen und die Übersicht nur die rote; hier gilt
    überall dieselbe Ampel. Die Farbe steht nie allein, die Anzeige schreibt das Wort
    dazu (Hausregel).
    """
    if auslastung_anteil > auslastungsgrenze:
        return Ampel.ROT
    if auslastung_anteil >= gelb_ab:
        return Ampel.GELB
    if auslastung_anteil < gruen_bis:
        return Ampel.GRUEN
    return Ampel.NEUTRAL


def horizont(aktuelle_kw: Kalenderwoche, wochen: int) -> list[Kalenderwoche]:
    """R-019: Planungshorizont, acht Wochen ab der aktuellen KW.

    Satz: Geplant wird über die Anzahl Wochen aus `parameter`, beginnend mit der
    aktuellen KW.

    Beispiel: aktuelle KW 2026-KW39, Horizont 8 -> 2026-KW39 bis 2026-KW46.
    Über den Jahreswechsel: 2026-KW50, 51, 52, 53, 2027-KW01, 02, 03, 04.

    Im Excel stehen die acht Wochennummern an vier Stellen von Hand eingetippt; hier
    leitet sich alles aus der aktuellen Woche und dem Parameter ab (F-4, F-5).
    """
    if wochen < 1:
        raise ValueError("Horizont muss mindestens eine Woche umfassen")
    return [aktuelle_kw.plus(versatz) for versatz in range(wochen)]


def ausserhalb_horizont(
    auftraege: list[Planauftrag], horizont_wochen: list[Kalenderwoche]
) -> list[Planauftrag]:
    """R-020: Aufträge ausserhalb des Horizonts fallen aus der Planung.

    Satz: Aufträge, deren KW eff. vor oder nach dem Horizont liegt, erscheinen in
    keinem Wochenplan und in keinem Bedarf; die App benennt sie.

    Beispiel: Bei Horizont 2026-KW39 bis KW46 fallen 26-0402 (KW eff. 37) und
    26-0446 (KW eff. 47) heraus. Erledigte Aufträge zählen nicht mit.

    Im Excel sieht man nur eine Zahl und muss von Hand nachsehen, welche Aufträge
    gemeint sind. Hier gibt die Funktion die Aufträge selbst zurück.
    """
    wochen = set(horizont_wochen)
    return [
        auftrag
        for auftrag in auftraege
        if ist_laufend(auftrag.status) and auftrag.kw_effektiv not in wochen
    ]


def _verschiebbar(auftrag: Planauftrag) -> bool:
    """R-021: Nur `offen` und nie Priorität A darf verschoben werden."""
    return auftrag.status is Status.OFFEN and auftrag.prioritaet is not Prioritaet.A


def verschiebungen(
    auftraege: list[Planauftrag],
    maschinen: list[str],
    horizont_wochen: list[Kalenderwoche],
    kapazitaet: dict[tuple[str, Kalenderwoche], Decimal],
    auslastungsgrenze: Decimal,
    hoechstens: int = 20,
) -> list[Verschiebung]:
    """R-021: Automatische Verschiebung bei Überlast.

    Satz: Übersteigt die Belastung einer Maschine in einer Woche die Auslastungsgrenze,
    wird so lange je ein Auftrag in die Folgewoche verschoben, bis die Grenze
    eingehalten ist; verschoben werden nur Aufträge mit Status `offen`, nie Priorität A,
    zuerst Priorität C dann B, und innerhalb einer Priorität der kleinste Auftrag, der
    die Überlast allein beseitigt, sonst der grösste.

    Beispiel: M1 in 2026-KW41 mit 62,0 h Belastung auf 52,0 h Kapazität und Grenze
    90 % (Limit 46,8 h): der Prio-C-Auftrag 26-0420 mit 18,0 h beseitigt die Überlast
    allein und wandert nach 2026-KW42.

    Die Funktion ändert nichts, sie gibt die Verschiebungen zurück. Damit entfällt der
    Rücksetzmechanismus des Makros über den Bemerkungstext: die Vorschläge werden jedes
    Mal neu gerechnet, und was ein Mensch von Hand gesetzt hat, bleibt unangetastet.
    Eine Verschiebung über das Horizontende hinaus wird nicht vorgeschlagen, weil der
    Auftrag sonst nach R-020 aus der Planung fiele.
    """
    stand = {auftrag.auftragsnummer: auftrag for auftrag in auftraege}
    ergebnis: list[Verschiebung] = []
    letzte_woche = horizont_wochen[-1]

    for maschine in maschinen:
        for kw in horizont_wochen:
            if kw == letzte_woche:
                continue
            for _ in range(hoechstens):
                aktuelle = list(stand.values())
                last = belastung_stunden(aktuelle, maschine, kw)
                limit = stunden(
                    Decimal(kapazitaet.get((maschine, kw), Decimal(0))) * Decimal(auslastungsgrenze)
                )
                if last <= limit:
                    break
                ueberlast = last - limit
                kandidat = _kandidat(aktuelle, maschine, kw, ueberlast)
                if kandidat is None:
                    break
                nach = kw.plus(1)
                stand[kandidat.auftragsnummer] = replace(kandidat, kw_effektiv=nach)
                ergebnis.append(
                    Verschiebung(
                        auftragsnummer=kandidat.auftragsnummer,
                        maschine=maschine,
                        von_kw=kw,
                        nach_kw=nach,
                        grund=(
                            f"Überlast {ueberlast} h über Limit {limit} h, "
                            f"Prio {kandidat.prioritaet.value}"
                        ),
                    )
                )
    return ergebnis


def _kandidat(
    auftraege: list[Planauftrag], maschine: str, kw: Kalenderwoche, ueberlast: Decimal
) -> Planauftrag | None:
    """R-021: Auswahl des zu verschiebenden Auftrags, erst Prio C, dann Prio B."""
    for prioritaet in (Prioritaet.C, Prioritaet.B):
        menge = sorted(
            (
                auftrag
                for auftrag in auftraege
                if auftrag.maschine == maschine
                and auftrag.kw_effektiv == kw
                and auftrag.prioritaet is prioritaet
                and _verschiebbar(auftrag)
            ),
            key=lambda auftrag: (auftrag.gesamtzeit_h, auftrag.auftragsnummer),
        )
        if not menge:
            continue
        for auftrag in menge:
            if auftrag.gesamtzeit_h >= ueberlast:
                return auftrag
        return menge[-1]
    return None
