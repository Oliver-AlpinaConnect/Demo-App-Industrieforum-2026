"""Stammdaten: Material, Artikel, Stückliste. Regeln R-010 bis R-013."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.regeln.typen import aufgerundet

# Die im Excel gepflegten Materialbezeichnungen. Die Liste im Zellkommentar auf
# `Artikel!C1` nennt 1.4404 nicht, in den Stammdaten kommt es aber vor (R-010).
MATERIALIEN: tuple[str, ...] = (
    "Alu",
    "1.4301",
    "1.4404",
    "S235JR",
    "GG25",
    "Messing",
    "42CrMo4",
)


class UnbekanntesMaterial(ValueError):
    """Die Materialbezeichnung steht nicht in der Liste (R-010)."""


class UnbekannterArtikel(ValueError):
    """Die Artikelnummer gibt es nicht (R-011)."""


def material_ist_bekannt(material: str) -> bool:
    """R-010: Material-Schreibweise ist exakt.

    Satz: Die Materialbezeichnung eines Artikels ist genau eine aus der Liste
    Alu, 1.4301, 1.4404, S235JR, GG25, Messing, 42CrMo4; Abweichungen werden nicht
    still korrigiert.

    Beispiel: "Alu" ist bekannt, "ALU" und "Aluminium" nicht. Stünde "ALU" im Artikel,
    fiele der Rüstzuschlag aus R-003 still weg.
    """
    return material in MATERIALIEN


def pruefe_material(material: str) -> str:
    """R-010: Material prüfen und unverändert zurückgeben, sonst Fehler.

    Der Import meldet die Abweichung und korrigiert nicht (Hausregel).
    Beispiel: pruefe_material("Alu") -> "Alu"; pruefe_material("alu") -> Fehler.
    """
    if not material_ist_bekannt(material):
        erlaubt = " / ".join(MATERIALIEN)
        raise UnbekanntesMaterial(
            f"Material {material!r} steht nicht in der Liste. Erlaubt: {erlaubt}"
        )
    return material


@dataclass(frozen=True)
class Artikelstamm:
    """Die Werte, die ein Auftrag aus dem Artikel übernimmt (R-011)."""

    artikelnummer: str
    bezeichnung: str
    material: str
    standardmaschine: str
    minuten_je_stueck: Decimal
    ruestzeit_basis_min: int
    aktiv: bool = True


def auftragsstammdaten(artikelnummer: str, artikel: dict[str, Artikelstamm]) -> Artikelstamm:
    """R-011: Der Artikel bestimmt Bezeichnung, Material, Maschine und Zeiten.

    Satz: Bezeichnung, Material, Standardmaschine, Bearbeitungszeit je Stück und
    Rüstzeit-Basis eines Auftrags kommen über die Artikelnummer aus den Artikelstamm-
    daten; der Auftrag speichert diese Werte nicht selbst.

    Beispiel: Auftrag 26-0413 mit Artikel A-1009 ergibt "Gehäuse G12 GG25", GG25,
    Maschine M4, 18,0 min/Stk, 120 min Rüstzeit-Basis.

    Eine unbekannte Artikelnummer wird abgelehnt. Im Excel liefert nur die Bezeichnung
    ein "??", Material, Maschine und Zeiten liefern `#NV`, das über die Gesamtzeit in
    die Summen des Wochenplans wandert.
    """
    if artikelnummer not in artikel:
        raise UnbekannterArtikel(f"Artikel {artikelnummer!r} gibt es nicht")
    return artikel[artikelnummer]


def maschine_des_auftrags(stamm: Artikelstamm, abweichende_maschine: str | None) -> str:
    """R-011: Maschine eines Auftrags, Umplanung schlägt die Standardmaschine.

    Satz: Ein Auftrag läuft auf der Standardmaschine seines Artikels, ausser es ist eine
    abweichende Maschine eingetragen.

    Beispiel: Artikel A-1009 hat Standardmaschine M4; ist am Auftrag M2 eingetragen,
    läuft er auf M2. Ohne Eintrag M4.

    Der Kommentar auf `Artikel!D1` sieht die Umplanung vor ("Manuelle Umplanung nur in
    Aufträge!"), im Excel gibt es dafür kein Feld (Entscheidung zu F-7).
    """
    return abweichende_maschine or stamm.standardmaschine


def darf_beauftragt_werden(stamm: Artikelstamm) -> bool:
    """R-011: Ein inaktiver Artikel bekommt keine neuen Aufträge.

    Beispiel: A-0998 ("Welle Ø20x180 1.4301 (alt)") ist inaktiv, ein neuer Auftrag
    darauf wird abgelehnt. Bestehende Aufträge rechnen normal weiter.

    Im Excel ist `Artikel!H` reine Anzeige, keine Formel liest ihn
    (Entscheidung zu F-9).
    """
    return stamm.aktiv


def stueckliste_schluessel(artikelnummer: str, position: int) -> str:
    """R-012: Schlüssel einer Stücklistenzeile aus Artikel und Position.

    Satz: Eine Stücklistenzeile wird über den Schlüssel "ArtNr-Pos" gefunden.

    Beispiel: A-1019 Position 1 -> "A-1019-1", Position 2 -> "A-1019-2".

    Die Grenze von zwei Positionen je Artikel ist im Excel nur die Breite der Spalten
    S bis V im Auftragsblatt. Hier sind beliebig viele Positionen erlaubt
    (Entscheidung zu F-8).
    """
    if position < 1:
        raise ValueError("Position beginnt bei 1")
    return f"{artikelnummer}-{position}"


def rohmaterialbedarf(
    menge_stk: int, menge_je_stueck: Decimal, verschnitt_prozent: Decimal
) -> Decimal:
    """R-013: Rohmaterialbedarf je Auftragsposition.

    Satz: Auftragsmenge mal Menge je Stück aus der Stückliste mal (1 + Verschnitt %),
    aufgerundet auf eine Dezimale.

    Beispiel: Auftrag 26-0414, Menge 620, 0,0140 Stangen/Stk, 8 % Verschnitt:
    620 * 0,0140 * 1,08 = 9,3744 -> 9,4 Stangen.
    Zweites Beispiel: Auftrag 26-0419, Menge 30, 1,0000 Stk/Stk, 0 % -> 30,0.

    Aufgerundet wird auch bei Stückgut, deshalb Decimal mit einer Dezimale.
    """
    roh = (
        Decimal(menge_stk)
        * Decimal(menge_je_stueck)
        * (Decimal(1) + Decimal(verschnitt_prozent) / Decimal(100))
    )
    return aufgerundet(roh, 1)
