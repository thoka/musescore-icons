#!/usr/bin/env python3
"""
make_deck.py -- ausgewaehlte Icons als Macro-Deck-Icon-Pack buendeln.

Rendert eine Liste von Icon-Namen frisch aus der Font und legt sie in der
flachen Struktur ab, die Macro Deck 3 fuer ein Icon-Pack erwartet:

    ExtensionManifest.json
    ExtensionIcon.png
    PLAY.png
    NOTE_8TH.png
    ...

Das Verzeichnis wird zusaetzlich als .zip und als gleichnamige .macroPack-Kopie
geschrieben -- welches der beiden Macro Deck beim Import annimmt, ist der
offene Punkt, den der Pilot klaeren soll (siehe docs/plans/0001-glyph-composer.md).

Beispiele:
    python make_deck.py --pilot
    python make_deck.py --icons PLAY,STOP,NOTE_8TH --size 256
    python make_deck.py --icons-file meine-icons.txt --format svg
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from make_packs import human, write_pack
from make_pages import detect_repo

# Die ~10 Icons des Piloten: Transport, Bearbeiten, Noten, Vorzeichen -- genug
# Vielfalt, um auf dem Geraet Groesse und Lesbarkeit zu beurteilen.
PILOT_ICONS = [
    "PLAY", "STOP", "LOOP", "METRONOME", "UNDO", "REDO",
    "NOTE_QUARTER", "NOTE_8TH", "REST", "SHARP",
]

# Die drei Testvarianten aus Schritt 2 des Plans:
# (Kuerzel fuer den Dateinamen, Zusatz im Pack-Namen, Format, Kantenlaenge)
PILOT_VARIANTS = [
    ("png256", "PNG 256", "png", 256),
    ("png128", "PNG 128", "png", 128),
    ("svg", "SVG", "svg", 256),
]

DEFAULT_OUT = "packs"
DEFAULT_NAME = "MuseScore Icons Pilot"
DEFAULT_AUTHOR = "thoka"
DEFAULT_VERSION = "0.1.0"
DEFAULT_TARGET = "3.0.0"
# Das Pack-Icon ist immer ein PNG -- auch in der SVG-Variante.
PACK_ICON_SIZE = 256


def package_id(author: str, name: str) -> str:
    """'thoka' + 'MuseScore Icons Pilot 256' -> 'thoka.MuseScoreIconsPilot256'."""
    slug = "".join(ch for ch in name if ch.isalnum())
    return f"{author}.{slug}"


def load_font(args):
    """Renderer und Namenstabelle (inkl. Aliase) aus musescore_icons holen."""
    from musescore_icons import Renderer, load_all, parse_color

    font_path, ttf, _codes, glyphs = load_all(
        argparse.Namespace(font=args.font, codes=args.codes))
    renderer = Renderer(font_path, ttf, args.mode, args.margin,
                        parse_color(args.color), parse_color(args.background))
    by_name = {}
    for g in glyphs:
        for nm in [g.name] + g.aliases:
            by_name.setdefault(nm, g)
    return renderer, by_name


def build_dir(renderer, by_name, names: list[str], dest: Path,
              fmt: str, size: int, meta: dict) -> list[Path]:
    """Pack-Verzeichnis schreiben und die enthaltenen Dateien zurueckgeben."""
    from musescore_icons import safe_filename

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    files = [dest / "ExtensionManifest.json", dest / "ExtensionIcon.png"]
    files[0].write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    renderer.render(by_name[names[0]], PACK_ICON_SIZE).save(
        files[1], "PNG", optimize=True)

    for nm in names:
        glyph = by_name[nm]
        target = dest / f"{safe_filename(nm)}.{fmt}"
        if fmt == "svg":
            target.write_text(renderer.svg(glyph, size), encoding="utf-8")
        else:
            renderer.render(glyph, size).save(target, "PNG", optimize=True)
        files.append(target)
    return files


def bundle(dest: Path, files: list[Path], out: Path) -> list[Path]:
    """Verzeichnis flach als .zip packen und als .macroPack danebenlegen."""
    zip_path = out / f"{dest.name}.zip"
    write_pack(zip_path, files, "")          # flach -- Macro Deck will keine Unterordner
    pack_path = zip_path.with_suffix(".macroPack")
    shutil.copyfile(zip_path, pack_path)
    return [zip_path, pack_path]


def build_variant(args, renderer, by_name, names: list[str],
                  label: str, display: str, fmt: str, size: int) -> None:
    name = f"{args.name} {display}"
    meta = {
        "type": "IconPack",
        "name": name,
        "author": args.author,
        "repository": args.repository,
        "packageId": args.package_id or package_id(args.author, name),
        "version": args.version,
        "target-macro-deck-version": args.target_version,
    }
    dest = Path(args.out) / f"macrodeck-{label}"
    files = build_dir(renderer, by_name, names, dest, fmt, size, meta)
    written = bundle(dest, files, Path(args.out))
    if not args.keep_dir:
        shutil.rmtree(dest)
    for path in written:
        print(f"  {path}  {len(names)} Icons ({fmt}, {size} px)  "
              f"{human(path.stat().st_size)}")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(
        description="Icons als Macro-Deck-Icon-Pack buendeln.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--font", default="fonts/MusescoreIcon.ttf",
                   help="Pfad zur MusescoreIcon.ttf")
    p.add_argument("--codes", default="fonts/iconcodes.h", help="Pfad zur iconcodes.h")
    p.add_argument("--icons", help="Icon-Namen, kommagetrennt (z.B. PLAY,STOP)")
    p.add_argument("--icons-file", help="Datei mit einem Icon-Namen je Zeile")
    p.add_argument("--pilot", action="store_true",
                   help="die drei Testvarianten des Piloten bauen "
                        "(PNG 256, PNG 128, SVG) statt einer einzelnen")
    p.add_argument("-s", "--size", type=int, default=256,
                   help="Kantenlaenge in px (Standard: 256)")
    p.add_argument("-f", "--format", choices=("png", "svg"), default="png",
                   help="Dateiformat der Icons im Pack (Standard: png)")
    p.add_argument("-c", "--color", default="white",
                   help="Icon-Farbe -- weiss, weil Macro-Deck-Tasten dunkel sind")
    p.add_argument("-b", "--background", default="transparent", help="Hintergrundfarbe")
    p.add_argument("-m", "--margin", type=float, default=0.08,
                   help="Rand als Anteil der Kantenlaenge")
    p.add_argument("--mode", choices=("fit", "em"), default="fit",
                   help="fit: jeder Glyph fuellt das Icon; em: Groessen wie im Font-Design")
    p.add_argument("-o", "--out", default=DEFAULT_OUT,
                   help=f"Zielordner fuer die Archive (Standard: {DEFAULT_OUT})")
    p.add_argument("--name", default=DEFAULT_NAME, help="Pack-Name im Manifest")
    p.add_argument("--author", default=DEFAULT_AUTHOR, help="Autor im Manifest")
    p.add_argument("--repository", default=None,
                   help="Repository-URL im Manifest (Standard: origin-Remote)")
    p.add_argument("--package-id", default=None,
                   help="packageId im Manifest (Standard: Autor.PackName)")
    p.add_argument("--version", default=DEFAULT_VERSION, help="Pack-Version (SemVer)")
    p.add_argument("--target-version", default=DEFAULT_TARGET,
                   help="target-macro-deck-version im Manifest")
    p.add_argument("--keep-dir", action="store_true",
                   help="entpacktes Pack-Verzeichnis nicht loeschen")
    args = p.parse_args(argv)

    if args.repository is None:
        args.repository = f"https://github.com/{detect_repo()}"

    names = list(PILOT_ICONS)
    if args.icons:
        names = [n.strip() for n in args.icons.split(",") if n.strip()]
    elif args.icons_file:
        names = [ln.strip() for ln in Path(args.icons_file).read_text(
            encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
    elif not args.pilot:
        print("Keine --icons angegeben -- nehme die Pilot-Auswahl.", file=sys.stderr)

    renderer, by_name = load_font(args)
    unknown = [n for n in names if n not in by_name]
    if unknown:
        raise SystemExit(f"Unbekannte Icon-Namen: {', '.join(unknown)}")

    Path(args.out).mkdir(parents=True, exist_ok=True)
    if args.pilot:
        for variant in PILOT_VARIANTS:
            build_variant(args, renderer, by_name, names, *variant)
    else:
        build_variant(args, renderer, by_name, names,
                      f"{args.format}{args.size}",
                      f"{args.format.upper()} {args.size}", args.format, args.size)


if __name__ == "__main__":
    main()
