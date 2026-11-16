"""Fristenkontrolle (Stand 16.11.2026).

Jede Frist ist ein Woerterbuch mit bezeichnung (Text), faellig_am (Datum) und
erledigt (True/False). Die Funktion rechnet keine gesetzlichen Fristen aus; das
Fristende traegt der Inhaber ein (bei Zweifeln nach Rueckfrage beim Anwalt).
"""
from datetime import date

FEHLT = "Angabe fehlt: "


def faellige(fristen: list, heute: date, vorlauf_tage: int) -> list:
    """Meldet ueberfaellige Fristen und solche, die in den naechsten vorlauf_tage faellig werden.

    Rueckgabe: Liste aus (tage_bis_faellig, text), die dringendste zuerst.
    Negative Zahl = ueberfaellig. Unvollstaendige Eintraege stehen ganz vorn.
    """
    unvollstaendig, treffer = [], []
    for nummer, frist in enumerate(fristen, start=1):
        fehlend = [feld for feld in ("bezeichnung", "faellig_am", "erledigt")
                   if feld not in frist or frist[feld] is None]
        if fehlend or not isinstance(frist["faellig_am"], date):
            name = frist.get("bezeichnung") or "Frist Nr. " + str(nummer)
            unvollstaendig.append((None, FEHLT + str(name) + ": " + ", ".join(fehlend or ["faellig_am als Datum"])))
            continue
        if frist["erledigt"] is True:
            continue
        tage = (frist["faellig_am"] - heute).days
        if tage <= vorlauf_tage:
            treffer.append((tage, frist["bezeichnung"]))
    return unvollstaendig + sorted(treffer)
