"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

N_MIN, N_MAX, DEFAULT_N = 4, 8, 8             # Zuordnung n mal n; alle n! Pläne werden aufgezählt (bis 8! = 40 320)
SEED_MAX, DEFAULT_SEED = 999999, 100007
FAMILIES = ("Kosten unabhängig 11 bis 109", "Kosten grob 1 bis 9", "Personeneffekt")
DEFAULT_FAMILY = 0
FAMILY_DATA = {0: "fein", 1: "grob", 2: "fein"}   # grobe Daten: wenige verschiedene Werte, viele Gleichstände

GOALS = ("S", "Q", "M", "L", "T")
GOAL_NAMES = {"S": "Summe", "Q": "Quadratsumme", "M": "Maximum (Gleichstand beliebig)", "L": "Maximum, dann Summe", "T": "Summe, dann Maximum"}
GOAL_SHORT = {"S": "Summe", "Q": "Quadrat", "M": "Maximum", "L": "Max → Summe", "T": "Summe → Max"}
LARGE_GOALS = ("S", "Q", "M", "L")            # für n = 30 gelöst (T wird nur aufgezählt)
LEX = 100000                                  # Gewicht der ersten Stufe der lexikographischen Ziele (Belastungen und Summen bleiben darunter)
BOTH_PCT = 5                                  # „beide Maße gut“: Summe und Maximum innerhalb dieser Prozent des jeweils Besten

PRIORITIES = ("Gesamtaufwand klein", "niemand überlastet", "ausgewogen", "stabiler Plan")
DEFAULT_PRIORITY = 1
UNIQUE_OPTIONS = ("nein", "ja")
DEFAULT_UNIQUE = 0
A_MIN, A_MAX, A_STEP, DEFAULT_A = 1, 10, 1, 5  # Rauschen: jede Zahl der Matrix ändert sich um -a bis +a ganze Einheiten
NOISE_DRAWS = 20                              # Ziehungen je Instanz

SWEEP_SEEDS = tuple(range(100000, 100020))    # feste Instanzen für alle Zählungen: nie ein einzelner Seed als Befund
HOLDOUT_SEEDS = tuple(range(100100, 100120))  # zweite Seed-Menge: die Regel wurde an SWEEP_SEEDS gebildet, hier gegengeprüft
SWEEP_FAMILIES = (0, 1, 2)
SWEEP_N = 8
SWEEP_LARGE_N = 30
SWEEP_NOISE = {0: 5, 1: 1, 2: 5}              # Rauschen je Familie (bei groben Daten ±1)

COLOR_ALL = "rgba(150,150,150,0.35)"
GOAL_COLORS = {"S": "#4c78a8", "Q": "#7b5ea7", "M": "#c0504d", "L": "#2F6B65", "T": "#d8a13a"}

PRESETS = {
    "Kein Ziel gewinnt überall": {"n": 8, "family": 0, "seed": 100007, "priority": 1, "unique": 0, "a": 5},
    "Das Maximum allein hat viele Optimalpläne": {"n": 8, "family": 1, "seed": 100022, "priority": 1, "unique": 0, "a": 1},
    "Alle Ziele wählen denselben Plan": {"n": 8, "family": 0, "seed": 100000, "priority": 1, "unique": 0, "a": 5},
    "Ausgewogen und eindeutig": {"n": 8, "family": 0, "seed": 100010, "priority": 2, "unique": 1, "a": 5},
    "Stabiler Plan: das Ziel hilft nicht": {"n": 8, "family": 0, "seed": 100020, "priority": 3, "unique": 0, "a": 5},
    "Das Maximum allein wird dominiert": {"n": 8, "family": 0, "seed": 100020, "priority": 1, "unique": 0, "a": 5},
    "Die Summe ist unfair": {"n": 8, "family": 0, "seed": 100001, "priority": 0, "unique": 0, "a": 5},
    "Kleinstes Beispiel (4 Personen)": {"n": 4, "family": 0, "seed": 100020, "priority": 2, "unique": 1, "a": 5},
}
PRESET_HELP = {
    "Kein Ziel gewinnt überall": "Die fünf Ziele wählen 4 verschiedene Pläne; die Summe liegt im Maximum 40,8 % über dem besten, das Maximum allein in der Summe 35,7 % über der besten, und Quadratsumme und „Max → Summe“ dominieren das Maximum allein.",
    "Das Maximum allein hat viele Optimalpläne": "Bei groben Daten (Kosten 1 bis 9) hat das Maximum allein 97 Optimalpläne und wählt einen beliebigen: dessen Summe ist 29,4 % schlechter als die beste; Summe und „Max → Summe“ wählen den besten Plan.",
    "Alle Ziele wählen denselben Plan": "Auf dieser Instanz gibt es keine Wahl: alle fünf Ziele wählen denselben der 40 320 Pläne (Summe 204, Maximum 38).",
    "Ausgewogen und eindeutig": "Für „ausgewogen“ mit eindeutigem Plan empfiehlt die Regel die Quadratsumme: sie hat einen Optimalplan, „Max → Summe“ zwei; das Maximum allein hat 10.",
    "Stabiler Plan: das Ziel hilft nicht": "Für „stabiler Plan“ entscheidet kein Ziel: bei Rauschen ±5 ist der Bestandsplan bei jedem Ziel in 7 bis 15 von 20 Ziehungen nicht mehr optimal; Wechselkosten helfen (Stück 11).",
    "Das Maximum allein wird dominiert": "Der Plan von „Max → Summe“ (Summe 231, Maximum 51) dominiert den des Maximums allein (290, 51), das 34 Optimalpläne hat.",
    "Die Summe ist unfair": "Der Summenplan ist der billigste (Summe 209), sein Maximum liegt aber 40,0 % über dem besten; Quadratsumme und „Max → Summe“ kosten 0,5 % mehr Summe und bringen das Maximum auf 35.",
    "Kleinstes Beispiel (4 Personen)": "Vier Personen, 24 Pläne: drei verschiedene Pläne werden gewählt; die Quadratsumme kostet 3,4 % mehr Summe als das Beste und liegt im Maximum am besten.",
}
