# Makler-System

Privates Repository für die technischen Bausteine des Makler-Betriebs von Marcel Stremel.
Ziel: Verwaltung und Vorbereitung laufen automatisch, damit mehr Zeit für persönliche Akquise bleibt.

Stand: 16.11.2026 – Gründungsphase, noch kein Code.

## Grundsätze

1. Das System bereitet vor, der Makler gibt frei. Preise, Flächen, Verträge, Rechnungen und jede Geldwäsche-Bewertung brauchen eine menschliche Freigabe.
2. Ein CRM ist die einzige Quelle für Kunden- und Objektdaten. Dieses Repository enthält nur Logik, keine Daten.
3. Automatisiert wird, was mindestens ein paar Mal von Hand gelaufen ist.
4. So wenige Werkzeuge und Anbieter wie möglich.

## Was hier NICHT hineingehört

- Kundendaten, Ausweise, Verträge, Belege, Kontoauszüge
- Seminarskripte, Audios, Transkripte (urheberrechtlich geschützt)
- Passwörter, API-Schlüssel, Zugangsdaten

## Geplante Struktur

    makler-system/
    ├── README.md      diese Datei (Überblick und Entscheidungen)
    ├── bewertung/     Wertermittlung: Bodenwert, Sachwert, Ertragswert, Vergleichswert
    ├── finanzen/      Rücklagenrechner, Kostenblatt je Objekt, Monatsabschluss, Belegprüfung
    ├── vorlagen/      Generatoren, die Verträge und Formulare vorbefüllen
    ├── ablaeufe/      Automatisierungen: Lead-Eingang, Unterlagen-Erinnerung, Besichtigung, Notartermin
    ├── pruefungen/    Pflichtangaben-Check für Anzeigen, Checkliste vor Notartermin, Geldwäsche-Akte
    └── tests/         Tests zu allen Rechen- und Prüfregeln

Die Ordner entstehen erst mit dem jeweiligen ersten Baustein.

## Geplante Bausteine (Reihenfolge)

| Nr. | Baustein | Ordner | Status |
| --- | --- | --- | --- |
| 1 | Bewertungsblatt (Bodenwert = Fläche × Bodenrichtwert, dann Gebäude) | bewertung/ | offen |
| 2 | Kostenblatt je Objekt mit Budget- und Fristwarnung | finanzen/ | offen |
| 3 | Rücklagenrechner je Provisionseingang | finanzen/ | offen |
| 4 | Checkliste vor Notartermin (vier Provisionsvoraussetzungen) | pruefungen/ | offen |
| 5 | Pflichtangaben-Check für Anzeigen (Energieangaben, Impressum, Endpreis) | pruefungen/ | offen |
| 6 | Vorbefüllung Alleinauftrag, Widerrufsbelehrung, Nachweisbestätigung, Interessentenliste | vorlagen/ | offen |
| 7 | Ablauf Objektaufnahme bis Exposé-Freigabe | ablaeufe/ | offen |
| 8 | Monatsabschluss Belege und Übergabepaket Steuerberater | finanzen/ | offen |

## Fachregeln, die der Code abbilden muss

Quelle: Seminarunterlagen und Mitschnitte. Rechtlich nicht geprüft; vor Einsatz anwaltlich bzw. mit Steuerberater bestätigen.

### Provision
- Vier Voraussetzungen: Maklervertrag, Maklertätigkeit, Hauptvertrag, Kausalität. Fehlt eine, keine Provision.
- Wohnung oder Einfamilienhaus mit Verbraucher als Käufer: Textform und Halbteilung. Ändert sich die Provision einer Seite, muss die andere sofort angepasst werden.
- Doppeltätigkeit muss in beiden Verträgen offengelegt sein.
- Gegenüber Verbrauchern immer Endpreis inklusive Umsatzsteuer.

### Nachweis
- Nachweisbestätigung nach der ersten Besichtigung, mit Wortlaut „erstmals nachgewiesen und besichtigt".
- Interessentenliste des Verkäufers als Anhang zum Alleinauftrag.
- Alle Anwesenden einer Besichtigung erfassen.

### Alleinauftrag
- Laufzeit sechs Monate, Wiedervorlage vier Wochen vor Ende.
- Alle Eigentümer bzw. Erben als Vertragspartei.
- Aufwendungsersatz vorab festlegen: pauschal oder auf Nachweis. Arbeitszeit bei Verbrauchern nicht abrechenbar.

### Kosten und Zeit
- Je Objekt Budget und Frist; Warnung bei Überschreitung.
- Zeiterfassung nach ABC: A = Akquise und Verhandlung, B = Verwaltung, C = Leerlauf.

### Werbung
- Energie-Pflichtangaben in jeder Anzeige: Ausweisart, Kennwert, Energieträger, Baujahr, Effizienzklasse.
- Impressum nach Digitale-Dienste-Gesetz.
- Nur eigene oder lizenzierte Bilder.

### Geldwäsche
- Je Jahr eine Akte: Risikoanalyse, dann je Geschäft Dokumentationsbogen und Ausweise von Verkäufer und Käufer.
- Verdachtsmeldung über goAML; Bewertung trifft immer der Makler.

### Aufbewahrung
- Auftragsunterlagen nach MaBV fünf Jahre, steuerliche Belege länger.

## Offene Entscheidungen

- Standort der Gewerbeanmeldung
- Eigenständig oder unter dem Dach eines Büros
- Nur Verkauf oder auch Vermietung; Bauträger als Zielgruppe
- Rechtsform und Steuerberater
- CRM-System
- Programmiersprache der Bausteine (Vorschlag: Python)

## Änderungsverlauf

- 16.11.2026: Repository angelegt, README mit Grundsätzen, Struktur und Fachregeln.
