"""Seite Wochenplan. Belastung, Kapazität, Auslastung und die Verschiebevorschläge."""

from __future__ import annotations

from collections import OrderedDict

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.dienste.planung import stand_laden
from app.modelle import Auftrag
from app.regeln.kapazitaet import Verschiebung
from app.routen.gemeinsam import Datenbank, protokolliere, seite

router = APIRouter(prefix="/wochenplan")


def netto_verschiebungen(schritte: list[Verschiebung]) -> list[Verschiebung]:
    """Fasst mehrere Schritte desselben Auftrags zu einer Verschiebung zusammen.

    R-021 geht die Wochen aufsteigend durch, deshalb kann ein Auftrag in einem Lauf
    mehrmals weiterrücken. Für die Anzeige zählt, wo er am Schluss liegt.
    """
    gebuendelt: OrderedDict[str, Verschiebung] = OrderedDict()
    for schritt in schritte:
        vorher = gebuendelt.get(schritt.auftragsnummer)
        gebuendelt[schritt.auftragsnummer] = (
            schritt
            if vorher is None
            else Verschiebung(
                auftragsnummer=schritt.auftragsnummer,
                maschine=schritt.maschine,
                von_kw=vorher.von_kw,
                nach_kw=schritt.nach_kw,
                grund=schritt.grund,
            )
        )
    return list(gebuendelt.values())


@router.get("")
def plan(request: Request, db: Datenbank):
    """R-014 bis R-021: der Wochenplan über den Horizont."""
    stand = stand_laden(db)
    vorschlaege = netto_verschiebungen(stand.verschiebungen)
    return seite(
        request,
        "seiten/wochenplan.html",
        "/wochenplan",
        stand=stand,
        vorschlaege=vorschlaege,
        auftraege_nach_woche={
            (maschine.kuerzel, kw): [
                zeile
                for zeile in stand.auftraege
                if zeile.maschine == maschine.kuerzel
                and zeile.kw_effektiv == kw
                and zeile.status.value != "erledigt"
            ]
            for maschine in stand.maschinen
            for kw in stand.horizont
        },
    )


@router.post("/uebernehmen")
def uebernehmen(request: Request, db: Datenbank):
    """R-021: die Vorschläge als manuelle Woche übernehmen.

    Die App verschiebt nie von selbst. Sie rechnet den Vorschlag und ein Mensch
    übernimmt ihn; damit entfällt das Rücksetzen über den Bemerkungstext aus dem Makro.
    """
    stand = stand_laden(db)
    for schritt in netto_verschiebungen(stand.verschiebungen):
        auftrag = db.get(Auftrag, schritt.auftragsnummer)
        if auftrag is None:
            continue
        alt = str(auftrag.manuelle_kw) if auftrag.manuelle_kw else ""
        protokolliere(
            db,
            "auftrag",
            auftrag.auftragsnummer,
            "manuelle_kw",
            alt,
            str(schritt.nach_kw),
        )
        auftrag.setze_manuelle_kw(schritt.nach_kw)
        vorher = auftrag.bemerkung
        vermerk = f"verschoben {schritt.von_kw} -> {schritt.nach_kw} (Vorschlag Wochenplan)"
        auftrag.bemerkung = f"{vorher}; {vermerk}" if vorher else vermerk
        protokolliere(db, "auftrag", auftrag.auftragsnummer, "bemerkung", vorher, auftrag.bemerkung)
    db.commit()
    return RedirectResponse("/wochenplan", status_code=303)
