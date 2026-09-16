---
name: whats-next
description: Overview of pending work — the three drawers (active, parked, empty) from one read-only script. Use when the user asks "was steht an?", "was ist zu tun", "was ist offen", "was läuft noch", "Überblick", "Stand", "what's next", "what's pending", or at a thread start that first needs orientation about what is open.
---

# What's next

Run the overview script once and relay its three drawers:

    python3 tools/pending.py

The script is read-only: git queries plus the index table in
`docs/plans/README.md` and the entry blocks of open plans. It prints

* **Active** — the checked-out branch and, if it carries a plan, that
  plan's next step,
* **Parked** — local branches without their `merge/` tag on `alpha`
  (half-done work that blocks nothing), and
* **Open plans** — every plan the index lists `open`, with where its
  work lives (on `alpha` behind its tag, parked on a branch, or not
  started) and its next step.

Rules for the reply:

* Relay the drawers compactly; do not re-derive them from git or the
  plan files, and do not open plan files the script did not point at.
* Quote a plan's next step when the script names one — that line is the
  handoff. Open the whole plan only once the user picks that work.
* End with one recommended move — continue the active plan step, resume
  a parked branch, or plan something new — and wait for the user's
  word. This skill only reports: no merge, no checkout, no new branch on
  its own initiative.
* If the script fails, say so plainly and fall back to `git branch`,
  `git tag --list 'merge/*'` and the table in `docs/plans/README.md`.
