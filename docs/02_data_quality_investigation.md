# Data Quality Investigation

## Ziel

Während der explorativen Analyse wurden mehrere Punkte gefunden, die vor der Berechnung der finalen KPIs geprüft werden müssen.

Der Schwerpunkt dieser Untersuchung liegt auf:

* ungewöhnlichen negativen Verspätungswerten
* fehlenden geplanten Zeiten
* der Interpretation von Ausfall-Datensätzen

## Negative Werte bei `delay_in_min`

Im Datensatz kommen auch negative Werte bei `delay_in_min` vor.

Die meisten negativen Werte sind relativ klein. Es gibt jedoch einzelne sehr große negative Werte.

Für März 2025 wurde zum Beispiel ein Minimum von etwa **-1.435 Minuten** gefunden.

Das entspricht einer Differenz von fast 24 Stunden und ist für eine normale Verspätung nicht plausibel.

### Untersuchung der Berechnung

Die Spalte `delay_in_min` wird aus den geplanten (`pt`) und geänderten (`ct`) Zeiten berechnet.

Vereinfacht:

```text
delay = changed_time - planned_time
```

Dabei ist `ct` laut der Dokumentation der Deutsche Bahn die neue geschätzte oder tatsächliche Ankunfts- bzw. Abfahrtszeit.

Die Untersuchung der zugrunde liegenden XML-Daten zeigte, dass die großen negativen Werte **nicht durch einen einfachen Fehler bei der Datumsumwandlung entstehen**.

Die genaue Ursache der extremen negativen Werte konnte auf Basis der verfügbaren Daten jedoch nicht eindeutig bestimmt werden.

Mögliche operative Fahrplanänderungen oder Anomalien in den zugrunde liegenden Änderungsdaten können nicht ausgeschlossen werden.

Deshalb werden solche Werte nicht ohne weitere Prüfung als normale Verspätungen interpretiert.

## Beispiel für einen ungewöhnlichen Wert

Bei der Untersuchung wurde unter anderem die Zugfahrt mit der ID `603466462240183523` betrachtet.

Für mehrere Bahnhöfe wurden dabei sehr große negative Werte beobachtet.

Die Werte traten an mehreren Stationen derselben Fahrt auf und verwendeten jeweils einen gemeinsamen Änderungszeitpunkt.

Dieses Muster zeigt, dass die Werte nicht einfach als normale negative Verspätungen interpretiert werden sollten.

Die genaue Ursache wird in diesem Projekt ni
