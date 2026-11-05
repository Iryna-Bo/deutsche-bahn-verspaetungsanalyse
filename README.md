# Deutsche Bahn – Verspätungsanalyse

## Projektüberblick

Dieses Portfolio-Projekt untersucht Zugverspätungen und Zugausfälle in Deutschland auf Basis historischer Daten und aktueller Informationen der Deutschen Bahn.

Ziel ist es, zeitliche und räumliche Muster zu erkennen, Unterschiede zwischen Zugtypen und Bahnhöfen zu untersuchen.  

Das Projekt verbindet Datenanalyse, statistische Methoden, SQL, Python, Datenvisualisierung und den Aufbau einer automatisierten Datenerhebung.  

## Fragen

- Wie unterscheiden sich Verspätungen und Zugausfälle nach Bahnhof und Zugtyp?
- Zu welchen Tageszeiten und an welchen Wochentagen treten Verspätungen häufiger auf?
- Wie häufig kommt es zu kurzen, mittleren und starken Verspätungen?
- Welche Bahnhöfe und Zugtypen weisen besonders hohe Verspätungswerte auf?
- Wie verändern sich Verspätungen und Ausfälle im Zeitverlauf?  
- Welche möglichen finanziellen Auswirkungen lassen sich anhand transparenter Annahmen abschätzen?


## Datenquellen

### Historische Daten

Für die historische Analyse wird der Datensatz [Deutsche Bahn Data](https://huggingface.co/datasets/piebro/deutsche-bahn-data) von `piebro` auf Hugging Face verwendet.

Die Daten basieren auf Informationen der Deutschen Bahn und enthalten unter anderem:

- Bahnhöfe und Zugnummern
- Zugtypen
- geplante und tatsächliche bzw. geänderte Ankunfts- und Abfahrtszeiten
- Verspätungen
- Zugausfälle und Ersatzverkehr

Die historische Analyse umfasst verschiedene Zeiträume aus den Jahren 2024 bis 2026. Für einzelne Analysen werden festgelegte Zeiträume und Bahnhofskohorten verwendet.

Die Rohdaten werden aufgrund ihres Umfangs nicht im GitHub-Repository gespeichert. Die Analysen werden mit DuckDB direkt auf den bereitgestellten Parquet-Dateien durchgeführt.

### Aktuelle Daten – Deutsche Bahn API

Zusätzlich werden aktuelle Fahrplaninformationen über die offizielle **Deutsche Bahn Timetables API** gesammelt.

Die Datenerhebung umfasst sechs ausgewählte Bahnhöfe:

- Frankfurt (Main) Hbf
- Mannheim Hbf
- Stuttgart Hbf
- Köln Hbf
- Hamburg Hbf
- Berlin Hbf

Die Erfassung erfolgt automatisiert alle zehn Minuten über **cron-job.org und GitHub Actions**. Die Daten werden als zeitgestempelte Parquet-Dateien gespeichert.

**Datenpipeline:**

`Deutsche Bahn API → XML → Python → Validierung → Parquet → DuckDB / SQL → Analyse → Power BI`

Die API-Analyse untersucht sowohl die Qualität und Abdeckung der gesammelten Momentaufnahmen als auch die zeitliche Entwicklung beobachteter Zugereignisse.

## Analysen und Ergebnisse

### Explorative Datenanalyse (EDA)

Die erste Untersuchung diente dazu, die Datenstruktur, Verteilungen und mögliche Datenqualitätsprobleme kennenzulernen.

[Dokumentation: Exploratory Data Analysis](docs/01_exploratory_data_analysis.md)

### Datenqualität und Datenstruktur

Die historischen Daten wurden auf Vollständigkeit, Plausibilität und strukturelle Besonderheiten untersucht. Dabei wurden unter anderem fehlende geplante Zeiten und auffällige Verspätungswerte identifiziert.

- [Data Quality Investigation](docs/02_data_quality_investigation.md)
- [Data Structure Investigation](docs/03_data_structure_investigation.md)

### KPI-Analyse

Die Verspätungs- und Ausfallkennzahlen wurden nach verschiedenen Dimensionen untersucht:

- Bahnhof
- Zugtyp
- Tageszeit
- Wochentag
- Monat und Zeitraum

Die Analysen umfassen unter anderem Verspätungsschwellen, Verteilungen, Ausfallquoten und Ersatzverkehr.

- [KPI-Analyse](docs/04_kpi_analysis.md)
- [Historischer Zeitraumvergleich](docs/05_historical_comparison.md)

### Statistische Analyse

Mit Python, SciPy und Statsmodels wurden Unterschiede zwischen Zugtypen statistisch untersucht.

Die Analyse umfasst deskriptive Statistiken, statistische Tests, Effektstärken, Konfidenzintervalle und Post-hoc-Vergleiche.

- [Dokumentation der statistischen Analyse](docs/06_statistical_analysis.md)
- [Python-Skript](src/analyze_statistical_tests.py)
- [SQL-Abfrage](sql/statistical_analysis.sql)
- [Ergebnisse und Visualisierungen](results/statistical_analysis/)

### API-Tagesanalyse

Die über einen Zeitraum von 24 Stunden gesammelten API-Daten wurden hinsichtlich Snapshot-Qualität, Stationsabdeckung, Ereignistypen und zeitlicher Entwicklung analysiert.

Untersucht wurden unter anderem:

- Vollständigkeit und zeitliche Abdeckung der Snapshots
- Verteilung der beobachteten Verspätungswerte
- Konsistenz zwischen geplanten und geänderten Zeitangaben
- Entwicklung der Verspätungen wiederholt beobachteter Zugereignisse

- [Dokumentation der API-Tagesanalyse](docs/07_api_day_analysis.md)
- [Snapshot-Analyse](src/analyze_api_day.py)
- [Ereignisentwicklung](src/analyze_api_event_evolution.py)
- [Analyseergebnisse](results/api_day/)

## Power BI Dashboards

Die Ergebnisse der Analysen werden in zwei Power BI Dashboards visualisiert.

<details>
<summary>Historische Analyse</summary>

Das Dashboard umfasst unter anderem Verspätungs- und Ausfallkennzahlen, zeitliche Muster, Zugtypen, Bahnhöfe, Ersatzverkehr und Zeitraumvergleiche.

[Power BI Dashboard – Historische Analyse](dashboard/historical_analysis/historical_analysis.pbix)

</details>

<details>
<summary>API-Tagesanalyse</summary>

Das Dashboard zeigt die Qualität der Datenerhebung und die Entwicklung der Verspätungen beobachteter Zugereignisse über den Erfassungszeitraum.

[Power BI Dashboard – API-Tagesanalyse](dashboard/api_day_analysis/api_day_analysis.pbix)

</details>

## AI-gestützter Workflow

Für die Entwicklung und Überarbeitung von Python-Skripten habe ich **OpenAI Codex als AI coding agent** eingesetzt.

Codex unterstützte mich insbesondere bei:

- der Entwicklung und Überarbeitung komplexer Python-Skripte
- der Fehlersuche und der Suche nach Lösungsansätzen
- der Prüfung von CSV-Dateien und Datenstrukturen
- der Erstellung und Anpassung von Visualisierungen (Python)
- der Aufbereitung von Analyseergebnissen und Dokumentation

Der Einsatz des AI coding agent beschleunigte die technische Umsetzung und erleichterte die Arbeit mit umfangreichen Skripten.

Die Vorschläge und Ergebnisse wurden von mir geprüft. Die Projektziele, methodischen Entscheidungen, Interpretation und fachliche Verantwortung lagen bei mir.

[Dokumentation: AI-gestützter Workflow](docs/08_ai_assisted_workflow.md)

## Tech Stack  

- **Programmiersprachen:** Python, SQL
- **Datenanalyse:** Pandas, NumPy, DuckDB, SciPy, Statsmodels
- **Datenvisualisierung:** Matplotlib, Power BI
- **Datenquellen:** Deutsche Bahn Timetables API, Hugging Face
- **Datenformate:** CSV, Parquet, XML
- **Automatisierung:** GitHub Actions, GitHub REST API, cron-job.org
- **Versionsverwaltung:** Git, GitHub
- **Entwicklungsumgebung:** Notepad, PowerShell
- **AI-Unterstützung:** OpenAI Codex  


## Projektstruktur

```text
deutsche-bahn-verspaetungsanalyse/
│
├── .github/workflows/
│   └── db_api_collect.yml
│
├── dashboard/
│   ├── api_day_analysis/
│   │   └── api_day_analysis.pbix
│   └── historical_analysis/
│       └── historical_analysis.pbix
│
├── docs/
│   ├── 01_exploratory_data_analysis.md
│   ├── 02_data_quality_investigation.md
│   ├── 03_data_structure_investigation.md
│   ├── 04_kpi_analysis.md
│   ├── 05_historical_comparison.md
│   ├── 06_statistical_analysis.md
│   ├── 07_api_day_analysis.md
│   └── 08_ai_assisted_workflow.md
│
├── pictures/     # Dashboard-Screenshots und Projektvisualisierungen
│
├── results/
│   ├── api_day/
│   ├── historical/
│   └── statistical_analysis/
│
├── scripts/
│   └── explore_route_reconstruction.py
│
├── sql/          # SQL-Abfragen für KPI- und statistische Analysen
│
├── src/          # Python-Skripte für Datenerhebung,
│                 # Datenverarbeitung und Analysen
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```  

### Ergänzende Hinweise

- **`src/`** enthält Python-Skripte zur Datenerhebung über die Deutsche Bahn API, zur Verarbeitung und Analyse der Daten sowie zur Berechnung von KPIs und statistischen Kennzahlen.
- **`sql/`** enthält SQL-Abfragen für verschiedene historische Analysen, darunter Verspätungskennzahlen nach Zugtyp, Bahnhof, Wochentag und Tageszeit sowie statistische Auswertungen.
- **`scripts/`** enthält einen ergänzenden experimentellen Skript zur Untersuchung und Rekonstruktion möglicher Zugrouten anhand historischer Daten. Es gehört nicht zum Kern der Analysen.
- **`results/`** enthält ausgewählte Analyseergebnisse in Form von CSV-Dateien und Visualisierungen.
- **`docs/`** dokumentiert die Fragestellungen, Datenstruktur, Datenqualität, Methodik und Ergebnisse des Projekts.
- **`dashboard/`** enthält die Power-BI-Dashboards für die historische Analyse und die API-basierte Tagesanalyse.
```  


## Reproduzierbarkeit und Einschränkungen

Die Analysen basieren auf festgelegten Datenquellen, Zeiträumen und Analyseeinheiten. Methodische Entscheidungen und wesentliche Einschränkungen sind in den jeweiligen Dokumentationen beschrieben.

Die historischen Rohdaten werden nicht im Repository gespeichert. Für die API-Analyse werden die erhobenen Momentaufnahmen und daraus erzeugten Ergebnisse verwendet.

Die Ergebnisse beschreiben beobachtete Muster und statistische Zusammenhänge. Sie erlauben nicht automatisch kausale Schlussfolgerungen. Finanzielle Auswirkungen beruhen auf transparenten Annahmen und sind als Schätzungen zu verstehen.

## Projektstatus

Die zentralen Analysen, SQL-Abfragen, Python-Skripte und Power BI Dashboards wurden umgesetzt. Die historische Analyse und die API-basierte Datenerhebung bilden zwei ergänzende Bestandteile des Projekts.

Das Projekt zeigt einen durchgängigen Analyseprozess von der Datenbeschaffung und -prüfung über SQL- und Python-Analysen bis zur Visualisierung und Interpretation der Ergebnisse.  



## Praktische und wirtschaftliche Relevanz

Verspätungen im Schienenverkehr können sowohl für Fahrgäste als auch für Verkehrsunternehmen wirtschaftliche Auswirkungen haben.

Für Fahrgäste gelten gemäß der europäischen Fahrgastrechte-Verordnung unter bestimmten Voraussetzungen Entschädigungsansprüche bei Verspätungen am Zielbahnhof:

- **Ab 60 Minuten Verspätung:** 25 % des Fahrpreises
- **Ab 120 Minuten Verspätung:** 50 % des Fahrpreises

Die Analyse betrachtet daher auch Verspätungen ab 60 Minuten als besonders relevant. Die entsprechenden Kennzahlen können helfen, das Ausmaß erheblicher Verspätungen im untersuchten Zeitraum einzuordnen.

Die Ergebnisse stellen jedoch keine Berechnung tatsächlicher Entschädigungszahlungen dar. Die analysierten Verspätungen einzelner Zugereignisse an Bahnhöfen lassen sich nicht unmittelbar mit Verspätungen am Zielbahnhof einzelner Reisender gleichsetzen.

Eine konkrete Schätzung der finanziellen Verluste der Deutschen Bahn ist nicht Bestandteil des Projekts, da hierfür zusätzliche betriebswirtschaftliche Daten erforderlich wären.

**Quelle:** [Bundesministerium für Verkehr – Fahrgastrechte im Eisenbahnverkehr](https://www.bmv.de/SharedDocs/DE/Artikel/E/schiene-schienenpersonenverkehr/fahrgastrechte-zug.html)  

