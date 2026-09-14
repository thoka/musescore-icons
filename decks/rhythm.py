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
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from deckgen import Button, Deck, press_key                      # noqa: E402
from deckgen.archive import MASTER_SIZE                          # noqa: E402
from deckgen.compose import Composition, Glyph, dot_dx, dots, ink_side  # noqa: E402
from deckgen.glyphs import Glyphs                                # noqa: E402


class Duration(NamedTuple):
    """Eine Spalte des Decks."""

    slug: str        # Teil des Icon-Namens
    label: str       # Aufschrift, falls --labels
    glyph: str       # Glyph der UI-Font
    key: str         # Kuerzel in MuseScore
    color: str       # Hintergrund der Taste


# Von lang nach kurz -- dieselbe Richtung wie die Werkzeugleiste in MuseScore.
DURATIONS = [
    Duration("whole",   "1/1",  "NOTE_WHOLE",   "7", "#6366f1"),
    Duration("half",    "1/2",  "NOTE_HALF",    "6", "#3b82f6"),
    Duration("quarter", "1/4",  "NOTE_QUARTER", "5", "#0ea5e9"),
    Duration("8th",     "1/8",  "NOTE_8TH",     "4", "#10b981"),
    Duration("16th",    "1/16", "NOTE_16TH",    "3", "#f59e0b"),
    Duration("32nd",    "1/32", "NOTE_32ND",    "2", "#ef4444"),
]

class Dotting(NamedTuple):
    """Eine Zeile des Decks. keys: Tasten, die nach der Dauer folgen."""

    suffix: str      # Teil des Icon-Namens
    label: str       # Anhang an die Aufschrift
    keys: list       # [(Taste, Modifikatoren), ...]


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

# The dot sits at head height (DOT_Y); how far right depends on the glyph:
# dot_dx() measures per note where its ink at dot height ends -- the head of
# a quarter reaches to 0.72 em, the head of an 8th only to 0.54, the flag of
# a 16th pushes the dot behind itself.
DOT_Y = 0.0


def cell(glyphs: Glyphs, duration: Duration, n_dots: int,
         side: float | None = None) -> Composition:
    """The icon of one cell: note plus dots, clear of the note's ink.

    `side` fixes one shared scale for all cells (value: the largest cell,
    see ink_side) and anchors the frame on the note -- the noteheads stay
    as large as the font draws them, the dots remain a right-hand appendage.
    """
    dx = dot_dx(glyphs, duration.glyph, dy=DOT_Y) if n_dots else 0.0
    return Composition([Glyph(duration.glyph), *dots(n_dots, dx=dx, dy=DOT_Y)],
                       side=side, anchor="note")


def deck_side(glyphs: Glyphs) -> float:
    """Edge length of the shared frame -- the largest cell sets it."""
    return max(ink_side(glyphs, cell(glyphs, d, n))
               for d in DURATIONS for n in range(len(DOTTINGS)))


def build(glyphs: Glyphs, name: str, target: str, labels: bool,
          svg_dir: Path | None) -> Deck:
    deck = Deck(name, rows=len(DOTTINGS), columns=len(DURATIONS))
    side = deck_side(glyphs)
    for x, duration in enumerate(DURATIONS):
        for n_dots, dotting in enumerate(DOTTINGS):
            comp = cell(glyphs, duration, n_dots, side=side)
            icon_name = f"note-{duration.slug}{dotting.suffix}"
            icon = deck.icons.add(icon_name, comp.to_image(glyphs, MASTER_SIZE),
                                  original_file_name=f"{icon_name}.png")
            if svg_dir is not None:
                (svg_dir / f"{icon_name}.svg").write_text(
                    comp.to_svg(glyphs, 256, title=icon_name), encoding="utf-8")

            # Erst die Dauer, dann die Punktierung -- in dieser Reihenfolge
            # laesst MuseScore den Punkt auf der neuen Dauer sitzen.
            actions = [press_key(duration.key, target_process=target)]
            actions += [press_key(key, modifiers=mods, target_process=target)
                        for key, mods in dotting.keys]

            deck.root.place(Button(
                label=f"{duration.label}{dotting.label}" if labels else "",
                icon=icon,
                background=duration.color,
                on_press=actions,
            ), x=x, y=n_dots)
    return deck


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
