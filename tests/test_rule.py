"""Die Regel `advise` als reine Funktion: jede Kombination der Eingaben, jede Zeile der Regel, die Verweise auf die Stücke."""

import pytest

import zlw_constants as C
import zlw_rule as R

GRID = [(p, d, u) for p in range(4) for d in ("fein", "grob") for u in (0, 1)]


@pytest.mark.parametrize("priority,data,unique", GRID)
def test_every_input_combination_gives_a_complete_advice(priority, data, unique):
    adv = R.advise(priority, data, unique)
    assert (adv.priority, adv.data, adv.unique) == (priority, data, unique) and adv.label and adv.tie_rule and adv.steps and adv.steps[-1].pieces == (13,)
    assert adv.goal is None or adv.goal in C.GOALS
    for step in adv.steps:
        assert step.question and step.answer and all(p in R.PIECES for p in step.pieces)


def test_each_row_of_the_rule():
    assert R.advise(0, "fein").goal == "T" and R.advise(0, "grob").goal == "T" and R.advise(0, "fein").label == "Summe, dann Maximum"
    assert R.advise(1, "fein").goal == "L" and R.advise(1, "grob").goal == "L" and R.advise(1, "fein").label == "Maximum, dann Summe"
    assert R.advise(2, "fein", 1).goal == "Q" and R.advise(2, "grob", 1).goal == "Q" and R.advise(2, "fein", 0).goal == "L" and R.advise(2, "grob", 0).goal == "L"
    assert R.advise(3, "fein").goal is None and R.advise(3, "grob", 1).goal is None and "Wechselkosten" in R.advise(3, "fein").tie_rule


def test_the_maximum_alone_is_never_recommended():
    assert all(R.advise(p, d, u).goal != "M" for p, d, u in GRID)


def test_the_unique_wish_only_matters_for_balanced():
    for p in (0, 1, 3):
        assert R.advise(p, "fein", 0).goal == R.advise(p, "fein", 1).goal
    assert R.advise(2, "fein", 0).goal != R.advise(2, "fein", 1).goal


def test_notes_depend_on_the_data_and_the_priority():
    assert any("Gleichstandsregel ist wichtiger" in n for n in R.advise(1, "grob").notes) and not R.advise(1, "fein").notes
    assert any("fast wirkungslos" in n for n in R.advise(0, "fein").notes) and not any("fast wirkungslos" in n for n in R.advise(0, "grob").notes)
    assert any("ähnlich schlecht" in n for n in R.advise(3, "grob").notes) and not any("Gleichstandsregel ist wichtiger" in n for n in R.advise(3, "grob").notes)


def test_invalid_inputs_raise():
    for bad in ((4, "fein", 0), (-1, "fein", 0), (0, "mittel", 0), (0, "fein", 2)):
        with pytest.raises(ValueError):
            R.advise(*bad)


def test_pieces_point_to_the_repos_of_the_line():
    assert R.PIECES[5] == ("Stück 5", "gleichstand-demo") and R.PIECES[11] == ("Stück 11", "planstabilitaet-demo") and R.PIECES[13] == ("Stück 13", "zielkarte-demo")
    assert all(repo.endswith("-demo") for _, repo in R.PIECES.values())


def test_the_rule_is_a_pure_function():
    assert R.advise(2, "grob", 1) == R.advise(2, "grob", 1)
