"""Die Entscheidungsregel: aus Anforderung, Daten und Eindeutigkeit das Ziel und die Gleichstandsregel. Eine reine Funktion, ohne Rechnung.

Die Regel steht VOR der Messung; die Messung (README, Zählungen der App) prüft jede Zeile und sagt, wo sie hält. Gemessen an Zuordnungen mit n = 8, drei Familien, 20 festen Instanzen:
  * Gesamtaufwand klein: Summe, dann Maximum (T). Die zweite Stufe kostet in der Summe nie etwas und löst die Gleichstände der Summe.
  * Niemand überlastet: Maximum, dann Summe (L), nie das Maximum allein (der Plan von L dominiert den des Maximums allein, nie umgekehrt).
  * Ausgewogen: Quadratsumme (Q), wenn ein eindeutiger Plan zählt; sonst Maximum, dann Summe (beide halten Summe und Maximum zugleich gleich oft innerhalb von 5 % des Besten).
  * Stabiler Plan: kein Ziel; Wechselkosten statt Zielwechsel (Stück 11), denn der Bestandsplan hält bei jedem Ziel ähnlich schlecht.
  * Immer: vor dem Einsatz den Extremwert-Test auf nicht gemessene Größen (Stück 13).
  * Grobe Daten: die Gleichstandsregel ist wichtiger als die Wahl des Ziels (Stück 5)."""

from __future__ import annotations

from dataclasses import dataclass

import zlw_constants as C

PIECES = {
    1: ("Stück 1", "zielvergleich-demo"), 2: ("Stück 2", "preis-der-fairness-demo"), 3: ("Stück 3", "zwei-kriterien-demo"), 4: ("Stück 4", "lexikographisch-demo"), 5: ("Stück 5", "gleichstand-demo"),
    6: ("Stück 6", "hart-gegen-weich-demo"), 8: ("Stück 8", "goodhart-kurve-demo"), 9: ("Stück 9", "modellluecken-demo"), 10: ("Stück 10", "verlagerung-demo"), 11: ("Stück 11", "planstabilitaet-demo"),
    13: ("Stück 13", "zielkarte-demo"),
}


@dataclass(frozen=True)
class Step:
    question: str
    answer: str
    pieces: tuple          # Nummern der Stücke, die die Antwort belegen


@dataclass(frozen=True)
class Advice:
    priority: int
    data: str
    unique: int
    goal: str | None       # Schlüssel des Ziels (C.GOALS) oder None, wenn kein Ziel entscheidet
    label: str
    tie_rule: str
    steps: tuple
    notes: tuple


def advise(priority: int, data: str, unique: int = 0) -> Advice:
    """Empfehlung für die Anforderung `priority` (Index in C.PRIORITIES), die Daten (`fein` / `grob`) und die Eindeutigkeit (0 egal, 1 ein eindeutiger Plan muss es sein)."""
    if priority not in range(len(C.PRIORITIES)) or data not in ("fein", "grob") or unique not in (0, 1):
        raise ValueError((priority, data, unique))
    steps, notes = [], []
    if priority == 0:
        goal, label = "T", "Summe, dann Maximum"
        tie = "Die zweite Stufe (Maximum) löst die Gleichstände der Summe und kostet in der Summe nichts."
        steps.append(Step("Was zählt?", "Der Gesamtaufwand: die Summe der Belastungen.", (1, 2)))
    elif priority == 1:
        goal, label = "L", "Maximum, dann Summe"
        tie = "Die zweite Stufe (Summe) löst die Gleichstände des Maximums; das Maximum allein wird von diesem Ziel dominiert und gehört nicht in die engere Wahl."
        steps.append(Step("Was zählt?", "Niemand darf überlastet sein: das Maximum der Belastungen.", (2, 4, 5)))
    elif priority == 2:
        if unique:
            goal, label = "Q", "Quadratsumme"
            tie = "Die Quadratsumme hat am seltensten mehrere Optimalpläne; eine Gleichstandsregel braucht sie kaum."
        else:
            goal, label = "L", "Maximum, dann Summe"
            tie = "Summe und Maximum zugleich gelingen hier ebenso oft wie bei der Quadratsumme, und das Maximum ist garantiert optimal."
        steps.append(Step("Was zählt?", "Beides ungefähr: Summe und Maximum zugleich nahe am Besten.", (1, 2)))
        steps.append(Step("Muss der Plan eindeutig sein?", "Ja: die Quadratsumme." if unique else "Nein: Maximum, dann Summe.", (5,)))
    else:
        goal, label = None, "kein Ziel entscheidet"
        tie = "Stabilität kaufen Wechselkosten (eine Strafe je geänderte Zuordnung), nicht ein anderes Ziel."
        steps.append(Step("Was zählt?", "Ein stabiler Plan: er soll sich bei kleinen Änderungen der Kosten nicht ändern.", (11,)))
    steps.append(Step("Wie grob sind die Daten?", "Grob: wenige verschiedene Werte, viele Gleichstände." if data == "grob" else "Fein: viele verschiedene Werte, Gleichstände sind selten.", (5,)))
    steps.append(Step("Vor dem Einsatz", "Den Extremwert-Test auf Größen laufen lassen, die das Ziel nicht misst.", (13,)))
    if data == "grob" and priority != 3:
        notes.append("Grobe Daten: Die Gleichstandsregel ist wichtiger als die Wahl des Ziels; das Maximum allein hat hier besonders viele Optimalpläne.")
    if priority == 0 and data == "fein":
        notes.append("Bei feinen Daten ist die Gleichstandsregel der Summe fast wirkungslos, sie schadet aber nicht.")
    if priority == 3:
        notes.append("Die Wahl des Ziels ändert an der Stabilität wenig: der Bestandsplan hält bei jedem Ziel ähnlich schlecht.")
    return Advice(priority, data, unique, goal, label, tie, tuple(steps), tuple(notes))
