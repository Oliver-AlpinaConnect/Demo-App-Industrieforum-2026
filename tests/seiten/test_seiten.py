"""Die fünf Seiten und der Export antworten und zeigen die erwarteten Werte."""

from __future__ import annotations

import pytest

from app.regeln.parameter import aktuelle_kalenderwoche

SEITEN = ["/", "/auftraege", "/wochenplan", "/material", "/regeln", "/galerie"]


@pytest.mark.parametrize("pfad", SEITEN)
def test_seite_antwortet(klient, pfad):
    antwort = klient.get(pfad)
    assert antwort.status_code == 200
    assert "Produktionsplanung" in antwort.text


def test_uebersicht_zeigt_die_kennzahlen(klient):
    text = klient.get("/").text
    assert "Offene Aufträge" in text
    assert "ausserhalb Horizont" in text
    assert "Bestellwert diese Woche" in text
    # R-009: Farbe nie allein, das Wort steht dabei.
    assert "überfällig" in text


def test_auftraege_zeigt_alle_fuenfzig(klient):
    text = klient.get("/auftraege").text
    assert "26-0414" in text
    assert "50 von 50" in text


def test_auftraege_lassen_sich_filtern(klient):
    text = klient.get("/auftraege", params={"status": "in Arbeit"}).text
    assert "26-0404" in text
    assert "26-0414" not in text


def test_auftraege_suche_findet_den_artikel(klient):
    text = klient.get("/auftraege", params={"suche": "A-1019"}).text
    assert "26-0419" in text
    assert "26-0388" not in text


def test_wochenplan_zeigt_maschinen_und_ampelwort(klient):
    text = klient.get("/wochenplan").text
    for kuerzel in ["M1", "M2", "M3", "M4"]:
        assert kuerzel in text
    assert "über Grenze" in text
    assert "Verschiebevorschläge" in text


def test_material_zeigt_fehl_kw_und_bestellvorschlag(klient):
    text = klient.get("/material").text
    assert "RM-109" in text
    assert "Fehl-KW" in text
    assert "Bestell-KW" in text


def test_regeln_zeigt_katalog_und_text(klient):
    text = klient.get("/regeln").text
    assert "R-001" in text
    assert "R-040" in text
    assert "Regelkatalog Produktionsplanung" in text


def test_export_liefert_eine_csv(klient):
    antwort = klient.get("/material/export.csv")
    assert antwort.status_code == 200
    assert "PLAN_BESTELL_" in antwort.headers["content-disposition"]
    inhalt = antwort.content.decode("cp1252")
    assert inhalt.splitlines()[0] == (
        "ARTNR;LIEFNR;MENGE;EINHEIT;BEDARFSDATUM;KOSTENSTELLE;BEMERKUNG"
    )
    assert len(inhalt.strip().splitlines()) == 6


def test_auftrag_abschliessen_schreibt_ins_aenderungslog(klient):
    vorher = klient.get("/auftraege", params={"suche": "26-0414"}).text
    assert "offen" in vorher
    antwort = klient.post("/auftraege/26-0414/abschliessen", follow_redirects=False)
    assert antwort.status_code == 303
    nachher = klient.get("/auftraege", params={"suche": "26-0414"}).text
    assert "erledigt" in nachher


def test_manuelle_woche_setzen_und_loeschen(klient):
    ziel = str(aktuelle_kalenderwoche().plus(4))
    klient.post("/auftraege/26-0414/woche", data={"manuelle_kw": ziel}, follow_redirects=False)
    text = klient.get("/auftraege", params={"suche": "26-0414"}).text
    assert f"{ziel} (manuell)" in text
    klient.post("/auftraege/26-0414/woche", data={"manuelle_kw": ""}, follow_redirects=False)
    text = klient.get("/auftraege", params={"suche": "26-0414"}).text
    assert "(manuell)" not in text


def test_unbekannter_auftrag_gibt_404(klient):
    assert klient.post("/auftraege/26-9999/abschliessen").status_code == 404


def test_falsches_wochenformat_wird_abgelehnt(klient):
    antwort = klient.post("/auftraege/26-0414/woche", data={"manuelle_kw": "43"})
    assert antwort.status_code == 400
