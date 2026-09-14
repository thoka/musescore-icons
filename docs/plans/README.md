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

* A plan is committed **before** the implementation starts, in its own commit.
* The implementation happens on a branch, never on a target branch directly;
  the branch name is pragmatic (`plan/NNNN-slug` for a plan). Commits are made
  freely; `alpha` collects finished but unproven work, `main` takes only what
  is proven. Both targets are updated on request with the same procedure: tag
  the branch tip, squash-merge it into a single commit whose message
  summarizes the work, then delete the branch — the tag keeps the individual
  commits findable. See *Plans* in `AGENTS.md`.
* Progress is ticked off inside the plan file itself, not in a separate note.
* When the work is done, set the status to `done`; do not delete the file.
* This table is the index — add a row in the same commit that adds a plan.

| # | Plan | Status | Written |
|---|---|---|---|
| 0001 | [Glyph composer: macro deck icons from MuseScore glyphs](0001-glyph-composer.md) | done | 2026-09-13 |
| 0002 | [Deck generator: write complete Macro Deck folders](0002-deck-generator.md) | open | 2026-09-14 |
