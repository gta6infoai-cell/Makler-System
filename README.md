# Makler-System

Bausteine fuer den Maklerbetrieb von Marcel Stremel (Steinfeld in Oldenburg, Niedersachsen).
Das System bereitet vor und prueft; freigegeben wird alles von Marcel selbst.
Keine Rechts- oder Steuerberatung. Stand: 16.11.2026.

## Grundregeln
- Keine Funktion hat Vorgabewerte. Fehlt eine Angabe, meldet die Funktion "Angabe fehlt: ...".
- Beispiele heissen BEISPIEL und stehen nur in den Tests; sie fliessen nie in echte Rechnungen.
- Gesetzliche Werte stehen als Konstanten mit Fundstelle im Code.
- Nicht ins Repository: Kundendaten, Belege, Adressen, Seminarunterlagen, Zugangsdaten.

## Inhalt
| Ordner | Datei | Zweck |
| --- | --- | --- |
| pruefungen | provision.py | Provision, Halbteilung, Checkliste Notartermin |
| pruefungen | pruefpunkte.py | Anzeige, Widerruf, Vermietung, Geldwaesche |
| pruefungen | ergaenzungen.py | Faelligkeit nach Paragraf 656d BGB, Grundbuch und Rechte am Objekt, Anruf erlaubt ja oder nein, Vermietung, Geldwaesche-Zusatz, Online-Abschluss (Bestellbutton), geplante Nutzung des Kaeufers |
| bewertung | verfahren.py | Rechenwege nach ImmoWertV: Bodenwert, Sachwert, Ertragswert, Restnutzungsdauer |
| bewertung | wert.py | aelterer Beispiel-Baustein, wird durch verfahren.py abgeloest |
| gebiet | entfernung.py | Arbeitsgebiet: 45 km Luftlinie um den Betriebssitz |
| finanzen | finanzen.py | Ruecklage je Provision, Kostenblatt je Objekt |
| tests | test_*.py | 53 Tests, darunter die Seminaraufgaben als BEISPIEL-Testfaelle |

## Tests starten
Im Hauptordner:

    python -m unittest tests.test_bausteine tests.test_pruefpunkte tests.test_verfahren tests.test_ergaenzungen tests.test_entfernung

Die Tests laufen ausserdem bei jeder Aenderung automatisch (Reiter "Actions").

## Wichtig zur Wertermittlung
Die Ergebnisse sind Marktpreiseinschaetzungen, keine Verkehrswertgutachten. Ohne die Daten des
zustaendigen Gutachterausschusses (Sachwertfaktor, Liegenschaftszinssatz, Umrechnungskoeffizienten)
ist jedes Ergebnis nur vorlaeufig.

## Offen
- Restnutzungsdauer nach Modernisierungspunkten und Tabelle der Kostenkennwerte (Werte aus dem Gesetzestext uebernehmen)
- Rechenbaustein am niedersaechsischen Sachwertmodell ausrichten
- Marktdaten fuer den Landkreis Vechta als Datentabelle
