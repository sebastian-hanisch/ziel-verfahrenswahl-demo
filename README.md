# Welches Ziel? – Streamlit-Demo (Verfahrenswahl)

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-ziel-verfahrenswahl-demo.streamlit.app/)** -->

Stück 14 von 14 (Abschluss) der Linie **Zielfunktionsdesign** („Das Ziel ist das Modell“) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (Arbeitsname; Name, Bereich und Themenfeld werden erst bei der Einbindung in die Website festgelegt). Die Stücke [1, Dasselbe Problem, drei Ziele](https://github.com/sebastian-hanisch/zielvergleich-demo), [2, Preis der Fairness](https://github.com/sebastian-hanisch/preis-der-fairness-demo), [3, Zwei Kriterien](https://github.com/sebastian-hanisch/zwei-kriterien-demo), [4, Lexikographisch](https://github.com/sebastian-hanisch/lexikographisch-demo), [5, Gleichstände](https://github.com/sebastian-hanisch/gleichstand-demo), [6, Hart gegen weich](https://github.com/sebastian-hanisch/hart-gegen-weich-demo), [8, Goodhart-Kurve](https://github.com/sebastian-hanisch/goodhart-kurve-demo), [9, Lücken ausnutzen](https://github.com/sebastian-hanisch/modellluecken-demo), [10, Verlagerung](https://github.com/sebastian-hanisch/verlagerung-demo), [11, Planstabilität](https://github.com/sebastian-hanisch/planstabilitaet-demo) und [13, Zielkarte](https://github.com/sebastian-hanisch/zielkarte-demo) haben je ein Ziel oder eine Prüfung geliefert (Stück 7 und 12 sind zurückgestellt). Dieses Stück **rechnet nichts Neues**: es stellt die Ziele auf derselben Zuordnung nebeneinander und fragt, **welches Ziel und welche Gleichstandsregel wofür taugen, gemessen woran**. Alles ist **simuliert**; keine Aussage über echte Zuordnungsprobleme.

## Warum dieses Problem

Die Stücke 1 bis 13 haben fünf Ziele angesammelt (Summe, Quadratsumme, Maximum, und zwei Zweistufen-Ziele), eine Gleichstandsfrage, eine Stabilitätsfrage und eine Prüfung. Hier steht die Frage, die man vor einer Aufgabe stellt: **Welches nehme ich, und was kostet mich die Wahl?** Wie in den anderen Abschlussstücken der Konzepte-Reihen steht die **Regel vor der Messung**, und die Messung sagt, wo sie hält. Die Antwort dieser Messung: **kein Ziel gewinnt überall, aber die Wahl ist weniger frei, als sie aussieht**: das Maximum allein ist nie zu empfehlen, die Summe braucht ihre Gleichstandsregel nur bei groben Daten, und die Stabilität eines Plans wählt man nicht über das Ziel.

## Modell

Gegeben `n` Personen und `n` Aufgaben, eine Belastungsmatrix `c` aus ganzen Zahlen; ein Plan ist eine Zuordnung (Permutation), die Belastung der Person `i` ist `c[i][p(i)]`; **alle `n!` Pläne werden aufgezählt** (bis `8! = 40 320`), alles exakt in ganzen Zahlen. **Fünf Ziele:** **Summe** (S), **Quadratsumme** (Q), **Maximum** (M, bei Gleichstand der kleinste Index), **Maximum, dann Summe** (L, lexikographisch) und **Summe, dann Maximum** (T, lexikographisch). **Aufschlag** eines Plans: Summe beziehungsweise Maximum gegen das jeweils Beste über alle Pläne. **Beide Maße gut:** Summe und Maximum innerhalb von 5 % des jeweils Besten. **Dominanz:** der Plan eines Ziels dominiert den eines anderen, wenn er in keinem Maß schlechter und in einem besser ist. **Stabilität:** jede Zahl der Matrix ändert sich um eine ganze Zahl von `−a` bis `+a` (mindestens 1); der **Bestandsplan** ist der Plan des Ziels bei den Ausgangskosten; er ist nicht mehr optimal, wenn sein Zielwert bei den neuen Kosten über dem Optimum liegt. Für `n = 30` lösen die Ungarische Methode (Summe, Quadratsumme) und das Engpassverfahren (Maximum, Maximum dann Summe) exakt; dort ist der Bestandsplan ein Optimalplan des Lösers. **Die Regel** (`zlw_rule.py`, reine Funktion): Anforderung, Daten und Wunsch nach Eindeutigkeit → Ziel und Gleichstandsregel. Formeln stehen im 📐-Expander der App.

## Methodik

Drei Kostenfamilien: **unabhängig** (11 bis 109), **grob** (1 bis 9, viele Gleichstände) und **Personeneffekt** (0 bis 40 plus 11 bis 69). Die App zeigt den Entscheidungsweg (die Regel mit Verweisen auf die Stücke), die fünf Ziele nebeneinander (Plan, Belastungen, Summe, Maximum, Aufschläge, Optimalpläne, „beide Maße gut“, Punktwolke aller Pläne), die Gleichstandsregel (Optimalpläne und Spanne der Summe darin) und die Stabilität. Zählungen über 20 feste Instanzen je Familie (`n` = 8, alle 40 320 Pläne; Stabilität zusätzlich `n` = 30) und eine zweite Menge (Seeds 100100 bis 100119) für die Regel liegen hinter Schaltern. Verdikte entstehen live aus der Rechnung, jede Zahl im Text kommt aus dem Ergebnis.

## Die Regel (vor der Messung gesetzt)

| Anforderung | Empfehlung | Belegt in |
|---|---|---|
| Gesamtaufwand klein | **Summe, dann Maximum**: die zweite Stufe kostet nichts und löst die Gleichstände der Summe | Stück 1, 2 |
| niemand überlastet | **Maximum, dann Summe**, nie das Maximum allein | Stück 2, 4, 5 |
| ausgewogen | **Quadratsumme**, wenn ein eindeutiger Plan zählt; sonst **Maximum, dann Summe** | Stück 1, 2, 5 |
| stabiler Plan | **kein Ziel**: Wechselkosten statt Zielwechsel | Stück 11 |
| immer | vor dem Einsatz den Extremwert-Test auf nicht gemessene Größen | Stück 13 |
| grobe Daten | die Gleichstandsregel ist wichtiger als die Wahl des Ziels | Stück 5 |

Die Zeile „ausgewogen“ war in der ersten Fassung „Quadratsumme“; die Messung hat sie zweigeteilt (siehe Korrektur).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stammen aus den Auswertungsfunktionen der App und sind in `tests/test_claims.py` nachgerechnet. „Je 20 feste Instanzen“ heißt `SWEEP_SEEDS` (Seeds 100000 bis 100019), nie ein einzelner Seed; die Zahlen sind **Zählungen und Spannen über Instanzen**, kein Satz und keine Aussage über andere Instanzen. Soweit nicht anders angegeben `n` = 8 (alle 40 320 Pläne). Familien: unabhängig / grob / Person. Ziele: S / Q / M / L (Maximum, dann Summe) / T (Summe, dann Maximum). Rauschen ±5, bei groben Daten ±1.

| Frage | Befund |
|---|---|
| Summe höher als die beste Summe (Median; Maximum in Klammern, %) | unabhängig 0,0 (0,0) / 0,0 (7,1) / **3,6** (35,7) / 0,0 (10,8) / 0,0 (0,0); grob 0,0 (0,0) / 0,0 (5,6) / **15,0** (33,3) / 0,0 (5,6) / 0,0 (0,0); Person 0,0 (0,0) / 0,0 (2,8) / **10,3** (36,6) / 0,0 (5,4) / 0,0 (0,0) |
| Maximum höher als das beste Maximum (Median; Maximum in Klammern, %) | unabhängig 0,0 (**40,8**) / 0,0 (22,2) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (40,8); grob 0,0 (**50,0**) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (50,0); Person 0,0 (**28,8**) / 0,0 (15,9) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (28,8) |
| Optimalpläne (Median; Maximum in Klammern) und Instanzen mit eindeutigem Optimum (von 20) | unabhängig 1 (2), 18 / 1 (1), **20** / 2 (61), **4** / 1 (2), 18 / 1 (2), 18; grob 2,5 (9), 7 / 1 (6), 13 / 13 (69), **1** / 1,5 (6), 10 / 2 (6), 9; Person 1 (2), 18 / 1 (2), 19 / 14,5 (460), **1** / 1 (2), 17 / 1 (2), 19 |
| Spanne der Summe in der Optimalmenge des Maximums allein (Median; Minimum bis Maximum, %; Instanzen mit mehr als einem Optimalplan) | unabhängig 11,3 (0,5 bis 46,6; 16), grob 38,5 (7,7 bis 57,1; 19), Person 17,3 (3,8 bis 64,2; 19) |
| Summe und Maximum zugleich innerhalb von 5 % des jeweils Besten (von 20) | unabhängig 13 / **17** / 11 / **17** / 13; grob 15 / **18** / 5 / **18** / 17; Person 14 / **17** / 4 / **19** / 14 |
| Dominanz der Pläne (Instanzen von 20): Max → Summe über Maximum / Quadrat über Maximum / Summe über Maximum | unabhängig **11** / 10 / 8; grob **15** / 15 / 11; Person **17** / 14 / 12 |
| dabei: Maximum allein über Max → Summe; Maximum über Quadrat; Summe über Quadrat; Quadrat über Summe | **0** in jeder Familie; unabhängig 0, grob 0, Person 1; 0 / 0 / 2; 0 / 2 / 0 |
| Garantien aus der Konstruktion (Instanzen von 60) | Max → Summe nie schlechter als das Maximum allein (gleiches Maximum, Summe nie größer): **60**; Summe → Max nie schlechter als die Summe (gleiche Summe, Maximum nie größer): **60** |
| Stabilität, `n` = 8: Bestandsplan nicht mehr optimal (% der Ziehungen, gesamt), S / Q / M / L / T | unabhängig ±5: 38,2 / 33,8 / 33,0 / 42,8 / 38,5; grob ±1: 66,8 / 70,0 / 49,8 / 65,5 / 68,2; Person ±5: 49,5 / 45,5 / 40,5 / 54,5 / 50,0 |
| Stabilität, `n` = 30 (Ungarische Methode, Engpassverfahren), S / Q / M / L | unabhängig ±5: 99,0 / 98,5 / 88,2 / 97,8; grob ±1: 100,0 / 100,0 / 91,7 / 100,0; Person ±5: 100,0 / 100,0 / 96,0 / 100,0 |
| **Hold-out** (Seeds 100100 bis 100119): Max → Summe über Maximum / Maximum allein über Max → Summe (von 20) | **13 / 14 / 16** und **0 / 0 / 0** |
| Hold-out: Summe höher beim Maximum allein (Median; %) | unabhängig 14,8, grob 17,2, Person 13,2 |
| Hold-out: eindeutiges Optimum, S / Q / M / L / T (von 20) | unabhängig 20 / 20 / 2 / 20 / 20; grob 8 / **15** / 1 / 11 / 12; Person 18 / **20** / 1 / 20 / 18 |
| Hold-out: beide Maße innerhalb von 5 %, S / Q / M / L / T (von 20) | unabhängig 13 / 17 / 7 / 14 / 13; grob 13 / 17 / 5 / 17 / 16; Person 12 / 14 / 3 / 16 / 13 |
| Preset „Kein Ziel gewinnt überall“ (Seed 100007) | die fünf Ziele wählen **4** verschiedene Pläne: Summe 244 und Maximum 69 (S), 250 und 49 (Q), 331 und 49 (M); S im Maximum **40,8 %**, M in der Summe **35,7 %** schlechter; M hat **6** Optimalpläne |
| Preset „Das Maximum allein hat viele Optimalpläne“ (grob, Seed 100022) | **97** Optimalpläne, die Summe des Maximum-Plans **29,4 %** über der besten; Summe und Max → Summe wählen den besten Plan |
| Preset „Alle Ziele wählen denselben Plan“ (Seed 100000) | ein Plan für alle fünf Ziele (Summe 204, Maximum 38) von 40 320 |
| Preset „Ausgewogen und eindeutig“ (Seed 100010) | Quadratsumme **1** Optimalplan, Max → Summe 2, Maximum allein 10 |
| Preset „Stabiler Plan: das Ziel hilft nicht“ (Seed 100020, ±5) | der Bestandsplan ist bei jedem Ziel in **7 bis 15** von 20 Ziehungen nicht mehr optimal |
| Preset „Das Maximum allein wird dominiert“ (Seed 100020) | Max → Summe (Summe 231, Maximum 51) dominiert das Maximum allein (290, 51; **34** Optimalpläne) |
| Preset „Die Summe ist unfair“ (Seed 100001) | Summenplan 209, sein Maximum **40,0 %** über dem besten; Max → Summe kostet **0,5 %** mehr Summe und senkt das Maximum auf 35 |
| Preset „Kleinstes Beispiel (4 Personen)“ (Seed 100020) | 24 Pläne, **3** verschiedene gewählt; Quadratsumme 3,4 % mehr Summe, Maximum am besten |

**Korrektur der Regel:** Die erste Fassung der Regel hielt die Quadratsumme für den Allrounder („ausgewogen“). Gemessen sind **Quadratsumme und „Maximum, dann Summe“ bei „beide Maße gut“ gleichauf** (17 / 18 / 17 gegen 17 / 18 / 19 von 20); der Unterschied ist die **Eindeutigkeit** (Quadratsumme 20 / 13 / 19 gegen 18 / 10 / 17). Im Hold-out liegt die Quadratsumme bei „beide Maße gut“ in einer Familie vorn, in einer gleichauf und in einer hinten (17 / 17 / 14 gegen 14 / 17 / 16) und bei der Eindeutigkeit mindestens gleichauf, bei groben Daten klar vorn (20 / 15 / 20 gegen 20 / 11 / 20); dort kostet „Maximum, dann Summe“ im Median bis 1,7 % mehr Summe (Quadratsumme 0,0 %). Die Zeile ist deshalb zweigeteilt: Quadratsumme, wenn ein eindeutiger Plan zählt, sonst „Maximum, dann Summe“. Die übrigen Zeilen halten in beiden Mengen: das Maximum allein wird nie empfohlen (der Plan von „Maximum, dann Summe“ ist in jeder der 60 Instanzen nicht schlechter und dominiert ihn in 11 / 15 / 17 von 20, im Hold-out in 13 / 14 / 16; umgekehrt nie), die Gleichstandsregel der Summe kostet nie etwas (60 von 60) und hilft bei groben Daten (eindeutig 7 → 9, im Hold-out 8 → 12), und die Stabilität hängt kaum am Ziel (`n` = 8: 33,0 bis 42,8 % bei unabhängigen Kosten, 49,8 bis 70,0 % bei groben, 40,5 bis 54,5 % bei Person; `n` = 30: 88,2 bis 100,0 %). Der kleinere Anteil beim Maximum allein geht mit einer großen Optimalmenge einher (Median 2 / 13 / 14,5 Optimalpläne); ob das die Ursache ist, ist nicht gemessen. Von der Literatur ist nichts gelesen und nichts zitiert (siehe „Ehrliche Grenzen“).

## Ehrliche Grenzen

- **Ein Beispiel:** Die Regel ist an der Zuordnung gemessen; andere Probleme haben andere Ziele. Zwei-Kriterien-Fälle (Stück 3) und Strafterme (Stück 6) sind nicht Teil des Portfolios.
- **„Fair“ heißt Maximum:** Das Maximum der Belastung ist eine Wahl; andere Maße (Gini, α-Fairness) sind nicht gemessen.
- **Regel und Messung am selben Material:** Die Regel wurde an denselben 20 Instanzen je Familie gebildet, an denen sie gemessen wird; der Hold-out an zweiten Seeds hält die Zeilen, relativiert aber „Quadratsumme gegen Maximum, dann Summe“ (bei „beide Maße gut“ mal vorn, mal hinten).
- **Stabilität nur mit additivem Rauschen:** gleichverteilt, je Zahl unabhängig; für `n` = 30 ist der Bestandsplan ein Optimalplan des Lösers, Gleichstände werden dort nicht aufgelöst.
- **Alle Pläne aufgezählt:** bis 40 320 (`n` = 8); größere Zuordnungen nur für die Stabilitätszählung mit Lösern.
- **Gleichstand: kleinster Index:** Beim Maximum allein entscheidet die Regel, nicht das Ziel; die Wahl ändert sich mit der Nummerierung (Stück 5).
- **Keine Literatur:** Zu α-Fairness und zum Preis der Fairness sind nur Suchtreffer bekannt; die Demo übernimmt daraus nichts.
- **Kein Satz:** Die Zahlen sind Zählungen über 20 feste Instanzen je Familie, nicht allgemein.

## Verifikation

Insgesamt 362 Tests (`pytest tests/`), alle grün.

- **Kern:** Handbeispiel (`n` = 4 aus Stück 1: drei verschiedene eindeutige Optima, Aufschläge 7,1 / 14,3 / 40,0 / 20,0 %, drei Pareto-Punkte) von Hand; Ziele, Wahl, Optimalmengen, Aufschläge, „beide Maße gut“, Dominanz und die Stabilität gegen reines Python (`itertools.permutations`, Schleifen); Ungarische Methode und Engpassverfahren gegen die Aufzählung.
- **Regel:** jede der 16 Kombinationen der Eingaben, jede Zeile, nie das Maximum allein, der Wunsch nach Eindeutigkeit nur bei „ausgewogen“, Hinweise, Verweise auf die Stücke, ungültige Eingaben.
- **Eigenschaften:** jedes Ziel ist in seinem eigenen Maß optimal; „Maximum, dann Summe“ nie schlechter als das Maximum allein (Optimalmenge eine Teilmenge); „Summe, dann Maximum“ nie schlechter als die Summe; Dominanz nie umgekehrt; Umnummerieren der Personen ändert die Optimalwerte nicht; Determinismus.
- **Randfälle:** alle Kosten gleich, ein einziger Plan, ein Plan in beiden Maßen am besten, jede Familie mal jede Größe, jeder Regler an den Grenzen, Aufzählungsgrenze, große Zuordnungen.
- **Verdikte:** reine Funktionen, jede Verzweigung und jede Zahl im Text an Hand- oder Presetwerten (`tests/test_verdicts.py`).
- **Presets:** Vollständigkeit, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung, kein anderes Preset gleich den Voreinstellungen, und dass jedes Preset zeigt, was sein Name sagt.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), jedes Preset, jede Anforderung, jede Familie, alle Zählungen und der Hold-out, Footer-Test, Layout.
- **Claims:** jede Zahl dieser README in `tests/test_claims.py`.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Entscheidungsweg, Ziele nebeneinander, Zählung, Gleichstandsregel, Stabilität |
| `zlw_rule.py` | Die Regel: Anforderung, Daten, Eindeutigkeit → Ziel und Gleichstandsregel (reine Funktion) |
| `zlw_algorithm.py` | Kern: Aufzählung, fünf Ziele, Wahl, Dominanz, „beide Maße gut“, Rauschen; Ungarische Methode und Engpassverfahren |
| `zlw_evaluation.py` | Die Ziele nebeneinander, Stabilität, Zählungen, Verdikte |
| `zlw_scenario.py` | Belastungsmatrizen der drei Familien |
| `zlw_constants.py` | Regler-Grenzen, Ziele, Zählungen, Farben, Presets |
| `zlw_layout.py` | Fester Kopf (Stylesheet) |
| `zlw_pdf_export.py` | PDF-Export der Empfehlung |
| `zlw_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `zlw_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handbeispiel, Orakel, Regel, Eigenschaften, Randfälle, Verdikte, Presets, Claims, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Keine neue Messung der Ziele:** Preis der Fairness, Zwei-Kriterien-Pareto, Strafterme und Goodhart-Kurve stehen in den Stücken 2, 3, 6 und 8; hier nur das Nebeneinander.
- **Keine Wahl des Lösers:** Alle Ziele sind exakt lösbar (Aufzählung, Ungarische Methode, Engpassverfahren).
- **Keine Gewichtung der Anforderungen:** Die Regel ordnet jeder Anforderung ein Ziel zu; ein Gewichtsregler wäre selbst wieder ein Ziel (Stück 3).
- **Keine Nachbauten der Literatur.**

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und SciPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
