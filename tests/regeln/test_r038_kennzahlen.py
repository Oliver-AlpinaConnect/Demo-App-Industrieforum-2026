"""R-038: Kennzahlen der Übersicht."""

from decimal import Decimal

from app.regeln.bedienung import kennzahlen
from app.regeln.typen import Kalenderwoche, Status


def test_r038_alle_sieben_kennzahlen(stand):
    zahlen = stand.kennzahlen
    assert zahlen.offene_auftraege == 47
    assert zahlen.davon_in_arbeit == 2
    assert zahlen.davon_ueberfaellig == 1
    assert zahlen.auftraege_aktuelle_kw == 7
    assert zahlen.ausserhalb_horizont == 2
    assert zahlen.bestellpositionen == 5
    assert zahlen.bestellpositionen_ueberfaellig == 2
    assert zahlen.bestellwert > Decimal(0)


def test_r038_offene_auftraege_sind_offen_plus_in_arbeit(stand):
    laufend = [zeile for zeile in stand.auftraege if zeile.status is not Status.ERLEDIGT]
    assert stand.kennzahlen.offene_auftraege == len(laufend)
    assert len(stand.auftraege) == 50


def test_r038_alle_zaehlungen_nutzen_dieselbe_liste(stand):
    # Im Excel zählt C6 ohne die Bedingung "AufNr nicht leer", der Rest mit.
    in_arbeit = [zeile for zeile in stand.auftraege if zeile.status is Status.IN_ARBEIT]
    assert stand.kennzahlen.davon_in_arbeit == len(in_arbeit)


def test_r038_auftraege_der_aktuellen_kw_zaehlen_nach_kw_eff(stand):
    aktuell = Kalenderwoche(2026, 39)
    gezaehlt = [
        zeile
        for zeile in stand.auftraege
        if zeile.kw_effektiv == aktuell and zeile.status is not Status.ERLEDIGT
    ]
    assert stand.kennzahlen.auftraege_aktuelle_kw == len(gezaehlt) == 7


def test_r038_ohne_daten_sind_alle_kennzahlen_null():
    leer = kennzahlen([], [Kalenderwoche(2026, 39)], Kalenderwoche(2026, 39), [])
    assert leer.offene_auftraege == 0
    assert leer.bestellwert == Decimal("0.00")
