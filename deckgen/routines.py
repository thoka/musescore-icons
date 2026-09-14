"""
deckgen.routines -- cell routines that write definitions into board regions.

Each routine knows one definition family and writes it through the Board
API; the data (which durations, which figures, which colours) lives with
the caller, the mechanics -- shared scale, icon names, key order -- live
here. A definition is written at one spot, along either axis, so the same
content can be presented horizontally or vertically (plan 0003).

The routines carry the display values their deck was accepted with: the
rhythm matrix at zoom 70 / font 14 / label centred (plan 0002, step 3),
figures and completions at zoom 100 / font 8 / label at the bottom
(plan 0002, step 4).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from . import notation
from .board import Board, Cell, _slug
from .compose import Composition, Glyph, dot_dx, dots, ink_side


# -- duration x dotting (the rhythm matrix) ------------------------------------

DOT_Y = 0.0


@dataclass(frozen=True)
class Duration:
    """One duration of the matrix: glyph, MuseScore key, colour."""

    slug: str        # part of the icon name
    label: str       # on the button, with --labels
    glyph: str       # glyph of the UI font
    key: str         # shortcut in MuseScore
    color: str       # button background


@dataclass(frozen=True)
class Dotting:
    """One dotting of the matrix; keys follow the duration key."""

    suffix: str      # part of the icon name
    label: str       # appended to the label
    keys: tuple[tuple[str, tuple[str, ...]], ...] = ()


def matrix_cell(glyphs, duration: Duration, n_dots: int,
                side: float | None = None) -> Composition:
    """The icon of one matrix cell: note plus dots, clear of the note's
    ink. With `side` one shared scale across all cells, anchored on the
    note -- the noteheads stay as large as the font draws them, the dots
    remain a right-hand appendage (plan 0002, step 3)."""
    dx = dot_dx(glyphs, duration.glyph, dy=DOT_Y) if n_dots else 0.0
    return Composition([Glyph(duration.glyph),
                        *dots(n_dots, dx=dx, dy=DOT_Y)],
                       side=side, anchor="note")


def matrix_side(glyphs, durations: list[Duration],
                dottings: list[Dotting]) -> float:
    """Edge length of the shared frame -- the largest cell sets it."""
    return max(ink_side(glyphs, matrix_cell(glyphs, d, n))
               for d in durations for n in range(len(dottings)))


def duration_matrix(board: Board, origin: tuple[int, int],
                    durations: list[Duration], dottings: list[Dotting], *,
                    axis: str = "x", labels: bool = False, prefix: str = "note",
                    zoom: int = 70, font_size: int = 14,
                    label_position: str = "center") -> None:
    """The duration x dotting matrix at one spot, one shared scale over all
    cells. axis="x" runs the durations to the right and stacks the dottings
    downwards -- the accepted rhythm deck; axis="y" is the same definition,
    turned."""
    glyphs = board.owner.glyphs
    side = matrix_side(glyphs, durations, dottings)

    def cell(d: Duration, n: int) -> Cell:
        dotting = dottings[n]
        return Cell(
            label=f"{d.label}{dotting.label}" if labels else "",
            name=f"{prefix}-{d.slug}{dotting.suffix}",
            comp=matrix_cell(glyphs, d, n, side=side),
            background=d.color,
            presses=[(d.key, ()), *dotting.keys],
            zoom=zoom, font_size=font_size, label_position=label_position)

    if axis == "x":
        rows = [[cell(d, n) for d in durations] for n in range(len(dottings))]
    else:
        rows = [[cell(d, n) for n in range(len(dottings))] for d in durations]
    board.grid(origin, rows, along="y")


# -- ABC figures ---------------------------------------------------------------

@dataclass(frozen=True)
class Figure:
    """One ABC figure: a name, the rhythm, a background."""

    name: str        # label (with --labels) and part of the icon name
    abc: str         # the figure in the rhythm subset of ABC
    color: str       # background of the button


def figure_composition(glyphs, figure: Figure,
                       side: float | None = None) -> Composition:
    """The icon of one figure, from the same event list as its keys."""
    return notation.composition(notation.parse(figure.abc), side=side)


def figure_side(glyphs, items: list[Figure]) -> float:
    """Edge length of the shared frame -- the widest figure sets it."""
    return max(ink_side(glyphs, figure_composition(glyphs, f)) for f in items)


def figures(board: Board, origin: tuple[int, int], items: list[Figure], *,
            per_row: int | None = None, along: str = "x", labels: bool = False,
            prefix: str = "figure", zoom: int = 100, font_size: int = 8,
            label_position: str = "bottom") -> None:
    """ABC figure buttons -- the icon from the same parse as the keys, one
    shared scale over all of them (the widest figure sets it, plan 0002,
    step 4). With per_row the figures fill a grid row by row, without it
    they run along one axis."""
    glyphs = board.owner.glyphs

    def comp(figure: Figure, side: float | None = None):
        return figure_composition(glyphs, figure, side)

    side = figure_side(glyphs, items)

    def cell(figure: Figure) -> Cell:
        return Cell(
            label=figure.name if labels else "",
            name=f"{prefix}-{_slug(figure.name)}",
            comp=comp(figure, side),
            background=figure.color,
            actions=notation.actions(notation.parse(figure.abc),
                                     target_process=board.owner.target),
            zoom=zoom, font_size=font_size, label_position=label_position)

    cells = [cell(f) for f in items]
    if per_row is None:
        board.line(origin, cells, along=along)
    else:
        board.grid(origin, [cells[i:i + per_row]
                            for i in range(0, len(cells), per_row)], along="y")


# -- completions ---------------------------------------------------------------

@dataclass(frozen=True)
class Length:
    """One note length, named -- a row or column of the completion grid."""

    name: str        # part of the icon name and the label
    value: Fraction  # of a whole note


def _dotted(value: Fraction) -> tuple[int, int] | None:
    """(denominator, dots) when `value` is one note with up to two dots."""
    for k in (0, 1, 2):
        factor = 2 - Fraction(1, 2 ** k)
        for v in notation.VALUES:
            if Fraction(factor, v) == value:
                return v, k
    return None


def _abc(value: int, k: int = 0) -> str:
    return f"c{value}" + "." * k


def completions(board: Board, origin: tuple[int, int],
                shorts: list[Length], targets: list[Length], *,
                colors: list[str] | None = None, labels: bool = False,
                axis: str = "y", zoom: int = 100, font_size: int = 8,
                label_position: str = "bottom") -> None:
    """The completion grid: one short note at the edge of a larger unit, the
    complementary long note filling the middle -- a double-dotted quarter
    and a 16th together are a half. Per short length a row, per target and
    order a column; every cell in both orders (short note last, then
    first). Cells whose complement is not one dotted note, or that collapse
    to an equal pair, stay empty -- leave the hard ones out (plan 0003).
    axis="y" stacks the short lengths downwards, axis="x" lays them out to
    the right -- the same definition, turned."""
    glyphs = board.owner.glyphs
    if not colors:
        colors = ["#3b82f6"] * len(shorts)
    elif len(colors) < len(shorts):
        colors = [colors[i % len(colors)] for i in range(len(shorts))]

    def abc(short: Length, fill: Fraction, order: str) -> str:
        base, k = _dotted(fill)
        long_, short_ = _abc(base, k), _abc(short.value.denominator)
        return f"{long_} {short_}" if order == "end" else f"{short_} {long_}"

    def cell(short: Length, target: Length, order: str, color: str,
             side: float | None = None) -> Cell | None:
        fill = target.value - short.value
        if fill <= 0 or fill <= short.value or _dotted(fill) is None:
            return None
        text = abc(short, fill, order)
        return Cell(
            label=f"{short.name} {target.name}" if labels else "",
            name=f"complement-{short.name}-{target.name}-{order}",
            comp=notation.composition(notation.parse(text), side=side),
            background=color,
            actions=notation.actions(notation.parse(text),
                                     target_process=board.owner.target),
            zoom=zoom, font_size=font_size, label_position=label_position)

    def rows(side: float | None) -> list[list[Cell | None]]:
        return [[cell(short, t, order, color, side)
                 for t in targets for order in ("end", "start")]
                for short, color in zip(shorts, colors)]

    first = rows(None)
    side = max(ink_side(glyphs, c.comp)
               for line_ in first for c in line_
               if c is not None and c.comp is not None)
    cells = rows(side)

    board.grid(origin, cells, along=axis)


# -- plain key rows --------------------------------------------------------------

def key_cell(label: str, glyph: str, background: str,
             *presses: tuple[str, tuple[str, ...]]) -> Cell:
    """One key button: icon from the UI font (text only with glyph=""),
    one or more presses."""
    return Cell(label=label,
                name=f"key-{_slug(label)}" if glyph else "",
                comp=Composition([Glyph(glyph)]) if glyph else None,
                background=background,
                presses=list(presses))
