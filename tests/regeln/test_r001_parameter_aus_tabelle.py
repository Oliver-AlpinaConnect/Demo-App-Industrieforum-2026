"""R-001: Alle Stellschrauben stehen in der Tabelle `parameter`."""

from decimal import Decimal

import pytest

from app.regeln.parameter import PARAMETER_KATALOG, Parameter, ParameterFehlt
from app.regeln.typen import Prioritaet


def test_r001_alle_stellschrauben_sind_gepflegt(parameter: Parameter):
    assert parameter.fehlende == []
    assert set(parameter.werte) >= set(PARAMETER_KATALOG)


def test_r001_werte_aus_dem_katalog(parameter: Parameter):
    assert parameter.ganzzahl("ruestzuschlag_alu_min") == 40
    assert parameter.ganzzahl("losgrenze_alu_stk") == 500
    assert parameter.ganzzahl("planungshorizont_wochen") == 8
    assert parameter.zahl("wartungsabzug_h") == Decimal(16)
    assert parameter.ganzzahl("kostenstelle_einkauf") == 4100


def test_r001_prozentwerte_kommen_als_anteil(parameter: Parameter):
    assert parameter.anteil("auslastungsgrenze_prozent") == Decimal("0.9")
    assert parameter.anteil("sicherheitsbestand_prozent") == Decimal("0.1")


def test_r001_vorlauf_je_prioritaet(parameter: Parameter):
    assert parameter.vorlauf(Prioritaet.A) == 2
    assert parameter.vorlauf(Prioritaet.B) == 1
    assert parameter.vorlauf(Prioritaet.C) == 1


def test_r001_fehlender_parameter_faellt_auf():
    leer = Parameter(werte={})
    with pytest.raises(ParameterFehlt):
        leer.zahl("losgrenze_alu_stk")
