#!/usr/bin/env python3
"""
decks/workbench.py -- the workbench deck: several boards under one roof
(plan 0003, step 3; layout per plan 0004, entry per plan 0006).

One Python script against the library: six boards on one uniform grid,
the vertical menu in column 0 of each (one button per board, the active
one in its accent colour; --menu horizontal gives the old strip on top
with the content in the row below), the content written by the routines
from `deckgen.routines`.

    python decks/workbench.py                     # packs/noten.macroDeckFolder
    python decks/workbench.py --labels --svg /tmp/vorschau

Boards:

* **Noten** (root) -- the duration x dotting matrix, the content of the
  accepted rhythm deck: it sets the note length.
* **Eingeben** -- the same matrix, but entering: middle C after duration
  and dots, below it the same values as rests ("0"). The rhythm goes in
  fast; the pitches are fixed later.
* **Ergaenzungen** -- one short note at the edge of a larger unit plus the
  complementary long note (a double-dotted quarter and a 16th are a half).
  Cells with no single dotted complement stay empty.
* **Rhythmen** -- the ABC figures of the patterns deck, room for more.
* **Transport**, **Bearbeiten** -- key rows. Their shortcuts are
  *unverified defaults*; the device decides, as with the duration codes in
  plan 0002, step 3: Play/Pause "space", rewind "ctrl+home", metronome
  "ctrl+shift+m", loop "ctrl+shift+l", and the edit keys are the standard
  ones (ctrl+z ...). Delete sends "delete" -- whether Macro Deck names
  non-printable keys this way is part of what the device answers.

The fixed bars (plan 0006): the piece's time signatures in the column
before the content of Noten and Eingeben (2/4, C, ¢, 6/8, 12/8 -- the
keys are the user's own assignment, docs/taktarten-kuerzel.md), and the
generic action bar along the bottom row of every board, the same cells
everywhere, the content growing step by step.

Display levers as flags, so a device iteration needs no commit; the
defaults are the values accepted with the figure deck (zoom 100, label
size 8 at the bottom).
"""

from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "decks"))            # the deck scripts live flat

from deckgen.board import BoardDeck                # noqa: E402
from deckgen.compose import Composition, Glyph     # noqa: E402
from deckgen.glyphs import Glyphs                  # noqa: E402
from deckgen.routines import (Length, completions, duration_matrix,
                              entry_matrix, figures, key_cell)
import patterns                                    # noqa: E402
import rhythm                                      # noqa: E402

# The boards: name, accent, menu icon. The root comes first -- the main
# board. Six boards, so the uniform grid is at least six rows tall.
ACCENTS = {
    "Noten":        "#3b82f6",
    "Eingeben":     "#14b8a6",
    "Ergänzungen":  "#f59e0b",
    "Rhythmen":     "#10b981",
    "Transport":    "#ef4444",
    "Bearbeiten":   "#a855f7",
}
MENU_ICONS = {
    "Noten":        "MUSIC_NOTES",
    "Eingeben":     "NOTE_QUARTER",
    "Ergänzungen":  "NOTE_DOTTED",
    "Rhythmen":     "NOTE_8TH",
    "Transport":    "PLAY",
    "Bearbeiten":   "EDIT",
}

# The fixed bars, one colour of their own -- distinct from every board
# accent, so the furniture reads as furniture. The time signatures sit in
# the column before the content (second column) of the Noten and Eingeben
# boards; the generic action bar runs along the bottom row of every board,
# the same cells everywhere, content decided step by step (plan 0006).
BAR_COLOR = "#475569"

# The piece's time signatures: label, shortcut. The keys are the user's
# own assignment -- proposed here, documented in docs/taktarten-kuerzel.md,
# and moved when the import file says otherwise. No Shift (the ":" lesson,
# decks/rhythm.py); the voices sit on Ctrl+Alt+0..4, so 5..9 is free.
TIME_SIGNATURES = [
    ("2/4",  "5", ("ctrl", "alt")),
    ("C",    "6", ("ctrl", "alt")),
    ("¢",    "7", ("ctrl", "alt")),
    ("6/8",  "8", ("ctrl", "alt")),
    ("12/8", "9", ("ctrl", "alt")),
]

# One grid for all boards -- the declared minimum everywhere; the uniform
# grid in menu_strip() settles on the maximum over them anyway. 11 x 7 is
# the trial size for the device (11 wide, 7 tall).
GRID_COLUMNS = 11
GRID_ROWS = 7

# Unverified defaults for the two key boards -- see the docstring.
TRANSPORT = [
    ("Play",     "PLAY",      [("space", ())]),
    ("Rewind",   "REWIND",    [("home", ("ctrl",))]),
    ("Metronom", "METRONOME", [("m", ("ctrl", "shift"))]),
    ("Loop",     "LOOP",      [("l", ("ctrl", "shift"))]),
]
EDIT = [
    ("Rückgängig", "UNDO",        [("z", ("ctrl",))]),
    ("Wiederholen", "REDO",       [("z", ("ctrl", "shift"))]),
    ("Ausschneiden", "CUT",       [("x", ("ctrl",))]),
    ("Kopieren",   "COPY",        [("c", ("ctrl",))]),
    ("Einfügen",   "PASTE",       [("v", ("ctrl",))]),
    ("Löschen",    "DELETE_TANK", [("delete", ())]),
]

# The completion grid: per short length a row, per target and order a
# column. Ganze - 16tel needs a triple dot -- no binding yet, that cell
# stays empty (plan 0003: leave the hard ones out).
SHORTS = [Length("16", Fraction(1, 16)), Length("8", Fraction(1, 8))]
TARGETS = [Length("Viertel", Fraction(1, 4)), Length("Halbe", Fraction(1, 2)),
           Length("Ganze", Fraction(1, 1))]


def build(glyphs: Glyphs, name: str, target: str, labels: bool,
          svg_dir: Path | None, zoom: int = 100, font_size: int = 8,
          label_position: str = "bottom", dim: str = "#1f2937",
          menu: str = "vertical") -> BoardDeck:
    root_name = "Noten"
    workbench = BoardDeck(glyphs, name=name, accent=ACCENTS[root_name],
                          icon=Composition([Glyph(MENU_ICONS[root_name])]),
                          rows=GRID_ROWS, columns=GRID_COLUMNS, target=target,
                          svg_dir=svg_dir)
    boards = {"Noten": workbench.root}
    for board_name in ("Eingeben", "Ergänzungen", "Rhythmen", "Transport",
                       "Bearbeiten"):
        boards[board_name] = workbench.board(
            board_name, accent=ACCENTS[board_name],
            icon=Composition([Glyph(MENU_ICONS[board_name])]),
            rows=GRID_ROWS, columns=GRID_COLUMNS)

    # The content origin: beside the vertical menu column it is (1, 0) --
    # full height to the right of it; under the horizontal strip it is
    # the row below, (0, 1). The time signatures sit in that column on
    # the Noten and Eingeben boards, so their content starts one
    # further right -- the signatures take the column before it.
    ox, oy = (0, 1) if menu == "horizontal" else (1, 0)
    sx, sy = ox + 1, oy
    durations = list(reversed(rhythm.DURATIONS))

    # The time-signature column: text buttons, one per signature, the
    # keys from TIME_SIGNATURES.
    signatures = [key_cell(label, "", BAR_COLOR, (key, mods))
                  for label, key, mods in TIME_SIGNATURES]
    for board_name in ("Noten", "Eingeben"):
        boards[board_name].line((ox, oy), signatures, along="y")

    # Noten: the duration x dotting matrix -- short durations first,
    # like the note input in MuseScore. rhythm.DURATIONS itself stays
    # long-to-short: the accepted rhythm deck keeps its layout.
    duration_matrix(boards["Noten"], (sx, sy), durations,
                    rhythm.DOTTINGS, labels=labels, zoom=zoom,
                    font_size=font_size, label_position=label_position)

    # Eingeben: the same matrix, entering -- middle C per cell, below it
    # the same values as rests.
    entry_matrix(boards["Eingeben"], (sx, sy), durations, rhythm.DOTTINGS,
                 rest=False, prefix="enter-note", labels=labels, zoom=zoom,
                 font_size=font_size, label_position=label_position)
    entry_matrix(boards["Eingeben"], (sx, sy + len(rhythm.DOTTINGS)),
                 durations, rhythm.DOTTINGS,
                 rest=True, prefix="enter-rest", labels=labels, zoom=zoom,
                 font_size=font_size, label_position=label_position)

    # Ergaenzungen: the completion grid.
    completions(boards["Ergänzungen"], (ox, oy), SHORTS, TARGETS,
                colors=[ACCENTS["Ergänzungen"]], labels=labels, axis="y",
                zoom=zoom, font_size=font_size,
                label_position=label_position)

    # Rhythmen: the accepted figures, two rows of six, room for more.
    figures(boards["Rhythmen"], (ox, oy), patterns.FIGURES, per_row=6,
            labels=labels, zoom=zoom, font_size=font_size,
            label_position=label_position)

    # Transport and Bearbeiten: key rows, always labelled.
    for board_name, keys in (("Transport", TRANSPORT), ("Bearbeiten", EDIT)):
        for i, (label, glyph, presses) in enumerate(keys):
            boards[board_name].place(
                ox + i, oy, key_cell(label, glyph, ACCENTS[board_name],
                                     *presses))

    workbench.menu_strip(dim=dim,
                         along="x" if menu == "horizontal" else "y")
    workbench.action_bar([])          # content comes step by step
    return workbench


def main() -> int:
    p = argparse.ArgumentParser(
        description="The workbench deck: note entry boards for MuseScore.")
    p.add_argument("--out", default="packs/noten.macroDeckFolder",
                   help="target file (default: packs/noten.macroDeckFolder)")
    p.add_argument("--name", default="Noten",
                   help="deck name in Macro Deck (default: Noten)")
    p.add_argument("--target", default="MuseScore4",
                   help="process that receives the keystrokes (default: MuseScore4)")
    p.add_argument("--labels", action="store_true",
                   help="write the definitions onto the buttons as well")
    p.add_argument("--zoom", type=int, default=100,
                   help="icon zoom on the buttons, percent (default: 100)")
    p.add_argument("--font-size", type=int, default=8,
                   help="label font size (default: 8)")
    p.add_argument("--label-position", default="bottom",
                   help="where the label sits (default: bottom)")
    p.add_argument("--dim", default="#1f2937",
                   help="menu colour of the inactive boards (default: #1f2937)")
    p.add_argument("--menu", choices=("vertical", "horizontal"),
                   default="vertical",
                   help="menu orientation (default: vertical, column 0)")
    p.add_argument("--svg", metavar="DIR",
                   help="also write every icon as SVG there (preview)")
    args = p.parse_args()

    svg_dir = None
    if args.svg:
        svg_dir = Path(args.svg)

    workbench = build(Glyphs(), args.name, args.target, args.labels, svg_dir,
                      zoom=args.zoom, font_size=args.font_size,
                      label_position=args.label_position, dim=args.dim,
                      menu=args.menu)
    path = workbench.deck.write(args.out)
    print(f"{path}  ({path.stat().st_size:,} Bytes)")
    for board in workbench.boards:
        folder = board.folder
        print(f"  {folder.name:<12} {folder.columns}x{folder.rows}  "
              f"{len(folder.placements)} Tasten  {board.accent}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
