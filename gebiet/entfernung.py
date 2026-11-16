"""Arbeitsgebiet: Entfernung eines Objekts vom Betriebssitz und Einordnung in Zonen.

Marcels Entscheidung vom 16.11.2026: Arbeitsgebiet ist ein Umkreis von hoechstens
45 km Luftlinie um den Betriebssitz. Was darueber liegt, wird nur als Ausnahme mit seinem
ausdruecklichen Ja bearbeitet. Koordinaten werden immer uebergeben; im Code
stehen keine Adressen und keine Vorgabewerte.
"""
from math import asin, cos, radians, sin, sqrt

ARBEITSRADIUS_KM = 45.0     # Luftlinie; Entscheidung des Inhabers vom 16.11.2026, keine Rechtsvorschrift
ERDRADIUS_KM = 6371.0

INNEN = "innerhalb des Arbeitsgebiets"
AUSNAHME = "ausserhalb - nur als Ausnahme mit ausdruecklichem Ja des Inhabers"


def luftlinie_km(breite_1: float, laenge_1: float, breite_2: float, laenge_2: float) -> float:
    """Entfernung zweier Punkte auf der Erdkugel in Kilometern (Luftlinie)."""
    for wert in (breite_1, laenge_1, breite_2, laenge_2):
        if wert is None:
            raise ValueError("Angabe fehlt: Koordinate")
    b1, l1, b2, l2 = map(radians, (breite_1, laenge_1, breite_2, laenge_2))
    h = sin((b2 - b1) / 2) ** 2 + cos(b1) * cos(b2) * sin((l2 - l1) / 2) ** 2
    return round(2 * ERDRADIUS_KM * asin(sqrt(h)), 1)


def zone(entfernung_km: float, radius_km: float) -> str:
    """Ordnet eine Entfernung ein. Der Radius wird uebergeben (ueblich: ARBEITSRADIUS_KM)."""
    if entfernung_km is None or entfernung_km < 0:
        raise ValueError("Angabe fehlt: Entfernung")
    if radius_km is None or radius_km <= 0:
        raise ValueError("Angabe fehlt: Radius")
    return INNEN if entfernung_km <= radius_km else AUSNAHME


def objekt_offen(akte: dict, radius_km: float) -> list:
    """Prueft, ob ein Objekt ins Arbeitsgebiet passt. Leere Liste = keine offenen Punkte."""
    offen = []
    for schluessel, text in (("entfernung_km", "Entfernung zum Betriebssitz"),
                             ("bundesland", "Bundesland des Objekts"),
                             ("gutachterausschuss", "zustaendiger Gutachterausschuss am Ort des Objekts")):
        if schluessel not in akte or akte[schluessel] in (None, ""):
            offen.append("Angabe fehlt: " + text)
    if "entfernung_km" in akte and akte["entfernung_km"] is not None:
        if zone(akte["entfernung_km"], radius_km) == AUSNAHME and akte.get("ausnahme_vom_inhaber_bestaetigt") is not True:
            offen.append("Objekt liegt ausserhalb des Arbeitsgebiets - Ja des Inhabers mit Begruendung fehlt")
    return offen
