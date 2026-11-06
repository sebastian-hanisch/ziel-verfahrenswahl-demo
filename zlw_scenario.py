"""Szenario: Zuordnung von n Personen auf n Aufgaben mit einer Belastungsmatrix aus ganzen Zahlen. Alles simuliert.

Familie 0 unabhängig: ganze Zahlen 11 bis 109. Familie 1 grob: ganze Zahlen 1 bis 9 (wenige Werte, viele Gleichstände). Familie 2 Person: Personeneffekt 0 bis 40 plus 11 bis 69.
Die Erzeugung entspricht der Messreihe der Planung (gleiche Seeds, gleiche Ziehungen)."""

import numpy as np


def make_matrix(n: int, family: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if family == 0:
        return rng.integers(11, 110, (n, n)).astype(np.int64)
    if family == 1:
        return rng.integers(1, 10, (n, n)).astype(np.int64)
    return (rng.integers(0, 41, (n, 1)) + rng.integers(11, 70, (n, n))).astype(np.int64)
