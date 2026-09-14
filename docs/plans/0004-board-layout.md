# Board layout: uniform grid and vertical menu

## Entry

* **Status**: branch `plan/0004-board-layout` (cut from the tip of
  `plan/0003-workbench`, whose board layer this builds on; `main` is still
  one commit behind). Plan committed, no code yet. Plan 0003 stands: 176
  tests green, the workbench deck not yet accepted on the device.
* **Next step**: Step 1 — library (`Model: GLM`).
* **Read**: `deckgen/board.py` (the whole file, 186 lines) and
  `tests/test_board.py` (menu tests). Step 2 additionally needs
  `decks/workbench.py` and `tests/test_workbench.py`. Nothing else — in
  particular no plan 0003 re-read beyond what the entry blocks say.
* **Run**: `.venv/bin/python -m pytest` — 176 green. After step 2:
  `python decks/workbench.py` writes `packs/noten.macroDeckFolder`, five
  boards of 7×5 each (69 buttons, unchanged).
* **Open**: nothing — the four questions are decided (grid 7×5, content
  origin (1, 0), orientation as the only CLI flag, default vertical column
  0). The round-trip below is a future plan, not part of this one.

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

### Stand: open

## Step 2 — Workbench deck

**Model: GLM.**

* `decks/workbench.py`: origins to (1, 0), the `--menu` flag, docstring;
  `tests/test_workbench.py`: structure and spot checks onto the moved
  positions (e. g. `note-whole` at (1, 0)), 7×5 on every board,
  bit-identity stays.

### Stand: open

## Verification

Everything checkable without the device lives in `tests/` and runs with
`.venv/bin/python -m pytest`: the uniform grid across boards, the menu
wiring in column 0, the horizontal option, bit-identity of the deck. Grid
and menu order are judged on the device after step 2.
