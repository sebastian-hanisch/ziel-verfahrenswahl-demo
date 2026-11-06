"""Welches Ziel? - interaktive Konzept-Demo (Verfahrenswahl, Abschluss der Reihe Zielfunktionsdesign)
Sebastian Hanisch - Operations Research und Machine Learning

Stück 14 der Reihe „Zielfunktionsdesign“: Die Demo rechnet nichts Neues. Sie stellt die Ziele der Stücke 1 bis 5 auf denselben Instanzen nebeneinander, gibt eine Regel (Anforderung → Ziel und Gleichstandsregel) vor der Messung an
und misst, wo sie hält: Aufschlag auf Summe und Maximum, Eindeutigkeit, „beide Maße gut“, Dominanz und Stabilität.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import zlw_constants as C
import zlw_rule as R
from zlw_evaluation import (
    Settings,
    advice_for,
    analyse,
    goal_row,
    num,
    pct,
    plan_text,
    stability,
    summary_enum,
    summary_stability,
    sweep_enum,
    sweep_large,
    sweep_stability,
    table,
    verdict_advice,
    verdict_enum_sweep,
    verdict_goals,
    verdict_stability,
    verdict_stability_sweep,
)
from zlw_layout import dunkles_design, kopf_css
from zlw_pdf_export import build_pdf
from zlw_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from zlw_visualization import build_enum_sweep, build_scatter, build_stability_sweep, build_upsides

st.set_page_config(page_title="Welches Ziel? – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner="60 feste Instanzen werden gerechnet (je 40 320 Pläne, drei Familien) ...")
def _enum():
    return sweep_enum()


@st.cache_data(show_spinner="60 weitere feste Instanzen werden gerechnet (zweite Seed-Menge) ...")
def _holdout():
    return sweep_enum(seeds=C.HOLDOUT_SEEDS)


@st.cache_data(show_spinner="60 feste Instanzen mal 20 Ziehungen werden gerechnet (n = 8, alle Pläne) ...")
def _stab():
    return sweep_stability()


@st.cache_data(show_spinner="60 feste Instanzen mal 20 Ziehungen werden gerechnet (n = 30, Ungarische Methode) ...")
def _large():
    return sweep_large()


def _link(piece: int) -> str:
    label, repo = R.PIECES[piece]
    return f"[{label}](https://github.com/sebastian-hanisch/{repo})"


def _rows_md(t, recommended):
    md = ["| Ziel | Plan | Belastungen | Summe | Maximum | Summe höher | Maximum höher | Optimalpläne | beide Maße gut |", "|---|---|---|---|---|---|---|---|---|"]
    for r in t["rows"]:
        mark = " ◀" if r["goal"] == recommended else ""
        md.append(f"| **{C.GOAL_NAMES[r['goal']]}**{mark} | {plan_text(r['plan'])} | {', '.join(str(x) for x in r['burdens'])} | {r['sum']} | {r['max']} | {pct(r['sum_up'])} | {pct(r['max_up'])} | {r['n_opt']} | {'ja' if r['both'] else 'nein'} |")
    return "\n".join(md)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in zlw_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧭 Welches Ziel?")
st.markdown(
    """
**Welches Ziel, welche Gleichstandsregel, gemessen woran?** Abschluss der Reihe „Zielfunktionsdesign“. Die Demo **rechnet nichts Neues**: dieselbe **Zuordnung** von **n Personen auf n Aufgaben** wie in den Stücken 1 bis 5, fünf Ziele
(**Summe**, **Quadratsumme**, **Maximum**, **Maximum dann Summe**, **Summe dann Maximum**) nebeneinander auf denselben Instanzen. Eine **Regel** sagt vor der Messung, welches Ziel zu welcher Anforderung passt; die Messung sagt, **wo sie hält**.
Kein Ziel gewinnt überall, aber die Wahl ist weniger frei, als sie aussieht.

Weiter unten: **🔬 Der Entscheidungsweg**, **🔬 Die Ziele nebeneinander**, **🔬 Die Zählung**, **🔬 Die Gleichstandsregel**, **🔬 Die Stabilität**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert der Vergleich", expanded=True):
    st.markdown(
        """
1. **Die Instanz:** eine Belastungsmatrix aus ganzen Zahlen; ein Plan weist jeder Person eine Aufgabe zu; alle n! Pläne werden aufgezählt. Das Ziel bestimmt, welcher Plan gewählt wird (bei Gleichstand der kleinste Index der Aufzählung).
2. **Die Regel:** aus der Anforderung (was zählt?), der Grobheit der Daten (aus der Kostenfamilie) und dem Wunsch nach einem eindeutigen Plan wird das Ziel gewählt; sie steht im Quelltext (`zlw_rule.py`) und ändert sich nicht mit der Messung.
3. **Die Messung:** Aufschlag des gewählten Plans auf die beste Summe und das beste Maximum, Zahl der Optimalpläne, „beide Maße innerhalb von 5 %“, Dominanz, Stabilität bei Rauschen.
4. **Messungen, kein Satz:** Alle Zahlen sind Zählungen über feste Instanzen dieses Zufallsmodells; sie sagen nichts über echte Zuordnungsprobleme.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Instanz**")
    n = st.slider("Personen und Aufgaben n", *bounds("n_slider"), key="n_slider", help="Alle n! Pläne werden aufgezählt (bis 40 320).")
    family = st.selectbox("Kosten", list(range(len(C.FAMILIES))), key="family_select", format_func=lambda i: C.FAMILIES[i], help="Grob heißt: wenige verschiedene Werte, viele Gleichstände.")
    seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    st.markdown("**Was zählt?**")
    priority = st.selectbox("Anforderung", list(range(len(C.PRIORITIES))), key="priority_select", format_func=lambda i: C.PRIORITIES[i])
    unique = st.selectbox("Muss der Plan eindeutig sein?", list(range(len(C.UNIQUE_OPTIONS))), key="unique_select", format_func=lambda i: C.UNIQUE_OPTIONS[i], help="Nur für die Anforderung „ausgewogen“ von Bedeutung.")
    st.markdown("**Rauschen**")
    a_noise = st.slider("Rauschen ± Einheiten", *bounds("a_slider"), key="a_slider", step=C.A_STEP, help="Für die Stabilität: jede Zahl der Matrix ändert sich um −a bis +a ganze Einheiten.")

sync_query_params({"n_slider": int(n), "family_select": int(family), "seed_input": int(seed), "priority_select": int(priority), "unique_select": int(unique), "a_slider": int(a_noise)})

settings = Settings(int(n), int(family), int(seed), int(priority), int(unique), int(a_noise))
a = _analysis(settings)
t = table(a)
adv = advice_for(settings)
row = None if adv.goal is None else goal_row(a, adv.goal)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis: welches Ziel empfiehlt die Regel?")
m1, m2, m3 = st.columns(3)
m1.metric("Empfehlung", "kein Ziel" if adv.goal is None else C.GOAL_SHORT[adv.goal], delta=C.PRIORITIES[settings.priority], delta_color="off")
m2.metric("Verschiedene Pläne", f"{t['distinct']} von 5", delta=f"{t['n_plans']} Pläne zur Wahl", delta_color="off")
if row is None:
    m3.metric("Preis der Empfehlung", "–", delta="kein Ziel entscheidet", delta_color="off")
else:
    m3.metric("Preis der Empfehlung", f"Summe {pct(row['sum_up'])}", delta=f"Maximum {pct(row['max_up'])} über dem Besten", delta_color="off")
st.plotly_chart(build_scatter(a, t, adv.goal), width="stretch", key="scatter_chart")
st.caption("Jeder graue Punkt ist ein Wert-Paar (Summe, Maximum) von mindestens einem Plan; links unten wäre gut für beides. Die farbigen Rauten sind die Pläne, die die fünf Ziele wählen, die größere ist die Empfehlung.")
st.download_button("📄 Empfehlung als PDF", data=build_pdf(a), file_name="welches-ziel.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Welches Ziel passt zu dem, was zählt?")
kind, text = verdict_advice(adv, row)
getattr(st, kind)(text)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Der Entscheidungsweg")
st.caption("Die Regel als Weg: jede Antwort verweist auf die Stücke der Reihe, die sie belegen. Sie steht vor der Messung und ist eine reine Funktion von Anforderung, Daten und Eindeutigkeit.")
for i, step in enumerate(adv.steps, 1):
    links = ", ".join(_link(p) for p in step.pieces)
    st.markdown(f"{i}. **{step.question}** {step.answer} ({links})")
st.markdown(f"**Gleichstandsregel:** {adv.tie_rule}")
for note in adv.notes:
    st.info(note)

st.markdown("---")

st.subheader("🔬 Die Ziele nebeneinander")
st.caption(f"Die fünf Ziele auf dieser Instanz ({C.FAMILIES[settings.family]}, n = {settings.n}, Seed {settings.seed}); ◀ ist die Empfehlung. Aufschläge sind auf das jeweils Beste in Summe beziehungsweise Maximum bezogen.")
st.markdown(_rows_md(t, adv.goal))
st.plotly_chart(build_upsides(t), width="stretch", key="upsides_chart")
kind, text = verdict_goals(t)
getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Die Zählung")
st.caption(f"Dieselben Größen über feste Instanzen (n = {C.SWEEP_N}, alle 40 320 Pläne, je {len(C.SWEEP_SEEDS)} Instanzen und Familie): Aufschläge, Eindeutigkeit, „beide Maße gut“ und Dominanz der Pläne. Der Hold-out prüft dieselben Größen an einer zweiten Menge.")
if st.toggle("Ziele über feste Instanzen nachrechnen (Aufschläge, Eindeutigkeit, Dominanz)", value=False, key="sweep_enum"):
    res = {fam: summary_enum(recs) for fam, recs in _enum().items()}
    kind, text = verdict_enum_sweep(res, f"Die fünf Ziele, n = {C.SWEEP_N}, je {len(C.SWEEP_SEEDS)} feste Instanzen")
    getattr(st, kind)(text)
    for fam in res:
        st.caption(C.FAMILIES[fam])
        st.plotly_chart(build_enum_sweep(res, fam), width="stretch", key=f"enum_chart_{fam}")
if st.toggle("Die Zählung an einer zweiten Menge fester Instanzen gegenprüfen (Hold-out)", value=False, key="sweep_holdout"):
    res = {fam: summary_enum(recs) for fam, recs in _holdout().items()}
    kind, text = verdict_enum_sweep(res, f"Hold-out: andere Seeds {C.HOLDOUT_SEEDS[0]} bis {C.HOLDOUT_SEEDS[-1]}")
    getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Die Gleichstandsregel")
st.caption("Welches Ziel hat mehrere Optimalpläne, und wie weit streut die Summe darin? Beim Maximum allein entscheidet der kleinste Index, nicht das Ziel; die zweite Stufe („dann Summe“) macht daraus einen eindeutigen oder nahezu eindeutigen Plan.")
tie_md = ["| Ziel | Optimalpläne | Spanne der Summe in der Optimalmenge |", "|---|---|---|"]
for r in t["rows"]:
    tie_md.append(f"| {C.GOAL_NAMES[r['goal']]} | {r['n_opt']} | {'–' if r['spread'] is None else pct(r['spread'])} |")
st.markdown("\n".join(tie_md))

st.markdown("---")

st.subheader("🔬 Die Stabilität")
st.caption(f"Wie oft ist der Bestandsplan jedes Ziels bei Rauschen ±{settings.a} nicht mehr optimal? Auf dieser Instanz {C.NOISE_DRAWS} Ziehungen; gezählt über feste Instanzen für n = 8 und n = 30.")
st_inst = stability(a)
kind, text = verdict_stability(st_inst, settings.a)
getattr(st, kind)(text)
if st.toggle("Die Stabilität über feste Instanzen nachrechnen (n = 8 und n = 30)", value=False, key="sweep_stability"):
    r8 = {fam: summary_stability(recs) for fam, recs in _stab().items()}
    rl = {fam: summary_stability(recs, C.LARGE_GOALS) for fam, recs in _large().items()}
    kind, text = verdict_stability_sweep(r8, f"n = {C.SWEEP_N}")
    getattr(st, kind)(text)
    kind, text = verdict_stability_sweep(rl, f"n = {C.SWEEP_LARGE_N} (Ungarische Methode, Engpassverfahren; der Bestandsplan ist ein Optimalplan des Lösers)")
    getattr(st, kind)(text)
    st.plotly_chart(build_stability_sweep(r8, rl), width="stretch", key="stability_chart")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Zuordnung als Beispiel** | Die Regel ist an der Zuordnung gemessen; andere Probleme haben andere Ziele, Zwei-Kriterien-Fälle und Strafterme sind nicht Teil des Portfolios | Stück 3, 6 |
| **„Fair“ heißt Maximum** | Das Maximum der Belastung ist eine Wahl; andere Maße (Gini, α-Fairness) sind nicht gemessen | Stück 2 |
| **Regel und Messung am selben Material** | Die Regel wurde an denselben 20 Instanzen je Familie gebildet, an denen sie gemessen wird; der Hold-out an zweiten Seeds relativiert das | – |
| **Stabilität nur mit additivem Rauschen** | Gleichverteiltes ganzzahliges Rauschen je Zahl; gemeinsame Fehler je Person oder Aufgabe ändern den Plan anders; für n = 30 ist der Bestandsplan ein Optimalplan des Lösers | Stück 11 |
| **Alle Pläne aufgezählt** | Bis 40 320 Pläne (n = 8); größere Zuordnungen nur mit Lösern, hier nur für die Stabilitätszählung | Dokumentation des Lösers |
| **Gleichstand: kleinster Index** | Beim Maximum allein entscheidet die Regel, nicht das Ziel; die Wahl ändert sich mit der Nummerierung | Stück 5 |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Problem.** Belastungsmatrix $c \in \mathbb{Z}^{n \times n}$; ein Plan ist eine Permutation $\pi$; die Belastung der Person $i$ ist $b_i = c_{i\pi(i)}$. Summe $\Sigma(\pi) = \sum_i b_i$, Maximum $\mu(\pi) = \max_i b_i$.

**Ziele.** $S = \Sigma$; $Q = \sum_i b_i^2$; $M = \mu$ (bei Gleichstand der kleinste Index); $L = L_0 \mu + \Sigma$ (erst das Maximum, dann die Summe); $T = L_0 \Sigma + \mu$ (erst die Summe, dann das Maximum) mit einer Konstanten $L_0$ über allen Summen.

**Größen.** Aufschlag eines Plans: $(\Sigma(\pi) - \Sigma^*) / \Sigma^*$ und $(\mu(\pi) - \mu^*) / \mu^*$ mit dem besten Wert $\Sigma^*$ beziehungsweise $\mu^*$ über alle Pläne. **Beide Maße gut:** $\Sigma(\pi) \le 1{,}05\,\Sigma^*$ und $\mu(\pi) \le 1{,}05\,\mu^*$ (ganzzahlig exakt). **Dominanz:** der Plan $\pi$ dominiert $\pi'$, wenn $\Sigma(\pi) \le \Sigma(\pi')$, $\mu(\pi) \le \mu(\pi')$ und die Paare verschieden sind. $L$ wählt unter den Optimalplänen von $M$ den mit kleinster Summe: sein Plan ist nie schlechter als der von $M$ und dominiert ihn, sobald die Summe kleiner ist. $T$ wählt unter den Optimalplänen von $S$ den mit kleinstem Maximum: nie schlechter als $S$.

**Stabilität.** Neue Kosten $c' = \max(1, c + e)$ mit $e_{ij} \in \{-a, \dots, a\}$. Der Bestandsplan $\pi_0$ ist optimal für $c$ unter dem Ziel; er ist bei $c'$ nicht mehr optimal, wenn sein Zielwert über dem Optimum liegt. Für $n = 30$: Ungarische Methode für $S$ und $Q$ (mit $c^2$), Engpassverfahren für $M$ und $L$ (danach die kleinste Summe unter allen Paaren mit $c \le \mu^*$).

**Literatur.** Keine Aussage dieser Demo stützt sich auf gelesene Literatur; alle Zahlen sind Messungen an dem Zufallsmodell der Demo.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
