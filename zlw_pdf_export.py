"""PDF-Export der Empfehlung und der Ziele nebeneinander (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

import zlw_constants as C
from zlw_evaluation import Analysis, advice_for, goal_row, pct, table, verdict_advice, verdict_goals

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "×": "x", "„": '"', "“": '"', "²": "2", "∞": "unendlich", "±": "+-"}


def _s(text) -> str:
    out = str(text).replace("**", "").replace("`", "")
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis) -> bytes:
    s = a.settings
    t = table(a)
    adv = advice_for(s)
    row = None if adv.goal is None else goal_row(a, adv.goal)
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Welches Ziel?"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _s(f"Zuordnung {s.n} x {s.n}, Familie: {C.FAMILIES[s.family]}, Seed {s.seed}. Alles simuliert."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.multi_cell(0, 5, _s(verdict_advice(adv, row)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    for step in adv.steps:
        pdf.multi_cell(0, 5, _s(f"- {step.question} {step.answer}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, _s("Die Ziele nebeneinander"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for r in t["rows"]:
        pdf.multi_cell(0, 5, _s(f"{C.GOAL_NAMES[r['goal']]}: Summe {r['sum']} ({pct(r['sum_up'])} über dem Besten), Maximum {r['max']} ({pct(r['max_up'])}), {r['n_opt']} Optimalpläne"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 5, _s(verdict_goals(t)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Bei Gleichstand gilt der kleinste Index der Aufzählung. Quelle: ziel-verfahrenswahl-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
