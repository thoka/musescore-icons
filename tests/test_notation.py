"""The notation layer: the ABC rhythm subset in, icon and keys out.

The plan's example is the normative case: "c8 c8 c4" becomes three events
with the note value as denominator. Everything else checks the mapping
tables, the subset's rejections, and that the key sequence reads like
MuseScore note entry.
"""

from __future__ import annotations

import pytest

from deckgen.compose import Dot, Glyph
from deckgen.notation import (Bar, DOT_KEYS, Event, ParseError, REST_KEY,
                              Tuplet, VALUE_KEYS, actions, composition, parse)


def combos(keys):
    """(modifiers, key) per press, read straight off the action blocks."""
    out = []
    for action in keys:
        combo = next(v for name, _t, v in action.parameters if name == "combo")
        out.append((tuple(combo["modifiers"]), combo["key"]))
    return out


# -- Parsing: the intermediate representation ---------------------------------

def test_the_plan_example():
    assert parse("c8 c8 c4") == [Event("note", "c", 8),
                                 Event("note", "c", 8),
                                 Event("note", "c", 4)]


def test_a_bare_note_is_a_quarter():
    assert parse("c") == [Event("note", "c", 4)]


def test_dots_belong_to_their_event():
    assert parse("c4. c8..") == [Event("note", "c", 4, dots=1),
                                 Event("note", "c", 8, dots=2)]


def test_rests_take_the_same_value_syntax():
    assert parse("z4 z8.") == [Event("rest", None, 4),
                               Event("rest", None, 8, dots=1)]


def test_a_tie_marks_its_event_and_jumps_a_barline():
    tied = parse("c8- | c8")
    assert tied[0].tie and not tied[-1].tie


def test_a_tuplet_marks_the_group_start():
    assert parse("(3 c8 c8 c8") == [Tuplet(3)] + [Event("note", "c", 8)] * 3


def test_a_barline_is_a_marker():
    assert parse("c8 | c8") == [Event("note", "c", 8), Bar(),
                                Event("note", "c", 8)]


def test_empty_input_is_an_empty_list():
    assert parse("") == []


@pytest.mark.parametrize("text,why", [
    ("C4", "unexpected"),                 # no uppercase
    ("c'h", "unexpected"),                # no octave marks, no letter h
    ("c3", "note values"),                # 3 is not a note value here
    ("c12", "note values"),
    ("c/2", "unexpected"),                # no / lengths -- write c16
    ("c4...", "at most two dots"),
    ("c8-", "tie without"),               # trailing tie
    ("c8- z8", "into a rest"),
    ("c8- d8", "same letter"),
    ("(x", "needs its count"),
    ("(2 c8 c8", "3 to 9"),
    ("(3 c8 c8", "short"),                # group never fills
    ("(3 c8 | c8 c8", "barline inside"),
    ("(3 c8 (3 c8 c8", "nested"),
])
def test_outside_the_subset_is_named(text, why):
    with pytest.raises(ParseError, match=why):
        parse(text)


# -- The icon out of the same list ---------------------------------------------

def glyph_names(events):
    return [l.name for l in composition(events).layers if isinstance(l, Glyph)]


def test_one_glyph_per_event():
    assert glyph_names(parse("c8 z4 c16")) == ["NOTE_8TH", "REST", "NOTE_16TH"]


def test_dots_follow_their_note_at_head_height():
    layers = composition(parse("c4.")).layers
    assert len(layers) == 2
    dot = layers[1]
    assert isinstance(dot, Dot) and dot.dy == 0.0


def test_rests_borrow_the_eighths_shape_when_the_font_has_no_fin():
    assert glyph_names(parse("z4 z8 z16")) == ["REST", "REST_8TH", "REST_8TH"]


def test_a_triplet_shows_its_number_over_full_size_notes():
    """The digit marks the group; the notes render like every other note
    (device finding: scaled-down tuplets were too small)."""
    layers = composition(parse("(3 c8 c8 c8")).layers
    mark, *notes = layers
    assert isinstance(mark, Glyph) and mark.name == "TUPLET_NUMBER_ONLY"
    assert mark.scale < 1.0 and mark.dy > 0.5
    assert [n.scale for n in notes] == [1.0, 1.0, 1.0]


def test_other_nlets_go_without_a_number():
    layers = composition(parse("(6 c32 c32 c32 c32 c32 c32")).layers
    assert len(layers) == 6 and all(l.scale == 1.0 for l in layers)


def test_a_tie_draws_the_arc_between_the_notes():
    layers = composition(parse("c8- c8")).layers
    assert [l.name for l in layers] == ["NOTE_8TH", "NOTE_TIE", "NOTE_8TH"]


def test_a_barline_adds_no_layer():
    assert len(composition(parse("c8 | c8")).layers) == 2


def test_a_fixed_side_shares_one_scale(glyphs):
    events = parse("c4 c8")
    assert composition(events, side=1234.0).side == 1234.0
    box = composition(events, side=1234.0).to_image(glyphs, 256)
    assert box.getchannel("A").getbbox() is not None


# -- The keys out of the same list ----------------------------------------------

def test_a_note_types_duration_then_letter():
    assert combos(actions(parse("c8"))) == [((), "4"), ((), "c")]


def test_a_dotted_note_sets_the_dot_before_the_letter():
    assert combos(actions(parse("c4."))) == [((), "5"), ((), "."), ((), "c")]


def test_the_double_dot_is_one_command_not_two():
    assert combos(actions(parse("c4.."))) == [((), "5"), ((), ","), ((), "c")]


def test_a_rest_is_zero():
    assert combos(actions(parse("z4"))) == [((), "5"), ((), REST_KEY)]


def test_an_nlet_starts_with_its_command():
    assert combos(actions(parse("(3 c8 c8 c8"))) == [
        (("ctrl",), "3"),
        ((), "4"), ((), "c"),
        ((), "4"), ((), "c"),
        ((), "4"), ((), "c"),
    ]


def test_two_consecutive_triplets_get_two_commands():
    keys = combos(actions(parse("(3 c8 c8 c8 (3 c8 c8 c8")))
    assert keys.count((("ctrl",), "3")) == 2


def test_ties_and_barlines_send_nothing():
    assert combos(actions(parse("c8- | c8"))) == \
        [((), "4"), ((), "c"), ((), "4"), ((), "c")]


def test_every_keystroke_reaches_its_target():
    for action in actions(parse("c4 z4"), target_process="Feuerwehr"):
        target = next(v for name, _t, v in action.parameters
                      if name == "targetProcess")
        assert target == "Feuerwehr"


def test_the_mapping_tables_agree_with_the_parser():
    for event in parse("c1 c2 c4 c8 c16 c32 c64"):
        assert event.value in VALUE_KEYS
    assert set(DOT_KEYS) == {1, 2}
