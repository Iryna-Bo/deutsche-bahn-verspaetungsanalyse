# Deutsche Bahn – Verspätungsanalyse

## Projektüberblick

Dieses Portfolio-Projekt untersucht Zugverspätungen und Zugausfälle in Deutschland.

Ziel ist es, Muster und Unterschiede nach Bahnhof, Zugtyp, Tageszeit und Zeitraum zu analysieren. Zusätzlich soll untersucht werden, welche möglichen finanziellen Auswirkungen häufige und starke Verspätungen haben können.

Das Projekt verbindet historische Daten mit aktuellen Daten aus der offiziellen Deutsche Bahn API.

## Business Questions

* Wie unterscheiden sich Zugverspätungen nach Bahnhof und Zugtyp?
* Zu welchen Tageszeiten und an welchen Wochentagen treten häufiger Verspätungen auf?
* Wie häufig kommt es zu starken Verspätungen und Zugausfällen?
* Welche Bahnhöfe oder Zugtypen zeigen besonders hohe Verspätungsrisiken?
* Wie kann das finanzielle Risiko auf Basis transparenter Annahmen geschätzt werden?

## Datenquellen

### Historische Daten

Für die historische Analyse wird der Datensatz **Deutsche Bahn Data** von `piebro` auf Hugging Face verwendet.

Die Daten basieren auf öffentlichen Deutsche-Bahn-APIs und enthalten unter anderem:

* Bahnhof
* Zugnummer und Zugtyp
* geplante und geänderte Ankunfts- und Abfahrtszeiten
* Verspätung
* Informationen zu Zugausfällen

Für die erste historische Analyse werden Daten aus dem Zeitraum **Januar bis Oktober 2025** verwendet.

Die Rohdaten werden aufgrund ihrer Größe nicht im GitHub-Repository gespeichert.

### Aktuelle Daten

Zusätzlich werden aktuelle Daten über die offizielle **Deutsche Bahn Timetables API** gesammelt.

Der API-Teil dient vor allem dazu, eine kleine Datenpipeline zu zeigen:

**API → XML → Python → Validierung → Parquet → SQL-Analyse**

Ein erster Testlauf wurde bereits mit sechs Bahnhöfen und vier Snapshots über etwa 30 Minuten durchgeführt.

## Exploratory Data Analysis

Vor der eigentlichen Analyse wurde eine explorative Untersuchung der historischen Daten durchgeführt.

Dabei wurden unter anderem Datenverteilung, Verspätungen, Zugtypen, Bahnhöfe und mögliche Datenqualitätsprobleme untersucht.

Die wichtigsten Ergebnisse sind dokumentiert in:

[Exploratory Data Analysis](docs/01_exploratory_data_analysis.md)

## Data Quality

Während der explorativen Analyse wurden unter anderem sehr große negative Werte bei `delay_in_min` sowie fehlende geplante Zeiten gefunden.

Diese Punkte werden vor der Berechnung der finalen KPIs berücksichtigt.

Details:

[Data Quality Investigation](docs/02_data_quality_investigation.md)

## Geplante Analyse

Im weiteren Projektverlauf werden folgende Bereiche ergänzt:

* Datenbereinigung und Validierung
* SQL-basierte Analyse
* Verspätungs-KPIs
* Analyse nach Bahnhof, Zugtyp, Tageszeit und Zeitraum
* Wahrscheinlichkeit verschiedener Verspätungsstufen
* Analyse von Zugausfällen
* geschätzte finanzielle Auswirkungen
* Dashboard
* Business Insights und Handlungsempfehlungen

## Tech Stack

* Python
* Pandas
* DuckDB
* SQL
* XML / REST API
* Parquet
* Power BI / Tableau
* Git & GitHub

## Projektstruktur

```text
deutsche-bahn-verspaetungsanalyse/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│   ├── 01_exploratory_data_analysis.md
│   └── 02_data_quality_investigation.md
│
├── notebooks/
│
├── src/
│   └── collect_db_data.py
│
├── sql/
│
├── dashboard/
│
├── README.md
└── .gitignore
```

## Aktueller Projektstatus

Das Projekt befindet sich in der Entwicklungsphase.

Die Datenquellen wurden ausgewählt, die historische Datenstruktur wurde untersucht und eine erste API-Datensammlung wurde erfolgreich getestet.

Die nächsten Schritte sind die reproduzierbare Aufbereitung der historischen Daten und die eigentliche Analyse.
