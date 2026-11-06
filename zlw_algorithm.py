"""Kern der Demo (numpy, scipy): Zuordnung n mal n, fünf Ziele, Optimalmengen, „beide Maße gut“, Dominanz, Rauschen; für n = 30 die Ungarische Methode und das Engpassverfahren.

  * `perms`: alle n! Pläne in der Reihenfolge von itertools.permutations (Index = Nummer); Plan p: Person i macht Aufgabe p[i]. Bei Gleichstand gilt überall der kleinste Index (Stück 5).
  * `values`: die fünf Ziele je Plan, ganzzahlig exakt: S Summe, Q Quadratsumme, M Maximum, L Maximum dann Summe (erste Stufe mal LEX plus Summe), T Summe dann Maximum.
  * `solve_goal`, `plan_value`: für große n (nur Zählungen); Gleichstände werden dort nicht aufgelöst, der Bestandsplan ist ein Optimalplan des Lösers.
Quelle des Beispiels: Stück 1 bis 5 der Linie (`zielvergleich-demo`, `gleichstand-demo`), neu geschrieben."""

import itertools
from functools import lru_cache

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

import zlw_constants as C

MAX_ENUM_N = 8


@lru_cache(maxsize=None)
def perms(n: int) -> np.ndarray:
    if n > MAX_ENUM_N:
        raise ValueError(f"n = {n} ist zu groß für die Aufzählung (höchstens {MAX_ENUM_N})")
    return np.array(list(itertools.permutations(range(n))), dtype=np.int8)


def burdens(c: np.ndarray, P: np.ndarray) -> np.ndarray:
    """Belastung je Person und Plan: Zeile = Plan, Spalte i = Kosten des Paares (Person i, Aufgabe p[i])."""
    n = c.shape[0]
    return c[np.arange(n)[None, :], P.astype(np.int64)]


def values(b: np.ndarray) -> dict[str, np.ndarray]:
    s = b.sum(axis=1)
    mx = b.max(axis=1)
    return {"S": s, "Q": (b ** 2).sum(axis=1), "M": mx, "L": mx * C.LEX + s, "T": s * C.LEX + mx}


def picks(v: dict[str, np.ndarray]) -> dict[str, int]:
    """Der gewählte Plan je Ziel: der kleinste Index unter den Optimalplänen."""
    return {g: int(np.argmin(v[g])) for g in C.GOALS}


def optimal_set(v: np.ndarray) -> np.ndarray:
    return np.flatnonzero(v == v.min())


def hamming(P: np.ndarray, i: int, j: int) -> int:
    return int((P[i] != P[j]).sum())


def dominates(a: tuple[int, int], b: tuple[int, int]) -> bool:
    """Der Punkt a = (Summe, Maximum) dominiert b: in keinem Maß schlechter, in einem besser."""
    return a[0] <= b[0] and a[1] <= b[1] and a != b


def both_good(point: tuple[int, int], s_min: int, m_min: int, pct: int = C.BOTH_PCT) -> bool:
    """Summe und Maximum innerhalb von pct Prozent des jeweils Besten (ganzzahlig exakt)."""
    return point[0] * 100 <= (100 + pct) * s_min and point[1] * 100 <= (100 + pct) * m_min


def noisy(c: np.ndarray, a: int, seed: int, draw: int) -> np.ndarray:
    """Jede Zahl ändert sich um eine ganze Zahl von -a bis +a (gleichverteilt), mindestens 1; Zufallsstrom seed * 1000 + draw."""
    rng = np.random.default_rng(seed * 1000 + draw)
    return np.maximum(1, c + rng.integers(-a, a + 1, c.shape))


# --- Große Zuordnungen (nur Zählungen) -----------------------------------------------------------------------------------------------------

def solve_bottleneck(c: np.ndarray) -> tuple[int, np.ndarray]:
    """Engpasszuordnung: kleinstes t, für das die Kanten mit c <= t ein perfektes Matching haben."""
    vals = np.unique(c)
    lo, hi, best = 0, len(vals) - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        t = vals[mid]
        m = maximum_bipartite_matching(csr_matrix((c <= t).astype(np.int8)), perm_type="column")
        if (m >= 0).all():
            best = (int(t), m.copy())
            hi = mid - 1
        else:
            lo = mid + 1
    return best


def solve_goal(c: np.ndarray, goal: str) -> np.ndarray:
    n = c.shape[0]
    if goal in ("S", "Q"):
        r, col = linear_sum_assignment(c.astype(np.int64) if goal == "S" else c.astype(np.int64) ** 2)
        out = np.empty(n, dtype=int)
        out[r] = col
        return out
    t, m = solve_bottleneck(c)
    if goal == "M":
        return m.astype(int)
    big = int(c.max()) * n * 10 + 1
    r, col = linear_sum_assignment(np.where(c <= t, c, big))                 # L: unter allen Engpass-Optima die kleinste Summe
    out = np.empty(n, dtype=int)
    out[r] = col
    return out


def plan_value(c: np.ndarray, plan: np.ndarray, goal: str) -> int:
    b = c[np.arange(len(plan)), plan].astype(np.int64)
    return {"S": int(b.sum()), "Q": int((b ** 2).sum()), "M": int(b.max()), "L": int(b.max()) * C.LEX + int(b.sum())}[goal]
