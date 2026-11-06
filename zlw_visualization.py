"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import numpy as np
import plotly.graph_objects as go

import zlw_constants as C
import zlw_evaluation as ev

FAM_COLORS = {0: "#4c78a8", 1: "#7b5ea7", 2: "#2F6B65"}


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_scatter(a: ev.Analysis, t: dict, recommended: str | None):
    """Alle Pläne als Punkte (Summe waagerecht, Maximum senkrecht; gleiche Punkte nur einmal) und die fünf gewählten Pläne; die Empfehlung ist größer."""
    pts = np.unique(np.stack([a.v["S"], a.v["M"]], axis=1), axis=0)
    fig = go.Figure(go.Scattergl(x=pts[:, 0], y=pts[:, 1], mode="markers", marker=dict(size=3, color=C.COLOR_ALL), name="Pläne", hovertemplate="Summe %{x} / Maximum %{y}<extra></extra>"))
    same = {}
    for r in t["rows"]:
        same.setdefault(r["point"], []).append(r["goal"])
    for r in t["rows"]:
        big = r["goal"] == recommended
        names = ", ".join(C.GOAL_SHORT[g] for g in same[r["point"]])
        fig.add_trace(go.Scatter(x=[r["sum"]], y=[r["max"]], mode="markers", marker=dict(symbol="diamond", size=17 if big else 11, color=C.GOAL_COLORS[r["goal"]], line=dict(width=2 if big else 1, color="white")),
                                 name=C.GOAL_SHORT[r["goal"]] + (" (Empfehlung)" if big else ""), hovertemplate=f"{names}: Summe %{{x}} / Maximum %{{y}}<extra></extra>"))
    fig.update_xaxes(title_text="Summe der Belastungen (kleiner ist besser)")
    fig.update_yaxes(title_text="Maximum der Belastungen (kleiner ist besser)")
    return _base(fig, height=420)


def build_upsides(t: dict):
    """Aufschlag der gewählten Pläne auf die beste Summe und das beste Maximum (Prozent)."""
    rows = t["rows"]
    xs = [C.GOAL_SHORT[r["goal"]] for r in rows]
    fig = go.Figure([go.Bar(x=xs, y=[r["sum_up"] * 100 for r in rows], name="Summe höher", marker_color="#4c78a8", hovertemplate="%{x}: Summe %{y:.1f} % über dem Besten<extra></extra>"),
                     go.Bar(x=xs, y=[r["max_up"] * 100 for r in rows], name="Maximum höher", marker_color="#c0504d", hovertemplate="%{x}: Maximum %{y:.1f} % über dem Besten<extra></extra>")])
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category", title_text="Ziel")
    fig.update_yaxes(title_text="Aufschlag auf das Beste in Prozent")
    return _base(fig, height=300)


def build_enum_sweep(res: dict, fam: int):
    """Je Ziel: Instanzen mit eindeutigem Optimum und Instanzen, in denen Summe und Maximum zugleich innerhalb von 5 % des Besten liegen."""
    s = res[fam]
    xs = [C.GOAL_SHORT[g] for g in C.GOALS]
    fig = go.Figure([go.Bar(x=xs, y=[s["goals"][g]["unique"] for g in C.GOALS], name="eindeutiges Optimum", marker_color="#2F6B65", hovertemplate="%{x}: eindeutig in %{y} Instanzen<extra></extra>"),
                     go.Bar(x=xs, y=[s["goals"][g]["both"] for g in C.GOALS], name=f"beide Maße innerhalb von {C.BOTH_PCT} %", marker_color="#d8a13a", hovertemplate="%{x}: beide Maße gut in %{y} Instanzen<extra></extra>")])
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category", title_text="Ziel")
    fig.update_yaxes(title_text=f"Instanzen von {s['seeds']}", range=[0, s["seeds"]])
    return _base(fig, height=300)


def build_stability_sweep(res8: dict, res_large: dict):
    """Anteil der Ziehungen, in denen der Bestandsplan nicht mehr optimal ist: je Familie für n = 8 und n = 30."""
    fig = go.Figure()
    for fam, s in res8.items():
        fig.add_trace(go.Bar(x=[C.GOAL_SHORT[g] for g in C.LARGE_GOALS], y=[s[g]["rate"] * 100 for g in C.LARGE_GOALS], name=f"{C.FAMILIES[fam]}, n = 8", marker_color=FAM_COLORS[fam],
                             hovertemplate="%{x}: %{y:.1f} % der Ziehungen<extra></extra>"))
    for fam, s in res_large.items():
        fig.add_trace(go.Bar(x=[C.GOAL_SHORT[g] for g in C.LARGE_GOALS], y=[s[g]["rate"] * 100 for g in C.LARGE_GOALS], name=f"{C.FAMILIES[fam]}, n = {C.SWEEP_LARGE_N}", marker_color=FAM_COLORS[fam],
                             marker_pattern_shape="/", hovertemplate="%{x}: %{y:.1f} % der Ziehungen<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category", title_text="Ziel")
    fig.update_yaxes(title_text="Bestandsplan nicht mehr optimal (% der Ziehungen)", range=[0, 100])
    return _base(fig, height=360)
