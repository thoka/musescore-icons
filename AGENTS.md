# Agent rules

Instructions for AI coding agents working in this repository.
Write these rules in English, even though most of the project prose is German.
The rules serve Claude sessions (Opus, Sonnet) and opencode sessions (GLM)
alike: where a capability exists on one harness only, the rule says so, and a
session that cannot act on a rule skips it without thought. Rules about this
file itself live in the `optimize-agent-rules` skill.

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

* **The user writes German; the agent thinks and answers in English.** This is
  fixed, so no reply ever starts with a language decision. Applies to
  conversation only — project prose follows the rules below.
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
* Commit a new plan on its own — the first commit on its `plan/NNNN-slug`
  branch, cut from `alpha` as soon as the plan is written. The plan file
  carries its metadata as YAML frontmatter at the top, before the title
  (`Title` in English, `Status`, `Written`); regenerate the index table with
  `python3 tools/pending.py --write-index` in the same commit.
* Tick off progress inside the plan file itself, not in a separate note. When
  the work is finished, set the plan's frontmatter `Status` to `done` and
  regenerate the table; never delete a plan and
  never reuse or renumber a number.
* Plan prose may be German like the rest of the project documentation; file
  names and the index table stay English.
* **Cutting the work into steps is Opus work, and the cut includes the model.**
  Every step says which model it is meant for — a line `Modell: Sonnet` or
  `Modell: GLM` under its heading, with a word on why when it is not obvious.
  The line names the session the step wants, not the session writing the plan;
  any harness may cut. Deciding that once, with the whole plan in view, is
  cheaper than re-deciding it in every later session. A session that runs a
  step on another model than the cut named says so in the handoff rather than
  quietly deviating — and a session with no model to choose, opencode's GLM,
  never weighs the line at all.

Work a plan step at a time, and treat each step as a session of its own: read
the step and its *Stand*, do the work, tick it off, commit, `/clear`. What that
costs is the subject of *Token efficiency* below. A thread that only wants to
know what stands open — active, parked, empty — runs `python3 tools/pending.py`
(the `whats-next` skill).

**Every plan opens with an `Einstieg` block**, directly under the
frontmatter, and the
session that finishes a step rewrites it before committing. The handoff is
written by whoever still has the context — never reconstructed by whoever
lacks it. A new thread must be able to start from that block alone, without
searching the repository first. Five entries, no prose:

* *Stand* — branch, the subject of the last commit, what works and what does
  not.
* *Nächster Schritt* — number, title, and the model from the cut.
* *Lesen* — the three to five paths the step actually needs, with line ranges
  where a file is long, plus the appendix that holds the measurements. Naming
  what is *not* needed is worth a line: it is what keeps the next session from
  reading the whole package.
* *Laufen lassen* — the commands that establish the state (`pytest`, the
  generator, the local server) and what their output should look like.
* *Offen* — what only the device or the user can decide.

If the repository has moved past the block, the code wins and the block gets
corrected on the spot.

**Branches are pragmatic, not ceremonial** — a mental separation of the work
at hand, nothing more. Development is single-track: there are no parallel
features, so there is never a "right branch" to work out. The whole model is
two questions:

* **At session start — is the checked-out branch mine for this task?** If yes,
  stay on it. If no, cut a fresh one from `alpha`: a plan gets its
  `plan/NNNN-slug` branch when the plan is committed (the plan commit is its
  first commit, so plans never stack), work without a plan gets a branch named
  after the work. Never start from another feature branch and never from
  `main`; work that builds on half-done work happens on that work's branch
  instead of dragging its commits across. A research branch, should one ever
  be needed, is simply created. Spend no thought on the choice.
* **After a merge — does the branch have its squash commit and tag on
  `alpha`?** Then it is disposable: the merge procedure deletes it, and nothing
  is lost, because the squash carries the whole diff and the tag keeps the
  individual commits findable. Any follow-up — a bug in an earlier plan noticed
  while working on a later one, a plan that arrived on `alpha` still `open` —
  starts as a new branch from `alpha`, never by resurrecting the old one. A
  branch without its tag yet is parked work: it blocks nothing and waits until
  its work is collected.

**Work never lands on a target branch**: `alpha` and `main` receive work only
through the merge procedure, and the procedure runs only when the user asks
for it — both targets, every time. On a feature branch the session acts
freely — commits, tests, regenerations — but it does not merge on its own
initiative; when it believes a branch is ready to collect, it says so and
waits for the user's word ("merge it", "bring it in").

Finished work collects on `alpha`; `main` takes only what is proven. Both
targets are updated with the same squash procedure behind a tag — the steps
live in the `merge-to-main` skill (`.claude/skills/merge-to-main/SKILL.md`):

* **`alpha`** collects finished but unproven work — on the user's request,
  never automatically. It is not served by GitHub Pages, so nothing goes
  live, but the merge still rewrites how `alpha` reads — and the device
  may be mid-test on an earlier import. A plan may arrive here still
  `open` and be continued from `alpha` on a new branch.
* **`main`** is the publish gate: GitHub Pages builds from `main` at `/`, so
  everything pushed to `main` is live at once. An unfinished page, or a
  generated file that no longer matches its generator, does not belong there.
  When `alpha` has proven itself, merging it to `main` is the publication
  step. A plan that crosses to `main` has its status `done` already.
* Verify a branch against a local `python3 -m http.server` when the merge
  touches pages. The site is static, so the local server is representative; the
  live page gets its screenshot after the merge to `main`.
* Regenerate `icons/` **once** per branch, in the last commit before the merge.
  It is a large committed tree and repeated rebuilds only produce conflicts.
* Infrastructure that is not part of a plan — agent rules, `.gitignore`,
  `mise.toml` — takes the same route as everything else: to `alpha`, or
  straight to `main` when the push should go live.

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
* **A warm thread is cheap; a fresh one is small.** Reading this session's own
  history again costs a fraction of reading it the first time — the cache makes
  continuing cheaper than it looks. A new thread is cheaper still in a
  different way: it reads the plan step and three files instead of the whole
  transcript. What is expensive is full price for context nobody needs: a long
  thread dragged into unrelated work, or a cache thrown away for nothing.
* **A step does not start on the wrong model — and `/model` mid-thread is not
  how that gets fixed.** The cached prefix belongs to the model that wrote it,
  so switching makes the next request re-read the entire thread at full price
  on the new model. That is a one-off toll, repaid only if a long stretch of
  cheap work follows. So there are three moves, not two:
  * **carry on** when the rest of the step is short. A warm cache on the big
    model beats a cold start on the small one, and mid-step the answer is
    almost always this one.
  * **delegate** when the work fits in a brief with a checkable end state (see
    *Subagents*). The agent starts small on the model it needs, and it costs
    the user no keystroke.
  * **cut the thread** when a long stretch of cheap work lies ahead: finish the
    commit, name the model the next step wants, and let the user start it fresh
    — `/clear` or a new session, with the plan file as the handoff.

  The decision therefore belongs at a step boundary, where the context is small
  and the cut costs nothing. Which is why the model is part of the cut (see
  *Plans*): by the time the question comes up mid-step, it is usually too late
  to be worth it. Working a long, obviously cheap step on the expensive model
  without saying anything remains the mistake this rule is about. Where the
  harness offers no model to switch — opencode runs GLM alone — the toll
  cannot arise: carry on, delegate, or cut, and never weigh a model.

### Subagents

A subagent keeps its tool output in its own context and hands back a report;
in Claude it can also be given a smaller model — a lever the session pulls
without the user, and the only such lever. opencode's GLM has a single model,
but the context saving remains. **Use one whenever the saving is likely** —
this section is the standing permission, no need to ask first.

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
  (see `.gitignore`). The packs are published as assets of a GitHub release;
  the `release` skill walks through publishing.
* `decks/*.py` are ordinary scripts against the library; each writes a
  `packs/<name>.macroDeckFolder` (not committed either). Do not verify a
  regenerated deck by re-parsing the artifact: the tests cover the generator
  (`tests/test_rhythm.py` reads its combos back from `rhythm.DOTTINGS`), so
  the check is *change the constant → pytest → regenerate* — the file on disk
  follows from the code.
* `index.html` in the repository root is generated by `make_pages.py` and **is**
  committed — it is the GitHub Pages entry point. Never edit it by hand; change
  the generator and re-run it. The same goes for `icons/index.html`, which
  `musescore_icons.py` writes.
* The empty `.nojekyll` file in the root must stay: without it GitHub Pages
  skips every path starting with an underscore, which would break the
  `_unnamed/` folders.
* `fonts/` holds upstream files fetched from `musescore/muse_framework`; do not
  edit them by hand.
* The index table in `docs/plans/README.md` is generated by
  `tools/pending.py --write-index` from the plans' frontmatter, between the
  `<!-- table:begin -->` / `<!-- table:end -->` markers. Never edit it by
  hand — change the frontmatter and regenerate.

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

Building on other projects' work is welcome; **"no dependencies" is an
anti-pattern here, not a virtue.** Reach for an established library before
hand-rolling — a hand-rolled parser, archive writer or format subset is a
maintenance cost, not an achievement. The discipline that comes with it:

* A dependency is declared before it is imported: `requirements.txt` for
  runtime, `requirements-dev.txt` for development. When that changes how a
  checkout is set up, the install section of `README.md` **and**
  `README-de.md` changes with it.
* A new dependency says in its commit which library it chose and why — the
  weigh-in happens once, in writing, not silently in the code.
