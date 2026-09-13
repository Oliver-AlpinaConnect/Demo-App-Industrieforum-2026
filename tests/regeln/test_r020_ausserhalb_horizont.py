"""R-020: Aufträge ausserhalb des Horizonts."""

from app.regeln.kapazitaet import ausserhalb_horizont
from app.regeln.typen import Kalenderwoche


def test_r020_zwei_auftraege_liegen_ausserhalb(stand):
    nummern = [zeile.auftragsnummer for zeile in stand.ausserhalb_horizont]
    assert nummern == ["26-0402", "26-0446"]
    assert stand.kennzahlen.ausserhalb_horizont == 2


def test_r020_die_app_benennt_sie_statt_nur_zu_zaehlen(stand):
    # Das Excel zeigt nur eine Zahl und sagt "von Hand prüfen".
    vorher, nachher = stand.ausserhalb_horizont
    assert vorher.kw_effektiv < stand.horizont[0]
    assert nachher.kw_effektiv > stand.horizont[-1]
    assert nachher.kw_effektiv == Kalenderwoche(2026, 47)


def test_r020_erledigte_auftraege_zaehlen_nicht_mit(stand):
    assert all(zeile.status.value != "erledigt" for zeile in stand.ausserhalb_horizont)


def test_r020_ihre_zeit_fehlt_im_wochenplan(stand):
    gesamt_im_plan = sum(
        zelle.belastung_h for maschine in stand.maschinen for zelle in maschine.zellen
    )
    ausserhalb = sum(zeile.gesamtzeit_h for zeile in stand.ausserhalb_horizont)
    assert ausserhalb > 0
    laufend = sum(
        zeile.gesamtzeit_h for zeile in stand.auftraege if zeile.status.value != "erledigt"
    )
    assert gesamt_im_plan == laufend - ausserhalb


def test_r020_leerer_horizont_gibt_alle_zurueck():
    assert ausserhalb_horizont([], []) == []
