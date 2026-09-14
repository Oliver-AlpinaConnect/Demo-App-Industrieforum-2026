"""Dienste: holen Daten aus der Datenbank, rufen die reinen Regeln auf, geben Sichten zurück.

Die Regeln in `app/regeln/` kennen keine Datenbank. Diese Schicht ist die Brücke: sie
lädt Zeilen, baut Werttypen, ruft die Regelfunktionen in der richtigen Reihenfolge auf
und liefert fertige Sichten an die Router.
"""
