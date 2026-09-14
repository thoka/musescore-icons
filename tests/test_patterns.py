"""The pattern generator: one button per figure.

Like test_rhythm.py, the deck is checked from the outside -- grid, keys,
icons, reproducibility -- so the next session runs one command instead of
re-deriving the wiring.
"""

from __future__ import annotations

import json

import pytest

import patterns
from deckgen.notation import DOT_KEYS, REST_KEY, Tuplet, VALUE_KEYS, parse
from test_rhythm import button_at, combos


def presses(button):
    """(modifiers, key) per keystroke of a button's flow."""
    return [(tuple(c["modifiers"]), c["key"]) for c in combos(button)]


@pytest.fixture(scope="module")
def deck(glyphs):
    return patterns.build(glyphs, "Figuren", "MuseScore4", labels=False,
                          svg_dir=None)


def test_grid_is_completely_filled(deck):
    assert (deck.root.columns, deck.root.rows) == \
        (patterns.COLUMNS, -(-len(patterns.FIGURES) // patterns.COLUMNS))
    positions = sorted((p.x, p.y) for p in deck.root.placements)
    assert positions == sorted((x, y) for x in range(deck.root.columns)
                               for y in range(deck.root.rows))


def test_every_cell_has_its_own_icon(deck):
    names = [i.name for i in deck.icons.icons]
    assert len(names) == len(set(names)) == len(deck.root.placements)


@pytest.mark.parametrize("i,figure", list(enumerate(patterns.FIGURES)))
def test_button_types_its_figure(deck, i, figure):
    """The keys read like the figure -- duration, dot, letter per event,
    the n-let command in front, 0 for a rest. Rebuilt here by hand so the
    test does not call the same code the button came from."""
    expected = []
    for item in parse(figure.abc):
        if isinstance(item, Tuplet):
            expected += [(("ctrl",), str(item.n))]
            continue
        expected += [((), VALUE_KEYS[item.value])]
        if item.dots:
            expected += [((), DOT_KEYS[item.dots])]
        expected += [((), item.pitch if item.kind == "note" else REST_KEY)]
    assert presses(button_at(deck, i % patterns.COLUMNS, i // patterns.COLUMNS)) \
        == expected
    assert button_at(deck, i % patterns.COLUMNS, i // patterns.COLUMNS) \
        .background == figure.color


def test_no_button_sends_a_tie(deck):
    """MuseScore has no default shortcut -- the notation layer documents it,
    the deck must not smuggle one in."""
    for placement in deck.root.placements:
        assert all(key != "-" for _mods, key in presses(placement.button))


def test_labels_name_the_figure(glyphs):
    plain = patterns.build(glyphs, "F", "MuseScore4", labels=False, svg_dir=None)
    assert {p.button.label for p in plain.root.placements} == {""}

    labelled = patterns.build(glyphs, "F", "MuseScore4", labels=True, svg_dir=None)
    labels = {(p.x, p.y): p.button.label for p in labelled.root.placements}
    assert labels[(0, 0)] == "Halbe"
    assert labels[(1, 1)] == "Vierteltriole"


def test_target_process_reaches_every_key(glyphs):
    deck = patterns.build(glyphs, "F", "Feuerwehr", labels=False, svg_dir=None)
    for placement in deck.root.placements:
        data = json.loads(json.loads(placement.button.data("x"))["flows"])
        for block in data[0]["children"]:
            target = next(p for p in block["parameters"]
                          if p["name"] == "targetProcess")
            assert target["value"] == "Feuerwehr"


def test_display_values_reach_the_button_data(deck):
    """The device findings as constants (plan 0002, step 4): the notes fill
    the button, the label shrinks and sits at the bottom edge."""
    assert (patterns.ZOOM, patterns.FONT_SIZE,
            patterns.LABEL_POSITION) == (100, 8, "bottom")
    for placement in deck.root.placements:
        data = json.loads(placement.button.data("x"))
        assert data["iconDisplay"]["zoom"] == patterns.ZOOM
        assert data["fontSize"] == patterns.FONT_SIZE
        assert data["labelPosition"] == patterns.LABEL_POSITION


def test_display_levers_are_build_parameters(glyphs):
    """The argparse flags route into the same fields, so a device iteration
    tries values without a commit."""
    deck = patterns.build(glyphs, "F", "MuseScore4", labels=False, svg_dir=None,
                          zoom=55, font_size=11, label_position="top")
    data = json.loads(deck.root.placements[0].button.data("x"))
    assert data["iconDisplay"]["zoom"] == 55
    assert data["fontSize"] == 11
    assert data["labelPosition"] == "top"


def test_svg_preview_is_written(glyphs, tmp_path):
    patterns.build(glyphs, "F", "MuseScore4", labels=False, svg_dir=tmp_path)
    files = sorted(p.name for p in tmp_path.glob("*.svg"))
    assert len(files) == len(patterns.FIGURES)
    assert "figure-achteltriole.svg" in files


def test_archive_is_written_and_reproducible(glyphs, tmp_path):
    first = patterns.build(glyphs, "Figuren", "MuseScore4", False, None) \
        .write(tmp_path / "a.macroDeckFolder")
    second = patterns.build(glyphs, "Figuren", "MuseScore4", False, None) \
        .write(tmp_path / "b.macroDeckFolder")
    assert first.read_bytes() == second.read_bytes()


# -- Geometrie der Icons: gemeinsame Skala ------------------------------------

def test_all_figures_share_the_frame(glyphs):
    """One scale for the whole deck -- same heads on every button (the
    lesson from step 3); the side mechanism itself is tested in
    test_compose.py."""
    side = patterns.deck_side(glyphs)
    for figure in patterns.FIGURES:
        assert patterns.composition(glyphs, figure, side=side).side == side


@pytest.mark.parametrize("figure", patterns.FIGURES)
def test_icon_has_ink(glyphs, figure):
    side = patterns.deck_side(glyphs)
    image = patterns.composition(glyphs, figure, side=side).to_image(glyphs, 256)
    assert image.getchannel("A").getbbox() is not None
