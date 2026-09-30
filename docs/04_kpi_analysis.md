# KPI Analysis

## 1. Ziel der Analyse

Ziel der KPI-Analyse ist es, die Zuverlässigkeit des deutschen Schienenverkehrs anhand von Verspätungen und Ausfällen zu untersuchen.

Die Analyse betrachtet insbesondere folgende Fragen:

* Wie häufig treten Verspätungen auf?
* Wie unterscheiden sich Verspätungen zwischen Bahnhöfen und Zugtypen?
* Zu welchen Tageszeiten und Wochentagen treten Verspätungen häufiger auf?
* Wie häufig treten längere Verspätungen auf?
* Wie unterscheiden sich reguläre und Ersatzverkehre?
* Wie entwickelt sich die Verspätungssituation über die Monate?
* Wie unterscheiden sich ausgewählte historische Vergleichszeiträume?

Die Analyse basiert auf historischen DB-Daten für 107 Bahnhöfe.

---

## 2. Analytische Einheit

Als zentrale analytische Einheit wird ein **Scheduled Station Event** verwendet.

Ein Scheduled Station Event beschreibt ein geplantes Ankunfts- oder Abfahrtsereignis eines wiederkehrenden Zuglaufs an einer bestimmten Bahnhofposition.

Die Ereigniszeit wird definiert als:

```text
planned_event_time =
COALESCE(departure_planned_time, arrival_planned_time)
```

Die technische Identifikation eines Ereignisses basiert auf:

```text
train_line_ride_id
+ train_line_station_num
+ planned_event_time
```

Diese Einheit wurde gewählt, weil `train_line_ride_id` allein keinen einzelnen physischen Zuglauf an einem bestimmten Tag identifiziert. Die Daten enthalten wiederkehrende Fahrplanmuster sowie mehrere operative Beobachtungen.

Daher werden die Ergebnisse dieser Analyse als **Bahnhofsevents bzw. Beobachtungen** interpretiert und nicht als Anzahl physischer Zugfahrten.

---

## 3. KPI-Definitionen

Für die Analyse werden robuste und klar interpretierbare Kennzahlen verwendet.

| KPI           | Definition                                                                          |
| ------------- | ----------------------------------------------------------------------------------- |
| Median        | Median der beobachteten Verspätung in Minuten                                       |
| P95           | 95. Perzentil der Verspätung                                                        |
| ≥5 Min.       | Anteil der Beobachtungen mit mindestens 5 Minuten Verspätung                        |
| ≥15 Min.      | Anteil der Beobachtungen mit mindestens 15 Minuten Verspätung                       |
| ≥60 Min.      | Anteil der Beobachtungen mit mindestens 60 Minuten Verspätung                       |
| Ausfallanteil | Anteil der beobachteten geplanten Bahnhofsevents mit Ankunfts- oder Abfahrtsausfall |
| Ersatzverkehr | Anteil der Beobachtungen mit `is_replacement_train = true`                          |

Der Median wird zusammen mit Perzentilen und Schwellenwerten verwendet, da einzelne extreme Werte die Verteilung der Verspätungen stark beeinflussen können.

Die Schwellenwerte ermöglichen außerdem eine differenzierte Betrachtung kleinerer, stärkerer und sehr langer Verspätungen.

---

## 4. Gesamtanalyse

Als Referenzmonat wurde März 2025 detailliert untersucht.

Im März 2025 umfasst der Datensatz:

* **2.004.921 Beobachtungen**
* **107 Bahnhöfe**
* **59 Zugtypen**
* Median: **1 Minute**
* P95: **16 Minuten**
* 18,72 % der Beobachtungen mit mindestens 5 Minuten Verspätung
* 5,52 % mit mindestens 15 Minuten Verspätung
* 0,43 % mit mindestens 60 Minuten Verspätung
* 4,84 % ausgefallene geplante Bahnhofsevents
* 0,72 % Ersatzverkehr-Beobachtungen

Die Verteilung zeigt, dass die typische Beobachtung nur eine geringe Abweichung vom Fahrplan aufweist. Gleichzeitig liegt ein relevanter Teil der stärkeren Verspätungen im oberen Bereich der Verteilung.

Der Median von 1 Minute sollte daher nicht isoliert betrachtet werden. Die Kombination aus Median, P95 und den Verspätungsschwellen liefert ein vollständigeres Bild.

---

## 5. Analyse nach Bahnhof

Die Analyse umfasst alle 107 Bahnhöfe der betrachteten Daten.

Die Bahnhöfe unterscheiden sich deutlich hinsichtlich des Anteils stärkerer Verspätungen.

Beispiele für hohe Anteile von Beobachtungen mit mindestens 5 Minuten Verspätung im März 2025:

| Bahnhof           | Beobachtungen | ≥5 Min. | ≥15 Min. | ≥60 Min. | Ausfall |
| ----------------- | ------------: | ------: | -------: | -------: | ------: |
| Hamm (Westf) Hbf  |        12.568 | 40,04 % |  16,47 % |   1,49 % |  4,26 % |
| Duisburg Hbf      |        22.797 | 34,24 % |  12,47 % |   1,00 % |  4,97 % |
| Gelsenkirchen Hbf |        12.165 | 33,87 % |   8,75 % |   0,58 % |  3,44 % |
| Stuttgart Hbf     |        46.162 | 31,97 % |   5,61 % |   0,34 % |  5,33 % |
| Fulda             |         8.968 | 31,68 % |  12,96 % |   1,16 % |  4,00 % |
| Osnabrück Hbf     |        10.920 | 30,31 % |  11,33 % |   0,94 % |  2,57 % |
| Köln Hbf          |        38.757 | 30,21 % |  10,44 % |   0,79 % |  4,05 % |

Die Ergebnisse zeigen, dass die Häufigkeit stärkerer Verspätungen zwischen den Bahnhöfen erheblich variiert.

Dabei werden die Ergebnisse nicht als Qualitätsranking der Bahnhöfe interpretiert. Unterschiede in Zugangebot, Verkehrsstruktur und Anzahl der Beobachtungen können die Kennzahlen beeinflussen.

Der Ausfallanteil zeigt außerdem ein teilweise anderes Muster als die Verspätungskennzahlen. Deshalb werden Verspätungen und Ausfälle getrennt betrachtet.

---

## 6. Analyse nach Zugtyp

Für einen stabilen Vergleich werden insbesondere die Zugtypen S, RB, RE, ICE und IC betrachtet.

| Zugtyp | Beobachtungen | ≥5 Min. | ≥15 Min. | ≥60 Min. | Ausfall |
| ------ | ------------: | ------: | -------: | -------: | ------: |
| S      |       828.870 | 12,51 % |   2,01 % |   0,04 % |  6,13 % |
| RB     |       275.665 | 15,61 % |   3,37 % |   0,12 % |  3,72 % |
| RE     |       355.990 | 24,84 % |   7,89 % |   0,42 % |  3,63 % |
| IC     |        34.501 | 36,58 % |  17,58 % |   2,12 % |  6,12 % |
| ICE    |       157.366 | 40,53 % |  19,85 % |   2,40 % |  6,87 % |

Die betrachteten Zugtypen zeigen deutliche Unterschiede bei den Verspätungskennzahlen.

Bei ICE und IC ist insbesondere der Anteil stärkerer Verspätungen höher als bei S-, RB- und RE-Verkehren.

Die Zugtypen unterscheiden sich jedoch strukturell hinsichtlich Streckenlänge, Haltemuster, Einsatzgebiet und Fahrplan. Daher werden die Unterschiede deskriptiv dargestellt und nicht als kausaler Effekt des Zugtyps interpretiert.

---

## 7. Analyse nach Tageszeit

Für die zeitliche Analyse wird die geplante Ereigniszeit verwendet.

Die Ergebnisse zeigen ein unterschiedliches Muster für kleinere und sehr lange Verspätungen:

* Verspätungen ab 5 Minuten treten besonders häufig am späten Nachmittag und frühen Abend auf.
* Der höchste Anteil von ≥5 Minuten wurde um **17:00 Uhr mit 23,26 %** beobachtet.
* Sehr lange Verspätungen ab 60 Minuten weisen dagegen höhere Anteile in den Nachtstunden auf.
* Besonders hohe Werte zeigen sich zwischen **00:00 und 03:00 Uhr**.

Die Ergebnisse müssen nach Zugtyp und Beobachtungszahl interpretiert werden, da sich die Zusammensetzung des Verkehrs über den Tag verändert.

---

## 8. Analyse nach Wochentag

Auch zwischen den Wochentagen zeigen sich Unterschiede.

Der Anteil der Beobachtungen mit mindestens 5 Minuten Verspätung lag im März 2025 bei:

| Wochentag  | ≥5 Min. | ≥15 Min. | ≥60 Min. |
| ---------- | ------: | -------: | -------: |
| Montag     | 19,56 % |   5,72 % |   0,41 % |
| Dienstag   | 19,82 % |   5,86 % |   0,59 % |
| Mittwoch   | 20,85 % |   6,04 % |   0,42 % |
| Donnerstag | 20,86 % |   6,11 % |   0,49 % |
| Freitag    | 20,93 % |   6,15 % |   0,46 % |
| Samstag    | 15,43 % |   4,63 % |   0,34 % |
| Sonntag    | 13,83 % |   4,22 % |   0,32 % |

Der Anteil stärkerer Verspätungen ab 5 bzw. 15 Minuten liegt an Werktagen höher als am Wochenende.

Für Verspätungen ab 60 Minuten ist der Unterschied zwischen den Wochentagen deutlich geringer.

---

## 9. Analyse der Ersatzverkehre

Die Daten enthalten seit der späteren Datenrevision ein Merkmal für Ersatzverkehre:

```text
is_replacement_train
```

Im März 2025 wurden insgesamt **14.504 Ersatzverkehr-Beobachtungen** identifiziert.

Zum Vergleich:

|                 | Reguläre Beobachtungen | Ersatzverkehr |
| --------------- | ---------------------: | ------------: |
| Beobachtungen   |              1.990.417 |        14.504 |
| Anteil ≥5 Min.  |                18,66 % |       26,39 % |
| Anteil ≥15 Min. |                 5,47 % |       12,03 % |
| Anteil ≥60 Min. |                 0,42 % |        1,59 % |

Ersatzverkehr-Beobachtungen weisen damit in den betrachteten Daten höhere Anteile stärkerer Verspätungen auf.

Die Ergebnisse zeigen eine statistische Auffälligkeit, erlauben jedoch keine Aussage darüber, dass Ersatzverkehr die Ursache der höheren Verspätungen ist.

Bei rund 80,5 % der Ersatzverkehr-Beobachtungen ist außerdem eine `replaced_train_number` vorhanden.

---

## 10. Monatliche Entwicklung 2025

Die monatliche Entwicklung wurde für Januar bis Dezember 2025 untersucht.

| Monat | P95 | ≥5 Min. | ≥15 Min. | ≥60 Min. | Ausfall | Ersatzverkehr |
| ----- | --: | ------: | -------: | -------: | ------: | ------------: |
| Jan   |  15 | 18,23 % |   5,39 % |   0,47 % |  4,46 % |        0,59 % |
| Feb   |  16 | 18,55 % |   5,46 % |   0,43 % |  4,63 % |        0,61 % |
| Mär   |  16 | 18,72 % |   5,52 % |   0,43 % |  4,84 % |        0,72 % |
| Apr   |  17 | 19,86 % |   6,09 % |   0,55 % |  5,40 % |        0,92 % |
| Mai   |  18 | 20,32 % |   6,34 % |   0,53 % |  4,43 % |        0,53 % |
| Jun   |  20 | 21,87 % |   7,20 % |   0,68 % |  5,82 % |        0,75 % |
| Jul   |  20 | 22,31 % |   7,35 % |   0,91 % |  6,26 % |        0,89 % |
| Aug   |  18 | 21,26 % |   6,59 % |   0,60 % |  4,90 % |        0,67 % |
| Sep   |  20 | 23,78 % |   7,58 % |   0,66 % |  5,12 % |        0,56 % |
| Okt   |  22 | 26,73 % |   8,79 % |   0,74 % |  5,04 % |        0,40 % |
| Nov   |  22 | 26,71 % |   8,68 % |   0,74 % |  4,80 % |        0,45 % |
| Dez   |  19 | 22,11 % |   6,99 % |   0,54 % |  4,69 % |        0,46 % |

Der Median blieb über das gesamte Jahr bei **1 Minute**.

Gleichzeitig stiegen P95 und die Anteile stärkerer Verspätungen im Jahresverlauf deutlich an. Der höchste Anteil ab 5 Minuten wurde im Oktober mit **26,73 %** beobachtet.

Die Ergebnisse zeigen somit vor allem eine Veränderung im oberen Bereich der Verspätungsverteilung, während der Median relativ stabil blieb.

---

## 11. Zentrale Erkenntnisse

Aus der KPI-Analyse ergeben sich mehrere zentrale Beobachtungen:

1. **Die typische Verspätung ist gering.**
   Der Median liegt im untersuchten Zeitraum bei 1 Minute.

2. **Stärkere Verspätungen sind deutlich häufiger als der Median allein vermuten lässt.**
   P95 und die Schwellenwerte ≥5, ≥15 und ≥60 Minuten zeigen einen relevanten oberen Bereich der Verteilung.

3. **Bahnhöfe unterscheiden sich deutlich.**
   Der Anteil stärkerer Verspätungen variiert zwischen den untersuchten Bahnhöfen erheblich.

4. **Auch zwischen Zugtypen bestehen deutliche Unterschiede.**
   Besonders bei ICE und IC sind stärkere Verspätungen in den untersuchten Daten häufiger.

5. **Verspätungen zeigen ein zeitliches Muster.**
   Kleinere Verspätungen ab 5 Minuten treten besonders am späten Nachmittag und frühen Abend auf, während sehr lange Verspätungen häufiger in den Nachtstunden beobachtet werden.

6. **Werktage weisen höhere Anteile stärkerer Verspätungen auf als Wochenenden.**

7. **Ersatzverkehr-Beobachtungen zeigen höhere Verspätungsanteile.**
   Dieser Zusammenhang wird deskriptiv dargestellt und nicht als kausaler Zusammenhang interpretiert.

8. **Die monatliche Entwicklung 2025 zeigt eine Zunahme stärkerer Verspätungen im Jahresverlauf.**
   Gleichzeitig blieb der Median stabil.

---

## 12. Limitationen

Die Ergebnisse sind deskriptiv und erlauben keine Aussage über die Ursachen der beobachteten Verspätungen oder Ausfälle.

Weitere wichtige Einschränkungen:

* Die Daten enthalten Beobachtungen auf Ebene geplanter Bahnhofsevents und nicht eindeutig identifizierte physische Zugfahrten.
* `train_line_ride_id` beschreibt wiederkehrende Fahrplanmuster und darf nicht direkt als Anzahl einzelner Zugfahrten interpretiert werden.
* Sehr große negative Werte in `delay_in_min` wurden als Data-Quality-Thema untersucht und nicht ohne weitere Validierung aus den Rohdaten entfernt.
* Die Analyse verwendet deshalb robuste Kennzahlen wie Median, P95 und Schwellenwerte anstelle eines einzelnen Durchschnittswerts.
* Die Daten enthalten unterschiedliche Verkehrsstrukturen nach Bahnhof, Zugtyp und Tageszeit. Direkte Vergleiche müssen daher im jeweiligen Kontext interpretiert werden.


Die Rohdaten wurden für die Analyse nicht verändert. Datenqualitätsprobleme und strukturelle Einschränkungen werden transparent dokumentiert und bei der Interpretation der Ergebnisse berücksichtigt.
