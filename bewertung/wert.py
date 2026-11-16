"""BEISPIEL-BAUSTEIN - vereinfachte Wertermittlung.

ACHTUNG: Alle Zahlen in BEISPIEL_OBJEKT sind erfundene Beispielwerte.
Das Ergebnis ist eine Orientierung fuer das Preisgespraech, kein Gutachten.
Faktoren (Bodenrichtwert, Herstellungskosten, Sachwertfaktor) muessen je
Objekt aus aktuellen Quellen stammen (z. B. BORIS-BW, Gutachterausschuss).
"""
from dataclasses import dataclass


@dataclass
class Objekt:
    grundstueck_qm: float
    bodenrichtwert: float          # Euro je qm
    bodenwert_anpassung: float     # 1.0 = keine Anpassung
    bgf_qm: float                  # Brutto-Grundflaeche Gebaeude
    herstellungskosten_qm: float   # Euro je qm BGF, bereits indexiert
    gesamtnutzungsdauer: int       # Jahre
    restnutzungsdauer: int         # Jahre
    aussenanlagen_anteil: float    # z. B. 0.05 = 5 % vom Gebaeudewert
    sachwertfaktor: float          # Marktanpassung


def bodenwert(o: Objekt) -> float:
    """Bodenwert = Flaeche x Bodenrichtwert x Anpassung."""
    return round(o.grundstueck_qm * o.bodenrichtwert * o.bodenwert_anpassung, 2)


def gebaeudewert(o: Objekt) -> float:
    """Herstellungskosten, linear alterswertgemindert."""
    if o.gesamtnutzungsdauer <= 0:
        raise ValueError("Gesamtnutzungsdauer muss groesser 0 sein")
    rest = max(0, min(o.restnutzungsdauer, o.gesamtnutzungsdauer))
    return round(o.bgf_qm * o.herstellungskosten_qm * rest / o.gesamtnutzungsdauer, 2)


def aussenanlagen(o: Objekt) -> float:
    return round(gebaeudewert(o) * o.aussenanlagen_anteil, 2)


def sachwert(o: Objekt) -> float:
    """Sachwert = (Gebaeude + Aussenanlagen + Boden) x Sachwertfaktor."""
    vorlaeufig = gebaeudewert(o) + aussenanlagen(o) + bodenwert(o)
    return round(vorlaeufig * o.sachwertfaktor, 2)


# BEISPIEL - erfundene Werte, nur zur Veranschaulichung
BEISPIEL_OBJEKT = Objekt(
    grundstueck_qm=500, bodenrichtwert=450, bodenwert_anpassung=1.0,
    bgf_qm=220, herstellungskosten_qm=1500, gesamtnutzungsdauer=80,
    restnutzungsdauer=40, aussenanlagen_anteil=0.05, sachwertfaktor=1.1,
)

if __name__ == "__main__":
    print("BEISPIEL - keine echten Daten")
    print("Bodenwert:", bodenwert(BEISPIEL_OBJEKT))
    print("Sachwert :", sachwert(BEISPIEL_OBJEKT))
