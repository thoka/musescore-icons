# Plans

Implementation plans for larger pieces of work, written before the code exists
so that later sessions and third parties can follow the original brief.

## Naming

One file per plan, `NNNN-slug.md`, numbered in the order the plans were written:

```
docs/plans/0001-glyph-composer.md
docs/plans/0002-....md
```

Numbers are never reused and never renumbered — a plan that is dropped keeps its
number and is marked `abandoned` in the table below. The prose of a plan may be
German (like the rest of the project documentation); the file name, the table
below and this file stay English.

## Working with a plan

* A plan is committed **before** the implementation starts, in its own commit
  — the first commit on its `plan/NNNN-slug` branch, cut from `alpha`.
* The implementation happens on a branch, never on a target branch directly;
  the branch name is pragmatic (`plan/NNNN-slug` for a plan). Commits are made
  freely; a branch is merged when the user asks for it — `alpha` collects
  finished but unproven work, `main` takes only what is proven, and neither
  merge runs on the session's own initiative. Both targets are updated with
  the same procedure: tag
  the branch tip, squash-merge it into a single commit whose message
  summarizes the work, then delete the branch — the tag keeps the individual
  commits findable. See *Plans* in `AGENTS.md`.
* Progress is ticked off inside the plan file itself, not in a separate note.
* Each plan file carries its metadata as YAML frontmatter at the top, before
  the title: `Title` (English, for the table — the H1 prose may be German),
  `Status` (`open` / `done` / `abandoned`) and `Written` (the date).
* When the work is done, set the plan's frontmatter `Status` to `done` and
  regenerate the table; do not delete the file.
* The table below is generated from that frontmatter — never edit it by
  hand; run `python3 tools/pending.py --write-index` in the same commit as
  the change that requires it.

<!-- table:begin -->

| # | Plan | Status | Written |
|---|---|---|---|
| 0001 | [Glyph composer: macro deck icons from MuseScore glyphs](0001-glyph-composer.md) | done | 2026-09-13 |
| 0002 | [Deck generator: write complete Macro Deck folders](0002-deck-generator.md) | open | 2026-09-14 |
| 0003 | [Board system: the workbench deck for note entry](0003-workbench.md) | done | 2026-09-14 |
| 0004 | [Board layout: uniform grid and vertical menu](0004-board-layout.md) | open | 2026-09-14 |
| 0005 | [Macro Deck → MuseScore plugin bridge](0005-macrodeck-plugin-bruecke.md) | open | 2026-09-15 |
| 0006 | [Rhythm entry: the Eingeben board and the fixed bars](0006-rhythm-entry.md) | open | 2026-09-15 |
| 0009 | [Plan frontmatter: metadata in files, table generated](0009-plan-frontmatter.md) | done | 2026-09-16 |

<!-- table:end -->
