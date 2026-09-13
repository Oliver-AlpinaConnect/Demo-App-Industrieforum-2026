"""Gemeinsame Vorrichtungen der Tests.

Die Testdaten stehen in `tests/daten/`. Bezugswoche ist 2026-KW39, die "aktuelle KW" aus
`docs/regeln.md`. Die Regelfunktionen bekommen die aktuelle Woche immer als Argument,
deshalb sind die Tests unabhängig vom heutigen Datum.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.dienste.planung import Auftragszeile, Materialzeile, Planungsstand, stand_laden
from app.modelle import Basis
from app.regeln.parameter import Parameter
from app.regeln.typen import Kalenderwoche
from app.startdaten import lade_startdaten

AKTUELLE_KW = Kalenderwoche(2026, 39)


@pytest.fixture(scope="session")
def sitzung() -> Iterator[Session]:
    """Eine Datenbank im Arbeitsspeicher mit den Demodaten."""
    maschine = create_engine("sqlite://")
    Basis.metadata.create_all(maschine)
    fabrik = sessionmaker(bind=maschine, expire_on_commit=False)
    with fabrik() as offen:
        lade_startdaten(offen)
        yield offen


@pytest.fixture(scope="session")
def stand(sitzung: Session) -> Planungsstand:
    """Der gerechnete Planungsstand zur Bezugswoche 2026-KW39."""
    return stand_laden(sitzung, AKTUELLE_KW)


@pytest.fixture(scope="session")
def parameter(stand: Planungsstand) -> Parameter:
    return stand.parameter


@pytest.fixture(scope="session")
def auftrag(stand: Planungsstand):
    """Einen Auftrag aus den Testdaten holen. Beispiel: auftrag("26-0414")."""

    def suche(nummer: str) -> Auftragszeile:
        for zeile in stand.auftraege:
            if zeile.auftragsnummer == nummer:
                return zeile
        raise AssertionError(f"Auftrag {nummer} steht nicht in den Testdaten")

    return suche


@pytest.fixture(scope="session")
def rohmaterial(stand: Planungsstand):
    """Ein Rohmaterial aus den Testdaten holen. Beispiel: rohmaterial("RM-109")."""

    def suche(nummer: str) -> Materialzeile:
        for zeile in stand.material:
            if zeile.rohnummer == nummer:
                return zeile
        raise AssertionError(f"Rohmaterial {nummer} steht nicht in den Testdaten")

    return suche
