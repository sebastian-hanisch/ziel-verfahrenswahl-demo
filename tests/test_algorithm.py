"""Kern an Handwerten (n = 4, drei verschiedene eindeutige Optima): Ziele, Wahl, Aufschläge, „beide Maße gut“, Dominanz, Rauschen und die Löser für große n."""

import itertools

import numpy as np
import pytest

import zlw_algorithm as A
import zlw_constants as C
import zlw_evaluation as ev
import zlw_scenario as S


def test_plans_are_the_permutations_in_itertools_order():
    assert A.perms(3).tolist() == [list(p) for p in itertools.permutations(range(3))] and A.perms(8).shape == (40320, 8)
    with pytest.raises(ValueError):
        A.perms(9)


def test_the_three_optima_of_the_hand_example(hand):
    P = A.perms(4)
    v = A.values(A.burdens(hand, P))
    pk = A.picks(v)
    plans = {g: tuple(int(x) for x in P[pk[g]]) for g in C.GOALS}
    assert plans["S"] == (0, 2, 3, 1) and plans["Q"] == (1, 2, 3, 0) and plans["M"] == (3, 2, 1, 0) and plans["L"] == plans["M"] and plans["T"] == plans["S"]
    b = {g: A.burdens(hand, P[pk[g]:pk[g] + 1])[0].tolist() for g in C.GOALS}
    assert b["S"] == [7, 3, 2, 2] and b["Q"] == [6, 3, 2, 4] and b["M"] == [5, 3, 4, 4]
    assert (v["S"][pk["S"]], v["Q"][pk["S"]], v["M"][pk["S"]]) == (14, 66, 7) and (v["S"][pk["Q"]], v["Q"][pk["Q"]], v["M"][pk["Q"]]) == (15, 65, 6) and (v["S"][pk["M"]], v["Q"][pk["M"]], v["M"][pk["M"]]) == (16, 66, 5)
    assert all(len(A.optimal_set(v[g])) == 1 for g in C.GOALS)                             # jeder Plan ist unter seinem Ziel eindeutig


def test_the_lexicographic_goals_use_one_hundred_thousand_as_first_stage(hand):
    v = A.values(A.burdens(hand, A.perms(4)))
    i = A.picks(v)["M"]
    assert v["L"][i] == 5 * C.LEX + 16 and v["T"][A.picks(v)["S"]] == 14 * C.LEX + 7


def test_rows_of_the_hand_example(hand_analysis):
    rows = {r["goal"]: r for r in ev.table(hand_analysis)["rows"]}
    assert (hand_analysis.best_s, hand_analysis.best_m) == (14, 5)
    assert rows["S"]["point"] == (14, 7) and rows["Q"]["point"] == (15, 6) and rows["M"]["point"] == (16, 5)
    assert rows["Q"]["sum_up"] == pytest.approx(1 / 14) and rows["M"]["sum_up"] == pytest.approx(2 / 14) and rows["S"]["max_up"] == pytest.approx(2 / 5) and rows["Q"]["max_up"] == pytest.approx(1 / 5)
    assert ev.pct(rows["Q"]["sum_up"]) == "7,1 %" and ev.pct(rows["M"]["sum_up"]) == "14,3 %" and ev.pct(rows["S"]["max_up"]) == "40,0 %" and ev.pct(rows["Q"]["max_up"]) == "20,0 %"
    assert [r["n_opt"] for r in rows.values()] == [1] * 5 and all(r["spread"] is None for r in rows.values())


def test_the_three_plans_are_all_pareto_points_and_none_dominates(hand_analysis):
    t = ev.table(hand_analysis)
    assert t["dominance"] == [] and t["distinct"] == 3 and t["pareto"] == set(C.GOALS) and not t["one_best"]
    assert ev.verdict_goals(t)[0] == "warning" and "3 verschiedene Pläne" in ev.verdict_goals(t)[1]


def test_both_good_and_dominance_are_exact_integers():
    assert not A.both_good((15, 6), 14, 5) and A.both_good((14, 5), 14, 5) and A.both_good((14, 5), 14, 5, 0)
    assert A.both_good((147, 105), 140, 100) and not A.both_good((148, 105), 140, 100)              # 147 = 1,05 * 140 genau
    assert A.dominates((14, 5), (15, 5)) and A.dominates((14, 5), (14, 6)) and not A.dominates((14, 5), (14, 5)) and not A.dominates((14, 7), (15, 6)) and not A.dominates((15, 6), (14, 7))


def test_noise_is_reproducible_clipped_and_inside_the_band():
    c = np.full((4, 4), 1, dtype=np.int64)
    n1, n2 = A.noisy(c, 5, 3, 7), A.noisy(c, 5, 3, 7)
    assert (n1 == n2).all() and n1.min() >= 1 and n1.max() <= 6 and not (n1 == A.noisy(c, 5, 3, 8)).all()
    d = np.full((4, 4), 50, dtype=np.int64)
    assert np.abs(A.noisy(d, 3, 1, 1) - d).max() <= 3


def test_matrices_are_reproducible_and_inside_the_documented_range():
    for fam, (lo, hi) in {0: (11, 109), 1: (1, 9), 2: (11, 109)}.items():
        c = S.make_matrix(8, fam, 5)
        assert (c == S.make_matrix(8, fam, 5)).all() and c.min() >= lo and c.max() <= hi + (0 if fam != 2 else 0)
    assert not (S.make_matrix(8, 0, 5) == S.make_matrix(8, 0, 6)).all()


@pytest.mark.parametrize("seed", range(5))
@pytest.mark.parametrize("family", range(3))
def test_the_solvers_reach_the_enumerated_optimum_values(seed, family):
    c = S.make_matrix(6, family, 300 + seed)
    v = A.values(A.burdens(c, A.perms(6)))
    for g in C.LARGE_GOALS:
        plan = A.solve_goal(c, g)
        assert sorted(plan.tolist()) == list(range(6)) and A.plan_value(c, plan, g) == int(v[g].min())
