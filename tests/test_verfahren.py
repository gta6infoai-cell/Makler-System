"""Tests zu bewertung/verfahren.py. Start im Hauptordner: python -m unittest tests.test_verfahren

ALLE ZAHLEN HIER SIND BEISPIEL: Uebungsaufgaben aus dem Seminar (Uebungsort in
Baden-Wuerttemberg, alter Marktbericht). Sie pruefen nur den Rechenweg und
duerfen nie in eine echte Preiseinschaetzung einfliessen.
"""
import inspect
import unittest

from bewertung import verfahren as v

# BEISPIEL - Kostenkennwerte eines Gebaeudetyps aus der Uebung, Euro je qm, Preisstand 2010
BEISPIEL_KENNWERTE = {1: 655, 2: 725, 3: 835, 4: 1005, 5: 1260}
BEISPIEL_WAEGUNG = {"Aussenwaende": 23, "Dach": 15, "Fenster": 11, "Innenwaende": 11,
                    "Decken": 11, "Fussboeden": 5, "Sanitaer": 9, "Heizung": 9, "Technik": 6}
BEISPIEL_ANTEILE = {"Aussenwaende": {3: 1}, "Dach": {3: 1}, "Fenster": {2: 0.6, 3: 0.2, 4: 0.2},
                    "Innenwaende": {3: 1}, "Decken": {3: 1}, "Fussboeden": {2: 0.4, 4: 0.6},
                    "Sanitaer": {3: 1}, "Heizung": {3: 1}, "Technik": {3: 1}}


class Bodenwert(unittest.TestCase):
    def test_uebung_folie(self):
        ausnutzung = v.anpassungsfaktor(0.685, 0.865, 3)
        groesse = v.anpassungsfaktor(85.0, 97.0, 3)
        self.assertEqual((ausnutzung, groesse), (0.792, 0.876))
        ergebnis = v.bodenwert(1000, 450, [("Ausnutzung", ausnutzung), ("Groesse", groesse)])
        self.assertEqual(ergebnis["schritte"][0][1], 450000.0)
        self.assertEqual(ergebnis["schritte"][1][1], 356400.0)
        self.assertEqual(ergebnis["bodenwert"], 312206.4)

    def test_uebung_notizbuch_1(self):
        self.assertEqual(v.wgfz(400, 800), 0.5)
        ausnutzung = v.anpassungsfaktor(0.820, 0.775, 3)
        groesse = v.anpassungsfaktor(91.0, 103.0, 3)
        self.assertEqual((ausnutzung, groesse), (1.058, 0.883))
        ergebnis = v.bodenwert(800, 340, [("Ausnutzung", ausnutzung), ("Groesse", groesse)])
        self.assertEqual(ergebnis["schritte"][1][1], 287776.0)
        self.assertEqual(ergebnis["bodenwert"], 254106.21)

    def test_uebung_notizbuch_2(self):
        self.assertEqual(v.wgfz(750, 500), 1.5)
        ausnutzung = v.anpassungsfaktor(1.100, 0.945, 3)
        groesse = v.anpassungsfaktor(100.0, 91.0, 3)
        self.assertEqual((ausnutzung, groesse), (1.164, 1.099))
        ergebnis = v.bodenwert(500, 180, [("Ausnutzung", ausnutzung), ("Groesse", groesse)])
        self.assertEqual(ergebnis["schritte"][1][1], 104760.0)
        self.assertEqual(ergebnis["bodenwert"], 115131.24)

    def test_fehlende_angaben(self):
        with self.assertRaises(ValueError):
            v.bodenwert(0, 450, [])
        with self.assertRaises(ValueError):
            v.anpassungsfaktor(0.8, 0, 3)


class Nutzungsdauer(unittest.TestCase):
    def test_kernsanierung(self):
        self.assertEqual(v.fiktives_baujahr_kernsanierung(1990, 80), 1982)
        self.assertEqual(v.alter(2026, 1982), 44)

    def test_anbau(self):
        self.assertEqual(v.restnutzungsdauer_gewichtet([(30, 180), (58, 80)]), 38.62)

    def test_alterswertminderung(self):
        self.assertEqual(v.alterswertminderung_prozent(44, 80), 55.0)
        self.assertEqual(v.alterswertminderung_prozent(124, 80), 100.0)
        self.assertEqual(v.restnutzungsdauer(80, 124), 0.0)


class Sachwert(unittest.TestCase):
    def test_kostenkennwert(self):
        self.assertEqual(v.gewogener_kostenkennwert(BEISPIEL_KENNWERTE, BEISPIEL_WAEGUNG, BEISPIEL_ANTEILE), 834.38)

    def test_kostenkennwert_fehlt(self):
        anteile = dict(BEISPIEL_ANTEILE)
        del anteile["Dach"]
        with self.assertRaises(ValueError):
            v.gewogener_kostenkennwert(BEISPIEL_KENNWERTE, BEISPIEL_WAEGUNG, anteile)

    def test_aufgabe_5(self):
        faktor = v.baupreisfaktor(141.7, 70.8)
        self.assertEqual(faktor, 200.14)
        ergebnis = v.sachwert_vorlaeufig(834.38, 420, 1.21, faktor, 44, 80, 0.0, 130000.0)
        self.assertEqual(ergebnis["herstellungskosten_basisjahr"], 350439.6)
        self.assertEqual(ergebnis["herstellungskosten_regional"], 424031.92)
        self.assertEqual(ergebnis["herstellungskosten_stichtag"], 848657.48)
        self.assertEqual(ergebnis["alterswertminderung"], 466761.61)
        self.assertEqual(ergebnis["gebaeudewert"], 381895.87)
        self.assertEqual(ergebnis["sachwert_vorlaeufig"], 511895.87)
        self.assertIn("vorlaeufig", ergebnis["hinweis"])


class Ertragswert(unittest.TestCase):
    def test_uebung(self):
        ergebnis = v.ertragswert_allgemein(18000, 100000, 4.5, 40)
        self.assertEqual(ergebnis["bodenwertverzinsung"], 4500.0)
        self.assertEqual(ergebnis["reinertrag_gebaeude"], 13500.0)
        self.assertEqual(ergebnis["barwertfaktor"], 18.4016)
        self.assertAlmostEqual(ergebnis["ertragswert_vorlaeufig"], 348421.60, delta=0.5)

    def test_allgemein_gleich_vereinfacht(self):
        allgemein = v.ertragswert_allgemein(18000, 100000, 4.5, 40)["ertragswert_vorlaeufig"]
        self.assertAlmostEqual(allgemein, v.ertragswert_vereinfacht(18000, 100000, 4.5, 40), delta=0.02)


class KeineVorgabewerte(unittest.TestCase):
    def test_keine_vorgabewerte(self):
        for name, funktion in inspect.getmembers(v, inspect.isfunction):
            for parameter in inspect.signature(funktion).parameters.values():
                self.assertIs(parameter.default, inspect.Parameter.empty, name)


if __name__ == "__main__":
    unittest.main()
