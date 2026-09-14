"""decks/workbench.py -- the workbench deck (plan 0003, step 3;
layout per plan 0004)."""

from __future__ import annotations

import json

import pytest

import workbench
import patterns
from deckgen.board import BoardDeck


@pytest.fixture(scope="module")
def glyphs():
    from deckgen.glyphs import Glyphs
    return Glyphs()


@pytest.fixture(scope="module")
def wb(glyphs):
    return workbench.build(glyphs, "Noten", "MuseScore4", labels=False,
                           svg_dir=None)


def _button_at(board, x, y):
    for p in board.folder.placements:
        if (p.x, p.y) == (x, y):
            return p.button
    return None


def _flows(button) -> list:
    return json.loads(json.loads(button.data("x"))["flows"])


def _keys(button) -> list[tuple[tuple, str]]:
    out = []
    for block in _flows(button)[0]["children"]:
        combo = next(p["value"] for p in block["parameters"]
                     if p["name"] == "combo")
        out.append((tuple(combo["modifiers"]), combo["key"]))
    return out


def _folder_id(button) -> str:
    block = _flows(button)[0]["children"][0]
    return next(p["value"] for p in block["parameters"]
                if p["name"] == "folderId")


# -- structure --------------------------------------------------------------------


def test_five_boards_on_one_grid_with_the_menu_in_column_zero(wb):
    assert [b.name for b in wb.boards] == \
        ["Noten", "Ergänzungen", "Rhythmen", "Transport", "Bearbeiten"]
    for board in wb.boards:
        assert (board.columns, board.rows) == (7, 5)
        menu_column = [(p.x, p.y) for p in board.folder.placements if p.x == 0]
        assert menu_column == [(0, i) for i in range(5)]


def test_menu_buttons_navigate(wb):
    for board in wb.boards:
        for i, target in enumerate(wb.boards):
            assert _folder_id(_button_at(board, 0, i)) == target.folder.id


def test_active_board_wears_its_accent(wb):
    for board in wb.boards:
        for i, target in enumerate(wb.boards):
            expected = target.accent if target is board else "#1f2937"
            assert _button_at(board, 0, i).background == expected


# -- Noten: the matrix beside the menu column -------------------------------------


def test_root_holds_the_duration_matrix(wb):
    for x in range(1, 7):
        for y in range(0, 3):
            button = _button_at(wb.root, x, y)
            assert button is not None and button.icon is not None
    assert _button_at(wb.root, 1, 0).icon.name == "note-32nd"
    assert _button_at(wb.root, 6, 2).icon.name == "note-whole-double-dotted"


def test_matrix_cell_sends_duration_then_dotting(wb):
    assert _keys(_button_at(wb.root, 4, 1)) == [((), "5"), ((), ".")]


# -- Ergänzungen ------------------------------------------------------------------


def test_completions_fill_two_rows(wb):
    board = wb.boards[1]
    # 16tel: Viertel und Halbe in beiden Lagen, Ganze bleibt leer (3 Punkte)
    assert _button_at(board, 1, 0).icon.name == "complement-16-Viertel-end"
    assert _button_at(board, 4, 0).icon.name == "complement-16-Halbe-start"
    assert _button_at(board, 5, 0) is None and _button_at(board, 6, 0) is None
    # 8tel: zum Viertel kollabiert das Paar -- leer, Halbe und Ganze da
    assert _button_at(board, 1, 1) is None
    assert _button_at(board, 3, 1).icon.name == "complement-8-Halbe-end"
    assert _button_at(board, 6, 1).icon.name == "complement-8-Ganze-start"


def test_the_dotted_eighth_sixteenth_button_types_the_whole_figure(wb):
    board = wb.boards[1]
    assert _keys(_button_at(board, 1, 0)) == \
        [((), "4"), ((), "."), ((), "c"), ((), "3"), ((), "c")]


# -- Rhythmen, Transport, Bearbeiten ---------------------------------------------


def test_rhythmen_hold_the_accepted_figures(wb):
    board = wb.boards[2]
    buttons = [p for p in board.folder.placements if p.x > 0]
    assert len(buttons) == len(patterns.FIGURES) == 12
    assert _button_at(board, 1, 0).icon.name == "figure-halbe"


def test_transport_and_edit_send_their_keys(wb):
    assert _keys(_button_at(wb.boards[3], 1, 0)) == [((), "space")]
    assert _keys(_button_at(wb.boards[4], 1, 0)) == [(("ctrl",), "z")]
    assert _button_at(wb.boards[4], 1, 0).label == "Rückgängig"


def test_key_boards_are_labelled_even_without_labels_flag(wb):
    for board in wb.boards[3:]:
        for p in board.folder.placements:
            if p.x > 0:
                assert p.button.label


def test_horizontal_menu_keeps_the_content_below_the_strip(glyphs):
    deck = workbench.build(glyphs, "Noten", "MuseScore4", False, None,
                           menu="horizontal")
    menu_row = [(p.x, p.y) for p in deck.root.folder.placements if p.y == 0]
    assert menu_row == [(i, 0) for i in range(5)]
    assert _button_at(deck.root, 0, 1).icon.name == "note-32nd"


# -- bit identity ----------------------------------------------------------------


def test_two_runs_are_bit_identical(glyphs, tmp_path):
    first = workbench.build(glyphs, "Noten", "MuseScore4", False, None)
    second = workbench.build(glyphs, "Noten", "MuseScore4", False, None)
    a = first.deck.write(tmp_path / "a.macroDeckFolder")
    b = second.deck.write(tmp_path / "b.macroDeckFolder")
    assert a.read_bytes() == b.read_bytes()


def test_boarddeck_is_what_build_returns(wb):
    assert isinstance(wb, BoardDeck)
    assert wb.deck.root.name == "Noten"
