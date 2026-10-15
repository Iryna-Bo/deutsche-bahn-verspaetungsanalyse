# Tägliche Analyse der DB API



## Ziel



Analyse einer 24-stündigen Sammlung von DB API-Snapshots, um die Datenqualität zu prüfen und Veränderungen der angezeigten Verspätungen für dieselben Zugereignisse im Zeitverlauf zu untersuchen.



## Datensammlung



* 143 Snapshots

* 10-Minuten-Intervall

* 6 ausgewählte Bahnhöfe

* 45.664 Beobachtungen



## Datenqualität



* 1 fehlender Snapshot

* Hamburg Hbf fehlt zwischen 02:00 und 03:50 Uhr

* keine doppelten Kombinationen aus Zugereignis und Snapshot



## Identifikation der Zugereignisse



Ein geplantes Zugereignis wird anhand folgender Felder identifiziert:



`station_eva + stop_id + train_number + planned_time + event_type`



Damit kann dasselbe Zugereignis in mehreren Snapshots wiedererkannt und seine Entwicklung im Zeitverlauf untersucht werden.



## Entwicklung der Verspätung



* **Increased:** 56,86 %

* **Stable:** 30,52 %

* **Decreased:** 11,12 %

* **No delay data:** 1,51 %



`No delay data` bedeutet, dass für das Ereignis keine ausreichenden Verspätungsdaten für die Auswertung vorlagen. Es bedeutet nicht, dass keine Verspätung vorhanden war.



Die Analyse zeigt, dass sich die angezeigte Verspätung eines Zugereignisses zwischen zwei Snapshots deutlich verändern kann. Die größten Veränderungen können anhand der Spalte delay_change untersucht werden.



## Einschränkungen



* Die API-Analyse umfasst nur sechs ausgewählte Bahnhöfe.

* Fehlende Snapshots und Lücken bei der Stationsabdeckung sind möglich.

* Wenn ein Zugereignis in einem späteren Snapshot nicht mehr vorhanden ist, bedeutet das nicht automatisch, dass der Zug ausgefallen ist.

* Die Analyse beschreibt Veränderungen der angezeigten Verspätungen und zeigt Zusammenhänge, stellt aber keine kausalen Zusammenhänge fest.



## Ergebnisse



Die Analyse erzeugt CSV-Dateien mit Informationen zu:



* Snapshot-Qualität

* Stationsabdeckung

* Zeitstempel-Qualität

* Ereignistypen

* Entwicklung der Zugereignisse und Verspätungen



## Power BI Dashboard



Die Ergebnisse der 24-Stunden-Snapshot-Analyse wurden in einem interaktiven Power BI Dashboard visualisiert.



<img src="https://github.com/Iryna-Bo/deutsche-bahn-verspaetungsanalyse/blob/master/results/api_day/db_api_dashboard.png" alt="24 Stunden Snapshot Analyse" width="2000" high="1400"/>  



Das Dashboard zeigt:



* **143 Snapshots** innerhalb des untersuchten Zeitraums

* **45.664 Beobachtungen**

* **7.619 beobachtete Zugereignisse**

* **56,9 %** der beobachteten Zugereignisse mit einer steigenden Verspätung zwischen dem ersten und letzten verfügbaren Snapshot

* den zeitlichen Verlauf des Anteils der Ereignisse mit einer Verspätung von mindestens 5 Minuten

* die Entwicklung der Verspätungen (`increased`, `stable`, `decreased`, `no_delay_data`)

* die 20 Zugereignisse mit den höchsten zuletzt beobachteten Verspätungen unter den Ereignissen mit steigender Verspätung



Das Dashboard konzentriert sich auf die wichtigsten Analyseergebnisse. Weitere Details zur Datenqualität und zur Stationsabdeckung sind in der Dokumentation der Analyse beschrieben.



Das Dashboard dient zur interaktiven Darstellung der Analyseergebnisse. Die zugrunde liegenden Python-Auswertungen und CSV-Dateien bilden die Grundlage für die Berechnungen.



