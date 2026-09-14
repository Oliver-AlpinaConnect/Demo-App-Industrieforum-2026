"""Seite Aufträge. Liste, Filter und die beiden Änderungen aus R-037 und R-007."""

from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.dienste.planung import stand_laden
from app.modelle import Auftrag
from app.regeln.bedienung import auftrag_abschliessen
from app.regeln.termine import status_aus_text
from app.regeln.typen import Kalenderwoche, Status
from app.routen.gemeinsam import Datenbank, jetzt, protokolliere, seite

router = APIRouter(prefix="/auftraege")


@router.get("")
def liste(
    request: Request,
    db: Datenbank,
    status: str = "",
    maschine: str = "",
    woche: str = "",
    suche: str = "",
):
    """Alle Aufträge mit den gerechneten Werten, gefiltert."""
    stand = stand_laden(db)
    zeilen = stand.auftraege
    if status:
        zeilen = [zeile for zeile in zeilen if zeile.status.value == status]
    if maschine:
        zeilen = [zeile for zeile in zeilen if zeile.maschine == maschine]
    if woche:
        zeilen = [zeile for zeile in zeilen if str(zeile.kw_effektiv) == woche]
    if suche:
        begriff = suche.strip().lower()
        zeilen = [
            zeile
            for zeile in zeilen
            if begriff in zeile.auftragsnummer.lower()
            or begriff in zeile.artikelnummer.lower()
            or begriff in zeile.bezeichnung.lower()
            or begriff in zeile.kunde.lower()
        ]
    return seite(
        request,
        "seiten/auftraege.html",
        "/auftraege",
        stand=stand,
        zeilen=sorted(zeilen, key=lambda zeile: (zeile.kw_effektiv, zeile.auftragsnummer)),
        filter={"status": status, "maschine": maschine, "woche": woche, "suche": suche},
        statuswerte=[("", "alle")] + [(wert.value, wert.value) for wert in Status],
        maschinenwerte=[("", "alle")]
        + [(eintrag.kuerzel, eintrag.kuerzel) for eintrag in stand.maschinen],
        wochenwerte=[("", "alle")] + [(str(kw), str(kw)) for kw in stand.horizont],
    )


@router.post("/{auftragsnummer}/abschliessen")
def abschliessen(auftragsnummer: str, request: Request, db: Datenbank):
    """R-037: Auftrag auf `erledigt` setzen und die Bemerkung ergänzen."""
    auftrag = db.get(Auftrag, auftragsnummer)
    if auftrag is None:
        raise HTTPException(status_code=404, detail="Auftrag gibt es nicht")
    alt_status = status_aus_text(auftrag.status)
    if alt_status is Status.ERLEDIGT:
        raise HTTPException(status_code=400, detail="Auftrag ist bereits erledigt")

    neuer_status, neue_bemerkung = auftrag_abschliessen(
        alt_status, auftrag.bemerkung, jetzt().date()
    )
    protokolliere(db, "auftrag", auftragsnummer, "status", alt_status.value, neuer_status.value)
    protokolliere(db, "auftrag", auftragsnummer, "bemerkung", auftrag.bemerkung, neue_bemerkung)
    auftrag.status = neuer_status.value
    auftrag.bemerkung = neue_bemerkung
    db.commit()
    return RedirectResponse(request.headers.get("referer", "/auftraege"), status_code=303)


@router.post("/{auftragsnummer}/woche")
def woche_setzen(
    auftragsnummer: str,
    request: Request,
    db: Datenbank,
    manuelle_kw: str = Form(default=""),
):
    """R-007: manuelle Woche setzen oder löschen. Leer heisst, die Plan-KW gilt wieder."""
    auftrag = db.get(Auftrag, auftragsnummer)
    if auftrag is None:
        raise HTTPException(status_code=404, detail="Auftrag gibt es nicht")

    neue_kw = None
    if manuelle_kw.strip():
        try:
            jahr, woche = manuelle_kw.split("-KW")
            neue_kw = Kalenderwoche(int(jahr), int(woche))
        except (ValueError, TypeError) as fehler:
            raise HTTPException(
                status_code=400, detail="Woche im Format 2026-KW39 angeben"
            ) from fehler

    alt = str(auftrag.manuelle_kw) if auftrag.manuelle_kw else ""
    protokolliere(
        db, "auftrag", auftragsnummer, "manuelle_kw", alt, str(neue_kw) if neue_kw else ""
    )
    auftrag.setze_manuelle_kw(neue_kw)
    db.commit()
    return RedirectResponse(request.headers.get("referer", "/auftraege"), status_code=303)
