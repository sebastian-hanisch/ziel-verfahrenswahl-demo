"""Eigenschaftstests (ORACLE-PLAYBOOK §5): Aussagen, die für jede Instanz gelten müssen, an festen Seeds und allen Familien."""

import numpy as np
import pytest

import zlw_algorithm as A
import zlw_constants as C
import zlw_evaluation as ev
import zlw_scenario as S

CASES = [(n, family, seed) for n in (4, 6, 8) for family in (0, 1, 2) for seed in (3, 4, 5)]


def _rows(n, family, seed):
    a = ev.analyse_matrix(S.make_matrix(n, family, seed), ev.Settings(n, family, seed))
    t = ev.table(a)
    return a, t, {r["goal"]: r for r in t["rows"]}


@pytest.mark.parametrize("n,family,seed", CASES)
def test_each_goal_is_optimal_in_its_own_measure(n, family, seed):
    a, t, r = _rows(n, family, seed)
    assert r["S"]["sum"] == a.best_s and r["T"]["sum"] == a.best_s and r["M"]["max"] == a.best_m and r["L"]["max"] == a.best_m
    assert r["Q"]["sumsq"] == int(a.v["Q"].min())


@pytest.mark.parametrize("n,family,seed", CASES)
def test_max_then_sum_is_never_worse_than_the_maximum_alone(n, family, seed):
    a, t, r = _rows(n, family, seed)
    assert r["L"]["max"] == r["M"]["max"] and r["L"]["sum"] <= r["M"]["sum"] and r["L"]["n_opt"] <= r["M"]["n_opt"]
    assert ("M", "L") not in t["dominance"]                                         # das Maximum allein dominiert „Max → Summe“ nie
    assert set(A.optimal_set(a.v["L"]).tolist()) <= set(A.optimal_set(a.v["M"]).tolist())
    assert (("L", "M") in t["dominance"]) == (r["L"]["sum"] < r["M"]["sum"])


@pytest.mark.parametrize("n,family,seed", CASES)
def test_sum_then_max_is_never_worse_than_the_sum_alone(n, family, seed):
    a, t, r = _rows(n, family, seed)
    assert r["T"]["sum"] == r["S"]["sum"] and r["T"]["max"] <= r["S"]["max"] and r["T"]["n_opt"] <= r["S"]["n_opt"]
    assert ("S", "T") not in t["dominance"]
    assert set(A.optimal_set(a.v["T"]).tolist()) <= set(A.optimal_set(a.v["S"]).tolist())


@pytest.mark.parametrize("n,family,seed", CASES)
def test_the_table_is_consistent(n, family, seed):
    a, t, r = _rows(n, family, seed)
    assert all(x["sum_up"] >= 0 and x["max_up"] >= 0 and x["n_opt"] >= 1 for x in r.values()) and 1 <= t["distinct"] <= 5
    assert t["pareto"] and all(not any(A.dominates(r[o]["point"], r[g]["point"]) for o in C.GOALS) for g in t["pareto"])
    assert not any(x == y for x, y in t["dominance"]) and all(x not in t["pareto"] for _, x in t["dominance"])
    assert (t["distinct"] == 1) == (len({r[g]["idx"] for g in C.GOALS}) == 1)


@pytest.mark.parametrize("n,family,seed", CASES)
def test_the_stability_rates_are_probabilities(n, family, seed):
    a = ev.analyse_matrix(S.make_matrix(n, family, seed), ev.Settings(n, family, seed, a=4))
    st = ev.stability(a)
    assert all(0 <= st[g]["rate"] <= 1 and st[g]["count"] == round(st[g]["rate"] * C.NOISE_DRAWS) for g in C.GOALS)
    a0 = ev.analyse_matrix(S.make_matrix(n, family, seed), ev.Settings(n, family, seed, a=4))
    assert ev.stability(a0) == st                                                   # deterministisch


def test_renumbering_the_persons_does_not_change_the_optimal_values():
    c = S.make_matrix(6, 0, 21)
    perm = np.random.default_rng(3).permutation(6)
    a1, a2 = ev.analyse_matrix(c, ev.Settings(6)), ev.analyse_matrix(c[perm], ev.Settings(6))
    assert (a1.best_s, a1.best_m) == (a2.best_s, a2.best_m) and int(a1.v["Q"].min()) == int(a2.v["Q"].min())
    assert [len(A.optimal_set(a1.v[g])) for g in C.GOALS] == [len(A.optimal_set(a2.v[g])) for g in C.GOALS]


def test_the_best_both_good_count_never_exceeds_the_instances():
    recs = ev.sweep_enum(families=(0,), seeds=C.SWEEP_SEEDS[:4])[0]
    s = ev.summary_enum(recs)
    assert all(0 <= s["goals"][g]["both"] <= 4 and 0 <= s["goals"][g]["unique"] <= 4 for g in C.GOALS)
