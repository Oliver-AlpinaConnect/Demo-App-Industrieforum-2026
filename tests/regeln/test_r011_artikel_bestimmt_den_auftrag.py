"""R-011: Der Artikel bestimmt Bezeichnung, Material, Maschine und Zeiten."""

from decimal import Decimal

import pytest

from app.regeln.stammdaten import (
    Artikelstamm,
    UnbekannterArtikel,
    auftragsstammdaten,
    darf_beauftragt_werden,
    maschine_des_auftrags,
)

A_1009 = Artikelstamm(
    artikelnummer="A-1009",
    bezeichnung="Gehäuse G12 GG25",
    material="GG25",
    standardmaschine="M4",
    minuten_je_stueck=Decimal("18.0"),
    ruestzeit_basis_min=120,
)


def test_r011_auftrag_uebernimmt_die_werte_des_artikels(auftrag):
    # 26-0413 hat Artikel A-1009.
    zeile = auftrag("26-0413")
    assert zeile.artikelnummer == "A-1009"
    assert zeile.bezeichnung == "Gehäuse G12 GG25"
    assert zeile.material == "GG25"
    assert zeile.maschine == "M4"
    assert zeile.ruestzeit_min == 120


def test_r011_unbekannte_artikelnummer_wird_abgelehnt():
    # Im Excel entsteht eine halbe Zeile mit "??" und #NV, die in die Summen wandert.
    with pytest.raises(UnbekannterArtikel):
        auftragsstammdaten("A-9999", {"A-1009": A_1009})


def test_r011_standardmaschine_gilt_ohne_umplanung():
    assert maschine_des_auftrags(A_1009, None) == "M4"


def test_r011_umplanung_schlaegt_die_standardmaschine():
    # Der Kommentar auf Artikel!D1 sieht das vor, im Excel gibt es dafür kein Feld (F-7).
    assert maschine_des_auftrags(A_1009, "M2") == "M2"


def test_r011_inaktiver_artikel_bekommt_keinen_neuen_auftrag():
    # A-0998 ist der einzige Artikel mit Aktiv = N (F-9).
    alt = Artikelstamm(
        artikelnummer="A-0998",
        bezeichnung="Welle Ø20x180 1.4301 (alt)",
        material="1.4301",
        standardmaschine="M1",
        minuten_je_stueck=Decimal("5.0"),
        ruestzeit_basis_min=30,
        aktiv=False,
    )
    assert not darf_beauftragt_werden(alt)
    assert darf_beauftragt_werden(A_1009)


def test_r011_kein_auftrag_der_testdaten_nutzt_den_inaktiven_artikel(stand):
    assert all(zeile.artikelnummer != "A-0998" for zeile in stand.auftraege)
