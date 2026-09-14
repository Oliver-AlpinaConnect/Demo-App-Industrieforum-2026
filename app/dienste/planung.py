"""Der Planungsstand: alles, was die Seiten anzeigen, in einem Rechengang."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modelle import (
    Artikel,
    Auftrag,
    Lieferant,
    Maschine,
    Parametersatz,
    Rohmaterial,
)
from app.regeln import kapazitaet as regel_kapazitaet
from app.regeln import material as regel_material
from app.regeln import stammdaten as regel_stammdaten
from app.regeln import termine as regel_termine
from app.regeln import zeiten as regel_zeiten
from app.regeln.bedienung import Kennzahlen, kennzahlen
from app.regeln.parameter import Parameter, aktuelle_kalenderwoche
from app.regeln.typen import (
    Ampel,
    Bewertung,
    Kalenderwoche,
    Prioritaet,
    Status,
)
from app.regeln.typen import (
    menge as runde_menge,
)


@dataclass(frozen=True)
class Auftragszeile:
    """Ein Auftrag mit allen gerechneten Werten (R-003 bis R-011)."""

    auftragsnummer: str
    kunde: str
    prioritaet: Prioritaet
    artikelnummer: str
    bezeichnung: str
    material: str
    maschine: str
    standardmaschine: str
    menge: int
    liefertermin: date
    liefer_kw: Kalenderwoche
    plan_kw: Kalenderwoche
    manuelle_kw: Kalenderwoche | None
    kw_effektiv: Kalenderwoche
    ruestzeit_min: int
    bearbeitungszeit_h: Decimal
    gesamtzeit_h: Decimal
    status: Status
    bemerkung: str
    ueberfaellig: bool
    im_horizont: bool
    positionen: list[Positionszeile] = field(default_factory=list)

    @property
    def umgeplant(self) -> bool:
        return self.maschine != self.standardmaschine


@dataclass(frozen=True)
class Positionszeile:
    """Eine Auftragsposition mit ihrem Rohmaterialbedarf (R-013)."""

    position: int
    rohnummer: str
    bezeichnung: str
    einheit: str
    bedarf: Decimal


@dataclass(frozen=True)
class Wochenzelle:
    """Eine Zelle des Wochenplans (R-016 bis R-018)."""

    kw: Kalenderwoche
    belastung_h: Decimal
    kapazitaet_h: Decimal
    auslastung: Decimal
    ampel: Ampel
    wartung: bool


@dataclass(frozen=True)
class Maschinenzeile:
    """Eine Maschine mit ihren acht Wochen (R-014, R-015)."""

    kuerzel: str
    bezeichnung: str
    verfuegbarkeit_prozent: Decimal
    grundkapazitaet_h: Decimal
    wartungs_kw: Kalenderwoche | None
    zellen: list[Wochenzelle]

    def zelle(self, kw: Kalenderwoche) -> Wochenzelle | None:
        for eintrag in self.zellen:
            if eintrag.kw == kw:
                return eintrag
        return None


@dataclass(frozen=True)
class Materialzeile:
    """Ein Rohmaterial mit Bedarf, Bestand und Bestellvorschlag (R-022 bis R-032)."""

    rohnummer: str
    bezeichnung: str
    einheit: str
    liefnummer: str
    lieferant: str
    lieferzeit_wochen: int
    bewertung: Bewertung
    lager: Decimal
    bestellt_offen: Decimal
    verfuegbar: Decimal
    gebinde: Decimal
    preis: Decimal
    erp_nummer: str
    erp_nummer_lieferant: str
    bedarf_reihe: list[Decimal]
    kumuliert_reihe: list[Decimal]
    summe_horizont: Decimal
    durchschnitt: Decimal
    sicherheitsbestand: Decimal
    fehl_kw: Kalenderwoche | None
    bestell_kw: Kalenderwoche | None
    bestellen: bool
    ueberfaellig: bool
    bestellmenge: Decimal
    bestellwert: Decimal
    bedarfsdatum: date | None


@dataclass(frozen=True)
class Planungsstand:
    """Alles, was die Seiten brauchen, einmal gerechnet."""

    aktuelle_kw: Kalenderwoche
    parameter: Parameter
    horizont: list[Kalenderwoche]
    auftraege: list[Auftragszeile]
    maschinen: list[Maschinenzeile]
    material: list[Materialzeile]
    verschiebungen: list[regel_kapazitaet.Verschiebung]
    kennzahlen: Kennzahlen

    @property
    def ausserhalb_horizont(self) -> list[Auftragszeile]:
        return [
            zeile
            for zeile in self.auftraege
            if not zeile.im_horizont and regel_termine.ist_laufend(zeile.status)
        ]

    @property
    def ueberfaellige(self) -> list[Auftragszeile]:
        return [zeile for zeile in self.auftraege if zeile.ueberfaellig]

    @property
    def bestellvorschlaege(self) -> list[Materialzeile]:
        return [zeile for zeile in self.material if zeile.bestellen]


def parameter_laden(sitzung: Session) -> Parameter:
    """R-001: Alle Stellschrauben aus der Tabelle `parameter` lesen."""
    werte = {satz.name: Decimal(satz.wert) for satz in sitzung.scalars(select(Parametersatz)).all()}
    return Parameter(werte=werte)


def stand_laden(sitzung: Session, aktuelle_kw: Kalenderwoche | None = None) -> Planungsstand:
    """Lädt alles und rechnet den vollständigen Planungsstand.

    Reihenfolge: Parameter (R-001), aktuelle Woche (R-002), Horizont (R-019),
    Aufträge mit Zeiten und Terminen (R-003 bis R-013), Wochenplan (R-014 bis R-018),
    Material (R-022 bis R-032), Kennzahlen (R-038).
    """
    parameter = parameter_laden(sitzung)
    kw_jetzt = aktuelle_kw or aktuelle_kalenderwoche()
    horizont = regel_kapazitaet.horizont(kw_jetzt, parameter.ganzzahl("planungshorizont_wochen"))

    artikel = {
        satz.artikelnummer: satz
        for satz in sitzung.scalars(select(Artikel).options(selectinload(Artikel.positionen))).all()
    }
    rohmaterial = {satz.rohnummer: satz for satz in sitzung.scalars(select(Rohmaterial)).all()}
    lieferanten = {satz.liefnummer: satz for satz in sitzung.scalars(select(Lieferant)).all()}
    maschinen = sitzung.scalars(select(Maschine).order_by(Maschine.kuerzel)).all()
    auftraege_roh = sitzung.scalars(select(Auftrag).order_by(Auftrag.auftragsnummer)).all()

    zeilen = [
        _auftragszeile(auftrag, artikel, rohmaterial, parameter, kw_jetzt, horizont)
        for auftrag in auftraege_roh
    ]

    planauftraege = [
        regel_kapazitaet.Planauftrag(
            auftragsnummer=zeile.auftragsnummer,
            maschine=zeile.maschine,
            kw_effektiv=zeile.kw_effektiv,
            liefer_kw=zeile.liefer_kw,
            gesamtzeit_h=zeile.gesamtzeit_h,
            status=zeile.status,
            prioritaet=zeile.prioritaet,
        )
        for zeile in zeilen
    ]

    maschinenzeilen, kapazitaeten = _wochenplan(maschinen, planauftraege, horizont, parameter)

    positionen = [
        regel_material.Materialposition(
            auftragsnummer=zeile.auftragsnummer,
            rohnummer=position.rohnummer,
            kw_effektiv=zeile.kw_effektiv,
            bedarf=position.bedarf,
            status=zeile.status,
        )
        for zeile in zeilen
        for position in zeile.positionen
    ]

    materialzeilen = [
        _materialzeile(
            rohmaterial[rohnummer],
            lieferanten[rohmaterial[rohnummer].liefnummer],
            positionen,
            horizont,
            parameter,
            kw_jetzt,
        )
        for rohnummer in sorted(rohmaterial)
    ]

    vorschlaege = [
        regel_material.Bestellvorschlag(
            rohnummer=zeile.rohnummer,
            fehl_kw=zeile.fehl_kw,
            bestell_kw=zeile.bestell_kw,
            bestellen=zeile.bestellen,
            ueberfaellig=zeile.ueberfaellig,
            bestellmenge=zeile.bestellmenge,
            bestellwert=zeile.bestellwert,
        )
        for zeile in materialzeilen
    ]

    return Planungsstand(
        aktuelle_kw=kw_jetzt,
        parameter=parameter,
        horizont=horizont,
        auftraege=zeilen,
        maschinen=maschinenzeilen,
        material=materialzeilen,
        verschiebungen=regel_kapazitaet.verschiebungen(
            planauftraege,
            [maschine.kuerzel for maschine in maschinen],
            horizont,
            kapazitaeten,
            parameter.anteil("auslastungsgrenze_prozent"),
        ),
        kennzahlen=kennzahlen(planauftraege, horizont, kw_jetzt, vorschlaege),
    )


def _auftragszeile(
    auftrag: Auftrag,
    artikel: dict[str, Artikel],
    rohmaterial: dict[str, Rohmaterial],
    parameter: Parameter,
    aktuelle_kw: Kalenderwoche,
    horizont: list[Kalenderwoche],
) -> Auftragszeile:
    stamm = artikel[auftrag.artikelnummer]
    prioritaet = Prioritaet(auftrag.prioritaet)
    status = regel_termine.status_aus_text(auftrag.status)

    ruestzeit = regel_zeiten.ruestzeit_minuten(
        ruestzeit_basis_min=stamm.ruestzeit_basis_min,
        material=stamm.material,
        menge_stk=auftrag.menge,
        losgrenze_stk=parameter.ganzzahl("losgrenze_alu_stk"),
        ruestzuschlag_min=parameter.ganzzahl("ruestzuschlag_alu_min"),
    )
    liefer_kw = regel_termine.liefer_kw(auftrag.liefertermin)
    plan_kw = regel_termine.plan_kw(liefer_kw, prioritaet, parameter.vorlauf(prioritaet))
    kw_eff = regel_termine.kw_effektiv(plan_kw, auftrag.manuelle_kw)

    positionen = [
        Positionszeile(
            position=position.position,
            rohnummer=position.rohnummer,
            bezeichnung=rohmaterial[position.rohnummer].bezeichnung,
            einheit=rohmaterial[position.rohnummer].einheit,
            bedarf=regel_stammdaten.rohmaterialbedarf(
                auftrag.menge, position.menge_je_stueck, position.verschnitt_prozent
            ),
        )
        for position in sorted(stamm.positionen, key=lambda satz: satz.position)
    ]

    return Auftragszeile(
        auftragsnummer=auftrag.auftragsnummer,
        kunde=auftrag.kunde,
        prioritaet=prioritaet,
        artikelnummer=stamm.artikelnummer,
        bezeichnung=stamm.bezeichnung,
        material=stamm.material,
        maschine=regel_stammdaten.maschine_des_auftrags(
            regel_stammdaten.Artikelstamm(
                artikelnummer=stamm.artikelnummer,
                bezeichnung=stamm.bezeichnung,
                material=stamm.material,
                standardmaschine=stamm.standardmaschine,
                minuten_je_stueck=stamm.minuten_je_stueck,
                ruestzeit_basis_min=stamm.ruestzeit_basis_min,
                aktiv=stamm.aktiv,
            ),
            auftrag.abweichende_maschine,
        ),
        standardmaschine=stamm.standardmaschine,
        menge=auftrag.menge,
        liefertermin=auftrag.liefertermin,
        liefer_kw=liefer_kw,
        plan_kw=plan_kw,
        manuelle_kw=auftrag.manuelle_kw,
        kw_effektiv=kw_eff,
        ruestzeit_min=ruestzeit,
        bearbeitungszeit_h=regel_zeiten.bearbeitungszeit_stunden(
            auftrag.menge, stamm.minuten_je_stueck
        ),
        gesamtzeit_h=regel_zeiten.gesamtzeit_stunden(
            auftrag.menge, stamm.minuten_je_stueck, ruestzeit
        ),
        status=status,
        bemerkung=auftrag.bemerkung,
        ueberfaellig=regel_termine.ist_ueberfaellig(status, liefer_kw, aktuelle_kw),
        im_horizont=kw_eff in set(horizont),
        positionen=positionen,
    )


def _wochenplan(
    maschinen: list[Maschine],
    planauftraege: list[regel_kapazitaet.Planauftrag],
    horizont: list[Kalenderwoche],
    parameter: Parameter,
) -> tuple[list[Maschinenzeile], dict[tuple[str, Kalenderwoche], Decimal]]:
    grenze = parameter.anteil("auslastungsgrenze_prozent")
    kapazitaeten: dict[tuple[str, Kalenderwoche], Decimal] = {}
    zeilen: list[Maschinenzeile] = []

    for maschine in maschinen:
        grund = regel_kapazitaet.wochenkapazitaet_stunden(
            schichten_pro_tag=parameter.ganzzahl("schichten_pro_tag"),
            stunden_pro_schicht=parameter.zahl("stunden_pro_schicht"),
            arbeitstage_pro_woche=parameter.ganzzahl("arbeitstage_pro_woche"),
            verfuegbarkeit_prozent=maschine.verfuegbarkeit_prozent,
        )
        wartungs_kw = (
            Kalenderwoche(maschine.wartung_jahr, maschine.wartung_woche)
            if maschine.wartung_jahr and maschine.wartung_woche
            else None
        )
        zellen: list[Wochenzelle] = []
        for kw in horizont:
            kapazitaet = regel_kapazitaet.kapazitaet_der_woche(
                grund, wartungs_kw, kw, parameter.zahl("wartungsabzug_h")
            )
            kapazitaeten[(maschine.kuerzel, kw)] = kapazitaet
            belastung = regel_kapazitaet.belastung_stunden(planauftraege, maschine.kuerzel, kw)
            anteil = regel_kapazitaet.auslastung(belastung, kapazitaet)
            zellen.append(
                Wochenzelle(
                    kw=kw,
                    belastung_h=belastung,
                    kapazitaet_h=kapazitaet,
                    auslastung=anteil,
                    ampel=regel_kapazitaet.ampel(anteil, grenze),
                    wartung=wartungs_kw == kw,
                )
            )
        zeilen.append(
            Maschinenzeile(
                kuerzel=maschine.kuerzel,
                bezeichnung=maschine.bezeichnung,
                verfuegbarkeit_prozent=maschine.verfuegbarkeit_prozent,
                grundkapazitaet_h=grund,
                wartungs_kw=wartungs_kw,
                zellen=zellen,
            )
        )
    return zeilen, kapazitaeten


def _materialzeile(
    roh: Rohmaterial,
    lieferant: Lieferant,
    positionen: list[regel_material.Materialposition],
    horizont: list[Kalenderwoche],
    parameter: Parameter,
    aktuelle_kw: Kalenderwoche,
) -> Materialzeile:
    reihe = regel_material.bedarf_je_woche(positionen, roh.rohnummer, horizont)
    summe = regel_material.summe_horizont(reihe)
    verfuegbar = regel_material.verfuegbarer_bestand(roh.lager, roh.bestellt_offen)
    durchschnitt = regel_material.durchschnittlicher_wochenbedarf(summe, len(horizont))
    sicherheit = regel_material.sicherheitsbestand(
        durchschnitt, parameter.zahl("sicherheitsbestand_prozent"), roh.gebinde
    )
    kumuliert = regel_material.kumulierter_bedarf(reihe)
    fehl = regel_material.fehl_kw(horizont, kumuliert, sicherheit, verfuegbar)
    bewertung = Bewertung(lieferant.bewertung)
    bestell = regel_material.bestell_kw(
        fehl,
        lieferant.lieferzeit_wochen,
        bewertung,
        parameter.ganzzahl("puffer_lieferant_c_wochen"),
    )
    bestellmenge = regel_material.bestellmenge(summe, sicherheit, verfuegbar, roh.gebinde, fehl)
    return Materialzeile(
        rohnummer=roh.rohnummer,
        bezeichnung=roh.bezeichnung,
        einheit=roh.einheit,
        liefnummer=roh.liefnummer,
        lieferant=lieferant.name,
        lieferzeit_wochen=lieferant.lieferzeit_wochen,
        bewertung=bewertung,
        lager=runde_menge(roh.lager),
        bestellt_offen=runde_menge(roh.bestellt_offen),
        verfuegbar=verfuegbar,
        gebinde=runde_menge(roh.gebinde),
        preis=roh.preis,
        erp_nummer=roh.erp_nummer,
        erp_nummer_lieferant=lieferant.erp_nummer,
        bedarf_reihe=reihe,
        kumuliert_reihe=kumuliert,
        summe_horizont=summe,
        durchschnitt=durchschnitt,
        sicherheitsbestand=sicherheit,
        fehl_kw=fehl,
        bestell_kw=bestell,
        bestellen=regel_material.bestellen(bestell, aktuelle_kw),
        ueberfaellig=regel_material.bestellung_ueberfaellig(bestell, aktuelle_kw),
        bestellmenge=bestellmenge,
        bestellwert=regel_material.bestellwert(bestellmenge, roh.preis),
        bedarfsdatum=regel_material.bedarfsdatum(fehl),
    )


def positionen_der_auftraege(
    zeilen: list[Auftragszeile],
) -> list[regel_material.Materialposition]:
    """Alle Auftragspositionen als Eingabe für den Bedarf (R-022)."""
    return [
        regel_material.Materialposition(
            auftragsnummer=zeile.auftragsnummer,
            rohnummer=position.rohnummer,
            kw_effektiv=zeile.kw_effektiv,
            bedarf=position.bedarf,
            status=zeile.status,
        )
        for zeile in zeilen
        for position in zeile.positionen
    ]
