"""Der Generator aus Schritt 3: Dauer x Punktierung.

Geprueft wird, was am Geraet sonst Taste fuer Taste nachgezaehlt werden muesste
-- Belegung des Rasters, Tastenfolge je Zelle, Icon je Zelle.
"""

from __future__ import annotations

import json

import pytest

import rhythm
from deckgen.compose import Dot
from test_compose import ink


@pytest.fixture(scope="module")
def deck(glyphs):
    return rhythm.build(glyphs, "Rhythmus", "MuseScore4", labels=False, svg_dir=None)


def combos(button) -> list[dict]:
    """Die Tastendruecke einer Taste, in der Reihenfolge des Flows."""
    flows = json.loads(json.loads(button.data("x"))["flows"])
    return [p["value"] for block in flows[0]["children"]
            for p in block["parameters"] if p["name"] == "combo"]


def button_at(deck, x: int, y: int):
    return next(p.button for p in deck.root.placements if (p.x, p.y) == (x, y))


def test_grid_is_completely_filled(deck):
    assert (deck.root.columns, deck.root.rows) == (len(rhythm.DURATIONS),
                                                   len(rhythm.DOTTINGS))
    positions = sorted((p.x, p.y) for p in deck.root.placements)
    assert positions == sorted((x, y) for x in range(deck.root.columns)
                               for y in range(deck.root.rows))


def test_every_cell_has_its_own_icon(deck):
    names = [i.name for i in deck.icons.icons]
    assert len(names) == len(set(names)) == len(deck.root.placements)
    assert all(p.button.icon is not None for p in deck.root.placements)


@pytest.mark.parametrize("x,duration", list(enumerate(rhythm.DURATIONS)))
def test_column_sends_its_duration_first(deck, x, duration):
    """Die Dauer kommt vor der Punktierung -- sonst faellt der Punkt weg."""
    for y in range(len(rhythm.DOTTINGS)):
        button = button_at(deck, x, y)
        assert combos(button)[0] == {"modifiers": [], "key": duration.key}
        assert button.background == duration.color


@pytest.mark.parametrize("y,dotting", list(enumerate(rhythm.DOTTINGS)))
def test_row_appends_its_dot_command(deck, y, dotting):
    for x in range(len(rhythm.DURATIONS)):
        assert combos(button_at(deck, x, y))[1:] == \
            [{"modifiers": list(mods), "key": key} for key, mods in dotting.keys]


def test_double_dot_is_one_command_not_two_dots(deck):
    """Zweimal "." wuerde die Punktierung wieder abschalten."""
    keys = [c["key"] for c in combos(button_at(deck, 0, 2))]
    assert keys.count(".") <= 1


def test_labels_are_off_by_default_and_readable_when_asked(glyphs):
    plain = rhythm.build(glyphs, "R", "MuseScore4", labels=False, svg_dir=None)
    assert {p.button.label for p in plain.root.placements} == {""}

    labelled = rhythm.build(glyphs, "R", "MuseScore4", labels=True, svg_dir=None)
    labels = {(p.x, p.y): p.button.label for p in labelled.root.placements}
    assert labels[(0, 0)] == "1/1"
    assert labels[(2, 1)] == "1/4."
    assert labels[(5, 2)] == "1/32.."


def test_target_process_reaches_every_key(glyphs):
    deck = rhythm.build(glyphs, "R", "Feuerwehr", labels=False, svg_dir=None)
    for placement in deck.root.placements:
        data = json.loads(json.loads(placement.button.data("x"))["flows"])
        for block in data[0]["children"]:
            target = next(p for p in block["parameters"]
                          if p["name"] == "targetProcess")
            assert target["value"] == "Feuerwehr"


def test_svg_preview_is_written(glyphs, tmp_path):
    rhythm.build(glyphs, "R", "MuseScore4", labels=False, svg_dir=tmp_path)
    files = sorted(p.name for p in tmp_path.glob("*.svg"))
    assert len(files) == len(rhythm.DURATIONS) * len(rhythm.DOTTINGS)
    assert "note-quarter-dotted.svg" in files


def test_archive_is_written_and_reproducible(glyphs, tmp_path):
    first = rhythm.build(glyphs, "Rhythmus", "MuseScore4", False, None) \
        .write(tmp_path / "a.macroDeckFolder")
    second = rhythm.build(glyphs, "Rhythmus", "MuseScore4", False, None) \
        .write(tmp_path / "b.macroDeckFolder")
    assert first.read_bytes() == second.read_bytes()


# -- Geometrie der Icons: Punktsitz und gemeinsame Skala ---------------------

def test_dot_seat_follows_the_note_ink(glyphs):
    """Measured per note: the 8th's head ends early, the 16th's flag pushes
    the dot behind itself, the quarter hugs its stem."""
    def seat(duration):
        comp = rhythm.cell(glyphs, duration, 1)
        return next(l.dx for l in comp.layers if isinstance(l, Dot))

    seats = {d.slug: seat(d) for d in rhythm.DURATIONS}
    assert seats["8th"] < 0.7
    assert seats["quarter"] < seats["16th"]
    assert seats["16th"] > 0.95
    assert seats["32nd"] > 0.9


def test_cells_share_one_scale(glyphs):
    """Every cell renders at the same scale: equal heads, and dots do not
    change the size of their note."""
    side = rhythm.deck_side(glyphs)

    def box(duration, n):
        comp = rhythm.cell(glyphs, duration, n, side=side)
        return ink(comp.to_image(glyphs, 256))

    whole0, whole2 = box(rhythm.DURATIONS[0], 0), box(rhythm.DURATIONS[0], 2)
    quarter0 = box(rhythm.DURATIONS[2], 0)
    assert whole0[2] - whole0[0] == quarter0[2] - quarter0[0]
    assert whole0[3] - whole0[1] == whole2[3] - whole2[1]
    assert quarter0[3] - quarter0[1] == box(rhythm.DURATIONS[2], 2)[3] \
        - box(rhythm.DURATIONS[2], 2)[1]
