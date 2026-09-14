"""
deckgen.notation -- the rhythm subset of ABC as the intermediate representation.

One analysis feeds both outputs of a pattern button: the icon (note glyphs
laid out in flow mode) and the key sequence for MuseScore note entry
(duration key, then note key, per event):

    "c8 c8 c4"  ->  [Event(c, 8), Event(c, 8), Event(c, 4)]
                    icon:  three glyphs in flow
                    keys:  4 c  4 c  5 c

The subset, deliberately small (plan 0002, Risks):

    a b c d e f g   notes -- the letter is the note key MuseScore gets;
                    no octaves, no accidentals, rhythm is the point
    1 2 4 8 16 32 64   note value, written as the denominator (c8 = eighth);
                    a bare letter defaults to a quarter
    .  ..           dotting -- MuseScore's "." sets one dot, the one-shot
                    "Double-dotted note" command sits on "," (the binding
                    proven on the device, see decks/rhythm.py)
    z               rest, same value and dot syntax as notes
    -               tie to the next event -- validated (same letter, next
                    event a note) but never sent: MuseScore ships no
                    default shortcut for a tie and none is proven yet
    (3 (4 ... (9    n-let over the next n events
    |               barline -- structure only, no layer and no key

Anything else is a ParseError that names the spot: uppercase letters,
octave marks, "/" lengths, slurs, chords -- the subset stays a rhythm.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .actions import Action, press_key
from .compose import Composition, Dot, Glyph, dots

# -- The intermediate representation ------------------------------------------

VALUES = (1, 2, 4, 8, 16, 32, 64)


@dataclass(frozen=True)
class Event:
    """One sounding or silent unit of the rhythm."""

    kind: str              # "note" or "rest"
    pitch: str | None      # "a".."g" for notes, None for rests
    value: int = 4         # note value as denominator: 8 is an eighth
    dots: int = 0
    tie: bool = False      # tied to the next event


@dataclass(frozen=True)
class Tuplet:
    """Start of an n-let -- the next n events form the group."""

    n: int


@dataclass(frozen=True)
class Bar:
    """A barline -- structure only, skipped by icon and keys alike."""


class ParseError(ValueError):
    """The text is outside the subset; the message names the spot."""


def _spot(text: str, i: int, why: str) -> str:
    return f"{text!r} at character {i}: {why}"


# -- MuseScore note entry ------------------------------------------------------

# 1 = 1/64 ... 7 = whole note; "3" = 1/16 is measured (plan 0002, appendix A),
# the rest follows the MuseScore documentation.
VALUE_KEYS = {64: "1", 32: "2", 16: "3", 8: "4", 4: "5", 2: "6", 1: "7"}

# "." sets one dot; pressing it twice would switch the dotting off again.
# MuseScore ships no default for the double dot -- the one-shot
# "Double-dotted note" command sits on "," (decks/rhythm.py, accepted).
DOT_KEYS = {1: ".", 2: ","}

# Note entry: 0 inserts a rest of the selected duration.
REST_KEY = "0"

# Ctrl+n starts an n-let of the selected duration (MuseScore default for
# n in 3..9). Not yet checked on the device -- acceptance will tell.
TUPLET_KEYS = {n: ("ctrl", str(n)) for n in range(3, 10)}

# Ties are parsed and drawn but never sent: no default shortcut, none proven
# on the device. The tied-to note still gets its duration and letter.


# -- Parser ---------------------------------------------------------------------

_NOTE = re.compile(r"([a-gz])(\d*)(\.*)(-?)")
_TUPLET = re.compile(r"\((\d+)")


def parse(text: str) -> list[Event | Tuplet | Bar]:
    """Read the rhythm subset into the event list."""
    out: list[Event | Tuplet | Bar] = []
    owed = 0                # events still expected by the open n-let
    pending_tie: Event | None = None
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch == "|":
            if owed:
                raise ParseError(_spot(text, i, "a barline inside an n-let"))
            out.append(Bar())
            i += 1
            continue
        if ch == "(":
            m = _TUPLET.match(text, i)
            if m is None:
                raise ParseError(_spot(text, i, "an n-let needs its count, as in (3"))
            n = int(m.group(1))
            if n not in TUPLET_KEYS:
                raise ParseError(_spot(text, i, "n-lets run from 3 to 9 -- "
                                               "MuseScore has no shortcut beyond"))
            if owed:
                raise ParseError(_spot(text, i, "nested n-lets"))
            out.append(Tuplet(n))
            owed = n
            i = m.end()
            continue
        m = _NOTE.match(text, i)
        if m is None:
            raise ParseError(_spot(text, i, f"unexpected {ch!r} -- the subset "
                                           "knows notes a-g, rests z, n-lets (n "
                                           "and barlines |"))
        letter, digits, dots_, tie = m.groups()
        if dots_:
            if len(dots_) > 2:
                raise ParseError(_spot(text, i, "at most two dots -- MuseScore "
                                               "has no command beyond the double"))
            n_dots = len(dots_)
        else:
            n_dots = 0
        value = int(digits) if digits else 4
        if value not in VALUES:
            raise ParseError(_spot(text, i, f"{digits} -- note values are "
                                            "1 2 4 8 16 32 64"))
        kind = "rest" if letter == "z" else "note"
        event = Event(kind, None if kind == "rest" else letter,
                      value, dots=n_dots, tie=bool(tie))
        if pending_tie is not None:
            if kind != "note":
                raise ParseError(_spot(text, i, "a tie runs into a rest"))
            if event.pitch != pending_tie.pitch:
                raise ParseError(_spot(text, i, "a tie joins two of the same letter"))
            pending_tie = None
        if tie:
            pending_tie = event
        out.append(event)
        if owed:
            owed -= 1
        i = m.end()
    if owed:
        raise ParseError(_spot(text, len(text), f"the n-let is short -- {owed} event(s) missing"))
    if pending_tie is not None:
        raise ParseError(_spot(text, len(text), "a tie without a following note"))
    return out


# -- Icon and keys out of the same list -----------------------------------------

NOTE_GLYPHS = {1: "NOTE_WHOLE", 2: "NOTE_HALF", 4: "NOTE_QUARTER",
               8: "NOTE_8TH", 16: "NOTE_16TH", 32: "NOTE_32ND", 64: "NOTE_64TH"}

# The UI font draws a quarter and an eighth rest and nothing finer (plan 0001);
# shorter rests borrow the eighth's shape until Leland supplies the real ones.
REST_GLYPHS = {1: "REST", 2: "REST", 4: "REST", 8: "REST_8TH",
               16: "REST_8TH", 32: "REST_8TH", 64: "REST_8TH"}

# The dots sit at head height; the font's dotted glyphs put them there.
DOT_Y = 0.0

# The n-let's notes read as one figure and render at full size like every
# other note (device finding: scaled-down tuplets were too small); the font
# has the digit 3 and nothing else, so only triplets carry their number --
# floating above the stems.
TUPLET_MARK = "TUPLET_NUMBER_ONLY"
TUPLET_MARK_SCALE = 0.6
TUPLET_MARK_DY = 0.8

# The tie arc hangs at head height: NOTE_TIE centres 0.47 em above the
# baseline (measured), so it takes that much dy to come down.
TIE_GLYPH = "NOTE_TIE"
TIE_DY = -0.47


def composition(events: list[Event | Tuplet | Bar],
                side: float | None = None) -> Composition:
    """The icon: one glyph per event, laid out in flow mode.

    `side` fixes a shared scale across several figures -- the largest sets
    it, every notehead keeps the size the font gives it (the lesson from
    decks/rhythm.py).
    """
    layers: list[Glyph | Dot] = []
    for item in events:
        if isinstance(item, Bar):
            continue
        if isinstance(item, Tuplet):
            if item.n == 3:
                layers.append(Glyph(TUPLET_MARK, scale=TUPLET_MARK_SCALE,
                                    dy=TUPLET_MARK_DY))
            continue
        if item.kind == "note":
            layers.append(Glyph(NOTE_GLYPHS[item.value]))
        else:
            layers.append(Glyph(REST_GLYPHS[item.value]))
        layers += dots(item.dots, dy=DOT_Y)
        if item.tie:
            layers.append(Glyph(TIE_GLYPH, dy=TIE_DY))
    return Composition(layers, flow=True, side=side)


def actions(events: list[Event | Tuplet | Bar],
            target_process: str = "MuseScore4") -> list[Action]:
    """The keys: Ctrl+n before an n-let, then duration, dots, letter per event."""
    out: list[Action] = []
    for item in events:
        if isinstance(item, Bar):
            continue
        if isinstance(item, Tuplet):
            modifier, key = TUPLET_KEYS[item.n]
            out.append(press_key(key, modifiers=(modifier,),
                                 target_process=target_process))
            continue
        out.append(press_key(VALUE_KEYS[item.value], target_process=target_process))
        if item.dots:
            out.append(press_key(DOT_KEYS[item.dots], target_process=target_process))
        # item.tie sends nothing -- see the note at TUPLET_KEYS.
        out.append(press_key(item.pitch if item.kind == "note" else REST_KEY,
                             target_process=target_process))
    return out
