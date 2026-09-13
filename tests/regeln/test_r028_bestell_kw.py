"""R-028: Bestell-KW."""

from app.regeln.material import bestell_kw
from app.regeln.typen import Bewertung, Kalenderwoche

PUFFER = 1


def test_r028_fehl_kw_minus_lieferzeit():
    # RM-101: Fehl-KW 42, Lieferzeit 2, Bewertung A -> 40.
    assert bestell_kw(Kalenderwoche(2026, 42), 2, Bewertung.A, PUFFER) == Kalenderwoche(2026, 40)


def test_r028_lieferant_c_bekommt_eine_woche_puffer():
    # RM-109: Fehl-KW 44, Lieferzeit 5, Bewertung C -> 44 - 5 - 1 = 38.
    assert bestell_kw(Kalenderwoche(2026, 44), 5, Bewertung.C, PUFFER) == Kalenderwoche(2026, 38)


def test_r028_bewertung_b_bekommt_keinen_puffer():
    assert bestell_kw(Kalenderwoche(2026, 44), 5, Bewertung.B, PUFFER) == Kalenderwoche(2026, 39)


def test_r028_ohne_fehl_kw_keine_bestell_kw():
    assert bestell_kw(None, 5, Bewertung.C, PUFFER) is None


def test_r028_bestell_kw_darf_in_der_vergangenheit_liegen(rohmaterial):
    # RM-106 hat Bestell-KW 37, das wird nicht auf die aktuelle Woche begrenzt.
    assert rohmaterial("RM-106").bestell_kw == Kalenderwoche(2026, 37)
    assert rohmaterial("RM-109").bestell_kw == Kalenderwoche(2026, 38)


def test_r028_bestell_kw_der_testdaten(rohmaterial):
    erwartet = {
        "RM-106": 37,
        "RM-107": 39,
        "RM-109": 38,
        "RM-110": 39,
        "RM-115": 39,
    }
    for nummer, woche in erwartet.items():
        assert rohmaterial(nummer).bestell_kw == Kalenderwoche(2026, woche)


def test_r028_nur_lieferant_l04_ist_kritisch(stand):
    kritisch = {zeile.liefnummer for zeile in stand.material if zeile.bewertung is Bewertung.C}
    assert kritisch == {"L-04"}
    betroffen = sorted(
        zeile.rohnummer for zeile in stand.material if zeile.bewertung is Bewertung.C
    )
    assert betroffen == ["RM-109", "RM-110"]


def test_r028_ueber_den_jahreswechsel():
    # Fehl-KW 2027-KW02, Lieferzeit 5, Bewertung C: fünf plus eine Woche zurück.
    assert bestell_kw(Kalenderwoche(2027, 2), 5, Bewertung.C, PUFFER) == Kalenderwoche(2026, 49)
