# Untersuchung der Datenstruktur

## Ziel

Vor der Berechnung von Kennzahlen zu Verspätungen und Zugausfällen wurde die Struktur der historischen DB-Daten untersucht.

Ein wichtiger Punkt war die Frage, welche Datensatz-Einheit einen konkreten Zug bzw. eine konkrete Fahrt beschreibt. Insbesondere wurde geprüft, ob `train_line_ride_id` direkt als ID einer einzelnen Zugfahrt verwendet werden kann.

Die Untersuchung wurde am Datensatz **März 2025** durchgeführt.

---

## 1. Ausgangspunkt

Der Datensatz enthält unter anderem folgende Felder:

* `train_line_ride_id`
* `train_line_station_num`
* `train_number`
* `time`
* `arrival_planned_time`
* `departure_planned_time`
* `delay_in_min`
* `arrival_is_canceled`
* `departure_is_canceled`
* `is_replacement_train`
* `replaced_train_number`

Zunächst lag die Vermutung nahe, dass `train_line_ride_id` eine einzelne Zugfahrt eindeutig identifiziert.

Die Datenprüfung zeigte jedoch, dass dies nicht der Fall ist.

---

## 2. `train_line_ride_id` ist kein eindeutiger physischer Zuglauf

Ein `train_line_ride_id` kann innerhalb eines Monats mehrfach vorkommen.

Beispiel:

```text
train_line_ride_id = -2821038168538545983
train_line_station_num = 1
train_number = 3670
```

Dieser Service erscheint an vielen verschiedenen Tagen im März 2025.

Damit beschreibt `train_line_ride_id` ein **wiederkehrendes geplantes Service- bzw. Fahrplanmuster** und nicht eine einzelne physische Zugfahrt an einem bestimmten Tag.

### Konsequenz

`train_line_ride_id` darf bei der Berechnung von Fahrt-Kennzahlen nicht einfach als Anzahl der einzelnen Zugfahrten interpretiert werden.

---

## 3. `time` ist nicht zuverlässig als Fahrt-Datum geeignet

Bei der Untersuchung mehrfach auftretender Kombinationen wurde festgestellt, dass `time` nicht immer dem Datum der geplanten Fahrt entspricht.

Dies ist besonders bei Fahrten relevant, die um Mitternacht stattfinden.

Beispiel:

| `time`           | `departure_planned_time` |
| ---------------- | ------------------------ |
| 2025-03-29 00:01 | 2025-03-28 23:35         |
| 2025-03-29 23:51 | 2025-03-29 23:35         |

Beide Datensätze können daher am selben Kalenderdatum in `time` erscheinen, obwohl sie zu unterschiedlichen geplanten Service-Ereignissen gehören.

### Konsequenz

`DATE(time)` wird nicht als primäre Definition des Fahrt- bzw. Service-Datums verwendet.

Für die Rekonstruktion eines geplanten Service-Ereignisses wird stattdessen die geplante Ankunfts- bzw. Abfahrtszeit betrachtet.

---

## 4. Definition von `planned_event_time`

Für die weitere Untersuchung wurde folgende Variable definiert:

```sql
COALESCE(
    departure_planned_time,
    arrival_planned_time
) AS planned_event_time
```

Damit wird – sofern vorhanden – die geplante Abfahrtszeit verwendet. Falls diese nicht vorhanden ist, wird auf die geplante Ankunftszeit zurückgegriffen.

---

## 5. Prüfung auf eindeutige Station Events

Anschließend wurde geprüft, ob folgende Kombination ein Event eindeutig identifiziert:

```text
train_line_ride_id
+ train_line_station_num
+ planned_event_time
```

SQL:

```sql
SELECT
    train_line_ride_id,
    train_line_station_num,
    train_type,
    COALESCE(
        departure_planned_time,
        arrival_planned_time
    ) AS planned_event_time,
    COUNT(*) AS records
FROM read_parquet('{url}')
WHERE train_line_ride_id IS NOT NULL
  AND train_line_station_num IS NOT NULL
  AND COALESCE(
        departure_planned_time,
        arrival_planned_time
      ) IS NOT NULL
GROUP BY
    train_line_ride_id,
    train_line_station_num,
    train_type,
    planned_event_time
HAVING COUNT(*) > 1
ORDER BY records DESC
LIMIT 30;
```

### Ergebnis

Die Abfrage lieferte ein leeres Ergebnis (`Empty DataFrame`).

Es wurden also **keine mehrfachen Datensätze** mit derselben Kombination gefunden.

Damit ist diese Kombination im untersuchten März-Datensatz eindeutig:

> `train_line_ride_id + train_line_station_num + planned_event_time`

---

## 6. Vergleich der Rohdaten mit den eindeutigen Station Events

Anschließend wurde die Anzahl der Rohdaten mit der Anzahl der eindeutigen geplanten Station Events verglichen.

```sql
SELECT
    COUNT(*) AS raw_observations,

    COUNT(DISTINCT
        train_line_ride_id
        || '-'
        || train_line_station_num::VARCHAR
        || '-'
        || COALESCE(
            departure_planned_time,
            arrival_planned_time
        )::VARCHAR
    ) AS unique_scheduled_station_events

FROM read_parquet('{url}')
WHERE train_line_ride_id IS NOT NULL
  AND train_line_station_num IS NOT NULL
  AND COALESCE(
        departure_planned_time,
        arrival_planned_time
      ) IS NOT NULL;
```

### Ergebnis März 2025

| Kennzahl                               |    Anzahl |
| -------------------------------------- | --------: |
| Rohdaten                               | 2.004.921 |
| Datensätze mit vollständigem Event-Key | 2.004.911 |
| Eindeutige geplante Station Events     | 2.004.911 |

Damit entspricht die Anzahl der eindeutigen Events exakt der Anzahl der Datensätze mit vollständigem Event-Key.

Es gibt also in diesem Datensatz **keine Duplikate auf dieser Ebene**.

---

## 7. Die 10 Datensätze ohne geplante Event-Zeit

Die Differenz von 10 Datensätzen wurde ebenfalls untersucht.

```sql
SELECT
    COUNT(*) AS rows_without_event_key,

    COUNT(*) FILTER (
        WHERE train_line_ride_id IS NULL
    ) AS missing_ride_id,

    COUNT(*) FILTER (
        WHERE train_line_station_num IS NULL
    ) AS missing_station_num,

    COUNT(*) FILTER (
        WHERE COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) IS NULL
    ) AS missing_planned_time

FROM read_parquet('{url}')
WHERE
    train_line_ride_id IS NULL
    OR train_line_station_num IS NULL
    OR COALESCE(
        departure_planned_time,
        arrival_planned_time
    ) IS NULL;
```

Ergebnis:

| Problem                                 | Anzahl |
| --------------------------------------- | -----: |
| Datensätze ohne vollständigen Event-Key |     10 |
| Fehlende `train_line_ride_id`           |      0 |
| Fehlende `train_line_station_num`       |      0 |
| Fehlende `planned_event_time`           |     10 |

Alle 10 ausgeschlossenen Datensätze besitzen also `train_line_ride_id` und `train_line_station_num`, aber keine geplante Ankunfts- oder Abfahrtszeit.

Die Rohdaten bleiben unverändert erhalten. Für Analysen, die eine geplante Event-Zeit benötigen, werden diese 10 Datensätze als fehlende Zeitinformation behandelt.

---

## 8. Beispiel: Cancellation und Replacement Train

Ein besonders interessantes Beispiel ist der `train_line_ride_id`:

```text
-2821038168538545983
```

an Station 1 mit Zugnummer 3670.

Am 03.03.2025 finden sich zwei unterschiedliche geplante Events:

| Planned Event | Train | Cancellation | Replacement | Delay |
| ------------- | ----: | ------------ | ----------- | ----: |
| 22:58         |  3670 | True         | False       | 0 min |
| 23:09         |  3670 | False        | True        | 1 min |

Die beiden Datensätze haben unterschiedliche `planned_event_time` und sind deshalb keine Duplikate.

Gleichzeitig zeigen die Merkmale `departure_is_canceled` und `is_replacement_train`, dass hier zwei unterschiedliche operative Zustände bzw. Ereignisse im Zusammenhang mit dem Service dokumentiert sind.

Aus diesen beiden Datensätzen allein wird jedoch **keine kausale Abfolge behauptet**. Es kann festgestellt werden, dass ein geplantes Event um 22:58 als ausgefallen markiert wurde und ein weiteres geplantes Event um 23:09 als Ersatzfahrt markiert wurde.

---

## 9. Aktuelle Interpretation der wichtigsten Felder

| Feld                     | Aktuelle Interpretation                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------ |
| `train_line_ride_id`     | Wiederkehrender geplanter Service / Fahrplanmuster                                         |
| `train_line_station_num` | Position der Station innerhalb des Service                                                 |
| `planned_event_time`     | Geplante Zeit des Station Events                                                           |
| `time`                   | Zeitpunkt des Datensatzes bzw. der Beobachtung; nicht als primäres Service-Datum verwendet |
| `train_number`           | Zugnummer des jeweiligen Datensatzes                                                       |
| `delay_in_min`           | Aus den geplanten und geänderten Zeitpunkten berechnete Zeitabweichung                     |
| `is_replacement_train`   | Kennzeichnung eines Ersatzverkehrs/-zuges gemäß Quelldatensatz                             |
| `departure_is_canceled`  | Kennzeichnung einer ausgefallenen Abfahrt gemäß Quelldatensatz                             |
| `arrival_is_canceled`    | Kennzeichnung einer ausgefallenen Ankunft gemäß Quelldatensatz                             |

---

## 10. Aktuelle analytische Einheit

Für die bisherige Datenstruktur-Untersuchung wird folgende Einheit verwendet:

> **Scheduled Station Event**

Identifiziert durch:

```text
train_line_ride_id
+ train_line_station_num
+ planned_event_time
```

Damit wird bewusst zwischen einem wiederkehrenden Service-Muster und einem einzelnen geplanten Ereignis an einer bestimmten Station unterschieden.

### Wichtig

Ein Scheduled Station Event ist **noch nicht automatisch eine vollständige Zugfahrt von Start bis Ziel**.

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

---

## 11. Konsequenz für die weitere Analyse

Die Untersuchung verhindert eine wichtige methodische Fehlinterpretation:

**Nicht:**

```text
1 train_line_ride_id = 1 Zugfahrt
```

sondern:

```text
train_line_ride_id
        ↓
wiederkehrendes Service-/Fahrplanmuster

        ↓
mehrere konkrete geplante Service Events

        ↓
jeweils mehrere Station Events
```

Die nächsten Analyseschritte sind daher:

1. Prüfen, ob ein vollständiger `service occurrence` zuverlässig rekonstruiert werden kann.
2. Falls ja: Definition einer belastbaren Fahrt-Einheit.
3. Falls nein: Analyse auf Station-Event-Ebene beibehalten.
4. Danach Berechnung der Verspätungs-, Ausfall- und Ersatzverkehrs-KPIs.

---

## Fazit

Die Datenprüfung zeigt, dass die Rohdaten für eine detaillierte Analyse geeignet sind. Vor der KPI-Berechnung muss jedoch die genaue Granularität der Daten berücksichtigt werden.

Für März 2025 konnten **2.004.911 eindeutige Scheduled Station Events** mit vollständiger Event-Zeit identifiziert werden. Auf dieser Ebene wurden keine Duplikate gefunden.

Die Untersuchung zeigt außerdem, dass `train_line_ride_id` nicht als eindeutige ID einer einzelnen physischen Zugfahrt verwendet werden kann.

### Test der Routenrekonstruktion

Es wurde mit Python geprüft, ob einzelne Zugfahrten aus mehreren Feldern der Daten rekonstruiert werden können. Dabei wurden unter anderem `train_number`, `train_type`, `train_line_ride_id`, `train_line_station_num` und `planned_event_time` verwendet.

Bei einfachen Fällen funktioniert die Rekonstruktion. Zum Beispiel konnte für ICE 920 am 15.03.2025 folgende Route aus den Daten rekonstruiert werden:

```text
ICE 920 | 2025-03-15
========================================
Gefundene mögliche Routen: 1

ROUTE 1 | Ride ID 8503777394879306018 | 13 Station Events
2025-03-15 23:24:00 Frankfurt (Main) Hbf -> 2025-03-16 06:38:00 Hamburg-Harburg

Route:
  1 | 2025-03-15 23:24:00 | Frankfurt (Main) Hbf | delay=1
  3 | 2025-03-16 00:01:00 | Mainz Hbf | delay=15
  5 | 2025-03-16 00:58:00 | Koblenz Hbf | delay=43
  6 | 2025-03-16 02:09:00 | Köln Hbf | delay=42
  7 | 2025-03-16 02:33:00 | Düsseldorf Hbf | delay=43
  9 | 2025-03-16 02:51:00 | Duisburg Hbf | delay=41
 10 | 2025-03-16 03:04:00 | Essen Hbf | delay=40
 11 | 2025-03-16 03:34:00 | Dortmund Hbf | delay=39
 12 | 2025-03-16 03:52:00 | Hamm (Westf) Hbf | delay=40
 13 | 2025-03-16 04:15:00 | Münster (Westf) Hbf | delay=36
 14 | 2025-03-16 04:50:00 | Osnabrück Hbf | delay=38
 16 | 2025-03-16 05:54:00 | Bremen Hbf | delay=29
 17 | 2025-03-16 06:38:00 | Hamburg-Harburg | delay=53
```

Auch **IC 2048** (Dresden Hbf → Köln Hbf) und **ICE 2500** (München Hbf → Berlin Ostbahnhof) konnten in einem einfachen Fall erfolgreich rekonstruiert werden.

Komplexere Fälle zeigen jedoch mehrere parallele Stationsfolgen sowie Ausfälle oder Ersatzfahrten. Diese Fälle können mit den vorhandenen Daten nicht zuverlässig voneinander getrennt werden.

**Deshalb werden die Scheduled Station Events als sichere analytische Einheit für die Hauptanalyse verwendet.** Die rekonstruierten Zugverläufe dienen nur als Ergebnis der Datenprüfung und werden nicht als Grundlage für allgemeine Fahrt-level-KPIs verwendet.





