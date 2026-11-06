"""Randfälle: alle Kosten gleich, ein einziger Plan, nur ein Plan bester in beiden Maßen, jede Familie und Größe, Regler an den Grenzen, Aufzählungsgrenze, große Zuordnungen."""

import numpy as np
import pytest

import zlw_algorithm as A
import zlw_constants as C
import zlw_evaluation as ev
import zlw_scenario as S


def test_all_costs_equal_every_goal_picks_the_first_plan_and_all_plans_are_optimal():
    a = ev.analyse_matrix(np.full((4, 4), 7, dtype=np.int64), ev.Settings(4))
    t = ev.table(a)
    assert all(r["idx"] == 0 and r["n_opt"] == 24 and r["sum_up"] == 0 and r["max_up"] == 0 for r in t["rows"]) and t["distinct"] == 1 and t["dominance"] == []
    assert ev.verdict_goals(t) == ("info", "Alle fünf Ziele wählen denselben Plan: auf dieser Instanz (von 24 Plänen) gibt es keine Wahl.")
    assert all(r["spread"] == 0 for r in t["rows"])                                       # mehrere Optimalpläne, alle mit gleicher Summe


def test_a_single_plan_has_no_choice_and_no_instability():
    a = ev.analyse_matrix(np.array([[5]], dtype=np.int64), ev.Settings(1))
    t = ev.table(a)
    assert t["n_plans"] == 1 and t["distinct"] == 1 and all(r["n_opt"] == 1 for r in t["rows"])
    st = ev.stability(a)
    assert all(st[g]["rate"] == 0 for g in C.GOALS)


def test_one_plan_that_is_best_in_both_measures_is_reported_as_such():
    c = np.array([[1, 9, 9], [9, 1, 9], [9, 9, 1]], dtype=np.int64)
    t = ev.table(ev.analyse_matrix(c, ev.Settings(3)))
    assert t["distinct"] == 1 and t["one_best"]
    c2 = np.array([[1, 1, 9], [1, 9, 1], [9, 1, 1]], dtype=np.int64)
    t2 = ev.table(ev.analyse_matrix(c2, ev.Settings(3)))
    assert t2["one_best"] and ev.verdict_goals(t2)[0] == "info"


def test_the_unfair_summe_example_from_a_preset():
    a = ev.analyse(ev.Settings(seed=100001, priority=0))
    t = ev.table(a)
    assert ev.pct({r["goal"]: r for r in t["rows"]}["S"]["max_up"]) == "40,0 %" and ev.verdict_goals(t)[0] == "warning"


def test_the_enumeration_limit_raises_a_clear_error():
    with pytest.raises(ValueError):
        A.perms(9)
    assert A.perms(8).shape == (40320, 8)


@pytest.mark.parametrize("n", range(C.N_MIN, C.N_MAX + 1))
@pytest.mark.parametrize("family", range(len(C.FAMILIES)))
def test_every_size_and_family_runs_every_experiment(n, family):
    for priority in range(len(C.PRIORITIES)):
        for unique in (0, 1):
            s = ev.Settings(n, family, 5, priority, unique, 5)
            a = ev.analyse(s)
            t = ev.table(a)
            adv = ev.advice_for(s)
            ev.verdict_advice(adv, None if adv.goal is None else ev.goal_row(a, adv.goal))
            ev.verdict_goals(t)
    ev.verdict_stability(ev.stability(a), 5)


def test_the_slider_extremes_are_valid_settings():
    for n in (C.N_MIN, C.N_MAX):
        for a_ in (C.A_MIN, C.A_MAX):
            a = ev.analyse(ev.Settings(n, 1, 7, 2, 1, a_))
            ev.stability(a)
            ev.verdict_goals(ev.table(a))


def test_large_assignments_are_solved_with_valid_plans():
    c = S.make_matrix(30, 0, 100000)
    for g in C.LARGE_GOALS:
        plan = A.solve_goal(c, g)
        assert sorted(plan.tolist()) == list(range(30)) and A.plan_value(c, plan, g) > 0
    assert A.plan_value(c, A.solve_goal(c, "L"), "M") == A.plan_value(c, A.solve_goal(c, "M"), "M")      # L hat dasselbe Maximum wie M


def test_text_helpers_format_numbers():
    assert ev.de(-0.0001, 1) == "0,0" and ev.pct(0.0) == "0,0 %" and ev.num(2.0) == "2" and ev.num(2.5) == "2,5" and ev.num(13.0) == "13" and ev.num(14.5) == "14,5"
