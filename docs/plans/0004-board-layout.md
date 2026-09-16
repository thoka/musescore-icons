---
Title: "Board layout: uniform grid and vertical menu"
Status: open
Written: 2026-09-14
---

# Board layout: uniform grid and vertical menu

## Entry

* **Stand**: branch `fix/manifest-size` (aus alpha geschnitten). Der
  erste Import von `packs/noten.macroDeckFolder` am Gerät wurde abgelehnt
  ("The file is not a valid Macro Deck archive"). Gemessen gegen den Fork:
  Macro Deck liest `manifest.json` nur bis 64 KiB
  (`MaxManifestBytes`, PortableArchive.cs); das eingerückte Manifest des
  Noten-Decks (89 Icons, 357 Dateieinträge) lag mit 69285 Bytes darüber
  und wurde als null gelesen — daher die generische Fehlermeldung. Behoben
  (Schritt 3 unten): `deckgen` schreibt das Manifest jetzt kompakt,
  59179 Bytes. `packs/noten.macroDeckFolder` ist mit dem gegenwärtigen
  Stand neu erzeugt: sechs Boards auf dem Versuchsraster 11×7, 129 Tasten,
  89 Icons (der Stand seit Plan 0006 — die "fünf Boards, 73 Tasten" aus
  Schritt 2 sind überholt). 184 Tests grün.
* **Next step**: Gerät — `packs/noten.macroDeckFolder` erneut
  importieren; Raster, Menü-Ordnung (Boards von oben nach unten in
  Spalte 0, root zuerst), Akzente beurteilen. Dann den Plan schließen
  (status done) und nach dem merge-to-main-Skill zusammenführen.
* **Read**: `docs/plans/0004-board-layout.md`, Abschnitt Schritt 3;
  `deckgen/archive.py` (`_manifest_bytes`). Für nichts weiter.
* **Run**: `.venv/bin/python -m pytest` — 184 grün.
  `python decks/workbench.py` schreibt `packs/noten.macroDeckFolder`
  (Manifest < 64 KiB, Prüfsummen im Manifest geprüft).
* **Open**: Gerät-Ortung von Raster und Menü-Ordnung. Gemessene Grenze:
  auch kompakt passen nur ~98 Icons unter das 64-KiB-Limit — das
  Noten-Deck sitzt bei 89 Icons mit ~6 KiB Luft. Decks wachsen jetzt in
  Tasten, nicht mehr in Icons; wer mehr braucht, muss das Format
  angreifen (nicht hier).

## Context

The first look at the generated multi-board (plan 0003, step 3) found it
good but the layout not: every board carries its own grid, and the menu
strip runs horizontally along the top. Decided with the user on 2026-09-14:

## Decided (not re-discussed)

* **One grid for all boards.** `menu_strip()` — the last call in every
  build — first settles *every* folder of the deck on one common grid: the
  largest occupied extent over all boards plus the menu's own need (one
  button per board along the menu axis, plus the menu row/column itself).
  Empty cells stay empty. The per-board `rows=`/`columns=` arguments remain
  as minimums; the uniform grid is the maximum over them. For the workbench
  deck that is **7 columns × 5 rows** on all five boards (content 6 wide
  beside the menu column, the menu 5 tall; the device accepts 7 columns).
* **The menu stands vertically.** Default `along="y"`, `index=0` — column 0
  ("far left comes first"), the boards in creation order from the top, root
  first. `along="x"` gives the old horizontal strip in row `index`. The old
  `y=` parameter goes away.
* **Configurable at the library; orientation as the only flag.**
  `menu_strip()` gets orientation and position parameters;
  `workbench.py` gains only `--menu vertical|horizontal` (default
  vertical). The position stays a library concern.
* **Content origin moves to (1, 0)** — full height to the right of the
  menu; content no longer leaves a row under a menu strip.

## On the horizon: round-trip

After this plan the user wants a round-trip: re-arranging boards and
buttons in Macro Deck on the device becomes the basis for further work on
the scripts — the changes are read back in and the program adapts (a plan
of its own, presumably 0005, not yet written). It will need IDs generated
or stored in some form that make the match possible. What this plan owes
it — nothing more:

* IDs stay name-derived and deterministic (`_guid` hashes names, not
  positions) so a re-imported archive can be matched back to definitions.
* Menu buttons already carry `menu-<slug>` names — the round-trip can key
  on those.
* Widget GUIDs (`name:x:y`) are position-based; how moved buttons are
  matched is exactly the subject of that plan. This plan must not make it
  worse — and does not have to solve it.

## Step 1 — Library: orientation and uniform grid

**Model: GLM** (small, mechanical, test-backed — as in plan 0003).

* `deckgen/board.py`: `menu_strip(*, along="y", index=0, dim=...)`; a
  private helper that, before writing, settles every folder on the uniform
  grid (largest occupied extent over all placements of all boards, at
  least the menu's own need); the old fit check goes — the menu fits by
  construction. The module docstring ("first row of every board") is
  corrected.
* `tests/test_board.py`: menu tests move to column 0; new tests: the
  uniform grid over boards declared with different sizes, the horizontal
  option still available.

### Stand: done

* [x] `deckgen/board.py` — `menu_strip(*, along="y", index=0, dim=...)`
      plus private `_settle_uniform_grid` (uniform grid over all boards
      before writing; the old fit check is gone), module docstring
      corrected (column 0, example content at (1, 0)).
* [x] `tests/test_board.py` — menu in column 0, uniform grid over boards
      declared with different sizes, too-small boards are widened, the
      horizontal option still available. 15 green; the 5 failures in
      `tests/test_workbench.py` are step 2's business.

## Step 2 — Workbench deck

**Model: GLM.**

* `decks/workbench.py`: origins to (1, 0), the `--menu` flag, docstring;
  `tests/test_workbench.py`: structure and spot checks onto the moved
  positions (e. g. `note-whole` at (1, 0)), 7×5 on every board,
  bit-identity stays.

### Stand: done

* [x] `decks/workbench.py` — content origins to (1, 0), the `--menu`
      flag, docstring; board declarations widened to columns=7 so the
      content fits before the grid settles.
* [x] `tests/test_workbench.py` — structure and spot checks onto the
      moved positions (`note-whole` at (1, 0)), 7×5 on every board,
      bit-identity stays. 179 green in total.
* Deviation, decided in step 2: under `--menu horizontal` the content
  origin is (0, 1) — the row below the strip. (1, 0) flat would put the
  content under the strip's own buttons. The vertical default is (1, 0)
  as decided.
* Measured: `python decks/workbench.py` writes
  `packs/noten.macroDeckFolder`, five boards of 7×5, **73** buttons —
  the same count as on alpha (the "69" this plan inherited from plan
  0003 was miscounted; 73 is the real number). The horizontal build
  lands on 7×4, same button count.

## Step 3 — The import rejected the Noten deck

**Model: GLM** (small, measured fix; the reader contract came straight
out of the fork in `vendor/macro-deck`).

Device feedback 2026-09-16: importing `packs/noten.macroDeckFolder`
failed with "The file is not a valid Macro Deck archive". Measured
against the fork: Macro Deck reads `manifest.json` only up to 64 KiB
(`MaxManifestBytes`, `PortableArchive.cs`); `ReadEntry` returns null past
it, the manifest reads as null, and every such archive maps to
`InvalidArchive` — the generic message, whatever the true cause. The
indented manifest of the Noten deck (89 icons → 357 declared files) was
69285 bytes. Smaller decks (rhythmus, probe) never came near the limit,
which is why they imported.

* `deckgen/archive.py`: the manifest is written compact (`Deck.manifest`
  holds the dict, `_manifest_bytes` serializes it without indent) —
  59179 bytes for the Noten deck. `content.json` stays indented; its
  limit is 64 MiB.
* `tests/test_archive.py`: 360 synthetic manifest entries (90 icons)
  stay under 64 KiB compact and would break indented — the regression
  the writer must not re-introduce.
* `tests/test_workbench.py`: the real Noten deck's manifest stays within
  64 KiB.

### Stand: done

* [x] Fix, both tests, regeneration of `packs/noten.macroDeckFolder`.
      184 tests green. Measured: even compact, ~98 icons is the ceiling
      under the 64-KiB limit; the Noten deck sits at 89 icons with
      ~6 KiB headroom.

## Verification

Everything checkable without the device lives in `tests/` and runs with
`.venv/bin/python -m pytest`: the uniform grid across boards, the menu
wiring in column 0, the horizontal option, bit-identity of the deck. Grid
and menu order are judged on the device after step 2.
