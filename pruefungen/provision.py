"""BEISPIEL-BAUSTEIN - Pruefungen vor dem Notartermin.

ACHTUNG: Vereinfachte Abbildung der Seminarregeln, rechtlich nicht geprueft.
Die Pruefung ersetzt keine anwaltliche Beratung; freigeben muss der Makler.
"""

VORAUSSETZUNGEN = ("maklervertrag", "maklertaetigkeit", "hauptvertrag", "kausalitaet")


def fehlende_voraussetzungen(stand: dict) -> list:
    """Gibt die Provisionsvoraussetzungen zurueck, die noch nicht erfuellt sind."""
    return [v for v in VORAUSSETZUNGEN if not stand.get(v, False)]


def halbteilung_ok(satz_verkaeufer: float, satz_kaeufer: float,
                   wohnimmobilie: bool, kaeufer_verbraucher: bool) -> bool:
    """Bei Wohnung/Einfamilienhaus und Verbraucher als Kaeufer muessen beide Saetze gleich sein."""
    if not (wohnimmobilie and kaeufer_verbraucher):
        return True
    if satz_verkaeufer == 0 or satz_kaeufer == 0:
        return satz_verkaeufer == satz_kaeufer
    return abs(satz_verkaeufer - satz_kaeufer) < 1e-9


def notartermin_checkliste(akte: dict) -> list:
    """Liste offener Punkte; leer bedeutet: bereit zur Freigabe durch den Makler."""
    offen = ["Voraussetzung fehlt: " + v for v in fehlende_voraussetzungen(akte)]
    pflicht = {
        "textform": "Maklervertrag in Textform",
        "widerrufsbelehrung": "Widerrufsbelehrung dokumentiert",
        "nachweisbestaetigung": "Nachweisbestaetigung (erstmals nachgewiesen und besichtigt)",
        "doppeltaetigkeit_offengelegt": "Doppeltaetigkeit offengelegt",
        "gwg_identifizierung": "Geldwaesche: Identifizierung Kaeufer und Verkaeufer",
        "energieausweis": "Energieausweis liegt vor",
    }
    offen += [text for key, text in pflicht.items() if not akte.get(key, False)]
    if not halbteilung_ok(akte.get("satz_verkaeufer", 0), akte.get("satz_kaeufer", 0),
                          akte.get("wohnimmobilie", True), akte.get("kaeufer_verbraucher", True)):
        offen.append("Halbteilung verletzt: Provisionssaetze angleichen")
    return offen
