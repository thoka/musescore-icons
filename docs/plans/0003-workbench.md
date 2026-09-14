# Board system: the workbench deck for note entry

## Entry

* **Status**: branch `plan/0003-workbench`. Steps 1–3 code done: board
  layer, routines, and `decks/workbench.py` — five boards ("Noten" as root
  with the duration matrix, "Ergänzungen", "Rhythmen", "Transport",
  "Bearbeiten"), the menu strip on top of each, 176 tests green.
  **The deck has not been on the device yet.**
* **Next step**: device acceptance of `packs/noten.macroDeckFolder` —
  import it, check the menu strip colours, fire matrix, completion and
  transport/edit keys; iterate presentation via flags (`--labels --zoom
  --font-size --label-position --dim`, `--svg DIR` for previews).
* **Read**: `decks/workbench.py` (boards, key tables, levers),
  `deckgen/routines.py`, `deckgen/board.py`, `tests/test_workbench.py`.
* **Run**: `.venv/bin/python -m pytest` — 176 tests green.
  `.venv/bin/python decks/workbench.py` writes `packs/noten.macroDeckFolder`
  (5 boards, 69 buttons).
* **Open**: everything the device decides: the unverified transport keys
  (space, ctrl+home, ctrl+shift+m, ctrl+shift+l) and whether Macro Deck
  names non-printables as "space"/"delete"; the triple-dot binding (the
  whole−16th cell stays empty); which presentation wins — the matrix and
  the completion grid can be turned with one flag each, but only in code
  so far (`axis=` parameter, not yet a CLI flag).

## Context

The device work in plan 0002 proved the pipeline: Python builds a complete
`.macroDeckFolder`, Macro Deck imports it, MuseScore fires. What is missing
is the deck the user actually plays — several boards under one roof, note
entry within reach. Decided in discussion on 2026-09-14:

## Decided (not re-discussed)

* **Python only.** The builder page from plan 0002, step 5 is deferred; the
  whole deck is one Python script against `deckgen/`.
* **The root is the main board.** The menu is not a hierarchy — it is a
  shortcut strip that is always present (first row of every board): one
  button per board, its icon, `change_folder` behind it. The active board's
  button wears the board's accent colour, the others stay dimmed. Boards may
  additionally link anywhere with their own icons.
* **Definitions write into regions, along either axis.** A definition (the
  duration matrix, a completion row, a key row) is written into a board at
  one spot — along a row or down a column — so the same content can be
  presented differently and the device decides which presentation wins.
* **Leave out what is difficult.** The whole−16th complement (a
  triple-dotted half) has no binding yet: its cells stay empty, no
  workaround is built. Requirements evolve iteratively on the device.
* Five boards to start: **Noten** (root: duration × dotting matrix),
  **Ergänzungen** (completion grid), **Rhythmen** (ABC figures), and
  **Transport** and **Bearbeiten** as key rows — their shortcuts are
  unverified defaults until the device confirms them.

## Step 1 — Board and regions

**Model: GLM** (the user chose it for this plan).

* `deckgen/board.py`: `Board` over a `Folder` — name, rows, columns, accent
  colour, menu icon. `write(origin, cells, along="row" | "column")`, plus a
  two-axis form for matrices with a swappable axis.
* The menu strip: built from the deck's boards, placed in row 0 of each;
  the active button in the accent colour, the others dimmed.
* Tests: placement math in both orientations, menu wiring (folder ids,
  colours).

### Stand: done

* [x] `deckgen/board.py` — `BoardDeck` (Deck, one shared renderer, icon
      cache, `press`), `Board` (accent, menu icon, `place`/`line`/`grid`),
      `Cell` (label, comp, presses, the accepted display levers).
* [x] `line(origin, cells, along=...)` — a one-axis definition at one spot,
      both orientations, `None` skips without moving on.
* [x] `grid(origin, rows, along=...)` — the transposed presentation of the
      same two-axis definition is one flag, not a re-cut of the data.
* [x] The menu strip on every board: one button per board, `change_folder`
      behind it, the active board's button in its accent colour, the others
      dimmed. Menu icons render once and are shared; the same name for a
      different composition raises.
* [x] 13 tests (`tests/test_board.py`); 153 green in all.

## Step 2 — Routines

**Model: GLM.**

* Extract, do not copy: the duration matrix out of `decks/rhythm.py`, the
  ABC figure cell out of `decks/patterns.py` — each a routine that writes
  through the Board API. `rhythm.py` and `patterns.py` become thin wrappers;
  their artifacts stay bit-identical (the tests already demand it).
* The completion grid: for each short length L and each target
  W ∈ {quarter, half, whole}, the complement C = W − L as one dotted note
  (0–2 dots), each cell in both orders (short note first / last). Cells
  that need three dots or collapse to an equal pair stay empty.
* A key row: label + icon from the UI font (PLAY, STOP, METRONOME, LOOP,
  UNDO, REDO, COPY, PASTE, CUT …) + one or more `press_key`.

### Stand: done

* [x] `deckgen/routines.py` — `duration_matrix` (with `axis="x"|"y"`, the
      shared scale and dot seats from the accepted rhythm deck),
      `figures` (line or grid, one shared scale), `completions`
      (complement math over `Fraction`, cells in both orders, the hard
      ones empty), `key_cell`. Dataclasses `Duration`, `Dotting`,
      `Figure`, `Length`.
* [x] `decks/rhythm.py` and `decks/patterns.py` are thin wrappers over the
      routines; their tests pass untouched — same artifacts.
* [x] `Cell` also carries ready `Action` lists (a figure sends more than
      one key).
* [x] 11 tests (`tests/test_routines.py`): axis mapping for matrix and
      completions, the complement table (3/16, 7/16, 15/16 empty),
      equal-pair skip, whole-figure key sequences, key cells. 164 green.

## Step 3 — The workbench deck

**Model: GLM.**

* `decks/workbench.py` — assembles the five boards, writes
  `packs/noten.macroDeckFolder`. Display levers as flags (zoom, font size,
  label position, axis orientation) so a device iteration needs no commit,
  as in the pattern deck.
* Device acceptance decides layout and presentation; the triple-dot binding
  and any unverified shortcut come back from the device with answers.

### Stand: code done, device acceptance open

* [x] `decks/workbench.py` — five boards: Noten (root, 6x4: menu + the
      duration matrix), Ergänzungen (6x3: menu + the completion grid,
      8 cells), Rhythmen (6x3: menu + the 12 accepted figures),
      Transport (6x2) and Bearbeiten (6x2) as labelled key rows.
      69 buttons, two runs bit-identical (test).
* [x] Key tables for Transport/Bearbeiten with *unverified default*
      shortcuts, flagged in the docstring; accents per board; menu strip
      shared.
* [x] Display levers as flags (`--zoom --font-size --label-position
      --dim --labels --svg`), defaults from the accepted figure deck.
* [x] 12 tests (`tests/test_workbench.py`): structure, menu wiring and
      colours, matrix spot checks, the completion cells (incl. the two
      empty ones), key sequences, bit-identity. 176 green.
* [ ] **Device acceptance** — import, colours, keys; the axis experiment
      (matrix/completions turned) waits for the device's verdict.

## Verification

Everything checkable without the device lives in `tests/` and runs with
`.venv/bin/python -m pytest`: region placement in both orientations, menu
wiring, bit-identity of the wrapped decks, complement math. The deck itself
is judged by import and use on the device.
