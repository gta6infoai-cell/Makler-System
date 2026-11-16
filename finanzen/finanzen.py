"""BEISPIEL-BAUSTEIN - Ruecklagenrechner und Kostenblatt je Objekt.

ACHTUNG: Alle Prozentsaetze und Betraege sind BEISPIELWERTE.
Den Ruecklagensatz und die Frage der Umsatzsteuer (Kleinunternehmer ja/nein)
legt der Steuerberater fest. Keine Steuerberatung.
"""
from dataclasses import dataclass, field
from datetime import date

BEISPIEL_UST_SATZ = 0.19        # Beispiel: Regelsteuersatz
BEISPIEL_RUECKLAGE_SATZ = 0.30  # Beispiel: 30 % vom Netto fuer Einkommensteuer


def ruecklage(provision_brutto: float, ust_pflichtig: bool = True,
              ust_satz: float = BEISPIEL_UST_SATZ,
              ruecklage_satz: float = BEISPIEL_RUECKLAGE_SATZ) -> dict:
    """Teilt einen Provisionseingang in Umsatzsteuer, Steuerruecklage und frei verfuegbar."""
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
    budget: float = 5000.0      # Beispielwert
    frist_monate: int = 6       # Beispielwert
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
    print(ruecklage(17850.00))
