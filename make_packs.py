#!/usr/bin/env python3
"""
make_packs.py -- jedes Icon-Verzeichnis als ZIP unter packs/ ablegen.

Durchsucht die angegebenen Wurzelordner (Standard: icons) nach Verzeichnissen,
die Icons enthalten, und schreibt fuer jedes davon ein eigenes Archiv. Der
Archivname besteht aus allen Pfadelementen, verbunden mit Punkten:

    icons/128px/edit-tools  ->  packs/icons.128px.edit-tools.zip
    icons/svg/lines         ->  packs/icons.svg.lines.zip

Beispiele:
    python make_packs.py
    python make_packs.py --clean
    python make_packs.py --root icons-light --suffixes .svg
    python make_packs.py --flat --dry-run
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

DEFAULT_ROOTS = ["icons"]
DEFAULT_SUFFIXES = [".png", ".svg"]
DEFAULT_OUT = "packs"

# Feste Zeitstempel -- damit ein erneuter Lauf bei unveraenderten Icons auch
# bitgleiche Archive erzeugt.
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def pack_name(directory: Path) -> str:
    """icons/128px/edit-tools -> 'icons.128px.edit-tools'."""
    parts = [p for p in directory.parts if p not in (".", "/")]
    return ".".join(parts)


def icon_dirs(root: Path, suffixes: set[str]) -> list[tuple[Path, list[Path]]]:
    """Alle Verzeichnisse unter (und einschliesslich) root, die Icons enthalten."""
    found = []
    for directory in sorted([root, *(p for p in root.rglob("*") if p.is_dir())]):
        files = sorted(
            f for f in directory.iterdir()
            if f.is_file() and f.suffix.lower() in suffixes
        )
        if files:
            found.append((directory, files))
    return found


def write_pack(target: Path, files: list[Path], arc_prefix: str) -> None:
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for f in files:
            arcname = f"{arc_prefix}/{f.name}" if arc_prefix else f.name
            info = zipfile.ZipInfo(arcname, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, f.read_bytes())


def human(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def main(argv=None) -> None:
    p = argparse.ArgumentParser(
        description="Icon-Verzeichnisse als ZIP-Pakete unter packs/ buendeln.")
    p.add_argument("-r", "--root", nargs="+", default=DEFAULT_ROOTS,
                   help="zu durchsuchende Wurzelordner (Standard: icons)")
    p.add_argument("-o", "--out", default=DEFAULT_OUT,
                   help="Zielordner fuer die Archive (Standard: packs)")
    p.add_argument("--suffixes", default=",".join(DEFAULT_SUFFIXES),
                   help="Dateiendungen, die als Icon zaehlen (Standard: .png,.svg)")
    p.add_argument("--flat", action="store_true",
                   help="Dateien direkt in die ZIP-Wurzel statt in einen Unterordner")
    p.add_argument("--clean", action="store_true",
                   help="vorhandene Archive im Zielordner vorher loeschen")
    p.add_argument("-n", "--dry-run", action="store_true",
                   help="nur anzeigen, was gepackt wuerde")
    args = p.parse_args(argv)

    suffixes = {
        s if s.startswith(".") else f".{s}"
        for s in (x.strip().lower() for x in args.suffixes.split(",")) if s
    }

    out = Path(args.out)
    if args.clean and out.is_dir() and not args.dry_run:
        for old in out.glob("*.zip"):
            old.unlink()

    jobs: list[tuple[Path, list[Path]]] = []
    for raw in args.root:
        root = Path(raw)
        if not root.is_dir():
            sys.exit(f"Kein Verzeichnis: {root}")
        jobs.extend(icon_dirs(root, suffixes))

    if not jobs:
        sys.exit("Keine Verzeichnisse mit Icons gefunden.")

    if not args.dry_run:
        out.mkdir(parents=True, exist_ok=True)

    total = 0
    for directory, files in jobs:
        name = pack_name(directory)
        target = out / f"{name}.zip"
        if args.dry_run:
            print(f"{target}  ({len(files)} Dateien)")
            continue
        write_pack(target, files, "" if args.flat else name)
        size = target.stat().st_size
        total += size
        print(f"{target}  {len(files):>4} Dateien  {human(size)}")

    if not args.dry_run:
        print(f"\n{len(jobs)} Archive, {human(total)} gesamt in {out}/")


if __name__ == "__main__":
    main()
