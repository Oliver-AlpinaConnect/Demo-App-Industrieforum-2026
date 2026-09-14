"""Seite Material. Bedarf, Bestand, Bestellvorschlag und der Export (R-022 bis R-036)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.config import einstellungen
from app.dienste.planung import Planungsstand, stand_laden
from app.regeln.export import (
    Exportposition,
    csv_bytes,
    exportdateiname,
    exportstempel,
    exportzeilen,
)
from app.routen.gemeinsam import Datenbank, jetzt, protokolliere, seite

router = APIRouter(prefix="/material")


def _positionen(stand: Planungsstand) -> list[Exportposition]:
    """R-033: nur die Zeilen mit Bestellen = ja gehen in den Export."""
    return [
        Exportposition(
            rohnummer=zeile.rohnummer,
            erp_artikelnummer=zeile.erp_nummer,
            erp_lieferantennummer=zeile.erp_nummer_lieferant,
            bestellmenge=zeile.bestellmenge,
            einheit=zeile.einheit,
            bedarfsdatum=zeile.bedarfsdatum,
            bestell_kw=zeile.bestell_kw,
        )
        for zeile in stand.bestellvorschlaege
    ]


@router.get("")
def material(request: Request, db: Datenbank):
    """Bedarf je Rohmaterial und Woche, Bestand und Bestellvorschlag."""
    stand = stand_laden(db)
    ergebnis = exportzeilen(
        _positionen(stand),
        stand.aktuelle_kw,
        stand.parameter.ganzzahl("kostenstelle_einkauf"),
    )
    return seite(
        request,
        "seiten/material.html",
        "/material",
        stand=stand,
        exportmeldungen=ergebnis.meldungen,
        exportzeilen_anzahl=len(ergebnis.zeilen),
        dateiname=exportdateiname(jetzt().date(), stand.aktuelle_kw),
    )


@router.get("/export.csv")
def export(db: Datenbank):
    """R-033 bis R-036: die Bestellvorschläge als CSV für Abacus."""
    stand = stand_laden(db)
    ergebnis = exportzeilen(
        _positionen(stand),
        stand.aktuelle_kw,
        stand.parameter.ganzzahl("kostenstelle_einkauf"),
    )
    stempel = exportstempel(jetzt(), einstellungen().benutzer)
    name = exportdateiname(stempel.zeitpunkt.date(), stand.aktuelle_kw)
    protokolliere(
        db,
        "export",
        name,
        "zeilen",
        "",
        f"{len(ergebnis.zeilen)} Positionen, Meldungen: {len(ergebnis.meldungen)}",
    )
    db.commit()
    return Response(
        content=csv_bytes(ergebnis.zeilen),
        media_type="text/csv; charset=windows-1252",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )
