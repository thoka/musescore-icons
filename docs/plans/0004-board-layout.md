# Board layout: uniform grid and vertical menu

## Entry

* **Stand**: branch `plan/0004-board-layout`. Both steps in, each
  committed: library (`menu_strip(*, along="y", index=0, ...)` +
  `_settle_uniform_grid`) and workbench deck (content at (1, 0),
  `--menu` flag, uniform 7×5 grid). 179 tests green.
  `packs/noten.macroDeckFolder` regenerated locally: five boards of
  7×5, 73 buttons (same count as alpha). User feedback since: the Noten
  matrix runs short durations first now (`reversed(rhythm.DURATIONS)`
  at the call site; the accepted rhythm deck keeps long-to-short).
* **Next step**: none in code — the device decides: grid, menu order
  (boards top-down in column 0, root first), accents. Then close the
  plan (status done) and merge per the merge-to-main skill.
* **Read**: nothing for the code. For the device look: import
  `packs/noten.macroDeckFolder`. If rework is needed, plan step 2 and
  `decks/workbench.py`.
* **Run**: `.venv/bin/python -m pytest` — after step 2 all green (179
  tests). `python decks/workbench.py` writes `packs/noten.macroDeckFolder`,
  five boards of 7×5 (73 buttons, unchanged from alpha — the plan's old
  "69" was a miscount); `--menu horizontal` gives the old strip on top
  (7×4).
* **Open**: device judgement of grid and menu order. The content origin
  under `--menu horizontal` is (0, 1) — decided in step 2 (see its
  Stand); the plan text said (1, 0) flat, which would collide with the
  strip.

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

## Verification

Everything checkable without the device lives in `tests/` and runs with
`.venv/bin/python -m pytest`: the uniform grid across boards, the menu
wiring in column 0, the horizontal option, bit-identity of the deck. Grid
and menu order are judged on the device after step 2.
