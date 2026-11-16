"""Tests zu pruefungen/ergaenzungen.py. Start: python -m unittest tests.test_ergaenzungen"""
import inspect
import unittest

from pruefungen import ergaenzungen as e


class Faelligkeit(unittest.TestCase):
    def test_kaeuferanteil(self):
        self.assertFalse(e.kaeuferanteil_faellig(True, False))
        self.assertTrue(e.kaeuferanteil_faellig(True, True))
        self.assertTrue(e.kaeuferanteil_faellig(False, False))


class Verkaufsauftrag(unittest.TestCase):
    def test_leere_akte_meldet_alles(self):
        offen = e.verkaufsauftrag_objekt_offen({})
        self.assertEqual(len(offen), 8)
        self.assertTrue(all(zeile.startswith(e.FEHLT) for zeile in offen))

    def test_vermietete_eigentumswohnung(self):
        akte = {"grundbuch_aktuell": True, "abteilung_1_geprueft": True, "abteilung_2_geprueft": True,
                "abteilung_3_notiert": True, "vorkenntnis_abgefragt": True, "ist_eigentumswohnung": True,
                "teilungserklaerung_liegt_vor": True, "ist_vermietet": True,
                "mieter_einverstanden_fotos": True, "ist_hof_oder_flaeche": False}
        offen = e.verkaufsauftrag_objekt_offen(akte)
        self.assertEqual(len(offen), 1)
        self.assertIn("Vorkaufsrecht des Mieters", offen[0])
        akte["mietervorkaufsrecht_geprueft"] = True
        self.assertEqual(e.verkaufsauftrag_objekt_offen(akte), [])


class Anruf(unittest.TestCase):
    def test_ohne_anlass(self):
        self.assertTrue(e.anruf_offen({})[0].startswith(e.FEHLT))
        self.assertEqual(e.anruf_offen({"anlass": "kaltakquise"}), ["Kein zulaessiger Anlass - nicht anrufen"])

    def test_einwilligung(self):
        self.assertEqual(e.anruf_offen({"anlass": "einwilligung", "einwilligung_dokumentiert": True}), [])
        self.assertEqual(len(e.anruf_offen({"anlass": "einwilligung", "einwilligung_dokumentiert": False})), 1)

    def test_suchkunde_braucht_anwalt(self):
        akte = {"anlass": "suchkunde", "suchauftrag_in_textform": True, "profil_passt_zum_objekt": True,
                "kein_eigenes_angebot": True, "anwalt_hat_bestaetigt": False}
        self.assertEqual(len(e.anruf_offen(akte)), 1)
        akte["anwalt_hat_bestaetigt"] = True
        self.assertEqual(e.anruf_offen(akte), [])


class VermietungUndGeldwaesche(unittest.TestCase):
    def test_wohnraum_schalter(self):
        self.assertTrue(e.vermietung_zusatz_offen({})[0].startswith(e.FEHLT))
        self.assertEqual(e.vermietung_zusatz_offen({"ist_wohnraum": False}), [])
        self.assertEqual(len(e.vermietung_zusatz_offen({"ist_wohnraum": True})), 4)

    def test_geldwaesche(self):
        akte = {"bogen_verkaeufer": True, "bogen_kaeufer": True, "risiko_eingestuft": True, "erhoehtes_risiko": True}
        self.assertEqual(len(e.geldwaesche_zusatz_offen(akte)), 1)
        akte["verstaerkte_pruefung_dokumentiert"] = True
        self.assertEqual(e.geldwaesche_zusatz_offen(akte), [])
        self.assertEqual(len(e.geldwaesche_zusatz_offen({})), 4)


class RechtsCheckNovember2026(unittest.TestCase):
    def test_online_abschluss(self):
        self.assertTrue(e.online_abschluss_offen({})[0].startswith(e.FEHLT))
        self.assertEqual(e.online_abschluss_offen({"vertrag_per_klick": False}), [])
        self.assertEqual(len(e.online_abschluss_offen({"vertrag_per_klick": True})), 3)
        akte = {"vertrag_per_klick": True, "schaltflaeche_zahlungspflicht": True,
                "widerrufsfunktion_vorhanden": True, "anwalt_hat_strecke_freigegeben": False}
        self.assertEqual(e.online_abschluss_offen(akte), ["Anwalt hat die Online-Strecke freigegeben"])

    def test_kaeufernutzung(self):
        self.assertTrue(e.kaeufernutzung_offen({})[0].startswith(e.FEHLT))
        self.assertEqual(e.kaeufernutzung_offen({"kaeufer_ist_verbraucher": False}), [])
        self.assertEqual(len(e.kaeufernutzung_offen({"kaeufer_ist_verbraucher": True})), 1)
        self.assertEqual(e.kaeufernutzung_offen({"kaeufer_ist_verbraucher": True,
                                                 "geplante_nutzung_in_textform": True}), [])


class KeineVorgabewerte(unittest.TestCase):
    def test_keine_vorgabewerte(self):
        for name, funktion in inspect.getmembers(e, inspect.isfunction):
            for parameter in inspect.signature(funktion).parameters.values():
                self.assertIs(parameter.default, inspect.Parameter.empty, name)


if __name__ == "__main__":
    unittest.main()
