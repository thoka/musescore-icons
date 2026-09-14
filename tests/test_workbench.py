"""decks/workbench.py -- das Arbeitsdeck (Plan 0003, Schritt 3)."""

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


# -- Struktur --------------------------------------------------------------------


def test_five_boards_with_the_menu_strip_on_top(wb):
    assert [b.name for b in wb.boards] == \
        ["Noten", "Ergänzungen", "Rhythmen", "Transport", "Bearbeiten"]
    for board in wb.boards:
        first_row = [(p.x, p.y) for p in board.folder.placements if p.y == 0]
        assert first_row == [(i, 0) for i in range(5)]


def test_menu_buttons_navigate(wb):
    for board in wb.boards:
        for i, target in enumerate(wb.boards):
            assert _folder_id(_button_at(board, i, 0)) == target.folder.id


def test_active_board_wears_its_accent(wb):
    for board in wb.boards:
        for i, target in enumerate(wb.boards):
            expected = target.accent if target is board else "#1f2937"
            assert _button_at(board, i, 0).background == expected


# -- Noten: die Matrix unter der Menüleiste --------------------------------------


def test_root_holds_the_duration_matrix(wb):
    for x in range(6):
        for y in range(1, 4):
            button = _button_at(wb.root, x, y)
            assert button is not None and button.icon is not None
    assert _button_at(wb.root, 0, 1).icon.name == "note-whole"
    assert _button_at(wb.root, 5, 3).icon.name == "note-32nd-double-dotted"


def test_matrix_cell_sends_duration_then_dotting(wb):
    assert _keys(_button_at(wb.root, 3, 2)) == [((), "4"), ((), ".")]


# -- Ergänzungen -----------------------------------------------------------------


def test_completions_fill_two_rows(wb):
    board = wb.boards[1]
    # 16tel: Viertel und Halbe in beiden Lagen, Ganze bleibt leer (3 Punkte)
    assert _button_at(board, 0, 1).icon.name == "complement-16-Viertel-end"
    assert _button_at(board, 3, 1).icon.name == "complement-16-Halbe-start"
    assert _button_at(board, 4, 1) is None and _button_at(board, 5, 1) is None
    # 8tel: zum Viertel kollabiert das Paar -- leer, Halbe und Ganze da
    assert _button_at(board, 0, 2) is None
    assert _button_at(board, 2, 2).icon.name == "complement-8-Halbe-end"
    assert _button_at(board, 5, 2).icon.name == "complement-8-Ganze-start"


def test_the_dotted_eighth_sixteenth_button_types_the_whole_figure(wb):
    board = wb.boards[1]
    assert _keys(_button_at(board, 0, 1)) == \
        [((), "4"), ((), "."), ((), "c"), ((), "3"), ((), "c")]


# -- Rhythmen, Transport, Bearbeiten ---------------------------------------------


def test_rhythmen_hold_the_accepted_figures(wb):
    board = wb.boards[2]
    buttons = [p for p in board.folder.placements if p.y > 0]
    assert len(buttons) == len(patterns.FIGURES) == 12
    assert _button_at(board, 0, 1).icon.name == "figure-halbe"


def test_transport_and_edit_send_their_keys(wb):
    assert _keys(_button_at(wb.boards[3], 0, 1)) == [((), "space")]
    assert _keys(_button_at(wb.boards[4], 0, 1)) == [(("ctrl",), "z")]
    assert _button_at(wb.boards[4], 0, 1).label == "Rückgängig"


def test_key_boards_are_labelled_even_without_labels_flag(wb):
    for board in wb.boards[3:]:
        for p in board.folder.placements:
            if p.y > 0:
                assert p.button.label


# -- Bitgleichheit ----------------------------------------------------------------


def test_two_runs_are_bit_identical(glyphs, tmp_path):
    first = workbench.build(glyphs, "Noten", "MuseScore4", False, None)
    second = workbench.build(glyphs, "Noten", "MuseScore4", False, None)
    a = first.deck.write(tmp_path / "a.macroDeckFolder")
    b = second.deck.write(tmp_path / "b.macroDeckFolder")
    assert a.read_bytes() == b.read_bytes()


def test_boarddeck_is_what_build_returns(wb):
    assert isinstance(wb, BoardDeck)
    assert wb.deck.root.name == "Noten"
