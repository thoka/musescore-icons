#!/usr/bin/env python3
"""
make_pages.py -- Uebersichtsseite (index.html) fuer GitHub Pages erzeugen.

Liest icons/manifest.json, gruppiert die Icons nach Kategorie und schreibt eine
statische Seite mit Vorschau, Zahlen und Download-Links auf die ZIP-Pakete des
GitHub-Releases. Die Dateigroessen kommen aus packs/, falls vorhanden.

Beispiele:
    python make_pages.py
    python make_pages.py --tag v1.0.0
    python make_pages.py --repo thoka/musescore-icons --preview 16
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

DEFAULT_MANIFEST = "icons/manifest.json"
DEFAULT_PACKS = "packs"
DEFAULT_OUT = "index.html"
FALLBACK_REPO = "thoka/musescore-icons"

# Reihenfolge der Kategorien auf der Seite -- _unnamed ans Ende.
CATEGORY_ORDER_LAST = "_unnamed"


def detect_repo() -> str:
    """owner/name aus dem origin-Remote ziehen, sonst Fallback."""
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return FALLBACK_REPO
    url = url.removesuffix(".git")
    if url.startswith("git@"):
        url = url.split(":", 1)[-1]
    parts = [p for p in url.split("/") if p]
    return "/".join(parts[-2:]) if len(parts) >= 2 else FALLBACK_REPO


def human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB"):
        if value < 1024 or unit == "MB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} MB"


def group_by_category(icons: list[dict]) -> "OrderedDict[str, list[dict]]":
    cats: dict[str, list[dict]] = {}
    for icon in icons:
        cats.setdefault(icon["category"], []).append(icon)
    ordered = OrderedDict()
    for name in sorted(cats, key=lambda c: (c == CATEGORY_ORDER_LAST, c)):
        ordered[name] = sorted(cats[name], key=lambda i: i["name"])
    return ordered


def pack_link(base: str, packs: Path, variant: str, category: str) -> tuple[str, str]:
    """(URL, Groessenangabe) fuer ein Kategorie-Paket."""
    name = f"icons.{variant}.{category}.zip"
    local = packs / name
    size = human(local.stat().st_size) if local.is_file() else ""
    return f"{base}/{name}", size


STYLE = """
  :root { color-scheme: dark; --bg:#25252b; --fg:#ffffff; --muted:#b0b0ba;
           --card:#32323a; --line:#43434e; --accent:#8cc0f0; }
  * { box-sizing:border-box; }
  body { margin:0; padding:24px 16px 64px; background:var(--bg); color:var(--fg);
         font:14px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif; }
  header, main, footer { max-width:1100px; margin:0 auto; }
  h1 { font-size:26px; margin:0 0 6px; }
  .sub { color:var(--muted); margin:0 0 16px; }
  .sub code { font-family:ui-monospace,monospace; }
  .links { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 28px; padding:0;
           list-style:none; }
  .links a { display:inline-block; padding:7px 12px; border-radius:8px;
             border:1px solid var(--line); background:var(--card);
             color:var(--fg); text-decoration:none; }
  .links a:hover { border-color:var(--accent); color:var(--accent); }
  .links a.primary { border-color:var(--accent); color:var(--accent); }
  .facts { display:grid; gap:10px; margin:0 0 32px; padding:0; list-style:none;
           grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); }
  .facts li { background:var(--card); border:1px solid var(--line);
              border-radius:8px; padding:12px 14px; }
  .facts b { display:block; font-size:20px; font-weight:600; }
  .facts span { color:var(--muted); font-size:12px; }
  h2 { font-size:15px; text-transform:uppercase; letter-spacing:.06em;
        color:var(--muted); margin:36px 0 12px; padding-bottom:6px;
        border-bottom:1px solid var(--line); }
  .cat { background:var(--card); border:1px solid var(--line); border-radius:10px;
         padding:14px 16px; margin:0 0 12px; }
  .cat-head { display:flex; flex-wrap:wrap; gap:10px 14px; align-items:baseline;
              justify-content:space-between; }
  .cat-name { font-family:ui-monospace,monospace; font-size:14px; font-weight:600; }
  .cat-count { color:var(--muted); font-size:12px; }
  .dl { display:flex; flex-wrap:wrap; gap:6px; }
  .dl a { font-size:12px; padding:4px 9px; border-radius:999px;
          border:1px solid var(--line); text-decoration:none; color:var(--fg);
          white-space:nowrap; }
  .dl a:hover { border-color:var(--accent); color:var(--accent); }
  .dl a .s { color:var(--muted); }
  .preview { display:grid; gap:6px; margin-top:14px;
             grid-template-columns:repeat(auto-fill,minmax(46px,1fr)); }
  /* Kachel und Bild getrennt: filter wirkt auf das ganze Element, ein
     Hover-Hintergrund direkt am <img> wuerde also mit invertiert. */
  .t { display:flex; align-items:center; justify-content:center; width:100%;
       max-width:46px; aspect-ratio:1/1; margin:0 auto; padding:5px;
       border-radius:6px; }
  .t:hover { background:var(--line); }
  /* Die PNGs sind schwarz -- auf dunklem Grund invertiert dargestellt. */
  .t img { width:100%; height:auto; aspect-ratio:1/1; display:block;
           filter:invert(1); }
  .preview .more { color:var(--muted); font-size:12px; align-self:center;
                   grid-column:1/-1; }
  footer { margin-top:40px; padding-top:16px; border-top:1px solid var(--line);
           color:var(--muted); font-size:12px; }
  footer a { color:var(--accent); }
"""


def render(meta: dict, cats: "OrderedDict[str, list[dict]]", base: str,
           packs: Path, repo: str, preview: int, releases_url: str) -> str:
    e = html.escape
    variants = [(f"{s}px", f"{s} px") for s in meta.get("sizes", [])] + [("svg", "SVG")]
    named = meta.get("named_count", 0)
    total = meta.get("glyph_count", len(sum(cats.values(), [])))

    out: list[str] = []
    add = out.append
    add('<!doctype html>')
    add('<html lang="en"><head><meta charset="utf-8">')
    add('<meta name="viewport" content="width=device-width, initial-scale=1">')
    add('<title>MuseScore UI Icons</title>')
    add(f'<style>{STYLE}</style></head><body>')

    add('<header>')
    add('<h1>MuseScore UI Icons</h1>')
    add('<p class="sub">Every glyph of the MuseScore Studio interface font '
        '<code>MusescoreIcon.ttf</code> rendered as a single icon &ndash; '
        'PNG and SVG, sorted into thematic folders.</p>')
    add('<ul class="links">')
    add('<li><a class="primary" href="icons/index.html">Browse all icons</a></li>')
    add(f'<li><a href="{e(releases_url)}">All downloads (release)</a></li>')
    add(f'<li><a href="https://github.com/{e(repo)}">Repository</a></li>')
    add(f'<li><a href="https://github.com/{e(repo)}/blob/main/README.md">README</a></li>')
    add('<li><a href="icons/manifest.json">manifest.json</a></li>')
    add('</ul>')
    add('<ul class="facts">')
    add(f'<li><b>{total}</b><span>glyphs in the font</span></li>')
    add(f'<li><b>{named}</b><span>with a name from <code>iconcodes.h</code></span></li>')
    add(f'<li><b>{len(cats)}</b><span>thematic categories</span></li>')
    add(f'<li><b>{len(variants)}</b><span>variants: '
        f'{e(", ".join(label for _, label in variants))}</span></li>')
    add('</ul>')
    add('</header>')

    add('<main>')
    add('<h2>Categories &amp; downloads</h2>')
    for category, icons in cats.items():
        add('<section class="cat">')
        add('<div class="cat-head">')
        add(f'<div><span class="cat-name">{e(category)}</span> '
            f'<span class="cat-count">{len(icons)} icons</span></div>')
        add('<div class="dl">')
        for variant, label in variants:
            url, size = pack_link(base, packs, variant, category)
            suffix = f' <span class="s">{e(size)}</span>' if size else ""
            add(f'<a href="{e(url)}">{e(label)}{suffix}</a>')
        add('</div></div>')
        add('<div class="preview">')
        shown = icons if preview <= 0 else icons[:preview]
        for icon in shown:
            png = f'icons/128px/{category}/{icon["name"]}.png'
            label = f'{icon["name"]} \u00b7 {icon["code"]}'
            add(f'<span class="t" title="{e(label)}">'
                f'<img src="{e(png)}" alt="{e(icon["name"])}" loading="lazy">'
                f'</span>')
        if len(shown) < len(icons):
            add(f'<span class="more">+{len(icons) - len(shown)} more</span>')
        add('</div>')
        add('</section>')
    add('</main>')

    add('<footer>')
    add('<p>The icon font is &copy; MuseScore Limited and licensed under GPL-3.0; '
        'the rendered icons are derivative works under the same license. '
        f'Source: <a href="https://github.com/musescore/muse_framework">'
        'musescore/muse_framework</a>.</p>')
    add('<p>This page is generated by <code>make_pages.py</code> &ndash; '
        'do not edit it by hand.</p>')
    add('</footer>')
    add('</body></html>')
    return "\n".join(out) + "\n"


def main(argv=None) -> None:
    p = argparse.ArgumentParser(
        description="Uebersichtsseite fuer GitHub Pages erzeugen.")
    p.add_argument("--manifest", default=DEFAULT_MANIFEST,
                   help=f"Pfad zur manifest.json (Standard: {DEFAULT_MANIFEST})")
    p.add_argument("--packs", default=DEFAULT_PACKS,
                   help="Ordner mit den ZIP-Paketen (nur fuer die Groessenangaben)")
    p.add_argument("-o", "--out", default=DEFAULT_OUT,
                   help=f"Zieldatei (Standard: {DEFAULT_OUT})")
    p.add_argument("--repo", default=None,
                   help="GitHub-Repo als owner/name (Standard: aus git remote)")
    p.add_argument("--tag", default="latest",
                   help="Release-Tag fuer die Download-Links, 'latest' fuer das "
                        "jeweils neueste Release (Standard: latest)")
    p.add_argument("--preview", type=int, default=0,
                   help="Anzahl Vorschau-Icons je Kategorie, 0 = alle (Standard: 0)")
    args = p.parse_args(argv)

    manifest = Path(args.manifest)
    if not manifest.is_file():
        sys.exit(f"Kein Manifest gefunden: {manifest} -- erst 'musescore_icons.py all'.")
    data = json.loads(manifest.read_text(encoding="utf-8"))

    repo = args.repo or detect_repo()
    latest = args.tag == "latest"
    base = (f"https://github.com/{repo}/releases/latest/download" if latest
            else f"https://github.com/{repo}/releases/download/{args.tag}")
    releases_url = (f"https://github.com/{repo}/releases/latest" if latest
                    else f"https://github.com/{repo}/releases/tag/{args.tag}")

    cats = group_by_category(data["icons"])
    page = render(data["meta"], cats, base, Path(args.packs), repo, args.preview,
                  releases_url)
    Path(args.out).write_text(page, encoding="utf-8")
    print(f"{args.out}  {len(cats)} Kategorien, Downloads von {base}")


if __name__ == "__main__":
    main()
