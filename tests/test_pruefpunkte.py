"""Tests zu den Pruefpunkten. Start im Hauptordner: python -m unittest tests.test_pruefpunkte

Alle Akten in diesen Tests sind BEISPIELE und haben nichts mit echten Faellen zu tun.
"""
import unittest
from datetime import date

from pruefungen.pruefpunkte import (FEHLT, anzeige_offen, geldwaesche_offen, gwg_pflicht_bei_miete,
                                    hoechstprovision_mieter, vermietung_offen, widerruf_offen)

BEISPIEL_UST_SATZ = 0.19

BEISPIEL_ANZEIGE = {
    "auftrag_liegt_vor": True, "flaeche_belegt": True, "preis_gesamt_inkl_ust": True,
    "bildrechte_geklaert": True, "aussagen_belegt": True, "energieausweis_vorhanden": True,
    "energieausweis_art": "Bedarf", "energietraeger": "Gas", "baujahr": 1998,
    "effizienzklasse": "D", "endenergiewert": 120.0, "vermietung": False,
}


class Anzeige(unittest.TestCase):
    def test_vollstaendig_2026(self):
        self.assertEqual(anzeige_offen(BEISPIEL_ANZEIGE, date(2026, 12, 1)), [])

    def test_ab_2027_neue_angaben(self):
        offen = anzeige_offen(BEISPIEL_ANZEIGE, date(2027, 1, 1))
        self.assertEqual(len(offen), 2)
        self.assertTrue(all(o.startswith(FEHLT) for o in offen))

    def test_leere_akte_nimmt_nichts_an(self):
        offen = anzeige_offen({}, date(2026, 12, 1))
        self.assertEqual(len(offen), 7)
        self.assertTrue(all(o.startswith(FEHLT) for o in offen))

    def test_mietanzeige_braucht_vermittlerangaben(self):
        akte = dict(BEISPIEL_ANZEIGE, vermietung=True)
        self.assertEqual(len(anzeige_offen(akte, date(2026, 12, 1))), 4)

    def test_stichtag_ist_pflicht(self):
        with self.assertRaises(TypeError):
            anzeige_offen(BEISPIEL_ANZEIGE)


class Widerruf(unittest.TestCase):
    def test_kein_verbraucher(self):
        self.assertEqual(widerruf_offen({"verbraucher": False, "vertragsort": "ausserhalb"}), [])

    def test_ausserhalb_mit_vorzeitigem_beginn(self):
        akte = {"verbraucher": True, "vertragsort": "ausserhalb", "belehrung_ausgehaendigt": True,
                "formular_beigefuegt": True, "vorzeitiger_beginn": True,
                "zustimmung_ausdruecklich": True, "kenntnis_bestaetigt": True}
        offen = widerruf_offen(akte)
        self.assertEqual(len(offen), 1)
        self.assertIn("dauerhaftem Datentraeger", offen[0])

    def test_online_braucht_widerrufsfunktion(self):
        akte = {"verbraucher": True, "vertragsort": "online", "belehrung_ausgehaendigt": True,
                "formular_beigefuegt": True, "vorzeitiger_beginn": False}
        self.assertEqual(len(widerruf_offen(akte)), 3)

    def test_fehlende_grundangabe(self):
        self.assertTrue(widerruf_offen({})[0].startswith(FEHLT))


class Vermietung(unittest.TestCase):
    def test_hoechstprovision(self):
        self.assertEqual(hoechstprovision_mieter(800.0, BEISPIEL_UST_SATZ), 1904.0)
        with self.assertRaises(TypeError):
            hoechstprovision_mieter(800.0)

    def test_mieterprovision_zu_hoch(self):
        akte = {"auftrag_vermieter_textform": True, "keine_verflechtung": True,
                "keine_zusatzgebuehren": True, "mietpreisbremse_geprueft": True, "zahler": "mieter",
                "suchauftrag_textform": True, "ausschliesslich_fuer_suchenden": True,
                "provision_brutto": 2000.0, "nettokaltmiete": 800.0, "ust_satz": BEISPIEL_UST_SATZ}
        self.assertEqual(len(vermietung_offen(akte)), 1)
        akte["provision_brutto"] = 1904.0
        self.assertEqual(vermietung_offen(akte), [])

    def test_mietpreisbremse(self):
        akte = {"auftrag_vermieter_textform": True, "keine_verflechtung": True,
                "keine_zusatzgebuehren": True, "mietpreisbremse_geprueft": True, "zahler": "vermieter",
                "mietpreisbremse_gilt": True, "nettokaltmiete": 900.0, "vergleichsmiete": 800.0,
                "ausnahme_mietpreisbremse": False}
        self.assertEqual(len(vermietung_offen(akte)), 1)
        akte["nettokaltmiete"] = 880.0
        self.assertEqual(vermietung_offen(akte), [])


class Geldwaesche(unittest.TestCase):
    def test_schwelle_miete(self):
        self.assertFalse(gwg_pflicht_bei_miete(9999.99))
        self.assertTrue(gwg_pflicht_bei_miete(10000.0))

    def test_identifizierung_bei_ernsthaftem_interesse(self):
        akte = {"goaml_registriert": True, "risikoanalyse_vorhanden": True,
                "hinweis_barzahlungsverbot": True, "ernsthaftes_kaufinteresse": True,
                "verkaeufer_identifiziert": True, "kaeufer_identifiziert": False,
                "wirtschaftlich_berechtigter_geklaert": True}
        self.assertEqual(geldwaesche_offen(akte), ["Kaeufer identifiziert und dokumentiert"])

    def test_auffaelligkeit_wird_gemeldet(self):
        akte = {"goaml_registriert": True, "risikoanalyse_vorhanden": True,
                "hinweis_barzahlungsverbot": True, "ernsthaftes_kaufinteresse": False,
                "auffaelligkeit": True}
        self.assertEqual(len(geldwaesche_offen(akte)), 1)


if __name__ == "__main__":
    unittest.main()
