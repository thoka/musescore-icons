#!/usr/bin/env python3
"""
decks/rhythm.py -- Deck aus Dauer x Punktierung (Plan 0002, Schritt 3).

Ein gewoehnliches Skript gegen die Bibliothek: `deckgen.compose` setzt die
Icons, `deckgen.archive` schreibt den Ordner. Herausgekommen ist ein
importierbares `.macroDeckFolder` mit einer Reihe je Punktierung und einer
Spalte je Notendauer -- also genau die Zuordnung, die man sonst Taste fuer
Taste von Hand klickt.

    python decks/rhythm.py                      # packs/rhythmus.macroDeckFolder
    python decks/rhythm.py --labels --svg /tmp/vorschau

Tastenkuerzel: MuseScore legt die Dauern auf 1..7 (1 = 1/64 ... 7 = ganze
Note), die einfache Punktierung auf ".". For the **double** dotting
MuseScore ships no shortcut; the "Double-dotted note" command sits on ","
here. Acceptance on the device showed ":" (Shift+"." on a German keyboard)
never reaches MuseScore. Whoever has it elsewhere changes the line.

Seit Plan 0003 lebt dieselbe Zelle als Routine (`deckgen.routines`), die in
ein beliebiges Board schreibt -- dieses Skript ist der duenne Wrapper, der
sie auf ein eigenes Deck legt. Sein Archiv aendert sich nicht.
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
from deckgen.routines import (Duration, Dotting, duration_matrix,  # noqa: E402
                              matrix_cell, matrix_side)


# Von lang nach kurz -- dieselbe Richtung wie die Werkzeugleiste in MuseScore.
DURATIONS = [
    Duration("whole",   "1/1",  "NOTE_WHOLE",   "7", "#6366f1"),
    Duration("half",    "1/2",  "NOTE_HALF",    "6", "#3b82f6"),
    Duration("quarter", "1/4",  "NOTE_QUARTER", "5", "#0ea5e9"),
    Duration("8th",     "1/8",  "NOTE_8TH",     "4", "#10b981"),
    Duration("16th",    "1/16", "NOTE_16TH",    "3", "#f59e0b"),
    Duration("32nd",    "1/32", "NOTE_32ND",    "2", "#ef4444"),
]

# Die Zeilennummer ist zugleich die Zahl der Punkte.
DOTTINGS = [
    Dotting("", "", []),
    Dotting("-dotted", ".", [(".", ())]),
    # MuseScore sets both dots with one command -- hence *no* second ".",
    # which would switch the dotting off again. Acceptance on the device
    # showed ":" (Shift+"." on a German keyboard) does not reach MuseScore;
    # "," -- a plain key, no shift -- does, so the shortcut sits there.
    Dotting("-double-dotted", "..", [(",", ())]),
]


def cell(glyphs: Glyphs, duration: Duration, n_dots: int,
         side: float | None = None) -> Composition:
    """The icon of one cell -- a delegate of the routine."""
    return matrix_cell(glyphs, duration, n_dots, side=side)


def deck_side(glyphs: Glyphs) -> float:
    """Edge length of the shared frame -- the largest cell sets it."""
    return matrix_side(glyphs, DURATIONS, DOTTINGS)


def build(glyphs: Glyphs, name: str, target: str, labels: bool,
          svg_dir: Path | None) -> Deck:
    workbench = BoardDeck(glyphs, name=name, rows=len(DOTTINGS),
                          columns=len(DURATIONS), accent=DURATIONS[0].color,
                          icon=Composition([Glyph(DURATIONS[0].glyph)]),
                          target=target, svg_dir=svg_dir)
    duration_matrix(workbench.root, (0, 0), DURATIONS, DOTTINGS, labels=labels)
    return workbench.deck


def main() -> int:
    p = argparse.ArgumentParser(
        description="Deck aus Notendauern und Punktierungen erzeugen.")
    p.add_argument("--out", default="packs/rhythmus.macroDeckFolder",
                   help="Zieldatei (Vorgabe: packs/rhythmus.macroDeckFolder)")
    p.add_argument("--name", default="Rhythmus",
                   help="Name des Ordners im Deck (Vorgabe: Rhythmus)")
    p.add_argument("--target", default="MuseScore4",
                   help="Prozess, der die Tastendruecke bekommt (Vorgabe: MuseScore4)")
    p.add_argument("--labels", action="store_true",
                   help="Dauer zusaetzlich als Text auf die Taste schreiben")
    p.add_argument("--svg", metavar="ORDNER",
                   help="dieselben Icons als SVG dorthin schreiben (Vorschau)")
    args = p.parse_args()

    svg_dir = None
    if args.svg:
        svg_dir = Path(args.svg)
        svg_dir.mkdir(parents=True, exist_ok=True)

    deck = build(Glyphs(), args.name, args.target, args.labels, svg_dir)
    path = deck.write(args.out)
    print(f"{path}  ({path.stat().st_size:,} Bytes)")
    print(f"  {len(deck.root.placements)} Tasten, {len(deck.icons.icons)} Icons, "
          f"Raster {deck.root.columns}x{deck.root.rows}")
    for duration in DURATIONS:
        print(f"  {duration.label:>4}  Taste {duration.key}  {duration.color}")
    if svg_dir:
        print(f"  SVG-Vorschau in {svg_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
