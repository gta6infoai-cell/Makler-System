"""Rechenwege der Wertermittlung nach ImmoWertV - nur Rechenwege, keine Marktdaten.

WICHTIG
- Ergebnis ist eine Marktpreiseinschaetzung, kein Verkehrswertgutachten.
- Keine Funktion hat Vorgabewerte. Jede Zahl (Bodenrichtwert, Koeffizienten,
  Regionalfaktor, Baupreisindex, Sachwertfaktor, Liegenschaftszinssatz) muss
  je Objekt mit Quelle und Stichtag eingegeben werden, in der Regel aus dem
  Grundstuecksmarktbericht des zustaendigen Gutachterausschusses.
- Ohne Sachwertfaktor bzw. Marktanpassung ist ein Ergebnis nur "vorlaeufig".
- Die Seminaraufgaben stehen als BEISPIEL nur in tests/test_verfahren.py.

Fundstellen: Paragraf 4 ImmoWertV (Alter, Restnutzungsdauer), Paragrafen 27
bis 34 (Ertragswert), 35 und 36 (Sachwert), 40 (Bodenwert), Anlage 1
(Gesamtnutzungsdauer), Anlage 2 (Kernsanierung), Anlage 4 (Kostenkennwerte).
"""

GESAMTNUTZUNGSDAUER_WOHNGEBAEUDE = 80   # Jahre, Modellansatz Anlage 1 ImmoWertV
KERNSANIERUNG_ANTEIL = 0.10             # Anlage 2: Restnutzungsdauer bis 90 Prozent
HINWEIS = "Marktpreiseinschaetzung, kein Verkehrswertgutachten"


def _positiv(wert: float, name: str) -> None:
    if wert is None or wert <= 0:
        raise ValueError(name + " muss groesser 0 sein")


# ---------- Bodenwert ----------

def wgfz(wertrelevante_geschossflaeche: float, grundstuecksflaeche: float) -> float:
    """Wertrelevante Geschossflaechenzahl = Geschossflaeche / Grundstuecksflaeche."""
    _positiv(grundstuecksflaeche, "Grundstuecksflaeche")
    return wertrelevante_geschossflaeche / grundstuecksflaeche


def anpassungsfaktor(koeffizient_objekt: float, koeffizient_vergleich: float, stellen: int) -> float:
    """Immer Objekt geteilt durch Vergleich (Richtwertgrundstueck)."""
    _positiv(koeffizient_vergleich, "Koeffizient des Vergleichsgrundstuecks")
    return round(koeffizient_objekt / koeffizient_vergleich, stellen)


def bodenwert(grundstuecksflaeche: float, bodenrichtwert: float, faktoren: list) -> dict:
    """Vorlaeufiger Bodenwert, danach Anpassungen in der uebergebenen Reihenfolge.

    faktoren: Liste aus (Bezeichnung, Faktor), z. B. Ausnutzung und Groesse.
    Gibt alle Zwischenschritte zurueck, damit die Rechnung nachvollziehbar bleibt.
    """
    _positiv(grundstuecksflaeche, "Grundstuecksflaeche")
    _positiv(bodenrichtwert, "Bodenrichtwert")
    wert = round(grundstuecksflaeche * bodenrichtwert, 2)
    schritte = [("vorlaeufiger Bodenwert", wert)]
    for bezeichnung, faktor in faktoren:
        _positiv(faktor, "Faktor " + bezeichnung)
        wert = round(wert * faktor, 2)
        schritte.append((bezeichnung, wert))
    return {"bodenwert": wert, "schritte": schritte}


# ---------- Alter und Restnutzungsdauer ----------

def alter(stichtagsjahr: int, baujahr: int) -> int:
    if baujahr > stichtagsjahr:
        raise ValueError("Baujahr liegt nach dem Stichtag")
    return stichtagsjahr - baujahr


def restnutzungsdauer(gesamtnutzungsdauer: float, alter_jahre: float) -> float:
    """Regelfall: Gesamtnutzungsdauer minus Alter, nie unter 0."""
    _positiv(gesamtnutzungsdauer, "Gesamtnutzungsdauer")
    return max(0.0, gesamtnutzungsdauer - alter_jahre)


def fiktives_baujahr_kernsanierung(jahr_kernsanierung: int, gesamtnutzungsdauer: float) -> int:
    """Kernsanierung: Sanierungsjahr minus 10 Prozent der Gesamtnutzungsdauer."""
    _positiv(gesamtnutzungsdauer, "Gesamtnutzungsdauer")
    return int(round(jahr_kernsanierung - gesamtnutzungsdauer * KERNSANIERUNG_ANTEIL))


def restnutzungsdauer_gewichtet(teile: list) -> float:
    """An-, Um-, Ausbau: nach Wohnflaeche gewichtete Restnutzungsdauer.

    teile: Liste aus (Restnutzungsdauer, Wohnflaeche) je Gebaeudeteil.
    """
    flaeche = sum(f for _, f in teile)
    _positiv(flaeche, "Summe der Wohnflaechen")
    return round(sum(r * f for r, f in teile) / flaeche, 2)


def alterswertminderung_prozent(alter_jahre: float, gesamtnutzungsdauer: float) -> float:
    """Lineare Alterswertminderung in Prozent, hoechstens 100."""
    _positiv(gesamtnutzungsdauer, "Gesamtnutzungsdauer")
    return round(min(100.0, max(0.0, alter_jahre / gesamtnutzungsdauer * 100)), 2)


# ---------- Sachwert ----------

def gewogener_kostenkennwert(kennwerte: dict, waegung: dict, anteile: dict) -> float:
    """Kostenkennwert je qm Brutto-Grundflaeche bei gemischtem Standard.

    kennwerte: Standardstufe -> Euro je qm (Anlage 4, fuer den Gebaeudetyp)
    waegung:   Bauteil -> Waegungsanteil in Prozent (Summe 100)
    anteile:   Bauteil -> {Standardstufe: Anteil}, Anteile je Bauteil summieren zu 1
    """
    if round(sum(waegung.values()), 6) != 100:
        raise ValueError("Waegungsanteile muessen zusammen 100 Prozent ergeben")
    summe = 0.0
    for bauteil, prozent in waegung.items():
        if bauteil not in anteile:
            raise ValueError("Angabe fehlt: Standardstufe fuer " + bauteil)
        stufen = anteile[bauteil]
        if round(sum(stufen.values()), 6) != 1:
            raise ValueError("Stufenanteile fuer " + bauteil + " muessen zusammen 1 ergeben")
        for stufe, anteil in stufen.items():
            summe += kennwerte[stufe] * anteil * prozent / 100
    return round(summe, 2)


def baupreisfaktor(index_stichtag: float, index_basisjahr_nhk: float) -> float:
    """Indexverhaeltnis in Prozent. Beide Werte muessen aus derselben Indexreihe stammen."""
    _positiv(index_basisjahr_nhk, "Index im Basisjahr der Kostenkennwerte")
    return round(index_stichtag / index_basisjahr_nhk * 100, 2)


def sachwert_vorlaeufig(kostenkennwert: float, brutto_grundflaeche: float, regionalfaktor: float,
                        baupreisfaktor_prozent: float, alter_jahre: float, gesamtnutzungsdauer: float,
                        aussenanlagen: float, bodenwert_euro: float) -> dict:
    """Vorlaeufiger Sachwert ohne Marktanpassung, mit allen Zwischenschritten."""
    for wert, name in ((kostenkennwert, "Kostenkennwert"), (brutto_grundflaeche, "Brutto-Grundflaeche"),
                       (regionalfaktor, "Regionalfaktor"), (baupreisfaktor_prozent, "Baupreisfaktor")):
        _positiv(wert, name)
    herstellung_basis = round(kostenkennwert * brutto_grundflaeche, 2)
    herstellung_region = round(herstellung_basis * regionalfaktor, 2)
    herstellung_stichtag = round(herstellung_region * baupreisfaktor_prozent / 100, 2)
    minderung_prozent = alterswertminderung_prozent(alter_jahre, gesamtnutzungsdauer)
    minderung = round(herstellung_stichtag * minderung_prozent / 100, 2)
    gebaeude = round(herstellung_stichtag - minderung, 2)
    vorlaeufig = round(gebaeude + aussenanlagen + bodenwert_euro, 2)
    return {
        "herstellungskosten_basisjahr": herstellung_basis,
        "herstellungskosten_regional": herstellung_region,
        "herstellungskosten_stichtag": herstellung_stichtag,
        "alterswertminderung_prozent": minderung_prozent,
        "alterswertminderung": minderung,
        "gebaeudewert": gebaeude,
        "aussenanlagen": aussenanlagen,
        "bodenwert": bodenwert_euro,
        "sachwert_vorlaeufig": vorlaeufig,
        "hinweis": "vorlaeufig - Sachwertfaktor und besondere Merkmale fehlen; " + HINWEIS,
    }


def sachwert_marktangepasst(sachwert_vorlaeufig_euro: float, sachwertfaktor: float,
                            besondere_merkmale: float) -> float:
    """Marktanpassung mit dem Sachwertfaktor des Gutachterausschusses, dann Zu-/Abschlaege."""
    _positiv(sachwertfaktor, "Sachwertfaktor")
    return round(sachwert_vorlaeufig_euro * sachwertfaktor + besondere_merkmale, 2)


# ---------- Ertragswert ----------

def reinertrag(rohertrag_jahr: float, bewirtschaftungskosten_jahr: float) -> float:
    return round(rohertrag_jahr - bewirtschaftungskosten_jahr, 2)


def barwertfaktor(liegenschaftszins_prozent: float, restnutzungsdauer_jahre: float) -> float:
    """Kapitalisierungsfaktor (Paragraf 34 ImmoWertV)."""
    _positiv(liegenschaftszins_prozent, "Liegenschaftszinssatz")
    _positiv(restnutzungsdauer_jahre, "Restnutzungsdauer")
    q = 1 + liegenschaftszins_prozent / 100
    return (q ** restnutzungsdauer_jahre - 1) / (q ** restnutzungsdauer_jahre * (q - 1))


def ertragswert_allgemein(reinertrag_jahr: float, bodenwert_euro: float,
                          liegenschaftszins_prozent: float, restnutzungsdauer_jahre: float) -> dict:
    """Allgemeines Ertragswertverfahren (Paragraf 28 ImmoWertV), vorlaeufig."""
    bodenverzinsung = round(bodenwert_euro * liegenschaftszins_prozent / 100, 2)
    gebaeude_reinertrag = round(reinertrag_jahr - bodenverzinsung, 2)
    faktor = barwertfaktor(liegenschaftszins_prozent, restnutzungsdauer_jahre)
    gebaeude = round(gebaeude_reinertrag * faktor, 2)
    return {
        "bodenwertverzinsung": bodenverzinsung,
        "reinertrag_gebaeude": gebaeude_reinertrag,
        "barwertfaktor": round(faktor, 4),
        "ertragswert_gebaeude": gebaeude,
        "ertragswert_vorlaeufig": round(gebaeude + bodenwert_euro, 2),
        "hinweis": "vorlaeufig - Marktanpassung und besondere Merkmale fehlen; " + HINWEIS,
    }


def ertragswert_vereinfacht(reinertrag_jahr: float, bodenwert_euro: float,
                            liegenschaftszins_prozent: float, restnutzungsdauer_jahre: float) -> float:
    """Vereinfachtes Verfahren (Paragraf 29): Barwert des Reinertrags plus abgezinster Bodenwert."""
    faktor = barwertfaktor(liegenschaftszins_prozent, restnutzungsdauer_jahre)
    q = 1 + liegenschaftszins_prozent / 100
    return round(reinertrag_jahr * faktor + bodenwert_euro / q ** restnutzungsdauer_jahre, 2)
