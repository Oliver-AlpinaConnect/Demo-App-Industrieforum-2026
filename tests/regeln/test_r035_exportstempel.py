"""R-035: Exportstempel."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.regeln.export import exportstempel

ZUERICH = ZoneInfo("Europe/Zurich")


def test_r035_zeitpunkt_und_person_werden_festgehalten():
    zeitpunkt = datetime(2026, 9, 13, 15, 7, tzinfo=ZUERICH)
    stempel = exportstempel(zeitpunkt, "sandra.meier")
    assert stempel.zeitpunkt == zeitpunkt
    assert stempel.benutzer == "sandra.meier"


def test_r035_ohne_angemeldete_person_kein_export():
    with pytest.raises(ValueError):
        exportstempel(datetime(2026, 9, 13, 15, 7, tzinfo=ZUERICH), "")


def test_r035_zeitpunkt_braucht_eine_zeitzone():
    with pytest.raises(ValueError):
        exportstempel(datetime(2026, 9, 13, 15, 7), "sandra.meier")
