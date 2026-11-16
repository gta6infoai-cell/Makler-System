"""Tests zu gebiet/entfernung.py. Start: python -m unittest tests.test_entfernung

Die Koordinaten sind BEISPIEL (Naeherungswerte zweier Ortsmitten), keine Adressen.
"""
import inspect
import unittest

from gebiet import entfernung as g

BEISPIEL_ORT_A = (52.59, 8.21)
BEISPIEL_ORT_B = (52.28, 8.05)


class Entfernung(unittest.TestCase):
    def test_luftlinie(self):
        km = g.luftlinie_km(*BEISPIEL_ORT_A, *BEISPIEL_ORT_B)
        self.assertAlmostEqual(km, 36.1, delta=0.3)
        self.assertEqual(g.luftlinie_km(*BEISPIEL_ORT_A, *BEISPIEL_ORT_A), 0.0)

    def test_zone(self):
        self.assertEqual(g.zone(44.9, g.ARBEITSRADIUS_KM), g.INNEN)
        self.assertEqual(g.zone(45.0, g.ARBEITSRADIUS_KM), g.INNEN)
        self.assertEqual(g.zone(45.1, g.ARBEITSRADIUS_KM), g.AUSNAHME)
        with self.assertRaises(ValueError):
            g.zone(10, 0)

    def test_objekt(self):
        self.assertEqual(len(g.objekt_offen({}, g.ARBEITSRADIUS_KM)), 3)
        akte = {"entfernung_km": 12.0, "bundesland": "Niedersachsen", "gutachterausschuss": "Oldenburg-Cloppenburg"}
        self.assertEqual(g.objekt_offen(akte, g.ARBEITSRADIUS_KM), [])
        akte["entfernung_km"] = 55.0
        self.assertEqual(len(g.objekt_offen(akte, g.ARBEITSRADIUS_KM)), 1)
        akte["ausnahme_vom_inhaber_bestaetigt"] = True
        self.assertEqual(g.objekt_offen(akte, g.ARBEITSRADIUS_KM), [])


class KeineVorgabewerte(unittest.TestCase):
    def test_keine_vorgabewerte(self):
        for name, funktion in inspect.getmembers(g, inspect.isfunction):
            if funktion.__module__ != g.__name__:
                continue
            for parameter in inspect.signature(funktion).parameters.values():
                self.assertIs(parameter.default, inspect.Parameter.empty, name)


if __name__ == "__main__":
    unittest.main()
