"""
deckgen.compose -- mehrere Glyphen zu einem Icon zusammensetzen.

Gerechnet wird in **Font-Einheiten** (upem 1024, y nach oben), weil alle Glyphen
der Font dasselbe Em-Quadrat teilen: uebereinandergelegt sitzen sie ohne
Ausrichtungsheuristik richtig. Erst wenn alle Layer stehen, wird die
Vereinigungs-Bounding-Box auf die Icon-Flaeche skaliert -- in dieser Reihenfolge,
denn Glyphen ragen ueber das Em-Quadrat hinaus.

Zwei Backends aus demselben Modell:

    to_svg()    Text  -- fuer Icon-Packs, Vorschau, Webseite
    to_image()  Bild  -- fuer die WebP-Stufen im Archiv

Beispiel -- punktierte Achtelnote:

    Composition([Glyph("NOTE_8TH"), Dot(dx=0.9, dy=0.05)]).to_image(glyphs, 1024)
"""

from __future__ import annotations

import html
from dataclasses import dataclass

# Punktabstand der Font, gemessen an NOTE_DOTTED/_2/_3: rund 128 Em-Einheiten.
DOT_SPACING = 0.125


@dataclass
class Glyph:
    """Ein Glyph der Font. dx/dy und r sind Anteile des Em-Quadrats."""

    name: str
    color: str = "#ffffff"
    scale: float = 1.0
    dx: float = 0.0
    dy: float = 0.0


@dataclass
class Dot:
    """Ein gefuellter Kreis -- Punktierungen, Notenkoepfe, Trenner."""

    color: str = "#ffffff"
    r: float = 0.05
    dx: float = 0.0
    dy: float = 0.0


def dots(n: int, dx: float = 0.9, dy: float = 0.05, spacing: float = DOT_SPACING,
         **kw) -> list[Dot]:
    """n Punkte nebeneinander, im Abstand der Font."""
    return [Dot(dx=dx + i * spacing, dy=dy, **kw) for i in range(n)]


def dot_dx(glyphs, name: str, dy: float = 0.0, r: float = 0.05,
           clearance: float = 0.05, min_x: float = 0.0) -> float:
    """dx so that the dots keep clear of the note's ink.

    Kerning search on the raster, per note: the seat is the first x where a
    disc of the dot's radius keeps `clearance` from every ink point within
    reach of the dot's height (the head edge for a quarter, the flag from
    1/16 down). The gap follows the font's own dotted glyphs.
    """
    upem = glyphs.renderer.upem
    reach = glyphs.renderer.clear_x(glyphs._glyph(name),
                                    dy * upem, (r + clearance) * upem)
    if reach is None:
        return min_x
    return max(min_x, reach / upem)


def ink_side(glyphs, comp: "Composition") -> float:
    """The edge length the fit frame would pick for this composition -- to
    fix one shared scale across several icons."""
    placed = comp._placed(glyphs)
    x0 = min(b[0] for *_, b in placed)
    y0 = min(b[1] for *_, b in placed)
    x1 = max(b[2] for *_, b in placed)
    y1 = max(b[3] for *_, b in placed)
    return max(x1 - x0, y1 - y0)


class Composition:
    """Layers in em coordinates, scaled together onto a square icon.

    Without `side` the frame picks its own edge length (fit/em). With `side`
    it is fixed in advance -- a series of icons shares one scale to keep the
    font's proportions; `anchor` says what moves to the middle: the union of
    all layers, or only the glyphs (dots stay a right-hand appendage).
    """

    def __init__(self, layers: list, mode: str = "fit", margin: float = 0.08,
                 flow: bool = False, gap: float = 0.06,
                 side: float | None = None, anchor: str = "union"):
        self.layers = layers
        self.mode = mode
        self.margin = margin
        self.flow = flow
        self.gap = gap
        self.side = side
        self.anchor = anchor

    # -- Geometrie -----------------------------------------------------------

    def _placed(self, glyphs) -> list[tuple[object, float, float, float, tuple]]:
        """Layer mit endgueltigem (scale, tx, ty) und Bounding-Box in Font-Einheiten."""
        upem = glyphs.renderer.upem
        out = []
        for layer in self.layers:
            s = getattr(layer, "scale", 1.0)
            tx, ty = layer.dx * upem, layer.dy * upem
            if isinstance(layer, Dot):
                r = layer.r * upem
                box = (tx - r, ty - r, tx + r, ty + r)
            else:
                x0, y0, x1, y1 = glyphs.renderer.bounds(glyphs._glyph(layer.name).glyph_name)
                c = upem / 2.0
                # Skaliert wird um die Mitte des Em-Quadrats, dann verschoben.
                off = c * (1.0 - s)
                box = (x0 * s + off + tx, y0 * s + off + ty,
                       x1 * s + off + tx, y1 * s + off + ty)
            out.append((layer, s, tx, ty, box))

        if self.flow:
            out = self._flowed(out)
        return out

    def _flowed(self, placed: list) -> list:
        """Layer nebeneinander legen -- Abstand nach Breite der Tinte, nicht nach
        Advance: der ist bei fast allen Glyphen 1024 und risse grosse Loecher."""
        upem = 1024.0
        gap = self.gap * upem
        pen = 0.0
        out = []
        for layer, s, tx, ty, (x0, y0, x1, y1) in placed:
            shift = pen - x0
            out.append((layer, s, tx + shift, ty,
                        (x0 + shift, y0, x1 + shift, y1)))
            pen = x1 + shift + gap
        return out

    def _frame(self, placed: list, upem: int) -> tuple[float, float, float]:
        """Mittelpunkt und Kantenlaenge des Ausschnitts in Font-Einheiten."""
        if self.side is not None:
            if self.anchor == "note":
                placed = [p for p in placed if not isinstance(p[0], Dot)]
            x0 = min(b[0] for *_, b in placed)
            y0 = min(b[1] for *_, b in placed)
            x1 = max(b[2] for *_, b in placed)
            y1 = max(b[3] for *_, b in placed)
            return (x0 + x1) / 2.0, (y0 + y1) / 2.0, self.side
        x0 = min(b[0] for *_, b in placed)
        y0 = min(b[1] for *_, b in placed)
        x1 = max(b[2] for *_, b in placed)
        y1 = max(b[3] for *_, b in placed)
        ink_w, ink_h = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
        if self.mode == "em" and ink_w <= upem and ink_h <= upem:
            return upem / 2.0, upem / 2.0, float(upem)
        return (x0 + x1) / 2.0, (y0 + y1) / 2.0, max(ink_w, ink_h)

    # -- Ausgabe -------------------------------------------------------------

    def to_image(self, glyphs, size: int = 1024):
        """PIL-Bild, transparenter Grund."""
        from PIL import Image, ImageDraw

        from musescore_icons import parse_color

        upem = glyphs.renderer.upem
        placed = self._placed(glyphs)
        cx, cy, side = self._frame(placed, upem)
        box = size * (1.0 - 2.0 * self.margin)
        S = box / side

        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        def to_px(ux: float, uy: float) -> tuple[float, float]:
            return (ux - cx) * S + size / 2.0, size / 2.0 - (uy - cy) * S

        for layer, s, tx, ty, _ in placed:
            fill = parse_color(layer.color)
            if isinstance(layer, Dot):
                px, py = to_px(tx, ty)
                r = layer.r * upem * S
                draw.ellipse((px - r, py - r, px + r, py + r), fill=fill)
                continue
            font_px = max(1, round(upem * S * s))
            off = (upem / 2.0) * (1.0 - s)
            # Stiftposition = Bild des Ursprungs (0,0) dieses Layers.
            px, py = to_px(off + tx, off + ty)
            draw.text((px, py), glyphs._glyph(layer.name).char,
                      font=glyphs.renderer._pil_font(font_px), fill=fill,
                      anchor="ls")
        return img

    def to_svg(self, glyphs, size: int = 256, title: str = "") -> str:
        """SVG-Text mit einem <path> bzw. <circle> je Layer."""
        from fontTools.pens.svgPathPen import SVGPathPen

        upem = glyphs.renderer.upem
        placed = self._placed(glyphs)
        cx, cy, side = self._frame(placed, upem)
        pad = side * self.margin / max(1e-6, (1.0 - 2.0 * self.margin))
        full = side + 2 * pad

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="{cx - full / 2:.2f} {-(cy + full / 2):.2f} '
            f'{full:.2f} {full:.2f}">'
        ]
        if title:
            parts.append(f"  <title>{html.escape(title)}</title>")
        parts.append('  <g transform="scale(1,-1)">')
        for layer, s, tx, ty, _ in placed:
            if isinstance(layer, Dot):
                parts.append(f'    <circle cx="{tx:.2f}" cy="{ty:.2f}" '
                             f'r="{layer.r * upem:.2f}" fill="{layer.color}"/>')
                continue
            glyph = glyphs._glyph(layer.name)
            pen = SVGPathPen(glyphs.renderer.glyphset)
            glyphs.renderer.glyphset[glyph.glyph_name].draw(pen)
            off = (upem / 2.0) * (1.0 - s)
            transform = (f' transform="translate({off + tx:.2f},{off + ty:.2f}) '
                         f'scale({s:.4f})"') if (s != 1.0 or tx or ty) else ""
            parts.append(f'    <path fill="{layer.color}"{transform} '
                         f'd="{pen.getCommands()}"/>')
        parts.append("  </g>\n</svg>\n")
        return "\n".join(parts)
