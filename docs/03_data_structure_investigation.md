\# Untersuchung der Datenstruktur



\## Ziel



Vor der Berechnung von Kennzahlen zu Verspätungen und Zugausfällen wurde die Struktur der historischen DB-Daten untersucht.



Ein wichtiger Punkt war die Frage, welche Datensatz-Einheit einen konkreten Zug bzw. eine konkrete Fahrt beschreibt. Insbesondere wurde geprüft, ob `train\_line\_ride\_id` direkt als ID einer einzelnen Zugfahrt verwendet werden kann.



Die Untersuchung wurde am Datensatz \*\*März 2025\*\* durchgeführt.



\---



\## 1. Ausgangspunkt



Der Datensatz enthält unter anderem folgende Felder:



\* `train\_line\_ride\_id`

\* `train\_line\_station\_num`

\* `train\_number`

\* `time`

\* `arrival\_planned\_time`

\* `departure\_planned\_time`

\* `delay\_in\_min`

\* `arrival\_is\_canceled`

\* `departure\_is\_canceled`

\* `is\_replacement\_train`

\* `replaced\_train\_number`



Zunächst lag die Vermutung nahe, dass `train\_line\_ride\_id` eine einzelne Zugfahrt eindeutig identifiziert.



Die Datenprüfung zeigte jedoch, dass dies nicht der Fall ist.



\---



\## 2. `train\_line\_ride\_id` ist kein eindeutiger physischer Zuglauf



Ein `train\_line\_ride\_id` kann innerhalb eines Monats mehrfach vorkommen.



Beispiel:



```text

train\_line\_ride\_id = -2821038168538545983

train\_line\_station\_num = 1

train\_number = 3670

```



Dieser Service erscheint an vielen verschiedenen Tagen im März 2025.



Damit beschreibt `train\_line\_ride\_id` ein \*\*wiederkehrendes geplantes Service- bzw. Fahrplanmuster\*\* und nicht eine einzelne physische Zugfahrt an einem bestimmten Tag.



\### Konsequenz



`train\_line\_ride\_id` darf bei der Berechnung von Fahrt-Kennzahlen nicht einfach als Anzahl der einzelnen Zugfahrten interpretiert werden.



\---



\## 3. `time` ist nicht zuverlässig als Fahrt-Datum geeignet



Bei der Untersuchung mehrfach auftretender Kombinationen wurde festgestellt, dass `time` nicht immer dem Datum der geplanten Fahrt entspricht.



Dies ist besonders bei Fahrten relevant, die um Mitternacht stattfinden.



Beispiel:



| `time`           | `departure\_planned\_time` |

| ---------------- | ------------------------ |

| 2025-03-29 00:01 | 2025-03-28 23:35         |

| 2025-03-29 23:51 | 2025-03-29 23:35         |



Beide Datensätze können daher am selben Kalenderdatum in `time` erscheinen, obwohl sie zu unterschiedlichen geplanten Service-Ereignissen gehören.



\### Konsequenz



`DATE(time)` wird nicht als primäre Definition des Fahrt- bzw. Service-Datums verwendet.



Für die Rekonstruktion eines geplanten Service-Ereignisses wird stattdessen die geplante Ankunfts- bzw. Abfahrtszeit betrachtet.



\---



\## 4. Definition von `planned\_event\_time`



Für die weitere Untersuchung wurde folgende Variable definiert:



```sql

COALESCE(

&#x20;   departure\_planned\_time,

&#x20;   arrival\_planned\_time

) AS planned\_event\_time

```



Damit wird – sofern vorhanden – die geplante Abfahrtszeit verwendet. Falls diese nicht vorhanden ist, wird auf die geplante Ankunftszeit zurückgegriffen.



\---



\## 5. Prüfung auf eindeutige Station Events



Anschließend wurde geprüft, ob folgende Kombination ein Event eindeutig identifiziert:



```text

train\_line\_ride\_id

\+ train\_line\_station\_num

\+ planned\_event\_time

```



SQL:



```sql

SELECT

&#x20;   train\_line\_ride\_id,

&#x20;   train\_line\_station\_num,

&#x20;   train\_type,

&#x20;   COALESCE(

&#x20;       departure\_planned\_time,

&#x20;       arrival\_planned\_time

&#x20;   ) AS planned\_event\_time,

&#x20;   COUNT(\*) AS records

FROM read\_parquet('{url}')

WHERE train\_line\_ride\_id IS NOT NULL

&#x20; AND train\_line\_station\_num IS NOT NULL

&#x20; AND COALESCE(

&#x20;       departure\_planned\_time,

&#x20;       arrival\_planned\_time

&#x20;     ) IS NOT NULL

GROUP BY

&#x20;   train\_line\_ride\_id,

&#x20;   train\_line\_station\_num,

&#x20;   train\_type,

&#x20;   planned\_event\_time

HAVING COUNT(\*) > 1

ORDER BY records DESC

LIMIT 30;

```



\### Ergebnis



Die Abfrage lieferte ein leeres Ergebnis (`Empty DataFrame`).



Es wurden also \*\*keine mehrfachen Datensätze\*\* mit derselben Kombination gefunden.



Damit ist diese Kombination im untersuchten März-Datensatz eindeutig:



> `train\_line\_ride\_id + train\_line\_station\_num + planned\_event\_time`



\---



\## 6. Vergleich der Rohdaten mit den eindeutigen Station Events



Anschließend wurde die Anzahl der Rohdaten mit der Anzahl der eindeutigen geplanten Station Events verglichen.



```sql

SELECT

&#x20;   COUNT(\*) AS raw\_observations,



&#x20;   COUNT(DISTINCT

&#x20;       train\_line\_ride\_id

&#x20;       || '-'

&#x20;       || train\_line\_station\_num::VARCHAR

&#x20;       || '-'

&#x20;       || COALESCE(

&#x20;           departure\_planned\_time,

&#x20;           arrival\_planned\_time

&#x20;       )::VARCHAR

&#x20;   ) AS unique\_scheduled\_station\_events



FROM read\_parquet('{url}')

WHERE train\_line\_ride\_id IS NOT NULL

&#x20; AND train\_line\_station\_num IS NOT NULL

&#x20; AND COALESCE(

&#x20;       departure\_planned\_time,

&#x20;       arrival\_planned\_time

&#x20;     ) IS NOT NULL;

```



\### Ergebnis März 2025



| Kennzahl                               |    Anzahl |

| -------------------------------------- | --------: |

| Rohdaten                               | 2.004.921 |

| Datensätze mit vollständigem Event-Key | 2.004.911 |

| Eindeutige geplante Station Events     | 2.004.911 |



Damit entspricht die Anzahl der eindeutigen Events exakt der Anzahl der Datensätze mit vollständigem Event-Key.



Es gibt also in diesem Datensatz \*\*keine Duplikate auf dieser Ebene\*\*.



\---



\## 7. Die 10 Datensätze ohne geplante Event-Zeit



Die Differenz von 10 Datensätzen wurde ebenfalls untersucht.



```sql

SELECT

&#x20;   COUNT(\*) AS rows\_without\_event\_key,



&#x20;   COUNT(\*) FILTER (

&#x20;       WHERE train\_line\_ride\_id IS NULL

&#x20;   ) AS missing\_ride\_id,



&#x20;   COUNT(\*) FILTER (

&#x20;       WHERE train\_line\_station\_num IS NULL

&#x20;   ) AS missing\_station\_num,



&#x20;   COUNT(\*) FILTER (

&#x20;       WHERE COALESCE(

&#x20;           departure\_planned\_time,

&#x20;           arrival\_planned\_time

&#x20;       ) IS NULL

&#x20;   ) AS missing\_planned\_time



FROM read\_parquet('{url}')

WHERE

&#x20;   train\_line\_ride\_id IS NULL

&#x20;   OR train\_line\_station\_num IS NULL

&#x20;   OR COALESCE(

&#x20;       departure\_planned\_time,

&#x20;       arrival\_planned\_time

&#x20;   ) IS NULL;

```



Ergebnis:



| Problem                                 | Anzahl |

| --------------------------------------- | -----: |

| Datensätze ohne vollständigen Event-Key |     10 |

| Fehlende `train\_line\_ride\_id`           |      0 |

| Fehlende `train\_line\_station\_num`       |      0 |

| Fehlende `planned\_event\_time`           |     10 |



Alle 10 ausgeschlossenen Datensätze besitzen also `train\_line\_ride\_id` und `train\_line\_station\_num`, aber keine geplante Ankunfts- oder Abfahrtszeit.



Die Rohdaten bleiben unverändert erhalten. Für Analysen, die eine geplante Event-Zeit benötigen, werden diese 10 Datensätze als fehlende Zeitinformation behandelt.



\---



\## 8. Beispiel: Cancellation und Replacement Train



Ein besonders interessantes Beispiel ist der `train\_line\_ride\_id`:



```text

\-2821038168538545983

```



an Station 1 mit Zugnummer 3670.



Am 03.03.2025 finden sich zwei unterschiedliche geplante Events:



| Planned Event | Train | Cancellation | Replacement | Delay |

| ------------- | ----: | ------------ | ----------- | ----: |

| 22:58         |  3670 | True         | False       | 0 min |

| 23:09         |  3670 | False        | True        | 1 min |



Die beiden Datensätze haben unterschiedliche `planned\_event\_time` und sind deshalb keine Duplikate.



Gleichzeitig zeigen die Merkmale `departure\_is\_canceled` und `is\_replacement\_train`, dass hier zwei unterschiedliche operative Zustände bzw. Ereignisse im Zusammenhang mit dem Service dokumentiert sind.



Aus diesen beiden Datensätzen allein wird jedoch \*\*keine kausale Abfolge behauptet\*\*. Es kann festgestellt werden, dass ein geplantes Event um 22:58 als ausgefallen markiert wurde und ein weiteres geplantes Event um 23:09 als Ersatzfahrt markiert wurde.



\---



\## 9. Aktuelle Interpretation der wichtigsten Felder



| Feld                     | Aktuelle Interpretation                                                                    |

| ------------------------ | ------------------------------------------------------------------------------------------ |

| `train\_line\_ride\_id`     | Wiederkehrender geplanter Service / Fahrplanmuster                                         |

| `train\_line\_station\_num` | Position der Station innerhalb des Service                                                 |

| `planned\_event\_time`     | Geplante Zeit des Station Events                                                           |

| `time`                   | Zeitpunkt des Datensatzes bzw. der Beobachtung; nicht als primäres Service-Datum verwendet |

| `train\_number`           | Zugnummer des jeweiligen Datensatzes                                                       |

| `delay\_in\_min`           | Aus den geplanten und geänderten Zeitpunkten berechnete Zeitabweichung                     |

| `is\_replacement\_train`   | Kennzeichnung eines Ersatzverkehrs/-zuges gemäß Quelldatensatz                             |

| `departure\_is\_canceled`  | Kennzeichnung einer ausgefallenen Abfahrt gemäß Quelldatensatz                             |

| `arrival\_is\_canceled`    | Kennzeichnung einer ausgefallenen Ankunft gemäß Quelldatensatz                             |



\---



\## 10. Aktuelle analytische Einheit



Für die bisherige Datenstruktur-Untersuchung wird folgende Einheit verwendet:



> \*\*Scheduled Station Event\*\*



Identifiziert durch:



```text

train\_line\_ride\_id

\+ train\_line\_station\_num

\+ planned\_event\_time

```



Damit wird bewusst zwischen einem wiederkehrenden Service-Muster und einem einzelnen geplanten Ereignis an einer bestimmten Station unterschieden.



\### Wichtig



Ein Scheduled Station Event ist \*\*noch nicht automatisch eine vollständige Zugfahrt von Start bis Ziel\*\*.



Ein Zug kann beispielsweise mehrere Station Events haben:



```text

Service A

│

├── Station 1 → 08:15

├── Station 2 → 08:42

├── Station 3 → 09:10

└── Station 4 → 09:38

```



Daher wird vor der Berechnung von vollständigen Fahrt-Kennzahlen noch geprüft, ob sich aus den vorhandenen Feldern ein kompletter Service Occurrence zuverlässig rekonstruieren lässt.



\---



\## 11. Konsequenz für die weitere Analyse



Die Untersuchung verhindert eine wichtige methodische Fehlinterpretation:



\*\*Nicht:\*\*



```text

1 train\_line\_ride\_id = 1 Zugfahrt

```



sondern:



```text

train\_line\_ride\_id

&#x20;       ↓

wiederkehrendes Service-/Fahrplanmuster



&#x20;       ↓

mehrere konkrete geplante Service Events



&#x20;       ↓

jeweils mehrere Station Events

```



Die nächsten Analyseschritte sind daher:



1\. Prüfen, ob ein vollständiger `service occurrence` zuverlässig rekonstruiert werden kann.

2\. Falls ja: Definition einer belastbaren Fahrt-Einheit.

3\. Falls nein: Analyse auf Station-Event-Ebene beibehalten.

4\. Danach Berechnung der Verspätungs-, Ausfall- und Ersatzverkehrs-KPIs.



\---



\## Fazit



Die Datenprüfung zeigt, dass die Rohdaten für eine detaillierte Analyse geeignet sind, die Granularität jedoch vor der KPI-Berechnung eindeutig definiert werden muss.



Für März 2025 konnten \*\*2.004.911 eindeutige Scheduled Station Events\*\* mit vollständiger Event-Zeit identifiziert werden. Es wurden keine Duplikate auf dieser Ebene gefunden.



Die Untersuchung zeigt außerdem, dass `train\_line\_ride\_id` nicht als eindeutige ID einer einzelnen physischen Zugfahrt verwendet werden sollte.



Die Rekonstruktion vollständiger Service Occurrences wird deshalb als separater Analyseschritt durchgeführt, bevor Fahrt-level Kennzahlen berechnet werden.



