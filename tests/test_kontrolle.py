"""Tests zu kontrolle/sperren.py und kontrolle/fristen.py."""
import inspect
import unittest
from datetime import date

from kontrolle import fristen, sperren

TAG = date(2026, 11, 16)


class Sperren(unittest.TestCase):
    def test_leere_akte_ist_nie_bereit(self):
        for stufe in sperren.STUFEN:
            bild = sperren.stand(stufe, {}, TAG)
            self.assertFalse(bild["bereit"], stufe)
            self.assertTrue(bild["offen"], stufe)

    def test_spaetere_stufe_gesperrt_ohne_freigabe(self):
        bild = sperren.stand("anzeige", {}, TAG)
        self.assertEqual(bild["sperren"], ["Stufe auftrag ist noch nicht vom Inhaber freigegeben"])
        bild = sperren.stand("rechnung", {}, TAG)
        self.assertEqual(len(bild["sperren"]), 4)

    def test_freigabe_braucht_datum(self):
        self.assertFalse(sperren.freigegeben("auftrag", {"freigaben": {"auftrag": True}}))
        self.assertTrue(sperren.freigegeben("auftrag", {"freigaben": {"auftrag": TAG}}))

    def test_besichtigung_bereit(self):
        akte = {"freigaben": {"auftrag": TAG, "anzeige": TAG},
                "kaeufer": {"provisionsvereinbarung_in_textform": True, "widerrufsbelehrung_uebergeben": True,
                            "nachweisbestaetigung_vorbereitet": True, "kaeufer_ist_verbraucher": True,
                            "geplante_nutzung_in_textform": False}}
        bild = sperren.stand("besichtigung", akte, TAG)
        self.assertFalse(bild["bereit"])
        self.assertEqual(len(bild["offen"]), 1)
        akte["kaeufer"]["geplante_nutzung_in_textform"] = True
        self.assertTrue(sperren.stand("besichtigung", akte, TAG)["bereit"])

    def test_rechnung_faelligkeit(self):
        rechnung = {"maklervertrag": True, "maklertaetigkeit": True, "hauptvertrag": True, "kausalitaet": True,
                    "hauptvertrag_wirksam": True, "steuerfrage_geklaert": True,
                    "nur_eine_seite_beauftragt": True, "zahlung_auftraggeber_nachgewiesen": False}
        offen = sperren.stufe_offen("rechnung", {"rechnung": rechnung}, TAG)
        self.assertEqual(offen, ["Anteil der anderen Seite noch nicht faellig (Paragraf 656d BGB)"])
        rechnung["zahlung_auftraggeber_nachgewiesen"] = True
        self.assertEqual(sperren.stufe_offen("rechnung", {"rechnung": rechnung}, TAG), [])

    def test_unbekannte_stufe(self):
        self.assertFalse(sperren.stand("versand", {}, TAG)["bereit"])


class Fristen(unittest.TestCase):
    def test_faellige(self):
        liste = [
            {"bezeichnung": "BEISPIEL Widerrufsfrist", "faellig_am": date(2026, 11, 20), "erledigt": False},
            {"bezeichnung": "BEISPIEL Alleinauftrag endet", "faellig_am": date(2027, 3, 1), "erledigt": False},
            {"bezeichnung": "BEISPIEL ueberfaellig", "faellig_am": date(2026, 11, 10), "erledigt": False},
            {"bezeichnung": "BEISPIEL erledigt", "faellig_am": date(2026, 11, 17), "erledigt": True},
        ]
        self.assertEqual(fristen.faellige(liste, TAG, 14),
                         [(-6, "BEISPIEL ueberfaellig"), (4, "BEISPIEL Widerrufsfrist")])

    def test_unvollstaendig_steht_vorn(self):
        ergebnis = fristen.faellige([{"bezeichnung": "BEISPIEL ohne Datum", "erledigt": False}], TAG, 14)
        self.assertEqual(len(ergebnis), 1)
        self.assertIsNone(ergebnis[0][0])
        self.assertTrue(ergebnis[0][1].startswith(fristen.FEHLT))


class KeineVorgabewerte(unittest.TestCase):
    def test_keine_vorgabewerte(self):
        for modul in (sperren, fristen):
            for name, funktion in inspect.getmembers(modul, inspect.isfunction):
                for parameter in inspect.signature(funktion).parameters.values():
                    self.assertIs(parameter.default, inspect.Parameter.empty, name)


if __name__ == "__main__":
    unittest.main()
