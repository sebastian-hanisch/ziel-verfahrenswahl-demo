"""Verdikte: Art und Wortlaut in den Fällen, die sie unterscheiden (DEMO-PLAYBOOK §6): jede Zahl im Text kommt aus der Rechnung."""

import zlw_constants as C
import zlw_evaluation as ev

(P_NONE, P_TIES, P_SAME, P_BALANCED, P_STABLE, P_DOM, P_UNFAIR, P_SMALL) = list(C.PRESETS)


def _a(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def _advice(name):
    a, s = _a(name), ev.Settings(**C.PRESETS[name])
    adv = ev.advice_for(s)
    return adv, None if adv.goal is None else ev.goal_row(a, adv.goal)


def test_advice_verdict_cases():
    kind, text = ev.verdict_advice(*_advice(P_NONE))
    assert kind == "success" and text == ("Für die Anforderung „niemand überlastet“ (feine Daten) empfiehlt die Regel **Maximum, dann Summe**. "
                                          "Auf dieser Instanz liegt die Summe 2,5 % und das Maximum 0,0 % über dem jeweils Besten; das Ziel hat 2 Optimalpläne.")
    kind, text = ev.verdict_advice(*_advice(P_STABLE))
    assert kind == "info" and text == "Für die Anforderung „stabiler Plan“ entscheidet **kein Ziel**: Stabilität kaufen Wechselkosten (eine Strafe je geänderte Zuordnung), nicht ein anderes Ziel."
    assert "(grobe Daten)" in ev.verdict_advice(*_advice(P_TIES))[1] and "**Quadratsumme**" in ev.verdict_advice(*_advice(P_BALANCED))[1] and "das Ziel hat 1 Optimalplan." in ev.verdict_advice(*_advice(P_BALANCED))[1]
    assert "**Summe, dann Maximum**" in ev.verdict_advice(*_advice(P_UNFAIR))[1] and "das Maximum 40,0 % über" in ev.verdict_advice(*_advice(P_UNFAIR))[1]
    adv, _ = _advice(P_NONE)
    assert ev.verdict_advice(adv, None) == ("success", "Für die Anforderung „niemand überlastet“ (feine Daten) empfiehlt die Regel **Maximum, dann Summe**. " + adv.tie_rule)


def test_goals_verdict_cases():
    kind, text = ev.verdict_goals(ev.table(_a(P_NONE)))
    assert kind == "warning" and text == ("**Kein Ziel gewinnt überall:** die fünf Ziele wählen 4 verschiedene Pläne, keiner ist in Summe und Maximum zugleich am besten. "
                                          "Nicht dominiert sind: Summe, Quadrat, Max → Summe, Summe → Max. Dominiert: Quadrat dominiert Maximum; Max → Summe dominiert Maximum.")
    assert ev.verdict_goals(ev.table(_a(P_SAME))) == ("info", "Alle fünf Ziele wählen denselben Plan: auf dieser Instanz (von 40320 Plänen) gibt es keine Wahl.")
    kind, text = ev.verdict_goals(ev.table(_a(P_TIES)))
    assert kind == "info" and text == "Ein Plan ist in Summe und Maximum zugleich am besten; 3 verschiedene Pläne werden gewählt, aber keiner schlägt ihn."
    assert "wählen 3 verschiedene Pläne" in ev.verdict_goals(ev.table(_a(P_SMALL)))[1] and "Dominiert: Max → Summe dominiert Maximum." in ev.verdict_goals(ev.table(_a(P_DOM)))[1]


def test_stability_verdict_names_every_goal_and_the_remedy():
    a = _a(P_NONE)
    kind, text = ev.verdict_stability(ev.stability(a), 5)
    assert kind == "info" and text == ("Bei Rauschen ±5 ist der Bestandsplan nicht mehr optimal: Summe 13 von 20, Quadrat 7 von 20, Maximum 8 von 20, Max → Summe 12 von 20, Summe → Max 13 von 20. "
                                       "Über viele Instanzen liegen die Ziele ähnlich (Zählung unten); stabil wird ein Plan durch Wechselkosten (Stück 11), nicht durch die Wahl des Ziels.")


def test_sweep_verdicts_carry_the_measured_numbers():
    se = ev.sweep_enum()
    res = {f: ev.summary_enum(r) for f, r in se.items()}
    text = ev.verdict_enum_sweep(res, "Zählung")[1]
    assert "Maximum: Summe höher Median 3,6 % (Maximum 35,7 %)" in text and "Optimalpläne Median 2 (Maximum 61), eindeutig in 4" in text and "Max → Summe über Maximum 11, Quadrat über Maximum 10" not in text
    assert "Quadrat über Maximum 10" in text and "Max → Summe über Maximum 11" in text and "Maximum über Max → Summe" not in text
    st = {f: ev.summary_stability(r) for f, r in ev.sweep_stability().items()}
    text = ev.verdict_stability_sweep(st, "n = 8")[1]
    assert "Summe 38,2 %" in text and "Quadrat 33,8 %" in text and "Maximum 33,0 %" in text and "Max → Summe 42,8 %" in text and "Rauschen ±1" in text
