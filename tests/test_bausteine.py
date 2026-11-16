"""Tests zu den Beispiel-Bausteinen. Start im Hauptordner: python -m unittest tests.test_bausteine"""
import unittest
from datetime import date

from bewertung.wert import BEISPIEL_OBJEKT, bodenwert, gebaeudewert, sachwert
from finanzen.finanzen import Kostenblatt, ruecklage
from pruefungen.provision import fehlende_voraussetzungen, halbteilung_ok, notartermin_checkliste


class Bewertung(unittest.TestCase):
    def test_bodenwert(self):
        self.assertEqual(bodenwert(BEISPIEL_OBJEKT), 225000.0)

    def test_gebaeudewert(self):
        self.assertEqual(gebaeudewert(BEISPIEL_OBJEKT), 165000.0)

    def test_sachwert(self):
        self.assertEqual(sachwert(BEISPIEL_OBJEKT), 438075.0)


class Finanzen(unittest.TestCase):
    def test_ruecklage(self):
        r = ruecklage(17850.00)
        self.assertEqual(r["netto"], 15000.0)
        self.assertEqual(r["umsatzsteuer"], 2850.0)
        self.assertEqual(r["steuerruecklage"], 4500.0)
        self.assertEqual(r["frei_verfuegbar"], 10500.0)

    def test_ruecklage_ohne_ust(self):
        self.assertEqual(ruecklage(10000, ust_pflichtig=False)["umsatzsteuer"], 0)

    def test_kostenblatt_warnungen(self):
        k = Kostenblatt("Beispielobjekt", date(2026, 1, 15))
        k.buchen(date(2026, 2, 1), "Fotograf", 800)
        self.assertEqual(k.warnungen(date(2026, 3, 1)), [])
        k.buchen(date(2026, 6, 1), "Anzeigen", 4500)
        self.assertEqual(len(k.warnungen(date(2026, 8, 1))), 3)


class Provision(unittest.TestCase):
    def test_voraussetzungen(self):
        self.assertEqual(fehlende_voraussetzungen({"maklervertrag": True}),
                         ["maklertaetigkeit", "hauptvertrag", "kausalitaet"])

    def test_halbteilung(self):
        self.assertTrue(halbteilung_ok(3.57, 3.57, True, True))
        self.assertFalse(halbteilung_ok(2.57, 3.57, True, True))
        self.assertTrue(halbteilung_ok(2.0, 5.0, False, True))

    def test_checkliste_leer_wenn_alles_erfuellt(self):
        akte = dict.fromkeys(["maklervertrag", "maklertaetigkeit", "hauptvertrag", "kausalitaet",
                              "textform", "widerrufsbelehrung", "nachweisbestaetigung",
                              "doppeltaetigkeit_offengelegt", "gwg_identifizierung", "energieausweis"], True)
        akte.update(satz_verkaeufer=3.57, satz_kaeufer=3.57)
        self.assertEqual(notartermin_checkliste(akte), [])


if __name__ == "__main__":
    unittest.main()
