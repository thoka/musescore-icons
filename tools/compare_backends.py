#!/usr/bin/env python3
"""Beide Backends einer Komposition gegeneinander messen (Plan 0002, Schritt 2).

deckgen.compose rendert dasselbe Modell auf zwei Wegen: Pillow zeichnet die
Glyphen -- daraus werden die WebP-Stufen im Archiv --, fontTools schreibt
dieselben Umrisse als SVG fuer Vorschau, Icon-Packs und Webseite. Beide muessen
dieselbe Flaeche treffen, sonst sieht dasselbe Icon im Browser anders aus als
auf dem Geraet.

Gemessen wird die Alpha-Bounding-Box in Pixeln: das Pillow-Bild in Python, das
SVG im Headless-Chrome, gezeichnet in ein Canvas derselben Kantenlaenge.
Verglichen werden die vier Kanten. Exakte Gleichheit ist kein Ziel -- die
Kantenglaettung der beiden Wege unterscheidet sich --, deshalb --tolerance.

    python tools/compare_backends.py
    python tools/compare_backends.py --size 512 --keep
"""

from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from deckgen.compose import Composition, Dot, Glyph, dots  # noqa: E402
from deckgen.glyphs import Glyphs  # noqa: E402

# Die Faelle decken die Rechenwege ab, die sich unterscheiden koennen:
# einzelner Glyph, Rahmen aus mehreren Layern, Skalierung, Verschiebung,
# beide Box-Modi und der Flow.
CASES: dict[str, Composition] = {
    "glyph-fit": Composition([Glyph("NOTE_QUARTER")]),
    # NOTE_HEAD_QUARTER passt ins Em-Quadrat -- nur so greift der Zweig "em".
    "glyph-em": Composition([Glyph("NOTE_HEAD_QUARTER")], mode="em"),
    "glyph-em-overflow": Composition([Glyph("NOTE_QUARTER")], mode="em"),
    "glyph-scaled": Composition([Glyph("NOTE_8TH", scale=0.6)]),
    # Zwei Layer, damit die Verschiebung im Rahmen ueberhaupt sichtbar wird:
    # bei einem einzelnen Layer waechst der Ausschnitt einfach mit.
    "glyph-moved": Composition(
        [Glyph("NOTE_QUARTER"), Glyph("NOTE_8TH", scale=0.5, dx=0.35, dy=-0.3)]),
    "dot-only": Composition([Dot(r=0.2)]),
    "dotted-8th": Composition([Glyph("NOTE_8TH"), *dots(1)]),
    "double-dotted-half": Composition([Glyph("NOTE_HALF"), *dots(2)]),
    "flow-three": Composition(
        [Glyph("NOTE_8TH"), Glyph("NOTE_8TH"), Glyph("NOTE_QUARTER")], flow=True),
    "flow-with-dot": Composition(
        [Glyph("NOTE_QUARTER"), Dot(r=0.08), Glyph("REST_8TH")], flow=True),
    "no-margin": Composition([Glyph("NOTE_16TH")], margin=0.0),
}

MEASURE_JS = """
async ({files, size, threshold}) => {
  const out = [];
  for (const file of files) {
    const img = new Image();
    img.src = file;
    await img.decode();
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = size;
    const ctx = canvas.getContext('2d', {willReadFrequently: true});
    ctx.drawImage(img, 0, 0, size, size);
    const data = ctx.getImageData(0, 0, size, size).data;
    let x0 = size, y0 = size, x1 = -1, y1 = -1;
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        if (data[(y * size + x) * 4 + 3] > threshold) {
          if (x < x0) x0 = x;
          if (x > x1) x1 = x;
          if (y < y0) y0 = y;
          if (y > y1) y1 = y;
        }
      }
    }
    out.push(x1 < 0 ? null : [x0, y0, x1, y1]);
  }
  return out;
}
"""


def image_box(image, threshold: int) -> tuple[int, int, int, int] | None:
    """Alpha-Bounding-Box des Pillow-Bildes, Kanten einschliesslich."""
    mask = image.getchannel("A").point(lambda a: 255 if a > threshold else 0)
    box = mask.getbbox()
    return None if box is None else (box[0], box[1], box[2] - 1, box[3] - 1)


def svg_boxes(directory: Path, names: list[str], size: int,
              threshold: int) -> list[tuple[int, int, int, int] | None]:
    """Dieselbe Messung im Browser: SVG ins Canvas, Alpha auslesen.

    Ausgeliefert wird ueber einen lokalen HTTP-Server; ueber file:// waeren die
    Bilder fremden Ursprungs und getImageData verweigerte die Auskunft.
    """
    from playwright.sync_api import sync_playwright

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from check_page import find_browser

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):                   # Requests nicht mitschreiben
            pass

    handler = functools.partial(Handler, directory=str(directory))
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{server.server_address[1]}/"
        binary, _ = find_browser()
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=binary)
            page = browser.new_page()
            page.goto(url + "blank.html")
            boxes = page.evaluate(MEASURE_JS, {
                "files": [f"{name}.svg" for name in names],
                "size": size,
                "threshold": threshold,
            })
            browser.close()
        server.shutdown()
    return [tuple(b) if b else None for b in boxes]


def main() -> int:
    p = argparse.ArgumentParser(
        description="Pillow- und SVG-Backend derselben Komposition vergleichen.")
    p.add_argument("--size", type=int, default=256,
                   help="Kantenlaenge der Messung in Pixeln (Vorgabe: 256)")
    p.add_argument("--tolerance", type=int, default=1,
                   help="erlaubte Abweichung je Kante in Pixeln (Vorgabe: 1)")
    p.add_argument("--threshold", type=int, default=127,
                   help="ab welchem Alpha ein Pixel als Tinte gilt (Vorgabe: 127)")
    p.add_argument("--keep", metavar="ORDNER",
                   help="SVG und PNG dorthin schreiben statt in ein Temp-Verzeichnis")
    args = p.parse_args()

    glyphs = Glyphs()
    names = list(CASES)

    tmp = None
    if args.keep:
        out = Path(args.keep)
        out.mkdir(parents=True, exist_ok=True)
    else:
        tmp = tempfile.TemporaryDirectory()
        out = Path(tmp.name)
    (out / "blank.html").write_text(
        "<!doctype html><meta charset=utf-8><title>compare</title>\n",
        encoding="utf-8")

    png_boxes = []
    for name in names:
        comp = CASES[name]
        (out / f"{name}.svg").write_text(
            comp.to_svg(glyphs, args.size, title=name), encoding="utf-8")
        image = comp.to_image(glyphs, args.size)
        if args.keep:
            image.save(out / f"{name}.png")
        png_boxes.append(image_box(image, args.threshold))

    boxes = svg_boxes(out, names, args.size, args.threshold)

    print(f"{'Fall':<20} {'Pillow':>20} {'SVG':>20}  Abweichung")
    bad = 0
    for name, png, svg in zip(names, png_boxes, boxes):
        if png is None or svg is None:
            print(f"{name:<20} {'leer' if png is None else 'ok':>20} "
                  f"{'leer' if svg is None else 'ok':>20}  FEHLT")
            bad += 1
            continue
        delta = [s - p for p, s in zip(png, svg)]
        worst = max(abs(d) for d in delta)
        flag = "" if worst <= args.tolerance else "  <-- zu gross"
        if flag:
            bad += 1
        fmt = lambda b: ",".join(f"{v:4d}" for v in b)  # noqa: E731
        print(f"{name:<20} {fmt(png):>20} {fmt(svg):>20}  "
              f"{','.join(f'{d:+d}' for d in delta)} (max {worst}){flag}")

    print(f"\n{len(names) - bad}/{len(names)} Faelle innerhalb "
          f"{args.tolerance} px bei {args.size} px Kantenlaenge.")
    if tmp:
        tmp.cleanup()
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
