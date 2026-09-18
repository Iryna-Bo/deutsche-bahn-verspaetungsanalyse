# Exploratory Data Analysis

## Ziel

Vor der eigentlichen Analyse wurde ein Teil der historischen Daten explorativ untersucht.

Ziel war es, die Struktur der Daten zu verstehen, erste Muster bei den Verspätungen zu erkennen und mögliche Probleme in den Daten früh zu identifizieren.

Für die erste Untersuchung wurde der Datensatz für **März 2025** verwendet.

## Datensatz

Der untersuchte Monatsdatensatz enthält rund **2 Millionen Datensätze** von etwa **107 Bahnhöfen**.

Die Daten enthalten unter anderem:

* Bahnhof
* Zugnummer
* Zugtyp
* geplante Ankunfts- und Abfahrtszeit
* geänderte Ankunfts- und Abfahrtszeit
* Verspätung
* Informationen zu Zugausfällen

Die Verspätung wird im Datensatz als `delay_in_min` angegeben.

## Verteilung der Verspätungen

Die Untersuchung zeigt eine deutlich rechtsschiefe Verteilung.

Für März 2025 wurden folgende Werte beobachtet:

| Kennzahl      |         Wert |
| ------------- | -----------: |
| Durchschnitt  | 3,42 Minuten |
| Median        |     1 Minute |
| 90. Perzentil |    8 Minuten |
| 95. Perzentil |   15 Minuten |
| Maximum       |  417 Minuten |

Der Median liegt deutlich unter dem Durchschnitt. Gleichzeitig gibt es einige sehr hohe Verspätungswerte, die den Durchschnitt nach oben beeinflussen.

Für die spätere Analyse sind deshalb neben dem Durchschnitt auch Median und Perzentile sinnvoll.

## Zugtypen

Im Datensatz sind viele verschiedene Zugtypen enthalten, unter anderem:

* ICE
* IC
* RE
* RB
* S
* EC
* ECE

Daneben gibt es weitere regionale und internationale Zugtypen.

Die Verteilung der Verspätungen sollte deshalb später auch nach Zugtyp untersucht werden. Dabei ist zu berücksichtigen, dass die Anzahl der Beobachtungen zwischen den Zugtypen sehr unterschiedlich sein kann.

## Bahnhöfe

Der Datensatz enthält rund 107 verschiedene Bahnhöfe.

Bahnhöfe können für die Analyse eine wichtige Rolle spielen, da Verspätungen und Störungen an großen Knotenpunkten Auswirkungen auf weitere Zugverbindungen haben können.

Für die weitere Analyse sollen deshalb unter anderem folgende Fragen untersucht werden:

* Welche Bahnhöfe haben besonders viele verspätete Züge?
* Wo treten besonders starke Verspätungen auf?
* Gibt es Unterschiede zwischen großen Knotenbahnhöfen und anderen Bahnhöfen?

## Zugausfälle

Im März-Datensatz wurden auch viele Datensätze mit Informationen zu ausgefallenen Ankünften oder Abfahrten gefunden.

Dabei ist wichtig:

Die Anzahl der Ausfall-Datensätze entspricht nicht automatisch der Anzahl der ausgefallenen Züge.

Ein Zug kann an mehreren Bahnhöfen mehrere Datensätze erzeugen. Deshalb müssen Ausfälle für die finale Analyse über geeignete Schlüssel wie Zugnummer und Fahrt-ID aggregiert werden.

## Zeitliche Analyse

Die Daten enthalten Zeitinformationen, sodass die Verspätungen später nach verschiedenen Zeitdimensionen untersucht werden können:

* Stunde
* Tageszeit
* Wochentag
* Monat
* Jahreszeit

Für die Business-Analyse ist insbesondere interessant, ob bestimmte Zeiträume mit einem höheren Verspätungsrisiko verbunden sind.

## Erste Erkenntnisse

Die explorative Untersuchung zeigt bereits einige wichtige Punkte:

1. Verspätungen sind nicht normalverteilt, sondern deutlich rechtsschief.
2. Die meisten beobachteten Verspätungen sind relativ klein, während einige wenige sehr hohe Werte auftreten.
3. Der Median ist deutlich niedriger als der Durchschnitt.
4. Für die spätere Analyse sind mehrere Verspätungsstufen sinnvoll, nicht nur ein durchschnittlicher Verspätungswert.
5. Zugtypen und Bahnhöfe sollten getrennt betrachtet werden.
6. Zugausfälle müssen auf Fahrt- oder Zug-Ebene und nicht nur anhand einzelner Datensätze analysiert werden.
7. Vor der Berechnung finaler KPIs müssen Datenqualitätsprobleme geprüft werden.

## Nächste Schritte

Auf Basis dieser ersten Untersuchung werden die Daten zunächst genauer validiert und bereinigt.

Danach folgen:

* Definition der finalen Verspätungs-KPIs
* Analyse nach Bahnhof, Zugtyp und Zeit
* Untersuchung von Verspätungswahrscheinlichkeiten
* Analyse von Zugausfällen
* Untersuchung möglicher finanzieller Auswirkungen
* Visualisierung der Ergebnisse in einem Dashboard

Die während der explorativen Analyse gefundenen Datenqualitätsprobleme werden separat dokumentiert.

→ [Data Quality Investigation](02_data_quality_investigation.md)
