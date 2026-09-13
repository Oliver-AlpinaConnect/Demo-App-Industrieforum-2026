"""R-012: Schlüssel einer Stücklistenzeile, beliebig viele Positionen."""

import pytest

from app.regeln.stammdaten import stueckliste_schluessel


def test_r012_schluessel_aus_artikel_und_position():
    assert stueckliste_schluessel("A-1019", 1) == "A-1019-1"
    assert stueckliste_schluessel("A-1019", 2) == "A-1019-2"


def test_r012_position_beginnt_bei_eins():
    with pytest.raises(ValueError):
        stueckliste_schluessel("A-1019", 0)


def test_r012_ein_artikel_mit_zwei_positionen(auftrag):
    # A-1019 (Lagerbock GG25 kompl.) ist der einzige Artikel mit zwei Positionen.
    zeile = auftrag("26-0419")
    assert [position.rohnummer for position in zeile.positionen] == ["RM-109", "RM-110"]


def test_r012_genau_zwei_auftraege_haben_eine_zweite_position(stand):
    mit_zwei = [zeile.auftragsnummer for zeile in stand.auftraege if len(zeile.positionen) > 1]
    assert mit_zwei == ["26-0419", "26-0439"]


def test_r012_mehr_als_zwei_positionen_sind_moeglich():
    # Die Grenze im Excel kommt nur von der Breite der Spalten S bis V (F-8).
    assert stueckliste_schluessel("A-1019", 3) == "A-1019-3"
