"""Die Ziele nebeneinander, die Regel auf einer Instanz, Zählungen über feste Instanzen und Verdikte (reine Funktionen: Art, Text; jede Zahl im Text kommt aus der Rechnung).

Gefragt wird: Welches Ziel, welche Gleichstandsregel, gemessen woran? Das Stück rechnet nichts Neues: es stellt fünf Ziele auf denselben Instanzen nebeneinander (Stück 1 bis 5),
misst sie an Summe, Maximum, Eindeutigkeit, „beide Maße gut“, Dominanz und Stabilität (Stück 2, 4, 5, 11) und prüft die Regel `zlw_rule.advise`."""

from dataclasses import dataclass

import numpy as np

import zlw_algorithm as A
import zlw_constants as C
import zlw_rule as R
import zlw_scenario as S


def de(x: float, digits: int = 1) -> str:
    text = f"{x:.{digits}f}"
    if float(text) == 0.0:
        text = f"{0.0:.{digits}f}"
    return text.replace(".", ",")


def num(x: float) -> str:
    """Zahl mit höchstens einer Nachkommastelle, ohne ,0 (2; 2,5)."""
    text = de(x, 1)
    return text[:-2] if text.endswith(",0") else text


def pct(x: float, digits: int = 1) -> str:
    return de(x * 100.0, digits) + " %"


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    family: int = C.DEFAULT_FAMILY
    seed: int = C.DEFAULT_SEED
    priority: int = C.DEFAULT_PRIORITY
    unique: int = C.DEFAULT_UNIQUE
    a: int = C.DEFAULT_A


@dataclass
class Analysis:
    settings: Settings
    c: np.ndarray
    v: dict                  # Zielwerte je Plan
    pk: dict                 # gewählter Plan (Index) je Ziel
    best_s: int
    best_m: int


def analyse_matrix(c: np.ndarray, settings: Settings) -> Analysis:
    P = A.perms(c.shape[0])
    v = A.values(A.burdens(c, P))
    return Analysis(settings, c, v, A.picks(v), int(v["S"].min()), int(v["M"].min()))


def analyse(settings: Settings) -> Analysis:
    return analyse_matrix(S.make_matrix(settings.n, settings.family, settings.seed), settings)


def data_kind(family: int) -> str:
    return C.FAMILY_DATA[family]


def plan_text(plan: np.ndarray) -> str:
    return " | ".join(f"P{i + 1}→A{int(t) + 1}" for i, t in enumerate(plan))


def goal_row(a: Analysis, g: str) -> dict:
    """Eine Zeile der Tabelle: Plan, Belastungen, Summe, Maximum, Aufschläge, Optimalpläne, Spanne der Summe darin."""
    n = a.c.shape[0]
    P = A.perms(n)
    idx = a.pk[g]
    b = A.burdens(a.c, P[idx:idx + 1])[0]
    opt = A.optimal_set(a.v[g])
    s_all = a.v["S"][opt]
    point = (int(a.v["S"][idx]), int(a.v["M"][idx]))
    return {"goal": g, "idx": idx, "plan": P[idx], "burdens": b.astype(int), "sum": point[0], "max": point[1], "sumsq": int(a.v["Q"][idx]), "sum_up": (point[0] - a.best_s) / a.best_s, "max_up": (point[1] - a.best_m) / a.best_m,
            "n_opt": int(len(opt)), "spread": float((s_all.max() - s_all.min()) / s_all.min()) if len(opt) > 1 else None, "both": A.both_good(point, a.best_s, a.best_m), "point": point}


def table(a: Analysis) -> dict:
    rows = [goal_row(a, g) for g in C.GOALS]
    points = {r["goal"]: r["point"] for r in rows}
    dom = [(x, y) for x in C.GOALS for y in C.GOALS if x != y and A.dominates(points[x], points[y])]
    distinct = len({r["idx"] for r in rows})
    pareto = {r["goal"] for r in rows if not any(A.dominates(points[o], r["point"]) for o in C.GOALS)}
    return {"rows": rows, "dominance": dom, "n_plans": len(a.v["S"]), "distinct": distinct, "pareto": pareto, "one_best": any(r["sum_up"] == 0 and r["max_up"] == 0 for r in rows)}


def advice_for(settings: Settings) -> R.Advice:
    return R.advise(settings.priority, data_kind(settings.family), settings.unique)


def stability(a: Analysis) -> dict:
    """Auf dieser Instanz: je Ziel der Anteil der Ziehungen (Rauschen ±a, NOISE_DRAWS Ziehungen), in denen der Bestandsplan nicht mehr optimal ist, und der Mindestumbau."""
    s = a.settings
    n = a.c.shape[0]
    P = A.perms(n)
    count = {g: 0 for g in C.GOALS}
    ham = {g: [] for g in C.GOALS}
    for d in range(C.NOISE_DRAWS):
        cn = A.noisy(a.c, s.a, s.seed, d)
        v = A.values(A.burdens(cn, P))
        for g in C.GOALS:
            mn = v[g].min()
            if v[g][a.pk[g]] > mn:
                count[g] += 1
                opt = np.flatnonzero(v[g] == mn)
                ham[g].append(int((P[opt] != P[a.pk[g]]).sum(axis=1).min()) / n)
    return {g: {"rate": count[g] / C.NOISE_DRAWS, "count": count[g], "ham": float(np.median(ham[g])) if ham[g] else None} for g in C.GOALS}


# --- Zählungen --------------------------------------------------------------------------------------------------------------------------------

def _q3(vals) -> tuple[float, float, float]:
    v = np.asarray(list(vals), dtype=float)
    return (float(v.min()), float(np.median(v)), float(v.max())) if len(v) else (0.0, 0.0, 0.0)


def _enum_record(family: int, seed: int) -> dict:
    a = analyse_matrix(S.make_matrix(C.SWEEP_N, family, seed), Settings(C.SWEEP_N, family, seed))
    t = table(a)
    return {"rows": {r["goal"]: r for r in t["rows"]}, "dominance": t["dominance"]}


def sweep_enum(families=C.SWEEP_FAMILIES, seeds=C.SWEEP_SEEDS) -> dict:
    """Je Familie die festen Instanzen (n = 8, alle 40 320 Pläne): die fünf Ziele nebeneinander."""
    return {fam: [_enum_record(fam, s) for s in seeds] for fam in families}


def _stability_record(family: int, seed: int) -> dict:
    a = analyse_matrix(S.make_matrix(C.SWEEP_N, family, seed), Settings(C.SWEEP_N, family, seed, a=C.SWEEP_NOISE[family]))
    return stability(a)


def sweep_stability(families=C.SWEEP_FAMILIES, seeds=C.SWEEP_SEEDS) -> dict:
    return {fam: [_stability_record(fam, s) for s in seeds] for fam in families}


def _large_record(family: int, seed: int) -> dict:
    c = S.make_matrix(C.SWEEP_LARGE_N, family, seed)
    a = C.SWEEP_NOISE[family]
    old = {g: A.solve_goal(c, g) for g in C.LARGE_GOALS}
    cnt = {g: 0 for g in C.LARGE_GOALS}
    for d in range(C.NOISE_DRAWS):
        cn = A.noisy(c, a, seed, d)
        for g in C.LARGE_GOALS:
            cnt[g] += A.plan_value(cn, old[g], g) > A.plan_value(cn, A.solve_goal(cn, g), g)
    return {g: {"rate": cnt[g] / C.NOISE_DRAWS} for g in C.LARGE_GOALS}


def sweep_large(families=C.SWEEP_FAMILIES, seeds=C.SWEEP_SEEDS) -> dict:
    return {fam: [_large_record(fam, s) for s in seeds] for fam in families}


def summary_enum(recs: list[dict]) -> dict:
    out = {"goals": {}, "dominance": {}, "seeds": len(recs)}
    for g in C.GOALS:
        rows = [r["rows"][g] for r in recs]
        spreads = [x["spread"] for x in rows if x["spread"] is not None]
        out["goals"][g] = {"sum_up": (float(np.median([x["sum_up"] for x in rows])), max(x["sum_up"] for x in rows)), "max_up": (float(np.median([x["max_up"] for x in rows])), max(x["max_up"] for x in rows)),
                           "n_opt": (float(np.median([x["n_opt"] for x in rows])), max(x["n_opt"] for x in rows)), "unique": sum(x["n_opt"] == 1 for x in rows), "both": sum(x["both"] for x in rows),
                           "spread": _q3(spreads), "n_spread": len(spreads)}
    for x in C.GOALS:
        for y in C.GOALS:
            if x != y:
                out["dominance"][(x, y)] = sum((x, y) in r["dominance"] for r in recs)
    return out


def summary_stability(recs: list[dict], goals=C.GOALS) -> dict:
    return {g: {"rate": float(np.mean([r[g]["rate"] for r in recs])), "inst": _q3(r[g]["rate"] for r in recs)} for g in goals}


# --- Verdikte -------------------------------------------------------------------------------------------------------------------------------------

def verdict_advice(adv: R.Advice, row: dict | None) -> tuple[str, str]:
    if adv.goal is None:
        return "info", f"Für die Anforderung „{C.PRIORITIES[adv.priority]}“ entscheidet **kein Ziel**: {adv.tie_rule}"
    base = f"Für die Anforderung „{C.PRIORITIES[adv.priority]}“ ({adv.data}e Daten) empfiehlt die Regel **{adv.label}**. "
    if row is None:
        return "success", base + adv.tie_rule
    return "success", base + (f"Auf dieser Instanz liegt die Summe {pct(row['sum_up'])} und das Maximum {pct(row['max_up'])} über dem jeweils Besten; das Ziel hat {row['n_opt']} "
                              f"{'Optimalplan' if row['n_opt'] == 1 else 'Optimalpläne'}.")


def verdict_goals(t: dict) -> tuple[str, str]:
    n_plans, distinct = t["n_plans"], t["distinct"]
    if distinct == 1:
        return "info", f"Alle fünf Ziele wählen denselben Plan: auf dieser Instanz (von {n_plans} Plänen) gibt es keine Wahl."
    if t["one_best"]:
        return "info", f"Ein Plan ist in Summe und Maximum zugleich am besten; {distinct} verschiedene Pläne werden gewählt, aber keiner schlägt ihn."
    pareto = ", ".join(C.GOAL_SHORT[g] for g in C.GOALS if g in t["pareto"])
    dom = "; ".join(f"{C.GOAL_SHORT[x]} dominiert {C.GOAL_SHORT[y]}" for x, y in t["dominance"])
    return "warning", (f"**Kein Ziel gewinnt überall:** die fünf Ziele wählen {distinct} verschiedene Pläne, keiner ist in Summe und Maximum zugleich am besten. Nicht dominiert sind: {pareto}."
                       + (f" Dominiert: {dom}." if dom else ""))


def verdict_enum_sweep(res: dict, title: str) -> tuple[str, str]:
    parts = []
    for fam, s in res.items():
        cells = "; ".join(f"{C.GOAL_SHORT[g]}: Summe höher Median {pct(s['goals'][g]['sum_up'][0])} (Maximum {pct(s['goals'][g]['sum_up'][1])}), Maximum höher Median {pct(s['goals'][g]['max_up'][0])} (Maximum {pct(s['goals'][g]['max_up'][1])}), "
                          f"Optimalpläne Median {num(s['goals'][g]['n_opt'][0])} (Maximum {s['goals'][g]['n_opt'][1]}), eindeutig in {s['goals'][g]['unique']}, beide Maße innerhalb von {C.BOTH_PCT} % in {s['goals'][g]['both']}" for g in C.GOALS)
        dom = ", ".join(f"{C.GOAL_SHORT[x]} über {C.GOAL_SHORT[y]} {v}" for (x, y), v in s["dominance"].items() if v)
        parts.append(f"{C.FAMILIES[fam]} (von {s['seeds']}): {cells}. Plan dominiert Plan (Instanzen): {dom or 'nie'}")
    return "info", f"{title}: " + ". ".join(parts) + "."


def verdict_stability_sweep(res: dict, title: str) -> tuple[str, str]:
    parts = []
    for fam, s in res.items():
        parts.append(f"{C.FAMILIES[fam]} (Rauschen ±{C.SWEEP_NOISE[fam]}): " + ", ".join(f"{C.GOAL_SHORT[g]} {pct(s[g]['rate'])}" for g in s))
    return "info", f"{title}, Bestandsplan nicht mehr optimal (Anteil der Ziehungen): " + "; ".join(parts) + "."


def verdict_stability(st: dict, a_noise: int) -> tuple[str, str]:
    cells = ", ".join(f"{C.GOAL_SHORT[g]} {st[g]['count']} von {C.NOISE_DRAWS}" for g in C.GOALS)
    return "info", (f"Bei Rauschen ±{a_noise} ist der Bestandsplan nicht mehr optimal: {cells}. Über viele Instanzen liegen die Ziele ähnlich (Zählung unten); stabil wird ein Plan durch Wechselkosten (Stück 11), nicht durch die Wahl des Ziels.")
