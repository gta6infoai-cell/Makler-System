"""BEISPIEL-BAUSTEIN - Ruecklagenrechner und Kostenblatt je Objekt.

ACHTUNG: Alle Konstanten mit BEISPIEL_ im Namen sind erfundene Beispielwerte.
Sie werden von keiner Funktion automatisch verwendet; echte Werte muessen
bei jedem Aufruf ausdruecklich angegeben werden.
Den Ruecklagensatz und die Frage der Umsatzsteuer (Kleinunternehmer ja/nein)
legt der Steuerberater fest. Keine Steuerberatung.
"""
from dataclasses import dataclass, field
from datetime import date

BEISPIEL_UST_SATZ = 0.19        # Beispiel: Regelsteuersatz
BEISPIEL_RUECKLAGE_SATZ = 0.30  # Beispiel: 30 % vom Netto fuer Einkommensteuer
BEISPIEL_BUDGET = 5000.0         # Beispiel: Budget je Objekt
BEISPIEL_FRIST_MONATE = 6        # Beispiel: Frist je Objekt


def ruecklage(provision_brutto: float, ust_pflichtig: bool,
              ust_satz: float, ruecklage_satz: float) -> dict:
    """Teilt einen Provisionseingang in Umsatzsteuer, Steuerruecklage und frei verfuegbar.

    Alle Saetze muessen ausdruecklich uebergeben werden. Es gibt bewusst keine
    Vorgabewerte, damit Beispielwerte nie unbemerkt in echte Rechnungen einfliessen.
    """
    if provision_brutto < 0:
        raise ValueError("Provision darf nicht negativ sein")
    netto = provision_brutto / (1 + ust_satz) if ust_pflichtig else provision_brutto
    ust = provision_brutto - netto
    steuer = netto * ruecklage_satz
    return {
        "brutto": round(provision_brutto, 2),
        "umsatzsteuer": round(ust, 2),
        "netto": round(netto, 2),
        "steuerruecklage": round(steuer, 2),
        "auf_ruecklagenkonto": round(ust + steuer, 2),
        "frei_verfuegbar": round(netto - steuer, 2),
    }


@dataclass
class Kostenblatt:
    """Kosten je Objekt mit Budget- und Fristwarnung."""
    objekt: str
    auftragsbeginn: date
    budget: float               # Pflichtangabe, kein Vorgabewert
    frist_monate: int           # Pflichtangabe, kein Vorgabewert
    posten: list = field(default_factory=list)

    def buchen(self, datum: date, art: str, betrag: float) -> None:
        self.posten.append((datum, art, round(betrag, 2)))

    def summe(self) -> float:
        return round(sum(p[2] for p in self.posten), 2)

    def monate_laufzeit(self, heute: date) -> int:
        return (heute.year - self.auftragsbeginn.year) * 12 + heute.month - self.auftragsbeginn.month

    def warnungen(self, heute: date) -> list:
        w = []
        if self.summe() > self.budget:
            w.append("Budget ueberschritten")
        if self.monate_laufzeit(heute) >= self.frist_monate:
            w.append("Frist erreicht")
        if len(w) == 2:
            w.append("Objekt pruefen: abgeben?")
        return w


if __name__ == "__main__":
    print("BEISPIEL - keine echten Daten")
    print(ruecklage(17850.00, True, BEISPIEL_UST_SATZ, BEISPIEL_RUECKLAGE_SATZ))
