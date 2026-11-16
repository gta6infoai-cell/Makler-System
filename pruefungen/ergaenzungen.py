"""Ergaenzende Pruefpunkte (Stand 16.11.2026) - aus dem Abgleich mit dem Seminarordner.

Gleiche Regeln wie in pruefpunkte.py: nichts wird angenommen, fehlende Angaben
werden als "Angabe fehlt: ..." gemeldet, keine Vorgabewerte. Keine Rechtsberatung;
jede Liste ist eine Erinnerung fuer Marcel, der selbst entscheidet und freigibt.

Fundstellen: Paragraf 656d BGB (Faelligkeit), Paragrafen 1030, 1093, 577 BGB
(Rechte am Objekt), Paragraf 7 UWG (Anrufe), Paragrafen 536, 536a, 536b BGB und
Wohnungsvermittlungsgesetz (Vermietung), Paragraf 15 GwG (verstaerkte Sorgfalt).
"""

FEHLT = "Angabe fehlt: "


def _offen(akte: dict, punkte) -> list:
    """punkte: Liste aus (Schluessel, Text). Offen ist alles, was fehlt oder nicht True ist."""
    offen = []
    for schluessel, text in punkte:
        if schluessel not in akte or akte[schluessel] is None:
            offen.append(FEHLT + text)
        elif akte[schluessel] is not True:
            offen.append(text)
    return offen


def kaeuferanteil_faellig(nur_eine_seite_beauftragt: bool, zahlung_auftraggeber_nachgewiesen: bool) -> bool:
    """Paragraf 656d BGB: Hat nur eine Seite beauftragt, wird der uebernommene Anteil
    der anderen Seite erst faellig, wenn der Auftraggeber seine Zahlung nachgewiesen hat."""
    if not nur_eine_seite_beauftragt:
        return True
    return zahlung_auftraggeber_nachgewiesen is True


def verkaufsauftrag_objekt_offen(akte: dict) -> list:
    """Rechte und Besonderheiten am Objekt vor Annahme des Verkaufsauftrags."""
    punkte = [
        ("grundbuch_aktuell", "aktueller Grundbuchauszug liegt vor"),
        ("abteilung_1_geprueft", "Abteilung I: alle Eigentuemer und Verfuegungsberechtigung geprueft"),
        ("abteilung_2_geprueft", "Abteilung II: jedes Recht einzeln erfasst (Niessbrauch, Wohnungsrecht, Vorkaufsrecht usw.)"),
        ("abteilung_3_notiert", "Abteilung III: Grundpfandrechte notiert"),
        ("vorkenntnis_abgefragt", "Eigeninserat und andere Makler abgefragt"),
    ]
    offen = _offen(akte, punkte)
    for schluessel, text, zusatz in (
        ("ist_eigentumswohnung", "Eigentumswohnung ja/nein",
         [("teilungserklaerung_liegt_vor", "Teilungserklaerung, Hausgeld, Ruecklage, Protokolle liegen vor")]),
        ("ist_vermietet", "vermietet ja/nein",
         [("mieter_einverstanden_fotos", "Einverstaendnis des Mieters mit Fotos und Besichtigungen")]),
        ("ist_hof_oder_flaeche", "Hof/Flaeche ja/nein",
         [("pachtvertraege_abgefragt", "laufende Pachtvertraege abgefragt")]),
    ):
        if schluessel not in akte or akte[schluessel] is None:
            offen.append(FEHLT + text)
        elif akte[schluessel] is True:
            offen.extend(_offen(akte, zusatz))
    if akte.get("ist_eigentumswohnung") is True and akte.get("ist_vermietet") is True:
        offen.extend(_offen(akte, [("mietervorkaufsrecht_geprueft",
                                    "Vorkaufsrecht des Mieters geprueft (Datum der Aufteilung, Einzugsdatum)")]))
    return offen


def anruf_offen(akte: dict) -> list:
    """Vor jedem Anruf bei einer Privatperson. Leere Liste = Anruf nach dieser Pruefung zulaessig.

    Zulaessige Anlaesse: Einwilligung, Rueckrufbitte, oder (nur nach anwaltlicher
    Bestaetigung) Anfrage fuer einen dokumentierten Suchkunden ohne eigenes Angebot.
    """
    if "anlass" not in akte or akte["anlass"] is None:
        return [FEHLT + "Anlass des Anrufs (einwilligung / rueckruf / suchkunde)"]
    anlass = akte["anlass"]
    if anlass == "einwilligung":
        return _offen(akte, [("einwilligung_dokumentiert", "Einwilligung mit Datum und Wortlaut dokumentiert")])
    if anlass == "rueckruf":
        return _offen(akte, [("rueckrufbitte_dokumentiert", "Rueckrufbitte dokumentiert")])
    if anlass == "suchkunde":
        return _offen(akte, [
            ("suchauftrag_in_textform", "Suchauftrag des Kunden in Textform liegt vor"),
            ("profil_passt_zum_objekt", "Suchprofil passt zum Objekt"),
            ("kein_eigenes_angebot", "im Gespraech wird keine eigene Verkaufshilfe angeboten"),
            ("anwalt_hat_bestaetigt", "Anwalt hat diese Vorgehensweise bestaetigt"),
        ])
    return ["Kein zulaessiger Anlass - nicht anrufen"]


def vermietung_zusatz_offen(akte: dict) -> list:
    """Zusaetzliche Punkte vor einer Wohnraumvermietung."""
    if "ist_wohnraum" not in akte or akte["ist_wohnraum"] is None:
        return [FEHLT + "Wohnraum ja/nein"]
    if akte["ist_wohnraum"] is not True:
        return []
    return _offen(akte, [
        ("zusagen_belegt", "zugesicherte Eigenschaften im Angebot belegt (Flaeche, Ausstattung, Stellplatz)"),
        ("maengel_geklaert", "bekannte Maengel mit dem Eigentuemer geklaert, gesundheitsgefaehrdende nicht verschwiegen"),
        ("maengel_im_protokoll", "bekannte Maengel mit Foto im Uebergabeprotokoll"),
        ("kaution_nachgehalten", "Kautionszahlung nachgehalten"),
    ])


def geldwaesche_zusatz_offen(akte: dict) -> list:
    """Zusaetzliche Punkte zur Geldwaesche-Akte eines Kaufgeschaefts."""
    offen = _offen(akte, [
        ("bogen_verkaeufer", "eigener Dokumentationsbogen fuer den Verkaeufer"),
        ("bogen_kaeufer", "eigener Dokumentationsbogen fuer den Kaeufer"),
        ("risiko_eingestuft", "Risikoeinstufung mit Begruendung notiert"),
    ])
    if "erhoehtes_risiko" not in akte or akte["erhoehtes_risiko"] is None:
        offen.append(FEHLT + "erhoehtes Risiko ja/nein")
    elif akte["erhoehtes_risiko"] is True:
        offen.extend(_offen(akte, [("verstaerkte_pruefung_dokumentiert",
                                    "verstaerkte Sorgfaltspflichten erfuellt und dokumentiert")]))
    return offen
