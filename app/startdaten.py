"""Startdaten laden.

Die Dateien in `tests/daten/` sind anonymisierte Demodaten, aufgebaut aus den
Beispielen in `docs/regeln.md`. Bezugswoche ist 2026-KW39, die "aktuelle KW" des
Katalogs. Beim Laden können alle Termine um eine feste Anzahl Wochen verschoben werden,
damit die App auch in einer anderen Woche einen vollen Horizont zeigt.

Echte Kunden- und Preisdaten stehen hier nicht drin (Hausregel).
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import WURZEL
from app.modelle import (
    Artikel,
    Auftrag,
    Lieferant,
    Maschine,
    Parametersatz,
    Rohmaterial,
    Stuecklistenposition,
)
from app.regeln.typen import Kalenderwoche

STARTDATEN = WURZEL / "tests" / "daten"
BEZUGSWOCHE = Kalenderwoche(2026, 39)


def _lies(ordner: Path, name: str) -> list[dict]:
    return json.loads((ordner / name).read_text(encoding="utf-8"))


def verschiebung_auf(ziel_kw: Kalenderwoche) -> int:
    """Anzahl Wochen, um die die Demodaten zu verschieben sind.

    Beispiel: Bezugswoche 2026-KW39, Ziel 2026-KW37 -> -2.
    """
    return BEZUGSWOCHE.abstand(ziel_kw)


def _woche_verschoben(kw: Kalenderwoche, wochen: int) -> Kalenderwoche:
    return kw.plus(wochen)


def ist_leer(sitzung: Session) -> bool:
    return sitzung.scalar(select(Auftrag).limit(1)) is None


def lade_startdaten(
    sitzung: Session, ordner: Path | None = None, wochen_verschoben: int = 0
) -> None:
    """Schreibt die Demodaten in eine leere Datenbank."""
    quelle = ordner or STARTDATEN

    for satz in _lies(quelle, "parameter.json"):
        sitzung.merge(
            Parametersatz(
                name=satz["name"],
                wert=Decimal(satz["wert"]),
                beschriftung=satz["beschriftung"],
                einheit=satz["einheit"],
            )
        )

    for satz in _lies(quelle, "maschinen.json"):
        wartung = None
        if satz["wartung_jahr"] and satz["wartung_woche"]:
            wartung = _woche_verschoben(
                Kalenderwoche(satz["wartung_jahr"], satz["wartung_woche"]),
                wochen_verschoben,
            )
        sitzung.merge(
            Maschine(
                kuerzel=satz["kuerzel"],
                bezeichnung=satz["bezeichnung"],
                verfuegbarkeit_prozent=Decimal(satz["verfuegbarkeit_prozent"]),
                wartung_jahr=wartung.jahr if wartung else None,
                wartung_woche=wartung.woche if wartung else None,
                bemerkung=satz["bemerkung"],
            )
        )

    for satz in _lies(quelle, "lieferanten.json"):
        sitzung.merge(
            Lieferant(
                liefnummer=satz["liefnummer"],
                name=satz["name"],
                ort=satz["ort"],
                lieferzeit_wochen=satz["lieferzeit_wochen"],
                bewertung=satz["bewertung"],
                erp_nummer=satz["erp_nummer"],
                bemerkung=satz["bemerkung"],
            )
        )

    for satz in _lies(quelle, "rohmaterial.json"):
        sitzung.merge(
            Rohmaterial(
                rohnummer=satz["rohnummer"],
                bezeichnung=satz["bezeichnung"],
                einheit=satz["einheit"],
                liefnummer=satz["liefnummer"],
                lager=Decimal(satz["lager"]),
                bestellt_offen=Decimal(satz["bestellt_offen"]),
                gebinde=Decimal(satz["gebinde"]),
                preis=Decimal(satz["preis"]),
                erp_nummer=satz["erp_nummer"],
                lagerort=satz["lagerort"],
            )
        )

    for satz in _lies(quelle, "artikel.json"):
        sitzung.merge(
            Artikel(
                artikelnummer=satz["artikelnummer"],
                bezeichnung=satz["bezeichnung"],
                material=satz["material"],
                standardmaschine=satz["standardmaschine"],
                minuten_je_stueck=Decimal(satz["minuten_je_stueck"]),
                ruestzeit_basis_min=satz["ruestzeit_basis_min"],
                zeichnung=satz["zeichnung"],
                aktiv=satz["aktiv"],
            )
        )
    sitzung.flush()

    vorhandene = {
        (position.artikelnummer, position.position)
        for position in sitzung.scalars(select(Stuecklistenposition)).all()
    }
    for satz in _lies(quelle, "stueckliste.json"):
        if (satz["artikelnummer"], satz["position"]) in vorhandene:
            continue
        sitzung.add(
            Stuecklistenposition(
                artikelnummer=satz["artikelnummer"],
                position=satz["position"],
                rohnummer=satz["rohnummer"],
                menge_je_stueck=Decimal(satz["menge_je_stueck"]),
                verschnitt_prozent=Decimal(satz["verschnitt_prozent"]),
                bemerkung=satz["bemerkung"],
            )
        )

    for satz in _lies(quelle, "auftraege.json"):
        liefertermin = date.fromisoformat(satz["liefertermin"]) + timedelta(weeks=wochen_verschoben)
        manuell = None
        if satz["manuelle_kw"]:
            manuell = _woche_verschoben(Kalenderwoche(*satz["manuelle_kw"]), wochen_verschoben)
        auftrag = Auftrag(
            auftragsnummer=satz["auftragsnummer"],
            kunde=satz["kunde"],
            prioritaet=satz["prioritaet"],
            artikelnummer=satz["artikelnummer"],
            menge=satz["menge"],
            liefertermin=liefertermin,
            abweichende_maschine=satz["abweichende_maschine"],
            status=satz["status"],
            bemerkung=satz["bemerkung"],
        )
        auftrag.setze_manuelle_kw(manuell)
        sitzung.merge(auftrag)

    sitzung.commit()
