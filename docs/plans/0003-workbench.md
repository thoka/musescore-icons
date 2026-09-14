# Board system: the workbench deck for note entry

## Entry

* **Status**: no code yet. Branch `plan/0003-workbench` is cut from
  `plan/0002-deck-generator` — it builds on the library from that plan's
  steps 1–4, which is not on `main` yet. This plan was committed before the
  implementation started.
* **Next step**: step 1 — Board and regions.
* **Read**: `deckgen/archive.py` (Deck/Folder/Button), `deckgen/compose.py`
  (side/anchor, flow), `deckgen/notation.py` (`DOT_KEYS`, two-dot limit),
  `decks/rhythm.py` and `decks/patterns.py` (the routines to extract).
* **Run**: `.venv/bin/python -m pytest` — 140 tests green.
* **Open**: nothing that blocks step 1.

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

## Step 3 — The workbench deck

**Model: GLM.**

* `decks/workbench.py` — assembles the five boards, writes
  `packs/noten.macroDeckFolder`. Display levers as flags (zoom, font size,
  label position, axis orientation) so a device iteration needs no commit,
  as in the pattern deck.
* Device acceptance decides layout and presentation; the triple-dot binding
  and any unverified shortcut come back from the device with answers.

## Verification

Everything checkable without the device lives in `tests/` and runs with
`.venv/bin/python -m pytest`: region placement in both orientations, menu
wiring, bit-identity of the wrapped decks, complement math. The deck itself
is judged by import and use on the device.
