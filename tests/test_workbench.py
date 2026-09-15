"""decks/workbench.py -- the workbench deck (plan 0003, step 3;
layout per plan 0004, entry board and bars per plan 0006)."""

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


def test_six_boards_on_one_grid_with_the_menu_in_column_zero(wb):
    assert [b.name for b in wb.boards] == \
        ["Noten", "Eingeben", "Ergänzungen", "Rhythmen", "Transport",
         "Bearbeiten"]
    for board in wb.boards:
        assert (board.columns, board.rows) == (11, 7)
        menu_column = [(p.x, p.y) for p in board.folder.placements if p.x == 0]
        assert menu_column == [(0, i) for i in range(6)]
        # the action bar is wired but empty: the bottom row stays free
        assert all(p.y < 6 for p in board.folder.placements)


def test_menu_buttons_navigate(wb):
    for board in wb.boards:
        for i, target in enumerate(wb.boards):
            assert _folder_id(_button_at(board, 0, i)) == target.folder.id


def test_active_board_wears_its_accent(wb):
    for board in wb.boards:
        for i, target in enumerate(wb.boards):
            expected = target.accent if target is board else "#1f2937"
            assert _button_at(board, 0, i).background == expected


# -- the time-signature column ----------------------------------------------------


def test_time_signature_column_before_the_content(wb):
    """Five text buttons in column 1 of Noten and Eingeben -- the keys are
    the proposed assignment (docs/taktarten-kuerzel.md), no icon: the UI
    font has no 2/4, C, cent glyphs."""
    for board in (wb.root, wb.boards[1]):
        for i, (label, key, mods) in enumerate(workbench.TIME_SIGNATURES):
            button = _button_at(board, 1, i)
            assert button is not None
            assert button.label == label
            assert button.icon is None
            assert button.background == workbench.BAR_COLOR
            assert _keys(button) == [(mods, key)]


# -- Noten: the matrix beside the signature column --------------------------------


def test_root_holds_the_duration_matrix(wb):
    for x in range(2, 8):
        for y in range(0, 3):
            button = _button_at(wb.root, x, y)
            assert button is not None and button.icon is not None
    assert _button_at(wb.root, 2, 0).icon.name == "note-32nd"
    assert _button_at(wb.root, 7, 2).icon.name == "note-whole-double-dotted"


def test_matrix_cell_sends_duration_then_dotting(wb):
    assert _keys(_button_at(wb.root, 5, 1)) == [((), "5"), ((), ".")]


# -- Eingeben: the same matrix, entering middle C -- or a rest --------------------


def test_entry_cells_type_middle_c_after_duration_and_dots(wb):
    board = wb.boards[1]
    assert _button_at(board, 2, 0).icon.name == "enter-note-32nd"
    assert _keys(_button_at(board, 4, 1)) == \
        [((), "4"), ((), "."), ((), "c")]      # dotted eighth


def test_rest_cells_send_zero_and_sit_below_the_notes(wb):
    board = wb.boards[1]
    assert _button_at(board, 2, 3).icon.name == "enter-rest-32nd"
    assert _keys(_button_at(board, 4, 4)) == \
        [((), "4"), ((), "."), ((), "0")]      # dotted eighth rest


# -- Ergänzungen ------------------------------------------------------------------


def test_completions_fill_two_rows(wb):
    board = wb.boards[2]
    # 16tel: Viertel und Halbe in beiden Lagen, Ganze bleibt leer (3 Punkte)
    assert _button_at(board, 1, 0).icon.name == "complement-16-Viertel-end"
    assert _button_at(board, 4, 0).icon.name == "complement-16-Halbe-start"
    assert _button_at(board, 5, 0) is None and _button_at(board, 6, 0) is None
    # 8tel: zum Viertel kollabiert das Paar -- leer, Halbe und Ganze da
    assert _button_at(board, 1, 1) is None
    assert _button_at(board, 3, 1).icon.name == "complement-8-Halbe-end"
    assert _button_at(board, 6, 1).icon.name == "complement-8-Ganze-start"


def test_the_dotted_eighth_sixteenth_button_types_the_whole_figure(wb):
    board = wb.boards[2]
    assert _keys(_button_at(board, 1, 0)) == \
        [((), "4"), ((), "."), ((), "c"), ((), "3"), ((), "c")]


# -- Rhythmen, Transport, Bearbeiten ---------------------------------------------


def test_rhythmen_hold_the_accepted_figures(wb):
    board = wb.boards[3]
    buttons = [p for p in board.folder.placements if p.x > 0]
    assert len(buttons) == len(patterns.FIGURES) == 11
    assert _button_at(board, 1, 0).icon.name == "figure-halbe"


def test_transport_and_edit_send_their_keys(wb):
    assert _keys(_button_at(wb.boards[4], 1, 0)) == [((), "space")]
    assert _keys(_button_at(wb.boards[5], 1, 0)) == [(("ctrl",), "z")]
    assert _button_at(wb.boards[5], 1, 0).label == "Rückgängig"


def test_key_boards_are_labelled_even_without_labels_flag(wb):
    for board in wb.boards[4:]:
        for p in board.folder.placements:
            if p.x > 0:
                assert p.button.label


def test_horizontal_menu_keeps_the_content_below_the_strip(glyphs):
    deck = workbench.build(glyphs, "Noten", "MuseScore4", False, None,
                           menu="horizontal")
    menu_row = [(p.x, p.y) for p in deck.root.folder.placements if p.y == 0]
    assert menu_row == [(i, 0) for i in range(6)]
    # the signatures take the column before the content, one row down
    assert _button_at(deck.root, 0, 1).label == "2/4"
    assert _button_at(deck.root, 1, 1).icon.name == "note-32nd"


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
