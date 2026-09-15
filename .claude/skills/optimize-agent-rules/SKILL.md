---
name: optimize-agent-rules
description: Use when reviewing, optimizing, or extending the agent rules (AGENTS.md, Agentenregeln überarbeiten) — hunting contradictions, decisions the rules leave open, or content that belongs in a skill. Also when writing a new skill that carries rules out of AGENTS.md.
---

# Optimizing the agent rules

`AGENTS.md` is loaded into every session, so every line in it costs every
session. Its purpose is not completeness but absence of deliberation: a
question a session would otherwise think about — which branch, which
language, which model — is answered once, in writing.

## The review

Read the file in full; a rules review is the one read that pays for itself.
Hunt for:

* **Open decisions.** Anywhere an agent would have to weigh options that
  repeat ("which branch", "which language", "commit here or there"), the rule
  answers outright. If it cannot, the question goes to the user — once.
* **Contradictions and drift.** Sections must not disagree. `AGENTS.md` also
  summarizes what the skills and `docs/plans/README.md` say in detail; re-read
  those in the same pass and fix drift in either direction.
* **Stale status.** Time-dependent facts ("`main` is frozen", "the project is
  unstable") do not belong in standing rules; they live in a plan's *Stand* or
  `Einstieg` block. A rule stays true across states and names the test
  ("served by GitHub Pages") rather than the state.
* **Capability, not identity.** The rules serve Claude (Opus, Sonnet) and
  opencode (GLM) sessions alike. A rule must let a session tell from itself
  whether it applies: where a capability exists on one harness only, the rule
  says so, and the session without it skips the rule without thought.
* **Behavior is not a rule.** Git history shows what happened, not what was
  meant; a rule derived from unclarified behavior persists the confusion.
  When practice is unclear or contradicts the intended rule, ask the user —
  once — and write the answer, not the anecdote.
* **Language.** Rules are written in English (a rule in the file itself); the
  user writes German and gets English replies. New rules follow suit.

## What lives where

`AGENTS.md` carries what every session needs — language, generated content,
tests, token efficiency — plus a one-line pointer to every skill. Move into a
skill when all three hold:

1. The content matters only in a specific situation (releasing, merging,
   cutting a new plan from scratch).
2. It is long enough to matter per session — more than a few lines.
3. A description can trigger on the user's actual words. The user writes
   German, so descriptions carry the English terms the user uses alongside
   German; skill bodies are English.

## Procedure

1. List findings; fix them in one pass.
2. Sync the summaries against the skills and `docs/plans/README.md`.
3. Land the change as one commit (message in English). A new skill gets its
   own directory under `.claude/skills/` with frontmatter `name` and
   `description`.
4. Report what changed and why, and flag every decision the rules now make
   that the user has not explicitly approved.
