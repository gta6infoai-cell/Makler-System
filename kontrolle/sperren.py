"""Sperren je Vorgang (Stand 16.11.2026).

Ein Verkaufsvorgang laeuft in festen Stufen. Eine Stufe gilt erst als bereit, wenn
alle Stufen davor freigegeben sind und die Pruef-Funktionen dieser Stufe nichts mehr
melden. Das System gibt nie selbst frei: "bereit" heisst nur "bereit zur Freigabe
durch den Inhaber". Die Freigabe traegt der Inhaber mit Datum in die Akte ein.

Keine Rechtsberatung. Nichts wird angenommen; fehlende Angaben werden gemeldet.

Aufbau der Akte: ein Woerterbuch mit je einem Unter-Woerterbuch pro Bereich:
objekt, grundbuch, widerruf, online, anzeige, kaeufer, notar, geldwaesche,
geldwaesche_zusatz, rechnung, freigaben.
"""
from datetime import date

from gebiet import entfernung
from pruefungen import ergaenzungen, provision, pruefpunkte

STUFEN = ("auftrag", "anzeige", "besichtigung", "notar", "rechnung")
FEHLT = "Angabe fehlt: "


def _teil(akte: dict, bereich: str) -> dict:
    """Unter-Akte eines Bereichs; fehlt sie, ist sie leer und alles wird als fehlend gemeldet."""
    teil = akte.get(bereich)
    return teil if isinstance(teil, dict) else {}


def _punkte(teil: dict, punkte) -> list:
    offen = []
    for schluessel, text in punkte:
        if schluessel not in teil or teil[schluessel] is None:
            offen.append(FEHLT + text)
        elif teil[schluessel] is not True:
            offen.append(text)
    return offen


def stufe_offen(stufe: str, akte: dict, stichtag: date) -> list:
    """Offene Punkte einer Stufe. Leere Liste = fachlich nichts mehr offen."""
    if stufe not in STUFEN:
        return ["Unbekannte Stufe: " + str(stufe)]
    if stufe == "auftrag":
        return (_punkte(_teil(akte, "objekt"), [
                    ("erlaubnis_34c_liegt_vor", "Erlaubnis nach Paragraf 34c GewO liegt vor"),
                    ("maklervertrag_in_textform", "Maklervertrag mit dem Auftraggeber in Textform"),
                    ("datenschutzinformation_uebergeben", "Datenschutzinformation uebergeben"),
                ])
                + entfernung.objekt_offen(_teil(akte, "objekt"), entfernung.ARBEITSRADIUS_KM)
                + ergaenzungen.verkaufsauftrag_objekt_offen(_teil(akte, "grundbuch"))
                + pruefpunkte.widerruf_offen(_teil(akte, "widerruf"))
                + ergaenzungen.online_abschluss_offen(_teil(akte, "online")))
    if stufe == "anzeige":
        return pruefpunkte.anzeige_offen(_teil(akte, "anzeige"), stichtag)
    if stufe == "besichtigung":
        kaeufer = _teil(akte, "kaeufer")
        return (_punkte(kaeufer, [
                    ("provisionsvereinbarung_in_textform", "Provisionsvereinbarung mit dem Interessenten in Textform vor der Besichtigung"),
                    ("widerrufsbelehrung_uebergeben", "Widerrufsbelehrung mit Formular an den Interessenten"),
                    ("nachweisbestaetigung_vorbereitet", "Nachweisbestaetigung zur Unterschrift vorbereitet"),
                ])
                + ergaenzungen.kaeufernutzung_offen(kaeufer))
    if stufe == "notar":
        return (provision.notartermin_checkliste(_teil(akte, "notar"))
                + pruefpunkte.geldwaesche_offen(_teil(akte, "geldwaesche"))
                + ergaenzungen.geldwaesche_zusatz_offen(_teil(akte, "geldwaesche_zusatz")))
    rechnung = _teil(akte, "rechnung")
    offen = ["Voraussetzung fehlt: " + v for v in provision.fehlende_voraussetzungen(rechnung)]
    offen += _punkte(rechnung, [
        ("hauptvertrag_wirksam", "Kaufvertrag wirksam, Bedingungen und Genehmigungen eingetreten"),
        ("steuerfrage_geklaert", "Kleinunternehmer ja/nein mit dem Steuerberater geklaert"),
    ])
    angaben_da = True
    for schluessel, text in (("nur_eine_seite_beauftragt", "nur eine Seite hat beauftragt ja/nein"),
                             ("zahlung_auftraggeber_nachgewiesen", "Zahlung des Auftraggebers nachgewiesen ja/nein")):
        if schluessel not in rechnung or rechnung[schluessel] is None:
            offen.append(FEHLT + text)
            angaben_da = False
    if angaben_da and not ergaenzungen.kaeuferanteil_faellig(rechnung["nur_eine_seite_beauftragt"],
                                                           rechnung["zahlung_auftraggeber_nachgewiesen"]):
        offen.append("Anteil der anderen Seite noch nicht faellig (Paragraf 656d BGB)")
    return offen


def freigegeben(stufe: str, akte: dict) -> bool:
    """True nur, wenn der Inhaber die Stufe mit Datum freigegeben hat."""
    eintrag = _teil(akte, "freigaben").get(stufe)
    return isinstance(eintrag, date)


def stand(stufe: str, akte: dict, stichtag: date) -> dict:
    """Gesamtbild fuer eine Stufe.

    bereit = alle frueheren Stufen vom Inhaber freigegeben und in dieser Stufe nichts offen.
    """
    if stufe not in STUFEN:
        return {"bereit": False, "sperren": ["Unbekannte Stufe: " + str(stufe)], "offen": []}
    sperren = ["Stufe " + frueher + " ist noch nicht vom Inhaber freigegeben"
               for frueher in STUFEN[:STUFEN.index(stufe)] if not freigegeben(frueher, akte)]
    offen = stufe_offen(stufe, akte, stichtag)
    return {"bereit": not sperren and not offen, "sperren": sperren, "offen": offen}
