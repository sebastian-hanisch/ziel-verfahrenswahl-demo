"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und was jedes Preset zeigen soll."""

import zlw_constants as C
import zlw_evaluation as ev
import zlw_presets as P

(P_NONE, P_TIES, P_SAME, P_BALANCED, P_STABLE, P_DOM, P_UNFAIR, P_SMALL) = list(C.PRESETS)


def _t(name):
    a = ev.analyse(ev.Settings(**C.PRESETS[name]))
    return a, ev.table(a), {r["goal"]: r for r in ev.table(a)["rows"]}


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for preset in C.PRESETS.values():
        assert C.N_MIN <= preset["n"] <= C.N_MAX and 0 <= preset["family"] < len(C.FAMILIES) and 0 <= preset["seed"] <= C.SEED_MAX
        assert 0 <= preset["priority"] < len(C.PRIORITIES) and 0 <= preset["unique"] < len(C.UNIQUE_OPTIONS) and C.A_MIN <= preset["a"] <= C.A_MAX


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[P_NONE]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_no_non_default_preset_equals_the_default_settings():
    """Lehre aus Stück 4 und 13: ein Preset, das den Voreinstellungen (auch mit einem Regler am Maximum) gleicht, wäre nicht von „nichts geklickt“ zu unterscheiden."""
    for name, preset in C.PRESETS.items():
        if name != P_NONE:
            assert ev.Settings(**preset) != ev.Settings(), name
    assert len({tuple(sorted(p.items())) for p in C.PRESETS.values()}) == len(C.PRESETS)


def test_default_preset_shows_no_winner_everywhere():
    a, t, r = _t(P_NONE)
    assert t["distinct"] == 4 and not t["one_best"] and t["dominance"] == [("Q", "M"), ("L", "M")]
    assert ev.pct(r["S"]["max_up"]) == "40,8 %" and ev.pct(r["M"]["sum_up"]) == "35,7 %" and r["M"]["n_opt"] == 6 and (r["S"]["sum"], r["Q"]["sum"], r["M"]["sum"]) == (244, 250, 331)


def test_ties_preset_has_ninety_seven_optimal_plans_for_the_maximum_alone():
    a, t, r = _t(P_TIES)
    assert a.settings.family == 1 and r["M"]["n_opt"] == 97 and ev.pct(r["M"]["sum_up"]) == "29,4 %" and r["S"]["max_up"] == 0 and t["one_best"] and t["distinct"] == 3


def test_same_preset_has_one_plan():
    a, t, r = _t(P_SAME)
    assert t["distinct"] == 1 and (r["S"]["sum"], r["S"]["max"]) == (204, 38) and t["n_plans"] == 40320


def test_balanced_preset_has_a_unique_quadratic_optimum():
    a, t, r = _t(P_BALANCED)
    assert r["Q"]["n_opt"] == 1 and r["L"]["n_opt"] == 2 and r["M"]["n_opt"] == 10 and ev.advice_for(ev.Settings(**C.PRESETS[P_BALANCED])).goal == "Q"


def test_stable_preset_recommends_no_goal_and_every_goal_is_unstable():
    a, t, r = _t(P_STABLE)
    adv = ev.advice_for(ev.Settings(**C.PRESETS[P_STABLE]))
    st = ev.stability(a)
    assert adv.goal is None and sorted(st[g]["count"] for g in C.GOALS) == [7, 8, 8, 14, 15]


def test_dominance_preset_has_the_lexicographic_plan_dominating_the_maximum_alone():
    a, t, r = _t(P_DOM)
    assert t["dominance"] == [("L", "M")] and (r["L"]["sum"], r["L"]["max"], r["M"]["sum"], r["M"]["max"], r["M"]["n_opt"]) == (231, 51, 290, 51, 34)


def test_unfair_preset_shows_the_sum_overloading_one_person():
    a, t, r = _t(P_UNFAIR)
    assert r["S"]["sum"] == 209 and ev.pct(r["S"]["max_up"]) == "40,0 %" and ev.pct(r["L"]["sum_up"]) == "0,5 %" and r["L"]["max"] == 35


def test_smallest_example_has_three_plans_of_twenty_four():
    a, t, r = _t(P_SMALL)
    assert a.settings.n == 4 and t["n_plans"] == 24 and t["distinct"] == 3 and ev.pct(r["Q"]["sum_up"]) == "3,4 %" and r["Q"]["max_up"] == 0
