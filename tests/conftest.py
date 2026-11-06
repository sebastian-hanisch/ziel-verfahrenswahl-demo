"""Gemeinsame Fixtures: das Handbeispiel (n = 4, aus Stück 1), an dem jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import zlw_evaluation as ev  # noqa: E402

HAND = np.array([[7, 6, 7, 5], [6, 4, 3, 6], [8, 4, 7, 2], [4, 2, 2, 6]], dtype=np.int64)


@pytest.fixture
def hand() -> np.ndarray:
    """Handbeispiel n = 4: Summe 14 (Belastungen 7, 3, 2, 2; Plan 0→0, 1→2, 2→3, 3→1), Quadratsumme 65 (6, 3, 2, 4; Summe 15, Maximum 6), Maximum 5 (5, 3, 4, 4; Summe 16);
    jeder der drei Pläne ist unter seinem Ziel eindeutig."""
    return HAND


@pytest.fixture
def hand_analysis(hand) -> ev.Analysis:
    return ev.analyse_matrix(hand, ev.Settings(4, 0, 0))
