# Data Quality Investigation

## Ziel

Während der explorativen Analyse wurden einige Punkte gefunden, die vor der Berechnung der finalen KPIs geprüft werden müssen:

* ungewöhnliche negative Werte bei `delay_in_min`
* fehlende geplante Zeiten
* Interpretation von Ausfall-Datensätzen

## Negative Werte bei `delay_in_min`

Im Datensatz kommen auch negative Werte bei `delay_in_min` vor. Kleine negative Werte können dabei normale Abweichungen darstellen, zum Beispiel eine frühere Ankunft oder Abfahrt.

Es gibt jedoch auch sehr große negative Werte. Für März 2025 wurde ein Minimum von **-1.435 Minuten** gefunden. Das entspricht fast 24 Stunden und ist für eine normale Verspätung nicht plausibel.

### Untersuchung

`delay_in_min` wird aus geplanten (`pt`) und geänderten (`ct`) Zeiten berechnet:

```text
delay = changed_time - planned_time
```

Die Untersuchung der zugrunde liegenden XML-Daten zeigte, dass die extremen negativen Werte **nicht durch einen einfachen Fehler bei der Datumsumwandlung entstehen**.

Die genaue Ursache konnte mit den verfügbaren Daten jedoch nicht eindeutig bestimmt werden. Mögliche Fahrplanänderungen oder Anomalien in den Änderungsdaten können nicht ausgeschlossen werden.

Ein Beispiel war die Zugfahrt mit der ID `603466462240183523`. Dabei wurden an mehreren Bahnhöfen sehr große negative Werte mit einem gemeinsamen Änderungszeitpunkt beobachtet.

## Umgang mit Ausreißern

Extreme Werte werden **nicht automatisch gelöscht**.

Sie bleiben im Rohdatensatz erhalten und werden für die weitere Analyse gekennzeichnet:

* unter **-60 Minuten** → `extreme_negative`
* ab **180 Minuten** → `extreme_positive`

Diese Kennzeichnung bedeutet nicht automatisch, dass die Werte falsch sind. Sie ermöglicht eine getrennte Prüfung bei der Berechnung der KPIs.

## Fehlende geplante Zeiten

Bei einem Teil der Datensätze fehlen geplante Ankunfts- oder Abfahrtszeiten (`pt`).

Für März 2025 waren geplante Zeiten bei ungefähr **22 % der Datensätze** nicht vorhanden.

Für zeitbasierte Verspätungs-KPIs werden deshalb nur Datensätze verwendet, bei denen die benötigten Zeitinformationen vorhanden sind.

## Ausfall-Datensätze

Die Anzahl der Ausfall-Datensätze entspricht nicht automatisch der Anzahl der ausgefallenen Zugfahrten.

Ein Zug kann an mehreren Bahnhöfen entsprechende Datensätze erzeugen. Deshalb müssen Datensätze und eindeutige Zugfahrten bei der weiteren Analyse unterschieden werden.

## Fazit

Die Datenqualitätsprüfung zeigt, dass einige Werte und Felder vor der KPI-Berechnung berücksichtigt werden müssen.

Die Rohdaten bleiben unverändert. Auffällige Werte werden gekennzeichnet und je nach KPI separat behandelt.
