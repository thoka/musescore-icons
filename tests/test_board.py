"""deckgen.board -- Boards, Regionen, Menüleiste (Plan 0003, Schritt 1)."""

from __future__ import annotations

import json

import pytest

from deckgen.board import BoardDeck, Cell
from deckgen.compose import Composition, Glyph


@pytest.fixture()
def workbench(glyphs):
    return BoardDeck(glyphs, name="Noten", accent="#3b82f6",
                     icon=Composition([Glyph("MUSIC_NOTES")]),
                     rows=4, columns=6)


def _second_board(workbench):
    return workbench.board("Rhythmen", accent="#10b981",
                           icon=Composition([Glyph("NOTE_8TH")]),
                           rows=4, columns=6)


def _button_at(board, x, y):
    for p in board.folder.placements:
        if (p.x, p.y) == (x, y):
            return p.button
    raise AssertionError(f"no button at {board.name} ({x}, {y})")


def _combos(button) -> list[dict]:
    flows = json.loads(json.loads(button.data("x"))["flows"])
    return [next(p["value"] for p in block["parameters"] if p["name"] == "combo")
            for block in flows[0]["children"]]


def _folder_id(button) -> str:
    flows = json.loads(json.loads(button.data("x"))["flows"])
    block = flows[0]["children"][0]
    return next(p["value"] for p in block["parameters"]
                if p["name"] == "folderId")


# -- line ---------------------------------------------------------------------


def test_line_along_x(workbench):
    cells = [Cell(name=f"c{i}", comp=Composition([Glyph("NOTE_QUARTER")]),
                  presses=[("5", ())])
             for i in range(3)]
    workbench.root.line((1, 1), cells, along="x")
    assert [(p.x, p.y) for p in workbench.root.folder.placements] == \
        [(1, 1), (2, 1), (3, 1)]
    assert _combos(_button_at(workbench.root, 2, 1)) == [{"modifiers": [],
                                                          "key": "5"}]


def test_line_along_y(workbench):
    cells = [Cell(name=f"c{i}", comp=Composition([Glyph("NOTE_QUARTER")]))
             for i in range(3)]
    workbench.root.line((1, 1), cells, along="y")
    assert [(p.x, p.y) for p in workbench.root.folder.placements] == \
        [(1, 1), (1, 2), (1, 3)]


def test_line_skips_none_without_moving_on(workbench):
    cells = [Cell(name="a", comp=Composition([Glyph("NOTE_QUARTER")])), None,
             Cell(name="c", comp=Composition([Glyph("NOTE_QUARTER")]))]
    workbench.root.line((0, 1), cells, along="x")
    assert [(p.x, p.y) for p in workbench.root.folder.placements] == \
        [(0, 1), (2, 1)]


# -- grid ---------------------------------------------------------------------


def _matrix_cells():
    """A 2x3 definition, each cell recognisable by its background."""
    def cell(i, j):
        return Cell(name=f"m{i}-{j}", background=f"#{i}{j}",
                    comp=Composition([Glyph("NOTE_QUARTER")]))
    return [[cell(i, j) for j in range(3)] for i in range(2)]


def test_grid_default_stacks_rows_downwards(workbench):
    rows = _matrix_cells()
    workbench.root.grid((0, 1), rows)
    assert _button_at(workbench.root, 0, 1).background == "#00"
    assert _button_at(workbench.root, 2, 1).background == "#02"
    assert _button_at(workbench.root, 0, 2).background == "#10"


def test_grid_along_x_is_the_transposed_presentation(workbench):
    rows = _matrix_cells()
    workbench.root.grid((0, 1), rows, along="x")
    assert _button_at(workbench.root, 0, 1).background == "#00"
    assert _button_at(workbench.root, 1, 1).background == "#10"
    assert _button_at(workbench.root, 0, 2).background == "#01"


# -- cells --------------------------------------------------------------------


def test_text_cell_without_composition(workbench):
    workbench.root.place(0, 1, Cell(label="Undo", presses=[("z", ("ctrl",))]))
    button = _button_at(workbench.root, 0, 1)
    data = json.loads(button.data("x"))
    assert data["label"] == "Undo"
    assert "icon" not in data
    assert _combos(button) == [{"modifiers": ["ctrl"], "key": "z"}]


def test_multi_press_cell_sends_keys_in_order(workbench):
    cell = Cell(name="dot", comp=Composition([Glyph("NOTE_QUARTER")]),
                presses=[("4", ()), (".", ()), (".", ())])
    workbench.root.place(0, 0, cell)
    assert _combos(_button_at(workbench.root, 0, 0)) == \
        [{"modifiers": [], "key": "4"},
         {"modifiers": [], "key": "."},
         {"modifiers": [], "key": "."}]


def test_icon_name_used_twice_is_an_error(workbench):
    workbench.root.place(0, 0, Cell(name="x", comp=Composition([Glyph("NOTE_8TH")])))
    with pytest.raises(ValueError):
        workbench.root.place(1, 0, Cell(name="x", comp=Composition([Glyph("NOTE_8TH")])))


def test_icon_name_falls_back_to_label_then_position(workbench):
    workbench.root.place(0, 0, Cell(label="Play",
                                    comp=Composition([Glyph("PLAY")])))
    workbench.root.place(1, 0, Cell(comp=Composition([Glyph("STOP")])))
    names = sorted(i.name for i in workbench.deck.icons.icons)
    assert names == ["noten-1-0", "play"]


# -- menu strip ---------------------------------------------------------------


def test_menu_strip_on_every_board(workbench):
    other = _second_board(workbench)
    workbench.menu_strip()
    for board in (workbench.root, other):
        assert [(p.x, p.y) for p in board.folder.placements] == \
            [(0, 0), (1, 0)]
    assert _folder_id(_button_at(other, 0, 0)) == workbench.deck.root.id
    assert _folder_id(_button_at(workbench.root, 1, 0)) == other.folder.id


def test_menu_strip_marks_the_active_board(workbench):
    other = _second_board(workbench)
    workbench.menu_strip(dim="#1f2937")
    assert _button_at(workbench.root, 0, 0).background == workbench.root.accent
    assert _button_at(workbench.root, 1, 0).background == "#1f2937"
    assert _button_at(other, 0, 0).background == "#1f2937"
    assert _button_at(other, 1, 0).background == other.accent


def test_menu_strip_needs_room(workbench):
    small = workbench.board("Eng", accent="#ef4444",
                            icon=Composition([Glyph("PLAY")]),
                            rows=4, columns=1)
    assert small.columns == 1
    with pytest.raises(ValueError, match="menu strip"):
        workbench.menu_strip()


def test_menu_icons_are_shared_not_duplicated(workbench):
    _second_board(workbench)
    workbench.menu_strip()
    menu_icons = [i for i in workbench.deck.icons.icons
                  if i.name.startswith("menu-")]
    assert sorted(i.name for i in menu_icons) == ["menu-noten", "menu-rhythmen"]
