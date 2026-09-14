"""FastAPI-App. Router einbinden, sonst nichts."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import einstellungen
from app.datenbank import Sitzung, tabellen_anlegen
from app.regeln.parameter import aktuelle_kalenderwoche
from app.routen import auftraege, galerie, material, regeln, uebersicht, wochenplan
from app.startdaten import ist_leer, lade_startdaten, verschiebung_auf


@asynccontextmanager
async def lebenszyklus(app: FastAPI):
    """Tabellen anlegen und beim ersten Start die Demodaten laden."""
    tabellen_anlegen()
    if einstellungen().startdaten_laden:
        with Sitzung() as sitzung:
            if ist_leer(sitzung):
                lade_startdaten(
                    sitzung, wochen_verschoben=verschiebung_auf(aktuelle_kalenderwoche())
                )
    yield


app = FastAPI(title="Produktionsplanung", lifespan=lebenszyklus)
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent / "static")),
    name="static",
)
app.include_router(uebersicht.router)
app.include_router(auftraege.router)
app.include_router(wochenplan.router)
app.include_router(material.router)
app.include_router(regeln.router)
app.include_router(galerie.router)
