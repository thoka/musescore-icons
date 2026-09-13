#!/usr/bin/env python3
"""Seite im Headless-Browser oeffnen und pruefen, was ein Screenshot nicht zeigt.

Meldet Konsolenfehler und fehlgeschlagene Requests (etwa 404 auf Icons), macht
auf Wunsch Screenshots der ganzen Seite oder einzelner Elemente und kann
JavaScript auswerten -- damit spaeter Canvas-Pixel gegen den Python-Renderer
verglichen werden koennen.

Der Exitcode ist 1, sobald Konsolenfehler oder fehlgeschlagene Requests
aufgetreten sind; so laesst sich das Skript in einer Pruefkette verwenden.

Die Browser-Binaries liegen bereits im Playwright-Cache, sind aber meist eine
andere Revision als die, die das Python-Paket erwartet. Deshalb wird die
vorhandene chrome-headless-shell ueber ``executable_path`` eingehaengt statt
nachgeladen.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


def find_browser() -> tuple[str, bool]:
    """Sucht einen Browser im Playwright-Cache.

    Liefert (Pfad, ist_headless_shell). Bevorzugt wird die schlanke
    chrome-headless-shell, ersatzweise der volle Chromium.
    """
    cache = os.environ.get(
        "PLAYWRIGHT_BROWSERS_PATH", str(Path.home() / ".cache" / "ms-playwright")
    )
    shells = sorted(
        glob.glob(
            f"{cache}/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell"
        )
    )
    if shells:
        return shells[-1], True
    full = sorted(glob.glob(f"{cache}/chromium-*/chrome-linux64/chrome"))
    if full:
        return full[-1], False
    raise SystemExit(f"Kein Chrome im Playwright-Cache gefunden ({cache}).")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Seite laden, Konsole und Requests pruefen, Screenshots machen."
    )
    p.add_argument("url", help="zu pruefende URL, z. B. http://localhost:8000/")
    p.add_argument("--shot", help="Screenshot der Seite in diese Datei schreiben")
    p.add_argument(
        "--full-page",
        action="store_true",
        help="ganze Seite statt nur des sichtbaren Ausschnitts aufnehmen",
    )
    p.add_argument(
        "--element",
        nargs=2,
        action="append",
        metavar=("SELEKTOR", "DATEI"),
        default=[],
        help="Screenshot eines einzelnen Elements (mehrfach moeglich)",
    )
    p.add_argument("--wait", help="vor dem Screenshot auf diesen Selektor warten")
    p.add_argument(
        "--js",
        help="JavaScript im Seitenkontext auswerten und das Ergebnis als JSON ausgeben",
    )
    p.add_argument(
        "--viewport",
        default="1280,900",
        help="Fenstergroesse als BREITE,HOEHE (Vorgabe: 1280,900)",
    )
    p.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="Geraete-Pixelverhaeltnis fuer schaerfere Screenshots (Vorgabe: 2)",
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=15000,
        help="Zeitlimit in Millisekunden (Vorgabe: 15000)",
    )
    args = p.parse_args()

    width, _, height = args.viewport.partition(",")
    binary, _is_shell = find_browser()

    errors: list[str] = []
    failed: list[str] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=binary)
        page = browser.new_page(
            viewport={"width": int(width), "height": int(height)},
            device_scale_factor=args.scale,
        )

        # Ohne das gilt fuer Selektoren weiter die Vorgabe von 30 s, egal was
        # --timeout sagt.
        page.set_default_timeout(args.timeout)

        page.on(
            "console",
            lambda msg: errors.append(f"{msg.type}: {msg.text}")
            if msg.type in ("error", "warning")
            else None,
        )
        page.on("pageerror", lambda exc: errors.append(f"pageerror: {exc}"))
        page.on(
            "requestfailed",
            lambda req: failed.append(f"{req.failure} {req.url}"),
        )
        page.on(
            "response",
            lambda res: failed.append(f"HTTP {res.status} {res.url}")
            if res.status >= 400
            else None,
        )

        page.goto(args.url, wait_until="networkidle", timeout=args.timeout)
        if args.wait:
            page.wait_for_selector(args.wait, timeout=args.timeout)
        page.wait_for_timeout(300)  # Layout und Fonts nachziehen lassen

        if args.shot:
            Path(args.shot).parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=args.shot, full_page=args.full_page)
            print(f"Screenshot: {args.shot}")

        for selector, dest in args.element:
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            try:
                page.locator(selector).first.screenshot(
                    path=dest, timeout=args.timeout
                )
            except PlaywrightError as exc:
                # Ein Selektor, der nichts trifft, ist ein Befund der Seite --
                # kein Absturz des Werkzeugs.
                errors.append(f"Selektor {selector!r}: {str(exc).splitlines()[0]}")
            else:
                print(f"Screenshot {selector}: {dest}")

        if args.js:
            print(json.dumps(page.evaluate(args.js), indent=2, ensure_ascii=False))

        title = page.title()
        browser.close()

    print(f"Titel: {title}")
    print(f"Konsolenfehler: {len(errors)}")
    for line in errors:
        print(f"  {line}")
    print(f"Fehlgeschlagene Requests: {len(failed)}")
    for line in failed:
        print(f"  {line}")

    return 1 if errors or failed else 0


if __name__ == "__main__":
    sys.exit(main())
