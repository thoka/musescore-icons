#!/usr/bin/env python3
"""
decks/workbench.py -- the workbench deck: several boards under one roof
(plan 0003, step 3).

One Python script against the library: five boards on one uniform grid,
the vertical menu in column 0 of each (one button per board, the active
one in its accent colour; --menu horizontal gives the old strip on top
with the content in the row below), the content written by the routines
from `deckgen.routines`.

    python decks/workbench.py                     # packs/noten.macroDeckFolder
    python decks/workbench.py --labels --svg /tmp/vorschau

Boards:

* **Noten** (root) -- the duration x dotting matrix, the content of the
  accepted rhythm deck.
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
from deckgen.routines import (Length, completions, duration_matrix,  # noqa: E402
                              figures, key_cell)
import patterns                                    # noqa: E402
import rhythm                                      # noqa: E402

# The boards: name, accent, menu icon. The root comes first -- the main
# board. Five boards, so the uniform grid is at least five rows tall.
ACCENTS = {
    "Noten":        "#3b82f6",
    "Ergänzungen":  "#f59e0b",
    "Rhythmen":     "#10b981",
    "Transport":    "#ef4444",
    "Bearbeiten":   "#a855f7",
}
MENU_ICONS = {
    "Noten":        "MUSIC_NOTES",
    "Ergänzungen":  "NOTE_DOTTED",
    "Rhythmen":     "NOTE_8TH",
    "Transport":    "PLAY",
    "Bearbeiten":   "EDIT",
}

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
                          rows=4, columns=7, target=target, svg_dir=svg_dir)
    boards = {"Noten": workbench.root}
    for board_name in ("Ergänzungen", "Rhythmen", "Transport", "Bearbeiten"):
        rows = {"Ergänzungen": 3, "Rhythmen": 3, "Transport": 2,
                "Bearbeiten": 2}[board_name]
        boards[board_name] = workbench.board(
            board_name, accent=ACCENTS[board_name],
            icon=Composition([Glyph(MENU_ICONS[board_name])]),
            rows=rows, columns=7)

    # The content origin: beside the vertical menu column it is (1, 0) --
    # full height to the right of it; under the horizontal strip it is
    # the row below, (0, 1).
    ox, oy = (0, 1) if menu == "horizontal" else (1, 0)

    # Noten: the duration x dotting matrix -- short durations first,
    # like the note input in MuseScore. rhythm.DURATIONS itself stays
    # long-to-short: the accepted rhythm deck keeps its layout.
    duration_matrix(boards["Noten"], (ox, oy),
                    list(reversed(rhythm.DURATIONS)),
                    rhythm.DOTTINGS, labels=labels, zoom=zoom,
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
