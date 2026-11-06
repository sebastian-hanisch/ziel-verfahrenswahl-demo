"""Experimente der App: jedes Preset, jede Familie, jede Anforderung, jeder Regler an den Grenzen, jede Größe und alle Zählungen laufen ohne Fehler."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import zlw_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at) -> str:
    return " ".join(m.value for kind in ("success", "info", "warning") for m in getattr(at, kind))


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_runs_and_shows_a_verdict(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, (name, [str(e) for e in at.exception])
    assert "Für die Anforderung" in _texts(at) and ("verschiedene Pläne" in _texts(at) or "denselben Plan" in _texts(at) or "zugleich am besten" in _texts(at))


def test_default_preset_shows_the_recommendation_and_the_goals():
    text = _texts(_app())
    assert "empfiehlt die Regel **Maximum, dann Summe**" in text and "**Kein Ziel gewinnt überall:**" in text and "4 verschiedene Pläne" in text


@pytest.mark.parametrize("priority", range(len(C.PRIORITIES)))
def test_every_priority_runs(priority):
    at = _app()
    at.sidebar.selectbox(key="priority_select").set_value(priority).run()
    assert not at.exception, [str(e) for e in at.exception]
    assert ("entscheidet **kein Ziel**" in _texts(at)) == (priority == 3)


def test_the_unique_wish_changes_the_balanced_recommendation():
    at = _app()
    at.sidebar.selectbox(key="priority_select").set_value(2).run()
    assert "**Maximum, dann Summe**" in _texts(at)
    at.sidebar.selectbox(key="unique_select").set_value(1).run()
    assert not at.exception and "**Quadratsumme**" in _texts(at)


@pytest.mark.parametrize("family", range(len(C.FAMILIES)))
def test_every_family_runs(family):
    at = _app()
    at.sidebar.selectbox(key="family_select").set_value(family).run()
    assert not at.exception, [str(e) for e in at.exception]
    assert (("(grobe Daten)" in _texts(at)) == (family == 1))


@pytest.mark.parametrize("key,value", [("a_slider", C.A_MIN), ("a_slider", C.A_MAX), ("n_slider", C.N_MIN), ("n_slider", C.N_MAX)])
def test_every_parameter_extreme_runs(key, value):
    at = _app()
    at.sidebar.slider(key=key).set_value(value).run()
    assert not at.exception, [str(e) for e in at.exception]


def test_the_counts_run_when_switched_on():
    at = _app()
    for key in ("sweep_enum", "sweep_holdout", "sweep_stability"):
        at.toggle(key=key).set_value(True).run()
        assert not at.exception, (key, [str(e) for e in at.exception])
    text = _texts(at)
    assert "Die fünf Ziele, n = 8, je 20 feste Instanzen" in text and "Hold-out: andere Seeds 100100 bis 100119" in text and "n = 30 (Ungarische Methode" in text
