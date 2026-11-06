"""Orakel (ORACLE-PLAYBOOK §5): reines Python (`itertools.permutations`, Schleifen), keine numpy-Zeile im Referenzweg.

Jeder Plan wird einzeln gerechnet (Belastungen, Summe, Quadratsumme, Maximum), daraus die fünf Ziele, die Wahl (kleinster Index), Optimalmengen, Aufschläge, „beide Maße gut“, Dominanz
und die Stabilität bei Rauschen (Bestandsplan, Mindestumbau). Verglichen wird mit dem numpy-Kern und der Auswertung."""

import itertools
import random

import numpy as np
import pytest

import zlw_algorithm as A
import zlw_constants as C
import zlw_evaluation as ev

CASES = [(n, family, seed) for n in (3, 4, 5) for family in (0, 1, 2) for seed in (1, 2, 3, 4)]


def _matrix(n, family, seed):
    rng = random.Random(seed * 7 + n + 100 * family)
    hi = 9 if family == 1 else 40
    return [[rng.randint(1, hi) for _ in range(n)] for _ in range(n)]


def _ref(c):
    n = len(c)
    out = []
    for p in itertools.permutations(range(n)):
        b = [c[i][p[i]] for i in range(n)]
        s, mx = sum(b), max(b)
        out.append({"S": s, "Q": sum(x * x for x in b), "M": mx, "L": mx * C.LEX + s, "T": s * C.LEX + mx, "point": (s, mx)})
    return out


@pytest.mark.parametrize("n,family,seed", CASES)
def test_goal_values_picks_and_optimal_sets_match_the_loops(n, family, seed):
    c = _matrix(n, family, seed)
    ref = _ref(c)
    v = A.values(A.burdens(np.array(c), A.perms(n)))
    for g in C.GOALS:
        assert v[g].tolist() == [x[g] for x in ref]
        best = min(x[g] for x in ref)
        assert A.picks(v)[g] == next(i for i, x in enumerate(ref) if x[g] == best)
        assert A.optimal_set(v[g]).tolist() == [i for i, x in enumerate(ref) if x[g] == best]


@pytest.mark.parametrize("n,family,seed", CASES)
def test_table_matches_the_loops(n, family, seed):
    c = _matrix(n, family, seed)
    ref = _ref(c)
    a = ev.analyse_matrix(np.array(c), ev.Settings(n, family, seed))
    s_min, m_min = min(x["S"] for x in ref), min(x["M"] for x in ref)
    t = ev.table(a)
    pts = {}
    for r in t["rows"]:
        g = r["goal"]
        best = min(x[g] for x in ref)
        opt = [x for x in ref if x[g] == best]
        pick = opt[0]
        pts[g] = pick["point"]
        assert r["point"] == pick["point"] and r["n_opt"] == len(opt)
        assert r["sum_up"] == pytest.approx((pick["S"] - s_min) / s_min) and r["max_up"] == pytest.approx((pick["M"] - m_min) / m_min)
        assert r["both"] == (pick["S"] <= 1.05 * s_min + 1e-9 and pick["M"] <= 1.05 * m_min + 1e-9)
        sums = [x["S"] for x in opt]
        assert (r["spread"] is None) == (len(opt) == 1) and (r["spread"] is None or r["spread"] == pytest.approx((max(sums) - min(sums)) / min(sums)))
    dom = [(x, y) for x in C.GOALS for y in C.GOALS if x != y and pts[x][0] <= pts[y][0] and pts[x][1] <= pts[y][1] and pts[x] != pts[y]]
    assert t["dominance"] == dom and t["distinct"] == len({tuple(r["plan"]) for r in t["rows"]})


@pytest.mark.parametrize("n,family,seed", CASES[:12])
def test_stability_matches_a_loop_over_all_plans(n, family, seed):
    c = _matrix(n, family, seed)
    s = ev.Settings(n, family, seed, a=3)
    a = ev.analyse_matrix(np.array(c), s)
    plans = list(itertools.permutations(range(n)))
    old = {g: min(range(len(plans)), key=lambda i: (_ref(c)[i][g], i)) for g in C.GOALS}
    ref0 = _ref(c)
    st = ev.stability(a)
    count = {g: 0 for g in C.GOALS}
    for d in range(C.NOISE_DRAWS):
        cn = A.noisy(np.array(c), 3, seed, d).tolist()
        refn = _ref(cn)
        for g in C.GOALS:
            best = min(x[g] for x in refn)
            if refn[old[g]][g] > best:
                count[g] += 1
    assert {g: st[g]["count"] for g in C.GOALS} == count and all(old[g] == a.pk[g] for g in C.GOALS) and ref0 is not None
