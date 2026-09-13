"""R-037: Auftrag abschliessen."""

from datetime import date

import pytest

from app.regeln.bedienung import auftrag_abschliessen
from app.regeln.typen import Status

TAG = date(2026, 9, 13)


def test_r037_status_wird_erledigt_und_die_bemerkung_ergaenzt():
    status, bemerkung = auftrag_abschliessen(Status.OFFEN, "Nachtrag zu 26-0416", TAG)
    assert status is Status.ERLEDIGT
    assert bemerkung == "Nachtrag zu 26-0416; erledigt 13.09."


def test_r037_ohne_bemerkung_steht_nur_der_vermerk():
    _, bemerkung = auftrag_abschliessen(Status.IN_ARBEIT, "", TAG)
    assert bemerkung == "erledigt 13.09."


def test_r037_ein_erledigter_auftrag_wird_nicht_zweimal_abgeschlossen():
    with pytest.raises(ValueError):
        auftrag_abschliessen(Status.ERLEDIGT, "erledigt 01.09.", TAG)


def test_r037_die_alte_bemerkung_bleibt_stehen():
    _, bemerkung = auftrag_abschliessen(Status.OFFEN, "ausgeliefert 17.09.", TAG)
    assert bemerkung.startswith("ausgeliefert 17.09.; ")
