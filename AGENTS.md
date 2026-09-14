# Agent rules

Instructions for AI coding agents working in this repository.
Write these rules in English, even though most of the project prose is German.

## Documentation is bilingual

The README exists in two languages and both are part of every change:

| File | Language | Role |
|---|---|---|
| `README.md` | English | default entry point of the repository |
| `README-de.md` | German | full German version, same content |

Rules:

* Whenever you change one README, change the other in the same commit. Never
  leave one of them behind — a change that only lands in one language is an
  incomplete change.
* Both files carry the same structure: same sections, same order, same tables,
  same code blocks. Only the prose and the table/option descriptions are
  translated; commands, file names, option flags and folder names stay
  identical.
* Keep the cross-link at the top of each file intact
  (`README.md` → `README-de.md` and back).
* If a user asks for a documentation change in one language only, apply it to
  both anyway and say so in the reply.
* The rule covers these two files only. Everything under `docs/` exists once;
  see *Plans* below.

## Language elsewhere

* Code comments, docstrings and `argparse` help texts in the Python scripts are
  **English**. Older code is German — it predates this rule. Translate what you
  touch anyway; leave the rest alone. A sweep through files nobody is working
  on is not worth the tokens.
* Commit messages: English.
* This file and any other agent instructions: English.

## Plans

Larger pieces of work get a written plan before the code exists, so that later
sessions and third parties can follow the original brief.

* Plans live in `docs/plans/` as `NNNN-slug.md`, numbered in the order they were
  written — never in the repository root. `docs/plans/README.md` explains the
  convention and indexes every plan.
* Commit a new plan on its own, before the implementation starts, and add its
  row to the table in `docs/plans/README.md` in the same commit.
* Tick off progress inside the plan file itself, not in a separate note. When
  the work is finished, set the plan's status to `done`; never delete a plan and
  never reuse or renumber a number.
* Plan prose may be German like the rest of the project documentation; file
  names and the index table stay English.
* **Cutting the work into steps is Opus work, and the cut includes the model.**
  Every step says which model it is meant to be worked on — a line
  `Modell: Sonnet` under its heading is enough, with a word on why when it is
  not obvious. Deciding that once, with the whole plan in view, is cheaper than
  re-deciding it in every later session. A session that disagrees with the
  plan's choice says so rather than quietly working on a bigger model.

Work a plan step at a time, and treat each step as a session of its own: read
the step and its *Stand*, do the work, tick it off, commit, `/clear`. What that
costs is the subject of *Token efficiency* below.

Each plan is implemented on its own branch, `plan/NNNN-slug`, merged with
`git merge --no-ff` once the package is complete:

* GitHub Pages builds from `main` at `/`, so everything pushed to `main` is live
  at once. An unfinished page, or a generated file that no longer matches its
  generator, does not belong there.
* Verify a branch against a local `python3 -m http.server`. The site is static,
  so the local server is representative; the live page gets its screenshot after
  the merge.
* Regenerate `icons/` **once** per branch, in the last commit before the merge.
  It is a large committed tree and repeated rebuilds only produce conflicts.
* Infrastructure that is not part of a plan — agent rules, `.gitignore`,
  `mise.toml` — goes straight to `main`.

## Token efficiency

A session pays for everything it reads and writes, so the cheapest step is the
one that does not repeat work an earlier session already did.

* **A check that runs twice becomes a test** (see *Tests*), never a snippet
  pasted into the session. Ten lines of pytest output beat sixty lines of
  throwaway Python, and the next session inherits the check.
* **Measure, do not look.** A bounding box, a checksum or a byte comparison
  costs a line; a rendered contact sheet costs as much as a few hundred lines
  of code. Open a picture when a design decision needs an eye — not to confirm
  that a rerun still works.
* **Read in parts.** A plan's *Stand* section answers "what is next"; the whole
  file seldom has to be in context. The same goes for source files — a grep and
  a line range beat a full read.
* **Edit in place.** Rewriting a whole file makes the harness put that whole
  file back into the session; a targeted edit does not.
* **One plan step per session.** Finish the step, tick it off, commit, then
  `/clear`. The plan file is the handoff — that is what it is for.
* **A step does not start on the wrong model.** Claude cannot switch the model
  of a running session; `/model` is typed by the user. So before the first edit
  of a step, compare what it needs with what the session runs on — plans,
  format archaeology and design decisions are Opus work, while filling in
  cells, writing a generator against a finished library or adding tests is
  Sonnet work. Where the session is the bigger one:
  * **delegate**, if the work can be handed over as a brief with a checkable
    end state (see *Subagents*) — that costs the user no keystroke;
  * **otherwise stop and say so**: which model the step wants, why, and what it
    would cost to do it here. Then wait for `/model`. Working the step on the
    expensive model anyway, quietly, is exactly what this rule forbids.

  A small fix in passing does not earn an interruption — mention it in a line
  and carry on. A plan step does.

### Subagents

A subagent keeps its tool output in its own context and hands back a report,
and it can be given a smaller model. That is the one lever Claude can pull
without the user, so **use one whenever the saving is likely** — this section
is the standing permission, no need to ask first.

The test is the ratio: **much input, little answer.** Delegate when the work
has to read far more than it concludes.

* Searching or surveying the repository — "where is X used", "which names
  exist", "does anything still do Y". An `Explore` agent on the cheapest model
  that can read.
* Long, noisy commands whose value is a verdict: regenerating `icons/`,
  building the packs, sweeping pages with `tools/check_page.py`, a `pytest` run
  that is expected to be green.
* Bulk mechanical edits with a checkable end state — translating the comments
  of a module, a rename, a regeneration. The agent spends its context on the
  file bodies, the session gets "done, tests green".

Keep the work in the session when:

* it needs what this session already knows — a fresh agent starts cold and
  re-derives it, and a fork inherits the context but not the cheaper model,
* the result is a file that has to be read here anyway,
* it is a single grep or one short file: the spawn costs more than it saves,
* the judge is the device, the user, or a design decision.

Every brief states the shape of the answer and keeps it small: a `file:line`
list, PASS/FAIL with the failing assertion, the three numbers that decide it.
An agent that reports its whole transcript has saved nothing. The report does
not reach the user — relay what matters.

## Generated content

* `icons/` is generated by `musescore_icons.py` but **is** committed, so the
  rendered set is browsable on GitHub. Regenerate it rather than editing single
  files by hand.
* `packs/` is generated by `make_packs.py` and is **not** committed
  (see `.gitignore`). The packs are published as assets of a GitHub release.
* `index.html` in the repository root is generated by `make_pages.py` and **is**
  committed — it is the GitHub Pages entry point. Never edit it by hand; change
  the generator and re-run it. The same goes for `icons/index.html`, which
  `musescore_icons.py` writes.
* The empty `.nojekyll` file in the root must stay: without it GitHub Pages
  skips every path starting with an underscore, which would break the
  `_unnamed/` folders.
* `fonts/` holds upstream files fetched from `musescore/muse_framework`; do not
  edit them by hand.

## Look of the generated pages

Both `index.html` and `icons/index.html` use a single dark theme — white text on
a grey ground, no `prefers-color-scheme` switch. The rendered PNGs are black, so
they are displayed with `filter: invert(1)`; keep that filter on the `<img>`
only and put hover backgrounds on a wrapping element, otherwise the filter
inverts the background as well. Icon boxes never get a fixed pixel width —
`width:100%` plus `max-width` — so icons cannot grow out of their card.

## Local toolchain (mise)

The repository carries a `mise.toml`; [mise](https://mise.jdx.dev) is installed
on the development machine and the directory is trusted.

* `mise.toml` is the repository's tool list: `claude` at `latest`, `node` (which
  brings `npm`) pinned to `24` and `uv` pinned to `0.11`. Keep the toolchain
  pinned to a major — `claude` is the deliberate exception, it should follow
  upstream. Raising a pin is a change of its own, not a side effect.
* Tools that exist in the global mise installation but are **not** listed there
  (pnpm, go, …) are not on `PATH` here. Reach them either ad hoc with
  `mise exec pnpm -- pnpm --version`, or add them for good with
  `mise use <tool>` — which rewrites `mise.toml` and belongs in a commit of its
  own.
* Python for the scripts stays the system interpreter plus `.venv`, as both
  READMEs describe. If that ever moves to mise or `uv`, the install section of
  `README.md` **and** `README-de.md` changes with it.

* Reach for the toolchain you are best trained on. Installing a dependency is
  cheap; working around a missing one costs tokens, and tokens are the scarce
  resource — pytest over a hand-rolled runner, a library over a clever
  workaround. This is about the tools *you* work with. What the shipped scripts
  may import is a different question, decided under *Dependencies* below.

## Tests

Checks belong in `tests/`, not in a throwaway snippet in the session. Every
plan step that can be verified from the outside leaves its check behind, so the
next session runs one command instead of writing the check again:

    .venv/bin/python -m pytest

* pytest is the runner (`requirements-dev.txt`), configured in `pytest.ini`,
  which puts the repository root on the path — `deckgen`, `tools/` and `decks/`
  import without an installation step.
* A test that needs something the machine may not have — the Playwright
  browser, a real export in `samples/` — skips instead of failing, so a bare
  checkout still gets a meaningful run.
* Rendered output is compared by measurement: alpha bounding boxes, checksums,
  byte-identical archives. Look at a picture when a design decision needs one,
  not to confirm that a rerun still works.

## Dependencies

Keep `make_packs.py` standard-library only. `musescore_icons.py` may use the
packages listed in `requirements.txt` (fonttools, pillow) and nothing else.
`make_deck.py` renders through `musescore_icons.Renderer` and therefore
depends on those two as well — nothing beyond `requirements.txt`.

## Releasing

1. `python3 make_packs.py --clean` — rebuild the ZIP packs.
2. `gh release create <tag> packs/*.zip` — attach every pack to the release.
3. `python3 make_pages.py` — refresh the file sizes on the overview page, then
   commit the regenerated `index.html`.

The download links on the overview page use
`/releases/latest/download/<pack>.zip`, so they keep working across releases as
long as the asset names stay the same.
