"""
deckgen.glyphs -- Glyphen der MuseScore-UI-Font als Bild.

Duennes Dach ueber musescore_icons.py: dieselbe Font, dieselbe Renderlogik
(Modus fit, Rand 0.08), nur mit freier Farbe und Groesse. Fuer zusammengesetzte
Icons kommt spaeter deckgen.compose dazu.
"""

from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_FONT = "fonts/MusescoreIcon.ttf"
DEFAULT_CODES = "fonts/iconcodes.h"


class Glyphs:
    """Laedt die Font einmal und liefert Bilder zu Icon-Namen."""

    def __init__(self, color: str = "white", background: str = "transparent",
                 mode: str = "fit", margin: float = 0.08,
                 font: str = DEFAULT_FONT, codes: str = DEFAULT_CODES):
        from musescore_icons import Renderer, load_all, parse_color

        font_path, ttf, _codes, glyphs = load_all(
            argparse.Namespace(font=font, codes=codes))
        self.renderer = Renderer(font_path, ttf, mode, margin,
                                 parse_color(color), parse_color(background))
        self.by_name = {}
        for g in glyphs:
            for name in [g.name] + g.aliases:
                self.by_name.setdefault(name, g)

    def __contains__(self, name: str) -> bool:
        return name in self.by_name

    def image(self, name: str, size: int = 1024):
        """PIL-Bild -- die Quelle fuer die WebP-Stufen im Archiv."""
        return self.renderer.render(self._glyph(name), size)

    def svg(self, name: str, size: int = 256) -> str:
        """SVG-Text -- fuer Icon-Packs und die Vorschau im Browser."""
        return self.renderer.svg(self._glyph(name), size)

    def _glyph(self, name: str):
        if name not in self.by_name:
            raise KeyError(f"Unbekanntes Icon: {name}")
        return self.by_name[name]
