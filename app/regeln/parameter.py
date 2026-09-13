"""Parameter und aktuelle Woche. Regeln R-001 und R-002."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.regeln.typen import ZEITZONE, Kalenderwoche, Prioritaet

# Alle Stellschrauben, die der Code aus der Tabelle `parameter` liest (R-001).
# Name, Beschriftung, Einheit. Keine dieser Zahlen steht irgendwo fest in einer Formel.
PARAMETER_KATALOG: dict[str, tuple[str, str]] = {
    "sicherheitsbestand_prozent": ("Sicherheitsbestand", "%"),
    "auslastungsgrenze_prozent": ("Auslastungsgrenze", "%"),
    "ruestzuschlag_alu_min": ("Rüstzuschlag Alu", "min"),
    "losgrenze_alu_stk": ("Losgrenze Alu", "Stk"),
    "schichten_pro_tag": ("Schichten pro Tag", ""),
    "stunden_pro_schicht": ("Std pro Schicht", "h"),
    "arbeitstage_pro_woche": ("Arbeitstage pro Woche", ""),
    "puffer_lieferant_c_wochen": ("Puffer Lieferant C", "Wochen"),
    "kostenstelle_einkauf": ("Kostenstelle Einkauf", ""),
    "planungshorizont_wochen": ("Planungshorizont", "Wochen"),
    "wartungsabzug_h": ("Wartungsabzug", "h"),
    "vorlauf_prio_a_wochen": ("Vorlauf Prio A", "Wochen"),
    "vorlauf_prio_b_wochen": ("Vorlauf Prio B", "Wochen"),
    "vorlauf_prio_c_wochen": ("Vorlauf Prio C", "Wochen"),
}


class ParameterFehlt(KeyError):
    """Ein Parameter wird gebraucht, steht aber nicht in der Tabelle `parameter`."""


@dataclass(frozen=True)
class Parameter:
    """R-001: Alle Stellschrauben stehen in der Tabelle `parameter`.

    Satz: Sicherheitsbestand, Auslastungsgrenze, Rüstzuschlag, Losgrenze, Horizont,
    Wartungsabzug, Puffer und Kostenstelle werden von den Regeln aus der Tabelle
    `parameter` gelesen, nie als Zahl in eine Formel geschrieben.

    Beispiel: `ruestzuschlag_alu_min` = 40 wird von R-003 gelesen, `losgrenze_alu_stk`
    = 500 ebenso. Im Excel steht die 40 an 29 von 50 Stellen fest in der Formel; hier
    gibt es genau eine Quelle.
    """

    werte: dict[str, Decimal]

    def __getitem__(self, name: str) -> Decimal:
        if name not in self.werte:
            raise ParameterFehlt(name)
        return self.werte[name]

    def zahl(self, name: str) -> Decimal:
        return self[name]

    def ganzzahl(self, name: str) -> int:
        return int(self[name])

    def anteil(self, name: str) -> Decimal:
        """Prozentparameter als Anteil: 90 % wird zu 0.90."""
        return self[name] / Decimal(100)

    @property
    def fehlende(self) -> list[str]:
        return [name for name in PARAMETER_KATALOG if name not in self.werte]

    def vorlauf(self, prioritaet: Prioritaet) -> int:
        """Vorlauf in Wochen je Priorität (R-006, Entscheidung zu F-3)."""
        return self.ganzzahl(f"vorlauf_prio_{prioritaet.value.lower()}_wochen")


def aktuelle_kalenderwoche(jetzt: datetime | None = None) -> Kalenderwoche:
    """R-002: Die aktuelle Kalenderwoche kommt aus dem Datum, nicht aus einer Handeingabe.

    Satz: Die aktuelle KW ist die ISO-Woche des heutigen Datums in der Zeitzone
    Europe/Zurich; das Montagsdatum ergibt sich daraus.

    Beispiel: 13.09.2026 (Sonntag) liegt in der ISO-Woche 37 von 2026, der zugehörige
    Montag ist der 07.09.2026. Im Excel wurden KW und Montag von Hand nachgetragen
    (`Parameter!B2`, `B4`), was die Jahreswechselfehler aus R-005 erst möglich machte.
    """
    if jetzt is None:
        jetzt = datetime.now(ZoneInfo(ZEITZONE))
    if jetzt.tzinfo is None:
        raise ValueError("Zeitpunkt muss zeitzonenbehaftet sein (Europe/Zurich)")
    return Kalenderwoche.von_datum(jetzt.astimezone(ZoneInfo(ZEITZONE)).date())


def montag_der_woche(kw: Kalenderwoche) -> date:
    """R-002: Montagsdatum einer Kalenderwoche. Beispiel: 2026-KW39 -> 21.09.2026."""
    return kw.montag
