"""Konfiguration. Die einzige Stelle, die Umgebungsvariablen liest (Hausregel)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

WURZEL = Path(__file__).resolve().parent.parent


class Einstellungen(BaseSettings):
    """Alle Umgebungsvariablen der App. Beschreibung in `docs/betrieb.md`."""

    model_config = SettingsConfigDict(env_prefix="PP_", env_file=".env", extra="ignore")

    # Datenbank. SQLite im Betrieb, PostgreSQL später mit denselben Modellen.
    datenbank_url: str = f"sqlite:///{WURZEL / 'data' / 'app.db'}"

    # Ablage der Exportdateien (R-036). Im Excel stand der Pfad in den Fachdaten
    # (`Parameter!B13`) und war an drei Stellen verschieden beschrieben (F-6).
    export_pfad: Path = WURZEL / "export"

    # Platzhalter, bis `app/auth/` steht. Schreibt den Namen ins `aenderungslog`.
    benutzer: str = "demo"

    # Zeitzone für Datum und Kalenderwoche (R-002).
    zeitzone: str = "Europe/Zurich"

    # Startdaten beim ersten Start laden, wenn die Datenbank leer ist.
    startdaten_laden: bool = True


@lru_cache
def einstellungen() -> Einstellungen:
    return Einstellungen()
