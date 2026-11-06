"""Jede Zahl aus dem README wird hier nachgerechnet (DEMO-PLAYBOOK §4). Aufzählung und feste Instanzerzeugung sind deterministisch."""

from pathlib import Path

import pytest

import zlw_constants as C
import zlw_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
(P_NONE, P_TIES, P_SAME, P_BALANCED, P_STABLE, P_DOM, P_UNFAIR, P_SMALL) = list(C.PRESETS)
G5 = C.GOALS


def _claim(text):
    assert text in README, text


def _slash(values):
    return " / ".join(values)


@pytest.fixture(scope="module")
def main():
    return ev.sweep_enum()


@pytest.fixture(scope="module")
def res(main):
    return {f: ev.summary_enum(r) for f, r in main.items()}


@pytest.fixture(scope="module")
def hold():
    return {f: ev.summary_enum(r) for f, r in ev.sweep_enum(seeds=C.HOLDOUT_SEEDS).items()}


def _up(x):
    return f"{ev.pct(x[0])[:-2]} ({ev.pct(x[1])[:-2]})"


def test_sweep_instances_are_the_documented_ones():
    assert C.SWEEP_SEEDS == tuple(range(100000, 100020)) and C.HOLDOUT_SEEDS == tuple(range(100100, 100120)) and C.SWEEP_N == 8 and C.SWEEP_LARGE_N == 30 and C.SWEEP_NOISE == {0: 5, 1: 1, 2: 5}
    _claim("Seeds 100000 bis 100019")
    _claim("Seeds 100100 bis 100119")


def test_sum_and_maximum_upside_claims(res):
    sum_up = lambda f: _slash(_up(res[f]["goals"][g]["sum_up"]) for g in G5)
    assert sum_up(0) == "0,0 (0,0) / 0,0 (7,1) / 3,6 (35,7) / 0,0 (10,8) / 0,0 (0,0)" and sum_up(1) == "0,0 (0,0) / 0,0 (5,6) / 15,0 (33,3) / 0,0 (5,6) / 0,0 (0,0)" and sum_up(2) == "0,0 (0,0) / 0,0 (2,8) / 10,3 (36,6) / 0,0 (5,4) / 0,0 (0,0)"
    _claim("unabhängig 0,0 (0,0) / 0,0 (7,1) / **3,6** (35,7) / 0,0 (10,8) / 0,0 (0,0); grob 0,0 (0,0) / 0,0 (5,6) / **15,0** (33,3) / 0,0 (5,6) / 0,0 (0,0); Person 0,0 (0,0) / 0,0 (2,8) / **10,3** (36,6) / 0,0 (5,4) / 0,0 (0,0)")
    max_up = lambda f: _slash(_up(res[f]["goals"][g]["max_up"]) for g in G5)
    assert max_up(0) == "0,0 (40,8) / 0,0 (22,2) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (40,8)" and max_up(1) == "0,0 (50,0) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (50,0)" and max_up(2) == "0,0 (28,8) / 0,0 (15,9) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (28,8)"
    _claim("unabhängig 0,0 (**40,8**) / 0,0 (22,2) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (40,8); grob 0,0 (**50,0**) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (50,0); Person 0,0 (**28,8**) / 0,0 (15,9) / 0,0 (0,0) / 0,0 (0,0) / 0,0 (28,8)")


def test_optimal_set_claims(res):
    opt = lambda f: _slash(f"{ev.num(res[f]['goals'][g]['n_opt'][0])} ({res[f]['goals'][g]['n_opt'][1]}), {res[f]['goals'][g]['unique']}" for g in G5)
    assert opt(0) == "1 (2), 18 / 1 (1), 20 / 2 (61), 4 / 1 (2), 18 / 1 (2), 18" and opt(1) == "2,5 (9), 7 / 1 (6), 13 / 13 (69), 1 / 1,5 (6), 10 / 2 (6), 9" and opt(2) == "1 (2), 18 / 1 (2), 19 / 14,5 (460), 1 / 1 (2), 17 / 1 (2), 19"
    _claim("unabhängig 1 (2), 18 / 1 (1), **20** / 2 (61), **4** / 1 (2), 18 / 1 (2), 18; grob 2,5 (9), 7 / 1 (6), 13 / 13 (69), **1** / 1,5 (6), 10 / 2 (6), 9; Person 1 (2), 18 / 1 (2), 19 / 14,5 (460), **1** / 1 (2), 17 / 1 (2), 19")
    sp = lambda f: f"{ev.num(res[f]['goals']['M']['spread'][1] * 100)} ({ev.num(res[f]['goals']['M']['spread'][0] * 100)} bis {ev.num(res[f]['goals']['M']['spread'][2] * 100)}; {res[f]['goals']['M']['n_spread']})"
    assert (sp(0), sp(1), sp(2)) == ("11,3 (0,5 bis 46,6; 16)", "38,5 (7,7 bis 57,1; 19)", "17,3 (3,8 bis 64,2; 19)")
    _claim("unabhängig 11,3 (0,5 bis 46,6; 16), grob 38,5 (7,7 bis 57,1; 19), Person 17,3 (3,8 bis 64,2; 19)")


def test_both_good_and_dominance_claims(res):
    both = lambda f: _slash(str(res[f]["goals"][g]["both"]) for g in G5)
    assert (both(0), both(1), both(2)) == ("13 / 17 / 11 / 17 / 13", "15 / 18 / 5 / 18 / 17", "14 / 17 / 4 / 19 / 14")
    _claim("unabhängig 13 / **17** / 11 / **17** / 13; grob 15 / **18** / 5 / **18** / 17; Person 14 / **17** / 4 / **19** / 14")
    d = lambda f, x, y: res[f]["dominance"][(x, y)]
    assert [_slash(str(d(f, "L", "M")) for f in (0, 1, 2)), _slash(str(d(f, "Q", "M")) for f in (0, 1, 2)), _slash(str(d(f, "S", "M")) for f in (0, 1, 2))] == ["11 / 15 / 17", "10 / 15 / 14", "8 / 11 / 12"]
    _claim("unabhängig **11** / 10 / 8; grob **15** / 15 / 11; Person **17** / 14 / 12")
    assert [d(f, "M", "L") for f in (0, 1, 2)] == [0, 0, 0] and [d(f, "M", "Q") for f in (0, 1, 2)] == [0, 0, 1] and [d(f, "S", "Q") for f in (0, 1, 2)] == [0, 0, 2] and [d(f, "Q", "S") for f in (0, 1, 2)] == [0, 2, 0]
    _claim("**0** in jeder Familie; unabhängig 0, grob 0, Person 1; 0 / 0 / 2; 0 / 2 / 0")


def test_guarantee_claims(main):
    recs = [r for f in (0, 1, 2) for r in main[f]]
    assert len(recs) == 60
    assert sum(r["rows"]["L"]["max"] == r["rows"]["M"]["max"] and r["rows"]["L"]["sum"] <= r["rows"]["M"]["sum"] for r in recs) == 60
    assert sum(r["rows"]["T"]["sum"] == r["rows"]["S"]["sum"] and r["rows"]["T"]["max"] <= r["rows"]["S"]["max"] for r in recs) == 60
    _claim("(gleiches Maximum, Summe nie größer): **60**; Summe → Max nie schlechter als die Summe (gleiche Summe, Maximum nie größer): **60**")


def test_stability_claims():
    st8 = {f: ev.summary_stability(r) for f, r in ev.sweep_stability().items()}
    row = lambda f: " / ".join(ev.pct(st8[f][g]["rate"])[:-2] for g in G5)
    assert (row(0), row(1), row(2)) == ("38,2 / 33,8 / 33,0 / 42,8 / 38,5", "66,8 / 70,0 / 49,8 / 65,5 / 68,2", "49,5 / 45,5 / 40,5 / 54,5 / 50,0")
    _claim("unabhängig ±5: 38,2 / 33,8 / 33,0 / 42,8 / 38,5; grob ±1: 66,8 / 70,0 / 49,8 / 65,5 / 68,2; Person ±5: 49,5 / 45,5 / 40,5 / 54,5 / 50,0")
    st30 = {f: ev.summary_stability(r, C.LARGE_GOALS) for f, r in ev.sweep_large().items()}
    row = lambda f: " / ".join(ev.pct(st30[f][g]["rate"])[:-2] for g in C.LARGE_GOALS)
    assert (row(0), row(1), row(2)) == ("99,0 / 98,5 / 88,2 / 97,8", "100,0 / 100,0 / 91,7 / 100,0", "100,0 / 100,0 / 96,0 / 100,0")
    _claim("unabhängig ±5: 99,0 / 98,5 / 88,2 / 97,8; grob ±1: 100,0 / 100,0 / 91,7 / 100,0; Person ±5: 100,0 / 100,0 / 96,0 / 100,0")
    _claim("(`n` = 8: 33,0 bis 42,8 % bei unabhängigen Kosten, 49,8 bis 70,0 % bei groben, 40,5 bis 54,5 % bei Person; `n` = 30: 88,2 bis 100,0 %)")


def test_holdout_claims(hold):
    d = lambda x, y: _slash(str(hold[f]["dominance"][(x, y)]) for f in (0, 1, 2))
    assert d("L", "M") == "13 / 14 / 16" and d("M", "L") == "0 / 0 / 0"
    _claim("**13 / 14 / 16** und **0 / 0 / 0**")
    assert _slash(ev.num(hold[f]["goals"]["M"]["sum_up"][0] * 100) for f in (0, 1, 2)) == "14,8 / 17,2 / 13,2"
    _claim("unabhängig 14,8, grob 17,2, Person 13,2")
    uq = lambda f: _slash(str(hold[f]["goals"][g]["unique"]) for g in G5)
    assert (uq(0), uq(1), uq(2)) == ("20 / 20 / 2 / 20 / 20", "8 / 15 / 1 / 11 / 12", "18 / 20 / 1 / 20 / 18")
    _claim("unabhängig 20 / 20 / 2 / 20 / 20; grob 8 / **15** / 1 / 11 / 12; Person 18 / **20** / 1 / 20 / 18")
    both = lambda f: _slash(str(hold[f]["goals"][g]["both"]) for g in G5)
    assert (both(0), both(1), both(2)) == ("13 / 17 / 7 / 14 / 13", "13 / 17 / 5 / 17 / 16", "12 / 14 / 3 / 16 / 13")
    _claim("unabhängig 13 / 17 / 7 / 14 / 13; grob 13 / 17 / 5 / 17 / 16; Person 12 / 14 / 3 / 16 / 13")
    assert [ev.pct(hold[f]["goals"]["L"]["sum_up"][0]) for f in (0, 1, 2)] == ["1,4 %", "0,0 %", "1,7 %"] and all(hold[f]["goals"]["Q"]["sum_up"][0] == 0 for f in (0, 1, 2))
    _claim("dort kostet „Maximum, dann Summe“ im Median bis 1,7 % mehr Summe (Quadratsumme 0,0 %)")
    assert all(hold[f]["goals"]["T"]["unique"] >= hold[f]["goals"]["S"]["unique"] for f in (0, 1, 2)) and hold[1]["goals"]["S"]["unique"] == 8 and hold[1]["goals"]["T"]["unique"] == 12
    _claim("(eindeutig 7 → 9, im Hold-out 8 → 12)")


def test_preset_claims():
    def run(name):
        s = ev.Settings(**C.PRESETS[name])
        a = ev.analyse(s)
        t = ev.table(a)
        return a, t, {r["goal"]: r for r in t["rows"]}
    a, t, r = run(P_NONE)
    assert t["distinct"] == 4 and (r["S"]["sum"], r["S"]["max"], r["Q"]["sum"], r["Q"]["max"], r["M"]["sum"], r["M"]["max"]) == (244, 69, 250, 49, 331, 49) and ev.pct(r["S"]["max_up"]) == "40,8 %" and ev.pct(r["M"]["sum_up"]) == "35,7 %" and r["M"]["n_opt"] == 6
    _claim("die fünf Ziele wählen **4** verschiedene Pläne: Summe 244 und Maximum 69 (S), 250 und 49 (Q), 331 und 49 (M); S im Maximum **40,8 %**, M in der Summe **35,7 %** schlechter; M hat **6** Optimalpläne")
    a, t, r = run(P_TIES)
    assert r["M"]["n_opt"] == 97 and ev.pct(r["M"]["sum_up"]) == "29,4 %" and r["S"]["sum_up"] == 0 and r["L"]["sum_up"] == 0 and r["T"]["sum_up"] == 0 and r["S"]["max_up"] == 0
    _claim("**97** Optimalpläne, die Summe des Maximum-Plans **29,4 %** über der besten; Summe und Max → Summe wählen den besten Plan")
    a, t, r = run(P_SAME)
    assert t["distinct"] == 1 and (r["S"]["sum"], r["S"]["max"]) == (204, 38) and t["n_plans"] == 40320
    _claim("ein Plan für alle fünf Ziele (Summe 204, Maximum 38) von 40 320")
    a, t, r = run(P_BALANCED)
    assert (r["Q"]["n_opt"], r["L"]["n_opt"], r["M"]["n_opt"]) == (1, 2, 10)
    _claim("Quadratsumme **1** Optimalplan, Max → Summe 2, Maximum allein 10")
    a, t, r = run(P_STABLE)
    st = ev.stability(a)
    assert min(st[g]["count"] for g in C.GOALS) == 7 and max(st[g]["count"] for g in C.GOALS) == 15
    _claim("der Bestandsplan ist bei jedem Ziel in **7 bis 15** von 20 Ziehungen nicht mehr optimal")
    a, t, r = run(P_DOM)
    assert t["dominance"] == [("L", "M")] and (r["L"]["sum"], r["L"]["max"], r["M"]["sum"], r["M"]["max"], r["M"]["n_opt"]) == (231, 51, 290, 51, 34)
    _claim("Max → Summe (Summe 231, Maximum 51) dominiert das Maximum allein (290, 51; **34** Optimalpläne)")
    a, t, r = run(P_UNFAIR)
    assert r["S"]["sum"] == 209 and ev.pct(r["S"]["max_up"]) == "40,0 %" and ev.pct(r["L"]["sum_up"]) == "0,5 %" and r["L"]["max"] == 35
    _claim("Summenplan 209, sein Maximum **40,0 %** über dem besten; Max → Summe kostet **0,5 %** mehr Summe und senkt das Maximum auf 35")
    a, t, r = run(P_SMALL)
    assert t["n_plans"] == 24 and t["distinct"] == 3 and ev.pct(r["Q"]["sum_up"]) == "3,4 %" and r["Q"]["max_up"] == 0
    _claim("24 Pläne, **3** verschiedene gewählt; Quadratsumme 3,4 % mehr Summe, Maximum am besten")


def test_correction_claims(res, hold):
    both = lambda f, g: res[f]["goals"][g]["both"]
    assert [both(f, "Q") for f in (0, 1, 2)] == [17, 18, 17] and [both(f, "L") for f in (0, 1, 2)] == [17, 18, 19] and [res[f]["goals"]["Q"]["unique"] for f in (0, 1, 2)] == [20, 13, 19] and [res[f]["goals"]["L"]["unique"] for f in (0, 1, 2)] == [18, 10, 17]
    _claim("(17 / 18 / 17 gegen 17 / 18 / 19 von 20); der Unterschied ist die **Eindeutigkeit** (Quadratsumme 20 / 13 / 19 gegen 18 / 10 / 17)")
    _claim("in einer Familie vorn, in einer gleichauf und in einer hinten (17 / 17 / 14 gegen 14 / 17 / 16)")
    _claim("(20 / 15 / 20 gegen 20 / 11 / 20)")
    _claim("in jeder der 60 Instanzen nicht schlechter und dominiert ihn in 11 / 15 / 17 von 20, im Hold-out in 13 / 14 / 16")
    _claim("(Median 2 / 13 / 14,5 Optimalpläne)")
    assert [ev.num(res[f]["goals"]["M"]["n_opt"][0]) for f in (0, 1, 2)] == ["2", "13", "14,5"]
