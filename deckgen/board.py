"""
deckgen.board -- boards, regions and the menu strip (plan 0003).

A deck is a set of boards, one Folder each. Generic routines write a
definition -- a duration matrix, a completion row, a key row -- into a
region of a board, along either axis, so the same content can be presented
horizontally or vertically and the device decides which wins.

The menu strip is the one constant: the first row of every board holds one
button per board, its icon, a change_folder behind it. The active board's
button wears the board's accent colour, the others stay dimmed.

Example:

    workbench = BoardDeck(glyphs, name="Noten", accent="#3b82f6",
                          icon=Composition([Glyph("MUSIC_NOTES")]))
    notes = workbench.root
    board("Rhythmen", accent="#10b981", icon=...)
    workbench.menu_strip()
    notes.line((0, 1), cells, along="x")
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .actions import change_folder, press_key
from .archive import Button, Deck, Folder, Icon, MASTER_SIZE
from .compose import Composition


def _slug(name: str) -> str:
    return name.lower().replace(" ", "-")


@dataclass
class Cell:
    """One button in the making -- what a routine hands to a Board.

    comp, when given, is rendered once into the deck's icon library under
    `name` (or, empty, derived from label or position); a cell without comp
    is a text button. The display levers carry the values accepted on the
    device in plan 0002, step 4.
    """

    label: str = ""
    name: str = ""
    comp: Composition | None = None
    background: str | None = None
    presses: list[tuple[str, tuple[str, ...]]] = field(default_factory=list)
    actions: list = field(default_factory=list)   # ready Action blocks
    zoom: int = 100
    font_size: int = 8
    label_position: str = "bottom"


class Board:
    """One board: a Folder plus how it presents itself in the menu."""

    def __init__(self, owner: "BoardDeck", folder: Folder, *, accent: str,
                 icon: Composition):
        self.owner = owner
        self.folder = folder
        self.accent = accent
        self.icon = icon

    @property
    def name(self) -> str:
        return self.folder.name

    @property
    def rows(self) -> int:
        return self.folder.rows

    @property
    def columns(self) -> int:
        return self.folder.columns

    # -- region writing -------------------------------------------------------

    def place(self, x: int, y: int, cell: Cell, w: int = 1, h: int = 1) -> Button:
        """One cell at one spot -- the primitive everything else uses."""
        button = Button(label=cell.label, background=cell.background,
                        font_size=cell.font_size,
                        label_position=cell.label_position,
                        icon_zoom=cell.zoom)
        if cell.comp is not None:
            name = cell.name or _slug(cell.label) \
                or f"{_slug(self.name)}-{x}-{y}"
            button.icon = self.owner.icon(name, cell.comp)
        if cell.presses or cell.actions:
            button.on_press = [*cell.actions,
                               *[self.owner.press(key, mods)
                                 for key, mods in cell.presses]]
        self.folder.place(button, x, y, w, h)
        return button

    def line(self, origin: tuple[int, int], cells: list[Cell | None],
             along: str = "x") -> None:
        """A one-axis definition at one spot: along="x" writes to the right,
        along="y" downwards. None skips a cell without moving on."""
        x, y = origin
        dx, dy = (1, 0) if along == "x" else (0, 1)
        for i, cell in enumerate(cells):
            if cell is not None:
                self.place(x + i * dx, y + i * dy, cell)

    def grid(self, origin: tuple[int, int], rows: list[list[Cell | None]],
             along: str = "y") -> None:
        """A two-axis definition at one spot. along="y" stacks the outer
        list downwards and runs each row to the right; along="x" is the
        same definition, transposed: the outer list runs to the right and
        each of its entries downwards."""
        x, y = origin
        for j, row in enumerate(rows):
            for i, cell in enumerate(row):
                if cell is None:
                    continue
                self.place(x + (j if along == "x" else i),
                           y + (i if along == "x" else j), cell)


class BoardDeck:
    """A Deck plus its boards -- and the one renderer they share."""

    def __init__(self, glyphs, *, name: str, accent: str, icon: Composition,
                 rows: int = 5, columns: int = 6, target: str = "MuseScore4",
                 svg_dir=None):
        self.deck = Deck(name, rows=rows, columns=columns)
        self.glyphs = glyphs
        self.target = target
        self.svg_dir = svg_dir
        if svg_dir is not None:
            svg_dir.mkdir(parents=True, exist_ok=True)
        self._icons: dict[str, Icon] = {}
        self._comps: dict[str, Composition] = {}
        self.boards: list[Board] = []
        self.root = Board(self, self.deck.root, accent=accent, icon=icon)
        self.boards.append(self.root)

    def board(self, name: str, *, accent: str, icon: Composition,
              rows: int | None = None, columns: int | None = None,
              parent: Board | None = None) -> Board:
        folder = self.deck.folder(name, rows=rows, columns=columns,
                                  parent=parent.folder if parent else None)
        board = Board(self, folder, accent=accent, icon=icon)
        self.boards.append(board)
        return board

    # -- shared renderer ------------------------------------------------------

    def icon(self, name: str, comp: Composition) -> Icon:
        """Render a composition once and share it; the same name for a
        different composition is a mistake."""
        if name in self._icons:
            if comp is self._comps[name]:
                return self._icons[name]
            raise ValueError(f"icon name used twice: {name}")
        image = comp.to_image(self.glyphs, MASTER_SIZE)
        icon = self.deck.icons.add(name, image, original_file_name=f"{name}.png")
        if self.svg_dir is not None:
            (self.svg_dir / f"{name}.svg").write_text(
                comp.to_svg(self.glyphs, 256, title=name), encoding="utf-8")
        self._icons[name] = icon
        self._comps[name] = comp
        return icon

    def press(self, key: str, mods: tuple[str, ...] = ()):
        return press_key(key, modifiers=mods, target_process=self.target)

    # -- the menu strip -------------------------------------------------------

    def menu_strip(self, *, y: int = 0, dim: str = "#1f2937") -> None:
        """One button per board in row `y` of every board; the active
        board's button in its accent colour, the others dimmed."""
        if any(len(self.boards) > b.columns for b in self.boards):
            raise ValueError(
                f"menu strip of {len(self.boards)} boards does not fit a "
                f"board with fewer columns -- widen the grids")
        for board in self.boards:
            for i, target in enumerate(self.boards):
                cell = Cell(label=target.name,
                            name=f"menu-{_slug(target.name)}",
                            comp=target.icon,
                            background=target.accent if target is board else dim)
                board.place(i, y, cell).on_press = change_folder(target.folder)
