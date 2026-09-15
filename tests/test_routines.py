"""deckgen.routines -- die Zell-Routinen (Plan 0003, Schritt 2)."""

from __future__ import annotations

import json

import pytest
from fractions import Fraction

from deckgen.board import BoardDeck
from deckgen.compose import Composition, Glyph
from deckgen.routines import (DOT_Y, Dotting, Duration, Length, _dotted,
                              completions, duration_matrix, entry_matrix,
                              key_cell)

# kleine Tabellen -- gross genug fuer die Achsen, klein im Rendern
DURATIONS = [
    Duration("whole", "1/1", "NOTE_WHOLE", "7", "#6366f1", 1),
    Duration("8th",   "1/8", "NOTE_8TH",   "4", "#10b981", 8),
]
DOTTINGS = [
    Dotting("", "", []),
    Dotting("-dotted", ".", [(".", ())]),
]

SHORTS = [Length("16", Fraction(1, 16)), Length("8", Fraction(1, 8))]
TARGETS = [Length("V", Fraction(1, 4)), Length("H", Fraction(1, 2)),
           Length("G", Fraction(1, 1))]
COLORS = ["#f59e0b", "#10b981"]


@pytest.fixture()
def board(glyphs):
    workbench = BoardDeck(glyphs, name="Test", accent="#3b82f6",
                          icon=Composition([Glyph("MUSIC_NOTES")]),
                          rows=6, columns=6)
    return workbench.root


def _button_at(board, x, y):
    for p in board.folder.placements:
        if (p.x, p.y) == (x, y):
            return p.button
    return None


def _keys(button) -> list[tuple[tuple, str]]:
    flows = json.loads(json.loads(button.data("x"))["flows"])
    out = []
    for block in flows[0]["children"]:
        combo = next(p["value"] for p in block["parameters"]
                     if p["name"] == "combo")
        out.append((tuple(combo["modifiers"]), combo["key"]))
    return out


# -- _dotted: Bruch -> eine punktierte Note -------------------------------------


def test_dotted_decomposition():
    assert _dotted(Fraction(3, 16)) == (8, 1)    # punktierte 8tel
    assert _dotted(Fraction(7, 16)) == (4, 2)    # doppelt punktierte Viertel
    assert _dotted(Fraction(1, 8)) == (8, 0)     # 8tel ohne Punkt
    assert _dotted(Fraction(15, 16)) is None     # dreifach punktiert -- leer
    assert _dotted(Fraction(1, 3)) is None       # Triolenanteil -- geht nicht


# -- duration_matrix ------------------------------------------------------------


def test_matrix_axis_x_puts_durations_side_by_side(board):
    duration_matrix(board, (0, 1), DURATIONS, DOTTINGS, axis="x")
    assert _button_at(board, 0, 1).icon.name == "note-whole"
    assert _button_at(board, 1, 1).icon.name == "note-8th"
    assert _button_at(board, 0, 2).icon.name == "note-whole-dotted"


def test_matrix_axis_y_is_the_same_definition_turned(board):
    duration_matrix(board, (0, 1), DURATIONS, DOTTINGS, axis="y")
    assert _button_at(board, 0, 1).icon.name == "note-whole"
    assert _button_at(board, 0, 2).icon.name == "note-8th"
    assert _button_at(board, 1, 1).icon.name == "note-whole-dotted"


def test_matrix_sends_duration_first_then_dotting(board):
    duration_matrix(board, (0, 0), DURATIONS, DOTTINGS, axis="x")
    assert _keys(_button_at(board, 1, 1)) == \
        [((), "4"), ((), ".")]   # 8tel, dann ein Punkt


def test_matrix_shares_one_scale(board):
    duration_matrix(board, (0, 0), DURATIONS, DOTTINGS, axis="x")
    widths = {round(p.button.icon.width, 6) for p in board.folder.placements}
    assert len(widths) == 1   # master size; die Skala steckt im Ausschnitt


# -- entry_matrix -----------------------------------------------------------------


def test_entry_matrix_types_the_letter_after_duration_and_dots(board):
    entry_matrix(board, (0, 0), DURATIONS, DOTTINGS, axis="x")
    assert _button_at(board, 1, 1).icon.name == "enter-8th-dotted"
    assert _keys(_button_at(board, 1, 1)) == \
        [((), "4"), ((), "."), ((), "c")]      # dotted eighth, middle C


def test_entry_matrix_rest_sends_zero_and_names_the_rest_cells(board):
    entry_matrix(board, (0, 0), DURATIONS, DOTTINGS, axis="x", rest=True,
                 prefix="enter-rest")
    button = _button_at(board, 0, 0)
    assert button.icon.name == "enter-rest-whole"
    assert _keys(button) == [((), "7"), ((), "0")]
    # dotted eighth rest below the plain one -- 0 inserts a rest of the
    # selected duration
    assert _keys(_button_at(board, 1, 1)) == \
        [((), "4"), ((), "."), ((), "0")]


def test_entry_matrix_rest_shares_the_matrix_scale(board):
    entry_matrix(board, (0, 0), DURATIONS, DOTTINGS, axis="x")
    entry_matrix(board, (3, 0), DURATIONS, DOTTINGS, axis="x", rest=True,
                 prefix="enter-rest")
    note = _button_at(board, 0, 0).icon
    rest = _button_at(board, 3, 0).icon
    assert (note.width, note.height) == (rest.width, rest.height)


# -- completions ----------------------------------------------------------------


def test_completion_cells_exist_and_skip_the_hard_ones(board):
    completions(board, (0, 1), SHORTS, TARGETS, colors=COLORS, axis="y")
    # 16tel-Zeile: Viertel und Halbe in beiden Lagen, Ganze leer (3 Punkte)
    assert _button_at(board, 0, 1) is not None   # c8. c16
    assert _button_at(board, 1, 1) is not None   # c16 c8.
    assert _button_at(board, 2, 1) is not None   # c4.. c16
    assert _button_at(board, 4, 1) is None       # Ganze - 16tel: fehlt
    # 8tel-Zeile: zum Viertel kollabiert das Paar (8tel+8tel) -- leer
    assert _button_at(board, 0, 2) is None
    assert _button_at(board, 2, 2) is not None   # c4. c8
    assert _button_at(board, 4, 2) is not None   # c2.. c8


def test_completion_types_the_whole_figure(board):
    """The dotted 8th + 16th cell sends: 8th key, one dot, the letter,
    then the 16th key and the letter."""
    completions(board, (0, 0), SHORTS, TARGETS, colors=COLORS, axis="y")
    assert _keys(_button_at(board, 0, 0)) == \
        [((), "4"), ((), "."), ((), "c"), ((), "3"), ((), "c")]


def test_completion_orders_run_end_then_start(board):
    completions(board, (0, 0), SHORTS, TARGETS, colors=COLORS, axis="y")
    assert _button_at(board, 0, 0).icon.name == "complement-16-V-end"
    assert _button_at(board, 1, 0).icon.name == "complement-16-V-start"


def test_completion_axis_x_is_the_turned_grid(board):
    completions(board, (0, 0), SHORTS, TARGETS, colors=COLORS, axis="x")
    assert _button_at(board, 0, 0).icon.name == "complement-16-V-end"
    # the 8th column starts at its first existing cell -- Viertel collapses
    assert _button_at(board, 1, 0) is None
    assert _button_at(board, 1, 2).icon.name == "complement-8-H-end"


# -- key_cell ---------------------------------------------------------------------


def test_key_cell_renders_the_glyph_and_sends_the_key(board):
    from deckgen.board import Cell

    board.place(0, 0, key_cell("Play", "PLAY", "#10b981", (" ", ())))
    button = _button_at(board, 0, 0)
    assert button.icon.name == "key-play"
    assert button.background == "#10b981"
    assert _keys(button) == [((), " ")]


def test_key_cell_without_glyph_is_text_only(board):
    board.place(0, 0, key_cell("Undo", "", "#1f2937", ("z", ("ctrl",))))
    data = json.loads(_button_at(board, 0, 0).data("x"))
    assert "icon" not in data
    assert data["label"] == "Undo"
    assert _keys(_button_at(board, 0, 0)) == [(("ctrl",), "z")]
