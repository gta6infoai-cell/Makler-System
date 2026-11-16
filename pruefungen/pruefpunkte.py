"""Pruefpunkte vor jedem Schritt mit Aussenwirkung (Anzeige, Maklervertrag, Vermietung, Geldwaesche).

Grundlage: Projektdokumente rechtslandkarte.md und pruefpunkte.md, Stand 16.11.2026.

ACHTUNG
- Keine Rechtsberatung. Die Funktionen melden nur offene Punkte; freigeben muss der Makler.
- Nichts wird angenommen: Fehlt eine Angabe in der Akte, wird sie als "Angabe fehlt" gemeldet.
- Gesetzliche Werte stehen als Konstanten mit Fundstelle im Kopf. Aendert sich das Gesetz,
  werden sie beim Rechts-Check (1. und 15. des Monats) angepasst.
- Eine leere Liste bedeutet: kein offener Punkt gefunden - nicht: rechtlich geprueft.
"""
from datetime import date

# Gesetzliche Werte (keine Beispiele), Stand 16.11.2026
MAX_MONATSMIETEN_MIETER = 2          # Paragraf 3 Abs. 2 WoVermRG, zuzueglich Umsatzsteuer
GWG_SCHWELLE_MIETE = 10000.0         # Paragraf 2 Abs. 1 Nr. 14 GwG, monatliche Nettokaltmiete
MIETPREISBREMSE_FAKTOR = 1.10        # Paragraf 556d Abs. 1 BGB
STICHTAG_ANZEIGE_NEU = date(2027, 1, 1)  # Paragraf 87 GModG neue Fassung - bisher nur eine Quelle

VERTRAGSORTE = ("geschaeftsraum", "ausserhalb", "fernabsatz", "online")
FEHLT = "Angabe fehlt: "


def _offen(akte: dict, punkte) -> list:
    """Meldet fehlende Angaben und nicht erfuellte Punkte. punkte = Folge von (schluessel, text)."""
    offen = []
    for schluessel, text in punkte:
        if schluessel not in akte:
            offen.append(FEHLT + text)
        elif not akte[schluessel]:
            offen.append(text)
    return offen


def anzeige_offen(akte: dict, stichtag: date) -> list:
    """Offene Punkte vor Veroeffentlichung einer Anzeige. stichtag = Tag der Veroeffentlichung."""
    offen = _offen(akte, (
        ("auftrag_liegt_vor", "Auftrag des Eigentuemers/Vermieters liegt vor"),
        ("flaeche_belegt", "Wohnflaeche ist belegt (Berechnung oder Quelle)"),
        ("preis_gesamt_inkl_ust", "Preisangaben als Gesamtbetrag inklusive Umsatzsteuer"),
        ("bildrechte_geklaert", "Bildrechte geklaert, keine Personen oder Kennzeichen erkennbar"),
        ("aussagen_belegt", "Alle Aussagen zu Lage, Zustand, Baurecht sind belegt"),
    ))
    if "energieausweis_vorhanden" not in akte:
        offen.append(FEHLT + "Energieausweis vorhanden (ja/nein)")
    elif akte["energieausweis_vorhanden"]:
        felder = [
            ("energieausweis_art", "Art des Energieausweises (Bedarf/Verbrauch)"),
            ("energietraeger", "Wesentlicher Energietraeger der Heizung"),
            ("baujahr", "Baujahr laut Energieausweis"),
            ("effizienzklasse", "Energieeffizienzklasse"),
        ]
        if stichtag >= STICHTAG_ANZEIGE_NEU:
            felder += [
                ("ausweis_ausstellungsdatum", "Ausstellungsdatum des Energieausweises (ab 2027)"),
                ("primaerenergiebedarf", "Jahres-Primaerenergiebedarf (ab 2027)"),
            ]
        else:
            felder.append(("endenergiewert", "Endenergiebedarf oder -verbrauch"))
        offen += _offen(akte, felder)
    else:
        offen += _offen(akte, (
            ("ausweis_bis_besichtigung", "Energieausweis liegt spaetestens zur Besichtigung vor"),
        ))
    if "vermietung" not in akte:
        offen.append(FEHLT + "Anzeige fuer Vermietung (ja/nein)")
    elif akte["vermietung"]:
        offen += _offen(akte, (
            ("name_genannt", "Name des Vermittlers in der Anzeige"),
            ("bezeichnung_wohnungsvermittler", "Bezeichnung als Wohnungsvermittler"),
            ("mietpreis_genannt", "Mietpreis genannt"),
            ("nebenkostenhinweis", "Hinweis auf gesonderte Nebenkosten"),
        ))
    return offen


def widerruf_offen(akte: dict) -> list:
    """Offene Punkte zum Widerrufsrecht vor Abschluss eines Maklervertrags."""
    for schluessel, text in (("verbraucher", "Auftraggeber ist Verbraucher (ja/nein)"),
                             ("vertragsort", "Vertragsort")):
        if schluessel not in akte:
            return [FEHLT + text]
    if akte["vertragsort"] not in VERTRAGSORTE:
        return ["Vertragsort unbekannt: erlaubt sind " + ", ".join(VERTRAGSORTE)]
    if not akte["verbraucher"] or akte["vertragsort"] == "geschaeftsraum":
        return []
    offen = _offen(akte, (
        ("belehrung_ausgehaendigt", "Widerrufsbelehrung ausgehaendigt und vollstaendig ausgefuellt"),
        ("formular_beigefuegt", "Muster-Widerrufsformular beigefuegt"),
    ))
    if "vorzeitiger_beginn" not in akte:
        offen.append(FEHLT + "Taetigkeit vor Ablauf der Widerrufsfrist (ja/nein)")
    elif akte["vorzeitiger_beginn"]:
        offen += _offen(akte, (
            ("zustimmung_ausdruecklich", "Ausdrueckliche Zustimmung zum vorzeitigen Beginn"),
            ("kenntnis_bestaetigt", "Kunde hat Verlust des Widerrufsrechts bei voller Leistung bestaetigt"),
        ))
        if akte["vertragsort"] == "ausserhalb":
            offen += _offen(akte, (
                ("zustimmung_dauerhafter_datentraeger",
                 "Zustimmung auf dauerhaftem Datentraeger (Papier oder E-Mail)"),
            ))
    if akte["vertragsort"] == "online":
        offen += _offen(akte, (
            ("widerrufsfunktion", "Elektronische Widerrufsfunktion auf der Website (Paragraf 356a BGB)"),
            ("belehrung_nennt_funktion", "Belehrung weist auf die Widerrufsfunktion hin"),
            ("anwalt_freigabe_online", "Online-Strecke anwaltlich freigegeben"),
        ))
    return offen


def hoechstprovision_mieter(nettokaltmiete: float, ust_satz: float) -> float:
    """Hoechstbetrag, den ein Wohnungssuchender zahlen darf (Monatsmiete ohne Nebenkosten)."""
    return round(MAX_MONATSMIETEN_MIETER * nettokaltmiete * (1 + ust_satz), 2)


def vermietung_offen(akte: dict) -> list:
    """Offene Punkte bei einem Vermietungsauftrag."""
    offen = _offen(akte, (
        ("auftrag_vermieter_textform", "Auftrag des Vermieters in Textform"),
        ("keine_verflechtung", "Makler ist nicht Eigentuemer, Verwalter, Mieter oder Vermieter"),
        ("keine_zusatzgebuehren", "Keine Zusatzgebuehren neben der Provision"),
        ("mietpreisbremse_geprueft", "Geprueft, ob die Gemeinde unter die Mietpreisbremse faellt"),
    ))
    if "zahler" not in akte:
        offen.append(FEHLT + "Wer zahlt die Provision (vermieter/mieter)")
    elif akte["zahler"] == "mieter":
        offen += _offen(akte, (
            ("suchauftrag_textform", "Suchauftrag des Wohnungssuchenden in Textform"),
            ("ausschliesslich_fuer_suchenden", "Wohnung ausschliesslich wegen dieses Suchauftrags beschafft"),
        ))
        noetig = ("provision_brutto", "nettokaltmiete", "ust_satz")
        fehlend = [k for k in noetig if k not in akte]
        if fehlend:
            offen += [FEHLT + k for k in fehlend]
        elif akte["provision_brutto"] > hoechstprovision_mieter(akte["nettokaltmiete"], akte["ust_satz"]):
            offen.append("Provision ueber der Hoechstgrenze von zwei Monatsmieten zuzueglich Umsatzsteuer")
    elif akte["zahler"] != "vermieter":
        offen.append("Zahler unbekannt: erlaubt sind vermieter, mieter")
    if akte.get("mietpreisbremse_gilt"):
        noetig = ("nettokaltmiete", "vergleichsmiete", "ausnahme_mietpreisbremse")
        fehlend = [k for k in noetig if k not in akte]
        if fehlend:
            offen += [FEHLT + k for k in fehlend]
        elif (akte["nettokaltmiete"] > round(akte["vergleichsmiete"] * MIETPREISBREMSE_FAKTOR, 2)
              and not akte["ausnahme_mietpreisbremse"]):
            offen.append("Miete ueber Vergleichsmiete plus 10 Prozent: Vermieter auf Mietpreisbremse hinweisen")
    return offen


def gwg_pflicht_bei_miete(nettokaltmiete_monat: float) -> bool:
    """Geldwaeschepflichten greifen bei Miete/Pacht erst ab der gesetzlichen Schwelle."""
    return nettokaltmiete_monat >= GWG_SCHWELLE_MIETE


def geldwaesche_offen(akte: dict) -> list:
    """Offene Punkte zur Geldwaesche bei einer Kaufvermittlung."""
    offen = _offen(akte, (
        ("goaml_registriert", "Registrierung im Meldeportal goAML"),
        ("risikoanalyse_vorhanden", "Schriftliche Risikoanalyse vorhanden und aktuell"),
        ("hinweis_barzahlungsverbot", "Parteien auf das Barzahlungsverbot hingewiesen"),
    ))
    if "ernsthaftes_kaufinteresse" not in akte:
        offen.append(FEHLT + "Ernsthaftes Kaufinteresse (ja/nein)")
    elif akte["ernsthaftes_kaufinteresse"]:
        offen += _offen(akte, (
            ("verkaeufer_identifiziert", "Verkaeufer identifiziert und dokumentiert"),
            ("kaeufer_identifiziert", "Kaeufer identifiziert und dokumentiert"),
            ("wirtschaftlich_berechtigter_geklaert", "Wirtschaftlich Berechtigter geklaert"),
        ))
    if akte.get("auffaelligkeit"):
        offen.append("Auffaelligkeit notiert: Makler entscheidet ueber Verdachtsmeldung, Kunden nicht informieren")
    return offen
