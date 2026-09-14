"""R-003: Rüstzeit mit Zuschlag für Alu über der Losgrenze."""

from app.regeln.zeiten import ruestzeit_minuten

BASIS_A1005 = 50
LOSGRENZE = 500
ZUSCHLAG = 40


def test_r003_alu_ueber_losgrenze_bekommt_zuschlag(auftrag):
    # Auftrag 26-0414, Artikel A-1005 (Alu), Menge 620: 50 + 40 = 90 min.
    zeile = auftrag("26-0414")
    assert zeile.material == "Alu"
    assert zeile.menge == 620
    assert zeile.ruestzeit_min == 90


def test_r003_alu_unter_losgrenze_ohne_zuschlag(auftrag):
    # Gegenprobe 26-0395, gleicher Artikel, Menge 120.
    zeile = auftrag("26-0395")
    assert zeile.ruestzeit_min == 50


def test_r003_grenze_ist_echt_groesser_als():
    assert ruestzeit_minuten(BASIS_A1005, "Alu", 500, LOSGRENZE, ZUSCHLAG) == 50
    assert ruestzeit_minuten(BASIS_A1005, "Alu", 501, LOSGRENZE, ZUSCHLAG) == 90


def test_r003_anderes_material_bekommt_nie_zuschlag():
    assert ruestzeit_minuten(120, "GG25", 5000, LOSGRENZE, ZUSCHLAG) == 120
    # Schreibweise ist exakt (R-010): "ALU" greift nicht.
    assert ruestzeit_minuten(50, "ALU", 620, LOSGRENZE, ZUSCHLAG) == 50


def test_r003_zuschlag_haengt_an_den_parametern():
    # Im Excel steht die 40 an 29 von 50 Stellen fest in der Formel. Hier nicht.
    assert ruestzeit_minuten(50, "Alu", 620, 400, 25) == 75


def test_r003_der_fall_aus_dem_katalog_rechnet_jetzt_richtig(auftrag):
    # 26-0430 (A-1005, 550 Stk) rechnete im Excel 50 min, weil der Zuschlagsteil
    # in Zeile 34 fehlte. Nach der Regel sind es 90 min (offene Frage F-1).
    zeile = auftrag("26-0430")
    assert zeile.menge == 550
    assert zeile.ruestzeit_min == 90
