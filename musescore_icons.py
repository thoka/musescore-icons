#!/usr/bin/env python3
"""
musescore_icons.py -- MuseScore UI-Icon-Font in PNG/SVG-Icons umwandeln.

Holt die UI-Icon-Font (MusescoreIcon.ttf) und die Namenstabelle (iconcodes.h)
aus dem MuseScore-Quellcode und rendert fuer jeden Glyph ein Icon.
Die Icons werden thematisch in Unterordner einsortiert.

Beispiele:
    python musescore_icons.py fetch
    python musescore_icons.py render --sizes 32,128 --svg
    python musescore_icons.py all --color "#ffffff" --out icons-light
    python musescore_icons.py list
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass, field, asdict
from pathlib import Path

# --------------------------------------------------------------------------
# Quellen
# --------------------------------------------------------------------------

REPO = "musescore/muse_framework"
FONT_PATH_IN_REPO = "framework/ui/data/MusescoreIcon.ttf"
CODES_PATH_IN_REPO = "framework/ui/view/iconcodes.h"
RAW = "https://raw.githubusercontent.com/{repo}/{ref}/{path}"

DEFAULT_FONT = Path("fonts/MusescoreIcon.ttf")
DEFAULT_CODES = Path("fonts/iconcodes.h")

# --------------------------------------------------------------------------
# Thematische Einsortierung
#
# Erste passende Regel gewinnt -- die Reihenfolge ist daher Teil der Logik.
# Jede Regel: (Ordnername, [Regex gegen den Icon-Namen in GROSSBUCHSTABEN])
# --------------------------------------------------------------------------

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("guitar-fretboard", [
        r"^GUITAR_", r"FRETBOARD", r"^FRET_FRAME", r"^TAPPING_",
    ]),
    ("transport-playback", [
        r"^PLAY(_|$)", r"^STOP", r"^PAUSE", r"^REWIND", r"^RECORD", r"^LOOP",
        r"^METRONOME$", r"^COUNT_IN$", r"^PLAYHEAD", r"^MUTE$", r"^SOLO$",
        r"^BPM$", r"^CLOCK$", r"^TEMPO_CHANGE$", r"^MIXER$", r"^MIDI_INPUT$",
        r"^FOOT_PEDAL$", r"^PAN_SCORE$", r"^TUNING_FORK$",
    ]),
    ("audio-waveform", [
        r"WAVEFORM", r"SPECTROGRAM", r"^MICROPHONE$", r"^SILENCE_AUDIO",
        r"^TRIM_AUDIO", r"^TRIM_HANDLE", r"^AUTOMATION$", r"^AUDIO$",
    ]),
    ("notes-rests-beams", [
        r"^NOTE", r"^REST", r"^LONGO$", r"^GRACE", r"^ACCIACCATURA$",
        r"^APPOGGIATURA$", r"^VOICE_", r"BEAM", r"^TUPLET", r"TREMOLO",
        r"^DURATION_CURSOR$", r"^SINGLE_NOTE$", r"^MUSIC_NOTES$",
    ]),
    ("pitch-accidentals-keys", [
        r"^KEY_SIGNATURE", r"^ACCIDENTAL_", r"^SHARP", r"^FLAT", r"^NATURAL$",
        r"^CLEF_", r"^AMBITUS",
    ]),
    ("articulations-ornaments", [
        r"^MARCATO$", r"^ACCENT$", r"^TENUTO$", r"^STACCATO$", r"^ARTICULATION$",
        r"^ORNAMENT$", r"^FERMATA$", r"^SLUR$", r"^TIE_", r"^LV_", r"^GLISSANDO$",
        r"^VIBRATO$", r"^TRILL",
    ]),
    ("dynamics-expression", [
        r"^DYNAMIC", r"^CRESCENDO", r"^DIMINUENDO", r"^HAIRPIN$", r"^EXPRESSION$",
        r"^PEDAL_MARKING$", r"^OTTAVA$", r"^VOLTA$", r"^LET_RING$", r"^PALM_MUTE$",
    ]),
    ("layout-breaks-frames", [
        r"BREAK", r"FRAME", r"^SYSTEM_LOCK", r"^PAGE_LOCK$", r"MARGIN$", r"GAP",
        r"^ORIENTATION_", r"EMPTY_STAVES$", r"^SPACER$", r"^HORIZONTAL$",
        r"^VERTICAL$", r"^STAFF_TYPE_CHANGE$",
    ]),
    ("score-elements", [
        r"^TIME_SIGNATURE", r"^TIMESIG_", r"^BARLINE", r"BAR_LINE", r"^BRACKET",
        r"^BRACE$", r"^REPEAT_START$", r"^MARKER$", r"^JUMP$", r"^MULTIMEASURE_REST$",
        r"^MEASURE_REPEAT$", r"^INSERT_ONE_MEASURE$", r"^PERCUSSION$", r"^SCORE$",
        r"^DOT_(ABOVE|BELOW)_LINE$", r"^TEXT_(ABOVE|BELOW)_STAFF$",
    ]),
    ("text-typography", [
        r"^TEXT_", r"ALIGN", r"^AUTO_TEXT$", r"^HP_", r"^FRACTION_", r"^IBEAM$",
        r"^LYRICS$", r"^CHORD_",
    ]),
    ("lines", [
        r"^LINE_", r"^LINE$",
    ]),
    ("arrows-navigation", [
        r"ARROW", r"^CHEVRON", r"^(UP|DOWN)$",
    ]),
    ("view-zoom", [
        r"^ZOOM", r"VIEW", r"^FIT_", r"^EYE_", r"^GRID$", r"^LIST$", r"^CAMERA$",
        r"^PAGE$",
    ]),
    ("file-cloud-online", [
        r"FILE", r"^SAVE$", r"^CLOUD", r"^SHARE", r"^IMPORT$", r"^PRINT$",
        r"LINK", r"^UPDATE$", r"^GLOBE$", r"^ACCOUNT$", r"_LOGO$", r"^VIDEO$",
        r"^IMAGE_",
    ]),
    ("edit-tools", [
        r"^UNDO$", r"^REDO$", r"^COPY$", r"^PASTE$", r"^CUT$", r"^EDIT$",
        r"^DELETE", r"^PLUS$", r"^MINUS$", r"^BRUSH$", r"^SPLIT_TOOL$",
        r"^MAGNET$", r"^SEARCH$", r"^RHYTHM_ONLY$", r"^RE_PITCH$", r"^BYPASS$",
        r"^APPLY_GLOBAL_STYLE$",
    ]),
    ("app-ui-status", [
        r"^APP_", r"^WARNING", r"^INFO$", r"^ERROR$", r"^QUESTION", r"^FEEDBACK$",
        r"^SETTINGS_COG$", r"^CONFIGURE$", r"^SHORTCUTS$", r"^WORKSPACE$",
        r"^PLUGIN$", r"^LEARN$", r"^MORTAR_BOARD$", r"^GRADUATION_CAP$",
        r"^TOOLBAR_GRIP$", r"^MENU_THREE_DOTS$", r"^CLOSE_X", r"^TICK", r"^CROSS$",
        r"^STAR$", r"^LOCK_", r"^INSIGHT$", r"^SPLIT_OUT_ARROWS$", r"^BRAILLE$",
    ]),
    ("shapes-misc", [
        r"^CIRCLE$", r"^TWO_CIRCLES$", r"^TRIANGLE", r"^SQUARE",
    ]),
]

UNNAMED_CATEGORY = "_unnamed"
FALLBACK_CATEGORY = "misc"


def categorize(name: str, named: bool) -> str:
    if not named:
        return UNNAMED_CATEGORY
    for folder, patterns in CATEGORY_RULES:
        for pat in patterns:
            if re.search(pat, name):
                return folder
    return FALLBACK_CATEGORY


# --------------------------------------------------------------------------
# Datenmodell
# --------------------------------------------------------------------------

@dataclass
class Glyph:
    name: str               # Dateiname-Basis, z.B. PLAY oder U+F3A3
    codepoint: int
    glyph_name: str         # interner Name in der Font-Datei
    category: str
    named: bool             # Name stammt aus iconcodes.h
    aliases: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)

    @property
    def code(self) -> str:
        return f"U+{self.codepoint:04X}"

    @property
    def char(self) -> str:
        return chr(self.codepoint)


# --------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------

def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "musescore-icons/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    dest.write_bytes(data)
    print(f"  {dest}  ({len(data):,} Bytes)")


def cmd_fetch(args) -> None:
    print(f"Lade UI-Font und Icon-Namen aus {REPO}@{args.ref}:")
    download(RAW.format(repo=REPO, ref=args.ref, path=FONT_PATH_IN_REPO), Path(args.font))
    download(RAW.format(repo=REPO, ref=args.ref, path=CODES_PATH_IN_REPO), Path(args.codes))


# --------------------------------------------------------------------------
# Namen einlesen
# --------------------------------------------------------------------------

ENUM_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*=\s*(0x[0-9A-Fa-f]+)\s*,", re.M)


def parse_iconcodes(path: Path) -> dict[int, list[str]]:
    """Liefert {Codepoint: [Name, Alias, ...]} aus iconcodes.h."""
    if not path.exists():
        return {}
    src = path.read_text(encoding="utf-8", errors="replace")
    try:
        body = src.split("enum class Code", 1)[1].split("{", 1)[1].split("};", 1)[0]
    except IndexError:
        raise SystemExit(f"Konnte enum 'Code' in {path} nicht finden.")
    out: dict[int, list[str]] = {}
    for name, value in ENUM_RE.findall(body):
        if name == "NONE":
            continue
        out.setdefault(int(value, 16), []).append(name)
    return out


def collect_glyphs(font, codes: dict[int, list[str]]) -> list[Glyph]:
    cmap = font.getBestCmap()
    glyphs: list[Glyph] = []
    for cp in sorted(cmap):
        names = codes.get(cp)
        if names:
            name, aliases, named = names[0], names[1:], True
        else:
            internal = cmap[cp]
            # svg2ttf vergibt teils sprechende Namen, sonst nur uniXXXX
            if re.fullmatch(r"uni[0-9A-Fa-f]{4,6}", internal):
                name, named = f"U+{cp:04X}", False
            else:
                name, named = internal.upper(), False
            aliases = []
        glyphs.append(Glyph(
            name=safe_filename(name),
            codepoint=cp,
            glyph_name=cmap[cp],
            category=categorize(name, named),
            named=named,
            aliases=aliases,
        ))
    return glyphs


def safe_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_+.-]", "_", name)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def parse_color(value: str) -> tuple[int, int, int, int]:
    v = value.strip().lower()
    presets = {
        "black": (0, 0, 0, 255), "white": (255, 255, 255, 255),
        "transparent": (0, 0, 0, 0), "none": (0, 0, 0, 0),
    }
    if v in presets:
        return presets[v]
    m = re.fullmatch(r"#?([0-9a-f]{3,8})", v)
    if not m:
        raise argparse.ArgumentTypeError(f"Unbekannte Farbe: {value}")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 6:
        h += "ff"
    if len(h) != 8:
        raise argparse.ArgumentTypeError(f"Unbekannte Farbe: {value}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))  # type: ignore[return-value]


class Renderer:
    """Rendert einzelne Glyphen mittig in ein quadratisches Bild."""

    def __init__(self, font_path: Path, ttfont, mode: str, margin: float,
                 fg: tuple[int, int, int, int], bg: tuple[int, int, int, int]):
        from fontTools.pens.boundsPen import BoundsPen

        self.font_path = str(font_path)
        self.ttf = ttfont
        self.mode = mode
        self.margin = margin
        self.fg = fg
        self.bg = bg
        self.upem = ttfont["head"].unitsPerEm
        self.hmtx = ttfont["hmtx"]
        self.glyphset = ttfont.getGlyphSet()
        self._bounds: dict[str, tuple[float, float, float, float]] = {}
        self._BoundsPen = BoundsPen
        self._fontcache: dict[int, object] = {}

    def bounds(self, glyph_name: str) -> tuple[float, float, float, float]:
        """Ink-Bounding-Box in Font-Einheiten."""
        if glyph_name not in self._bounds:
            pen = self._BoundsPen(self.glyphset)
            self.glyphset[glyph_name].draw(pen)
            self._bounds[glyph_name] = pen.bounds or (0.0, 0.0, 0.0, 0.0)
        return self._bounds[glyph_name]

    def _pil_font(self, size_px: int):
        from PIL import ImageFont
        if size_px not in self._fontcache:
            self._fontcache[size_px] = ImageFont.truetype(self.font_path, size_px)
        return self._fontcache[size_px]

    def render(self, glyph: Glyph, size: int):
        from PIL import Image, ImageDraw

        box = size * (1.0 - 2.0 * self.margin)          # nutzbare Kantenlaenge
        x0, y0, x1, y1 = self.bounds(glyph.glyph_name)
        ink_w, ink_h = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)

        if self.mode == "fit":
            # Jeder Glyph wird auf die volle Icon-Flaeche skaliert.
            scale = box / max(ink_w, ink_h)
            cx_u, cy_u = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        else:
            # "em": Groessenverhaeltnisse wie im Font-Design; nur Ueberstaende
            # werden so weit verkleinert, dass nichts abgeschnitten wird.
            scale = box / self.upem
            if ink_w * scale > box or ink_h * scale > box:
                scale = box / max(ink_w, ink_h)
                cx_u, cy_u = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            else:
                adv = self.hmtx[glyph.glyph_name][0] or self.upem
                cx_u, cy_u = adv / 2.0, self.upem / 2.0

        font_px = max(1, round(self.upem * scale))
        scale = font_px / self.upem                      # tatsaechlicher Massstab
        pil_font = self._pil_font(font_px)

        img = Image.new("RGBA", (size, size), self.bg)
        draw = ImageDraw.Draw(img)
        # Anker "ls" = Stiftposition auf der Grundlinie, y waechst nach unten.
        ox = size / 2.0 - cx_u * scale
        oy = size / 2.0 + cy_u * scale
        draw.text((ox, oy), glyph.char, font=pil_font, fill=self.fg, anchor="ls")
        return img

    def svg(self, glyph: Glyph, size: int = 1000) -> str:
        from fontTools.pens.svgPathPen import SVGPathPen

        pen = SVGPathPen(self.glyphset)
        self.glyphset[glyph.glyph_name].draw(pen)
        d = pen.getCommands()

        x0, y0, x1, y1 = self.bounds(glyph.glyph_name)
        ink_w, ink_h = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
        if self.mode == "fit":
            side = max(ink_w, ink_h)
            cx_u, cy_u = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        else:
            adv = self.hmtx[glyph.glyph_name][0] or self.upem
            side = max(self.upem, ink_w, ink_h)
            cx_u, cy_u = (adv / 2.0, self.upem / 2.0) if side == self.upem \
                else ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
        pad = side * self.margin / max(1e-6, (1.0 - 2.0 * self.margin))
        full = side + 2 * pad
        vb_x = cx_u - full / 2.0
        vb_y = -(cy_u + full / 2.0)                      # y-Flip fuer SVG
        color = "#%02x%02x%02x" % self.fg[:3]
        opacity = "" if self.fg[3] == 255 else f' fill-opacity="{self.fg[3] / 255:.3f}"'
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="{vb_x:.2f} {vb_y:.2f} {full:.2f} {full:.2f}">\n'
            f'  <title>{html.escape(glyph.name)} ({glyph.code})</title>\n'
            f'  <g transform="scale(1,-1)">\n'
            f'    <path fill="{color}"{opacity} d="{d}"/>\n'
            f'  </g>\n</svg>\n'
        )


# --------------------------------------------------------------------------
# Galerie
# --------------------------------------------------------------------------

def write_gallery(out: Path, glyphs: list[Glyph], preview_size: int, meta: dict) -> Path:
    by_cat: dict[str, list[Glyph]] = {}
    for g in glyphs:
        by_cat.setdefault(g.category, []).append(g)

    parts = [f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MuseScore UI-Icons</title>
<style>
  :root {{ color-scheme: light dark; --bg:#fbfbfa; --fg:#1b1b18; --muted:#6b6b60;
           --card:#fff; --line:#e4e4dd; --accent:#2b6cb0; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#16161a; --fg:#f0f0ea; --muted:#9a9a90; --card:#1f1f24;
             --line:#32323a; --accent:#7cb3ec; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:24px 16px 64px; background:var(--bg); color:var(--fg);
         font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }}
  header {{ max-width:1100px; margin:0 auto 24px; }}
  h1 {{ font-size:24px; margin:0 0 4px; }}
  .sub {{ color:var(--muted); }}
  main {{ max-width:1100px; margin:0 auto; }}
  h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:.06em;
        color:var(--muted); margin:32px 0 12px; padding-bottom:6px;
        border-bottom:1px solid var(--line); }}
  .grid {{ display:grid; gap:10px;
           grid-template-columns:repeat(auto-fill,minmax(112px,1fr)); }}
  .cell {{ background:var(--card); border:1px solid var(--line); border-radius:8px;
           padding:10px 6px; text-align:center; cursor:pointer; }}
  .cell:hover {{ border-color:var(--accent); }}
  .cell img {{ width:{preview_size}px; height:{preview_size}px; display:block;
               margin:0 auto 8px; image-rendering:auto; }}
  .n {{ font-size:10px; word-break:break-all; line-height:1.3; }}
  .c {{ font-size:10px; color:var(--muted); font-family:ui-monospace,monospace; }}
  #q {{ width:100%; max-width:420px; padding:8px 10px; border-radius:8px;
        border:1px solid var(--line); background:var(--card); color:var(--fg); }}
  .hidden {{ display:none; }}
  #toast {{ position:fixed; bottom:20px; left:50%; transform:translateX(-50%);
            background:var(--fg); color:var(--bg); padding:8px 14px;
            border-radius:999px; opacity:0; transition:opacity .2s; }}
</style></head><body>
<header>
  <h1>MuseScore UI-Icons</h1>
  <p class="sub">{len(glyphs)} Glyphen aus <code>{html.escape(meta.get('font', ''))}</code>
     &middot; {len(by_cat)} Kategorien &middot; Klick kopiert den Namen</p>
  <input id="q" type="search" placeholder="Filtern nach Name oder Codepoint&hellip;">
</header>
<main>"""]

    for cat in sorted(by_cat):
        items = sorted(by_cat[cat], key=lambda g: g.codepoint)
        parts.append(f'<section data-cat="{html.escape(cat)}">'
                     f'<h2>{html.escape(cat)} <span class="c">({len(items)})</span></h2>'
                     f'<div class="grid">')
        for g in items:
            rel = f"{preview_size}px/{g.category}/{g.name}.png"
            title = html.escape(", ".join([g.name] + g.aliases))
            parts.append(
                f'<div class="cell" data-k="{html.escape((g.name + " " + g.code).lower())}" '
                f'data-name="{html.escape(g.name)}" title="{title}">'
                f'<img src="{html.escape(rel)}" alt="{html.escape(g.name)}" loading="lazy">'
                f'<div class="n">{html.escape(g.name)}</div>'
                f'<div class="c">{g.code}</div></div>')
        parts.append("</div></section>")

    parts.append("""</main><div id="toast"></div>
<script>
const q = document.getElementById('q'), toast = document.getElementById('toast');
q.addEventListener('input', () => {
  const t = q.value.trim().toLowerCase();
  for (const s of document.querySelectorAll('section')) {
    let n = 0;
    for (const c of s.querySelectorAll('.cell')) {
      const hit = !t || c.dataset.k.includes(t);
      c.classList.toggle('hidden', !hit); if (hit) n++;
    }
    s.classList.toggle('hidden', n === 0);
  }
});
document.addEventListener('click', e => {
  const cell = e.target.closest('.cell'); if (!cell) return;
  navigator.clipboard?.writeText(cell.dataset.name);
  toast.textContent = cell.dataset.name + ' kopiert';
  toast.style.opacity = 1; setTimeout(() => toast.style.opacity = 0, 1200);
});
</script></body></html>""")

    path = out / "index.html"
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Kommandos
# --------------------------------------------------------------------------

def load_all(args):
    from fontTools.ttLib import TTFont

    font_path = Path(args.font)
    if not font_path.exists():
        raise SystemExit(f"Font nicht gefunden: {font_path}\n"
                         f"Erst 'python {Path(sys.argv[0]).name} fetch' ausfuehren.")
    ttf = TTFont(font_path, fontNumber=0, lazy=True)
    codes = parse_iconcodes(Path(args.codes))
    if not codes:
        print(f"Warnung: {args.codes} fehlt -- alle Icons landen in "
              f"'{UNNAMED_CATEGORY}'.", file=sys.stderr)
    return font_path, ttf, codes, collect_glyphs(ttf, codes)


def cmd_list(args) -> None:
    _, _, codes, glyphs = load_all(args)
    by_cat: dict[str, list[Glyph]] = {}
    for g in glyphs:
        by_cat.setdefault(g.category, []).append(g)
    for cat in sorted(by_cat):
        items = sorted(by_cat[cat], key=lambda g: g.codepoint)
        print(f"\n{cat}  ({len(items)})")
        for g in items:
            alias = f"  (= {', '.join(g.aliases)})" if g.aliases else ""
            print(f"    {g.code}  {g.name}{alias}")
    print(f"\nSumme: {len(glyphs)} Glyphen, {len(by_cat)} Kategorien, "
          f"{sum(1 for g in glyphs if g.named)} mit Namen aus iconcodes.h")


def cmd_render(args) -> None:
    font_path, ttf, codes, glyphs = load_all(args)
    out = Path(args.out)
    sizes = [int(s) for s in str(args.sizes).replace(" ", "").split(",") if s]
    fg, bg = parse_color(args.color), parse_color(args.background)
    renderer = Renderer(font_path, ttf, args.mode, args.margin, fg, bg)

    out.mkdir(parents=True, exist_ok=True)
    written = 0
    for size in sizes:
        n = 0
        for g in glyphs:
            d = out / f"{size}px" / ("" if args.flat else g.category)
            d.mkdir(parents=True, exist_ok=True)
            img = renderer.render(g, size)
            for nm in [g.name] + ([] if args.no_aliases else g.aliases):
                p = d / f"{safe_filename(nm)}.png"
                img.save(p, "PNG", optimize=True)
                g.files.append(str(p.relative_to(out)))
                written += 1
                n += 1
        print(f"  {n} PNG @ {size}px -> {out}/{size}px/")

    if args.svg:
        n = 0
        for g in glyphs:
            d = out / "svg" / ("" if args.flat else g.category)
            d.mkdir(parents=True, exist_ok=True)
            data = renderer.svg(g)
            for nm in [g.name] + ([] if args.no_aliases else g.aliases):
                p = d / f"{safe_filename(nm)}.svg"
                p.write_text(data, encoding="utf-8")
                g.files.append(str(p.relative_to(out)))
                written += 1
                n += 1
        print(f"  {n} SVG -> {out}/svg/")

    meta = {
        "font": str(font_path),
        "source": RAW.format(repo=REPO, ref=args.ref, path=FONT_PATH_IN_REPO),
        "names_source": RAW.format(repo=REPO, ref=args.ref, path=CODES_PATH_IN_REPO),
        "units_per_em": renderer.upem,
        "mode": args.mode,
        "margin": args.margin,
        "sizes": sizes,
        "color": args.color,
        "background": args.background,
        "glyph_count": len(glyphs),
        "named_count": sum(1 for g in glyphs if g.named),
    }
    (out / "manifest.json").write_text(
        json.dumps({"meta": meta, "icons": [asdict(g) | {"code": g.code}
                                            for g in glyphs]},
                   indent=2, ensure_ascii=False), encoding="utf-8")

    if args.gallery and not args.flat:
        preview = max(sizes) if len(sizes) == 1 else sorted(sizes)[len(sizes) // 2]
        page = write_gallery(out, glyphs, preview, meta)
        print(f"  Galerie -> {page}")

    cats = len({g.category for g in glyphs})
    print(f"\nFertig: {written} Dateien, {len(glyphs)} Glyphen, {cats} Kategorien.")


def cmd_all(args) -> None:
    cmd_fetch(args)
    print()
    cmd_render(args)


# --------------------------------------------------------------------------

def main(argv=None) -> None:
    p = argparse.ArgumentParser(
        description="MuseScore-UI-Icon-Font als PNG/SVG-Icons exportieren.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    p.add_argument("--font", default=str(DEFAULT_FONT), help="Pfad zur MusescoreIcon.ttf")
    p.add_argument("--codes", default=str(DEFAULT_CODES), help="Pfad zur iconcodes.h")
    p.add_argument("--ref", default="main", help="Git-Ref/Tag/Commit im MuseScore-Repo")
    sub = p.add_subparsers(dest="cmd")

    def add_render_opts(sp):
        sp.add_argument("-o", "--out", default="icons", help="Ausgabeordner")
        sp.add_argument("-s", "--sizes", default="128",
                        help="PNG-Kantenlaengen in px, kommagetrennt (z.B. 24,48,128)")
        sp.add_argument("-c", "--color", default="black", help="Icon-Farbe (#rrggbb[aa])")
        sp.add_argument("-b", "--background", default="transparent", help="Hintergrundfarbe")
        sp.add_argument("-m", "--margin", type=float, default=0.08,
                        help="Rand als Anteil der Kantenlaenge (0..0.4)")
        sp.add_argument("--mode", choices=("fit", "em"), default="fit",
                        help="fit: jeder Glyph fuellt das Icon; "
                             "em: Groessen wie im Font-Design")
        sp.add_argument("--svg", action="store_true", help="zusaetzlich SVG exportieren")
        sp.add_argument("--no-aliases", action="store_true",
                        help="fuer Alias-Namen keine Kopien anlegen")
        sp.add_argument("--flat", action="store_true",
                        help="keine thematischen Unterordner")
        sp.add_argument("--no-gallery", dest="gallery", action="store_false",
                        help="keine index.html erzeugen")

    sub.add_parser("fetch", help="Font und Namenstabelle herunterladen")
    add_render_opts(sub.add_parser("render", help="Icons rendern"))
    add_render_opts(sub.add_parser("all", help="fetch + render"))
    sub.add_parser("list", help="Glyphen und Kategorien auflisten")

    args = p.parse_args(argv)
    if not args.cmd:
        args.cmd = "all"
        for k, v in dict(out="icons", sizes="128", color="black",
                         background="transparent", margin=0.08, mode="fit",
                         svg=False, flat=False, gallery=True,
                         no_aliases=False).items():
            setattr(args, k, v)
    if not 0 <= getattr(args, "margin", 0) < 0.45:
        raise SystemExit("--margin muss zwischen 0 und 0.45 liegen.")
    {"fetch": cmd_fetch, "render": cmd_render, "all": cmd_all,
     "list": cmd_list}[args.cmd](args)


if __name__ == "__main__":
    main()
