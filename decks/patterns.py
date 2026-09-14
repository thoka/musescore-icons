#!/usr/bin/env python3
"""
decks/patterns.py -- a deck of typical rhythm figures (plan 0002, step 4).

One button per figure. The icon shows the figure's notes in flow mode, the
action types it into MuseScore note entry: per event the duration key, then
the note key; Ctrl+n starts an n-let, 0 is a rest. Ties parse but send no
key -- MuseScore has no default shortcut (see deckgen.notation).

    python decks/patterns.py                      # packs/figuren.macroDeckFolder
    python decks/patterns.py --labels --svg /tmp/vorschau

The display levers --zoom, --font-size and --label-position exist so a
device iteration can try values without a commit; the defaults are the
constants ZOOM, FONT_SIZE and LABEL_POSITION below.

Every figure types the letter "c" -- a rhythm pattern; the pitch is one
keystroke the player can move afterwards.

Since plan 0003 the same cells are a routine (`deckgen.routines.figures`)
that writes into any board; this script is the thin wrapper putting them on
a deck of their own.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from deckgen import Deck                                           # noqa: E402
from deckgen.board import BoardDeck                                # noqa: E402
from deckgen.compose import Composition, Glyph                     # noqa: E402
from deckgen.glyphs import Glyphs                                  # noqa: E402
from deckgen.routines import (Figure, figure_composition, figures,   # noqa: E402
                              figure_side)


# One row of the grid per four figures.
FIGURES = [
    Figure("Halbe",         "c2 c2",                                        "#6366f1"),
    Figure("Viertel",       "c4 c4 c4 c4",                                  "#3b82f6"),
    Figure("Achtel",        "c8 c8 c8 c8",                                  "#0ea5e9"),
    Figure("Sechzehntel",   "c16 c16 c16 c16 c16 c16 c16 c16",              "#10b981"),
    Figure("Achteltriole",  "(3 c8 c8 c8",                                  "#14b8a6"),
    Figure("Vierteltriole", "(3 c4 c4 c4",                                  "#f59e0b"),
    Figure("Sextole",       "(6 c32 c32 c32 c32 c32 c32",                   "#ef4444"),
    Figure("Punktiert",     "c4. c8 c4. c8",                                "#ec4899"),
    Figure("Umgekehrt",     "c8 c4. c8 c4.",                                "#a855f7"),
    Figure("Galopp",        "c16 c16 c8 c16 c16 c8",                        "#f97316"),
    Figure("Pausen",        "c8 z8 c8 z8 c8 z8 c8 z8",                      "#84cc16"),
    Figure("Taktende",      "c2. z4",                                       "#06b6d4"),
]

COLUMNS = 4

# Display findings from the first device import (plan 0002, step 4): the
# notes were too small on the button and the label sat on them too
# dominant. The notes fill the button (zoom 100 instead of the app default
# 70), the label only points to the definition -- size 8 at the bottom
# edge. Each lever is also an argparse flag so a device iteration needs no
# commit; the re-import decides the final values.
ZOOM = 100
FONT_SIZE = 8
LABEL_POSITION = "bottom"


def composition(glyphs: Glyphs, figure: Figure,
                side: float | None = None) -> Composition:
    """The icon of one figure -- a delegate of the routine."""
    return figure_composition(glyphs, figure, side)


def deck_side(glyphs: Glyphs) -> float:
    """Edge length of the shared frame -- the widest figure sets it."""
    return figure_side(glyphs, FIGURES)


def build(glyphs: Glyphs, name: str, target: str, labels: bool,
          svg_dir: Path | None, zoom: int = ZOOM, font_size: int = FONT_SIZE,
          label_position: str = LABEL_POSITION) -> Deck:
    workbench = BoardDeck(glyphs, name=name,
                          rows=-(-len(FIGURES) // COLUMNS), columns=COLUMNS,
                          accent=FIGURES[0].color,
                          icon=Composition([Glyph("MUSIC_NOTES")]),
                          target=target, svg_dir=svg_dir)
    figures(workbench.root, (0, 0), FIGURES, per_row=COLUMNS, labels=labels,
            zoom=zoom, font_size=font_size, label_position=label_position)
    return workbench.deck


def main() -> int:
    p = argparse.ArgumentParser(
        description="Deck of typical rhythm figures for MuseScore note entry.")
    p.add_argument("--out", default="packs/figuren.macroDeckFolder",
                   help="target file (default: packs/figuren.macroDeckFolder)")
    p.add_argument("--name", default="Figuren",
                   help="name of the folder in the deck (default: Figuren)")
    p.add_argument("--target", default="MuseScore4",
                   help="process that receives the keystrokes (default: MuseScore4)")
    p.add_argument("--labels", action="store_true",
                   help="write the figure name onto the button as well")
    p.add_argument("--zoom", type=int, default=ZOOM,
                   help=f"icon zoom on the button, percent (default: {ZOOM})")
    p.add_argument("--font-size", type=int, default=FONT_SIZE,
                   help=f"label font size (default: {FONT_SIZE})")
    p.add_argument("--label-position", default=LABEL_POSITION,
                   help=f"where the label sits (default: {LABEL_POSITION})")
    p.add_argument("--svg", metavar="DIR",
                   help="also write the same icons as SVG there (preview)")
    args = p.parse_args()

    svg_dir = None
    if args.svg:
        svg_dir = Path(args.svg)
        svg_dir.mkdir(parents=True, exist_ok=True)

    deck = build(Glyphs(), args.name, args.target, args.labels, svg_dir,
                 zoom=args.zoom, font_size=args.font_size,
                 label_position=args.label_position)
    path = deck.write(args.out)
    print(f"{path}  ({path.stat().st_size:,} Bytes)")
    print(f"  {len(deck.root.placements)} buttons, {len(deck.icons.icons)} icons, "
          f"grid {deck.root.columns}x{deck.root.rows}")
    for figure in FIGURES:
        print(f"  {figure.name:<14} {figure.abc}")
    if svg_dir:
        print(f"  SVG preview in {svg_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
