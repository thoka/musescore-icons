# Rhythm entry: the Eingeben board and the fixed bars

## Entry

* **Stand**: branch `plan/0006-rhythm-entry`. Plan committed
  (`5f212fe`, cut from alpha at `041250f` — plan 0004 squash-merged
  there, still open, device judgement pending). Step 1 in: the
  library's `action_bar(cells)` — same cells bottom-right on every
  board, settle extracted into `_settle(min_columns=, min_rows=)`,
  empty list is a no-op. 183 tests green.
* **Next step**: step 2 — the Eingeben board and the time-signature
  column (Model: GLM).
* **Read**: `decks/workbench.py`, `deckgen/routines.py`, `decks/rhythm.py`
  (DURATIONS, DOTTINGS), `deckgen/notation.py` (REST_GLYPHS, VALUE_KEYS),
  `tests/test_workbench.py`, `tests/test_routines.py`.
* **Run**: `.venv/bin/python -m pytest` — all green. `python
  decks/workbench.py` writes `packs/noten.macroDeckFolder` (five
  boards, 73 buttons until step 2).
* **Open**: the generic action bar's content — it comes gradually, one
  step each; the time-signature keys are a proposal until the user's
  import file arrives; the device judgement from plan 0004 still
  pending and may rework what this plan builds on.

## Context

Brief from 2026-09-15: the Noten board only *sets* the note length —
that stays as it is. A board after it must actually *enter* the note;
the pitch can always be middle C. It needs all values, also as rests.
Goal: fast entry of the rhythm, before the pitches are fixed in a later
step. For that, certain boards (first: all) get a bottom action bar
holding the same actions everywhere — to be defined one by one over
time. Position: bottom right corner, as a horizontal element. And: such
a fixed bar in the second column of the Noten ("notenlänge setzen") and
Eingeben ("noten eingeben") boards; its content is the piece's common
time signatures: 2/4, C, ¢ (alla breve), 6/8, 12/8.

## Decided (not re-discussed)

* **Two bars, not one** (user's choice): the *generic action bar* —
  horizontal, anchored bottom right, the same cells on every board,
  content empty for now — plus a *time-signature column* in the second
  column (column 1, between menu and content) of exactly the Noten and
  Eingeben boards. The content of those two boards shifts to column 2.
* **The new board is "Eingeben"**, second in the menu right after
  Noten (creation order: root first): accent `#14b8a6`, icon
  `NOTE_QUARTER` (free in the icon set; Rhythmen wears `NOTE_8TH`).
* **Middle C always**: an entry cell sends the duration key, the dot
  keys, then "c" — the rest variant sends the duration key, the dot
  keys, then "0" (MuseScore: 0 = rest of the selected duration). The
  icons are the matrix cells' glyphs; rests sit on the rest glyphs
  (`deckgen.notation.REST_GLYPHS` — finer rests borrow the eighth's
  shape until Leland supplies them, accepted since plan 0001).
* **Time-signature buttons are text buttons**: the UI font has no 2/4,
  C, ¢ glyphs (`fonts/iconcodes.h` knows only TIME_SIGNATURE and the
  tuplet digit 3) — the labels are the symbols themselves: 2/4, C, ¢,
  6/8, 12/8.
* **The time-signature keys are the user's own assignment**, managed by
  them; an import file will land in the repo and the settings are
  documented and adapted as needed. Proposal until then — checked
  against `docs/action-codes.md`, no default collides: Ctrl+Alt+5 =
  2/4, Ctrl+Alt+6 = C, Ctrl+Alt+7 = ¢, Ctrl+Alt+8 = 6/8, Ctrl+Alt+9 =
  12/8. No Shift (the ":" lesson from decks/rhythm.py); the voices sit
  on Ctrl+Alt+0..4 and the intervals on Alt+0..9, so 5..9 is free.
* **The import file lands as `musescore/shortcuts.xml`**; the
  assignment is documented in `docs/taktarten-kuerzel.md` (step 3).

## Step 1 — Library: the action bar

**Model: GLM** (mechanical, test-backed — like the menu work of plan
0004).

* `deckgen/board.py`: `BoardDeck.action_bar(cells)` — writes the same
  cells onto *every* board, in the bottom row, anchored right (bottom
  right corner, horizontal). It settles the uniform grid first, like
  `menu_strip()` does, plus its own need (one row, len(cells) columns
  from the right). The position is the routine's constant — the same
  decision menu_strip made; knobs only when the device asks. An empty
  list settles nothing and writes nothing.
* `tests/test_board.py`: the bar lands bottom-right on every board and
  moves nothing else; boards with different content still share the
  grid; an empty list is a no-op; the bar's icons are shared across
  boards (same name, same composition — the library's cache, no
  re-render).

### Stand: done

* [x] `deckgen/board.py` — `BoardDeck.action_bar(cells)`: the same
      cells on every board, bottom row, anchored right; the settle
      logic extracted into `_settle(min_columns=, min_rows=)` and
      reused by `menu_strip`; an empty list is a no-op. Module
      docstring names both constants.
* [x] `tests/test_board.py` — the bar lands bottom-right on every
      board and moves nothing else; icons shared across boards; empty
      list a no-op; after a menu that grows the grid the bar still
      lands on the final bottom row. 183 green in total.

## Step 2 — Workbench: the Eingeben board and the time-signature column

**Model: GLM.**

* `deckgen/routines.py`: `entry_matrix(board, origin, durations,
  dottings, *, rest=False, ...)` — the duration matrix plus the entry
  tail: "c" for notes, "0" for rests, after duration and dots. The
  icon is the matrix cell; the rest block sits on the rest glyphs, so
  the durations need their note value — a `value` field on
  `rhythm.Duration` (whole = 1 … 32nd = 32). The accepted rhythm
  deck's archive stays bit-identical (its test asserts it). Icon
  prefixes distinct per board ("enter-note-*", "enter-rest-*") — the
  shared library raises on a name used twice.
* `decks/workbench.py`: the board **Eingeben** right after Noten — the
  matrix as notes at (2, 0), the same matrix as rests below it; the
  time-signature column at (1, 0) on Noten and Eingeben; their content
  origin moves to column 2. The generic action bar wired with an empty
  list (content comes later).
* `tests/test_workbench.py` + `tests/test_routines.py`: spot checks —
  the eighth-note entry cell sends 4 c and the rest variant 4 0; the
  five time-signature buttons sit at (1, 0)..(1, 4) and send the
  proposed keys; six boards, menu in creation order; bit-identity of
  the deck.

### Stand: open

## Step 3 — Documentation and the import file

**Model: GLM.**

* `docs/taktarten-kuerzel.md`: which key triggers which time signature,
  how the assignment came to be (palette cell shortcut, assigned on the
  device), where the import file lives (`musescore/shortcuts.xml`) and
  that the buttons in `decks/workbench.py` follow it. The proposal
  above stands until the file arrives; the file is committed when it
  lands, and the keys move if it differs.
* No README change — device-internal matter, the generated pages are
  untouched. (A README section comes with the import file, if the flow
  needs one — then in both languages.)

### Stand: open

## Verification

Everything checkable without the device lives in `tests/` and runs
with `.venv/bin/python -m pytest`: the bar's position and the uniform
grid, the entry cells' key sequences, the time-signature column's keys
and positions, bit-identity of the deck. The keys' effect in MuseScore
is the device's judgement — as with transport and edit (unverified
defaults) — and is documented until the import file settles it.
