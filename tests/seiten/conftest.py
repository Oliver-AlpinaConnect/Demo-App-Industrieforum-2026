"""Vorrichtungen für die Seitentests: eine App auf einer eigenen Datenbank."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.datenbank import sitzung
from app.main import app
from app.modelle import Basis
from app.regeln.parameter import aktuelle_kalenderwoche
from app.startdaten import lade_startdaten, verschiebung_auf


@pytest.fixture
def klient() -> Iterator[TestClient]:
    maschine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Basis.metadata.create_all(maschine)
    fabrik = sessionmaker(bind=maschine, expire_on_commit=False)
    # Wie beim Start der App: die Demodaten auf die heutige Woche schieben, damit die
    # Seiten immer einen vollen Horizont zeigen (siehe app/startdaten.py).
    with fabrik() as vorbereitung:
        lade_startdaten(vorbereitung, wochen_verschoben=verschiebung_auf(aktuelle_kalenderwoche()))

    def eigene_sitzung():
        with fabrik() as offen:
            yield offen

    app.dependency_overrides[sitzung] = eigene_sitzung
    with TestClient(app) as klient:
        yield klient
    app.dependency_overrides.clear()
