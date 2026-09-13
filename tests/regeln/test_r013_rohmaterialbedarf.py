"""R-013: Rohmaterialbedarf je Auftragsposition."""

from decimal import Decimal

from app.regeln.stammdaten import rohmaterialbedarf


def test_r013_menge_mal_stueckliste_mal_verschnitt(auftrag):
    # 26-0414: 620 Stk, 0,0140 Stangen/Stk, 8 % Verschnitt = 9,3744 -> 9,4.
    zeile = auftrag("26-0414")
    assert zeile.positionen[0].rohnummer == "RM-106"
    assert zeile.positionen[0].bedarf == Decimal("9.4")


def test_r013_wird_immer_aufgerundet():
    assert rohmaterialbedarf(620, Decimal("0.0140"), Decimal(8)) == Decimal("9.4")
    # 9,3001 rundet auf 9,4, nicht auf 9,3.
    assert rohmaterialbedarf(1, Decimal("9.3001"), Decimal(0)) == Decimal("9.4")


def test_r013_ohne_verschnitt_bei_guss(auftrag):
    # 26-0419: 30 Stk, beide Positionen 1,0000 Stk/Stk, 0 % Verschnitt.
    zeile = auftrag("26-0419")
    assert [position.bedarf for position in zeile.positionen] == [
        Decimal("30.0"),
        Decimal("30.0"),
    ]


def test_r013_auch_stueckgut_bekommt_eine_dezimale(auftrag):
    # 26-0405 braucht 240,0 Stück RM-110.
    zeile = auftrag("26-0405")
    assert zeile.positionen[0].bedarf == Decimal("240.0")
    assert str(zeile.positionen[0].bedarf) == "240.0"


def test_r013_zweites_beispiel_aus_dem_katalog(auftrag):
    # 26-0430: 550 Stk mal 0,0140 mal 1,08 = 8,316 -> 8,4.
    zeile = auftrag("26-0430")
    assert zeile.positionen[0].bedarf == Decimal("8.4")
