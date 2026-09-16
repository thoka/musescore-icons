#!/usr/bin/env python3
"""Overview of pending work: what stands open, what is parked, what is next.

Read-only. Looks at three places and reports them as three drawers:

* **Active** -- the checked-out branch and, if it carries a plan, the
  plan's next step from its entry block.
* **Parked** -- local branches (other than ``alpha``/``main``) that have
  no ``merge/<branch>`` tag on ``alpha`` yet: half-done work that is
  waiting and blocks nothing.
* **Open plans** -- every plan the index in ``docs/plans/README.md``
  lists as ``open``, with where its work lives (on ``alpha`` behind a
  merge tag, parked on a branch, or not started) and its next step.

Stdlib only; the only side effects are git queries.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLANS_INDEX = REPO / "docs" / "plans" / "README.md"
TARGETS = {"alpha", "main"}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, check=True, capture_output=True, text=True
    ).stdout.strip()


def local_branches() -> list[str]:
    return git("for-each-ref", "refs/heads", "--format=%(refname:short)").splitlines()


def merge_tags() -> set[str]:
    return set(git("tag", "--list", "merge/*").splitlines())


def last_commit(branch: str) -> str:
    return git("log", "-1", "--format=%h %cs %s", branch)


def short(text: str, limit: int = 160) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if not text[limit].isspace():
        cut = cut.rsplit(" ", 1)[0]
    return cut + " …"


ROW = re.compile(
    r"^\| (\d{4}) \| \[([^]]+)\]\(([^)]+)\) \| (\S+) \| (\d{4}-\d{2}-\d{2}) \|",
    re.M,
)


def plans_index() -> list[dict[str, str]]:
    rows = []
    for m in ROW.finditer(PLANS_INDEX.read_text(encoding="utf-8")):
        rows.append(
            {
                "num": m.group(1),
                "title": m.group(2),
                "file": m.group(3),
                "status": m.group(4),
                "written": m.group(5),
            }
        )
    return rows


ENTRY = re.compile(r"^\* \*\*(.+?)\*\*\s*[:—–-]\s*(.*)$")


def entry_entries(block: str) -> dict[str, str]:
    """Parse the ``* **Label**: text`` entries of a plan's entry block.

    Labels vary between plans (``Stand``/``Status``, ``Next step``/
    ``Nächster Schritt``); a continuation line joins its entry.
    """
    entries: dict[str, str] = {}
    label: str | None = None
    lines: list[str] = []
    for line in block.splitlines():
        m = ENTRY.match(line)
        if m:
            if label is not None:
                entries[label] = short(" ".join(lines))
            label = m.group(1).strip()
            lines = [m.group(2)]
        elif label is not None:
            lines.append(line)
    if label is not None:
        entries[label] = short(" ".join(lines))
    return entries


def entry_block(text: str) -> str:
    """The plan's entry section (``## Entry`` or ``## Einstieg``)."""
    m = re.search(r"^## (?:Einstieg|Entry)\s*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def next_step_key(entries: dict[str, str]) -> str | None:
    for label in entries:
        low = label.lower()
        if "next" in low or "schritt" in low:
            return label
    return None


def plan_path(plan: dict[str, str]) -> Path:
    return PLANS_INDEX.parent / plan["file"]


def plan_next(plan: dict[str, str]) -> str | None:
    """The plan's next step, or None when the file is not on this checkout."""
    path = plan_path(plan)
    if not path.exists():
        return None
    entries = entry_entries(entry_block(path.read_text(encoding="utf-8")))
    key = next_step_key(entries)
    return entries[key] if key else None


def branch_plan_num(branch: str) -> str | None:
    m = re.search(r"(\d{4})", branch)
    return m.group(1) if m else None


def main() -> int:
    current = git("rev-parse", "--abbrev-ref", "HEAD")
    dirty = git("status", "--porcelain").splitlines()
    branches = [b for b in local_branches() if b not in TARGETS]
    tags = merge_tags()
    index = {p["num"]: p for p in plans_index()}

    print("== Active")
    state = "dirty: " + ", ".join(dirty) if dirty else "clean"
    print(f"branch {current} ({state})")
    num = branch_plan_num(current) if current not in TARGETS else None
    if num and num in index:
        nxt = plan_next(index[num])
        if nxt:
            print(f"  plan {num} next: {nxt}")
        else:
            print(f"  plan {num} carries no next step")
    elif current in TARGETS:
        print("  on a target branch — no work happens here; cut a branch first")

    parked = [b for b in branches if f"merge/{b}" not in tags]
    print(f"\n== Parked ({len(parked)} branches without their merge/ tag)")
    for branch in parked:
        mark = ""
        num = branch_plan_num(branch)
        if num and num in index:
            if index[num]["status"] == "done":
                mark = f" (plan {num} is done — stale leftover?)"
            else:
                mark = f" (plan {num}, {index[num]['status']})"
        elif num:
            mark = f" (plan {num} not indexed in docs/plans/README.md)"
        print(f"  {branch:<28} {last_commit(branch)[:96]}{mark}")
    if not parked:
        print("  none")

    open_plans = [p for p in index.values() if p["status"] == "open"]
    print(f"\n== Open plans ({len(open_plans)})")
    for plan in open_plans:
        branch = f"plan/{plan['num']}-"
        tagged = any(t.startswith(f"merge/plan/{plan['num']}-") for t in tags)
        if any(b.startswith(branch) for b in branches):
            where = "parked on its branch (see above)"
        elif tagged:
            where = "on alpha behind its merge/ tag — continue from alpha"
        else:
            where = "not started — no branch, no tag"
        print(f"  {plan['num']} {plan['title']:<55} {where}")
        nxt = plan_next(plan)
        if nxt:
            print(f"      next: {nxt}")
    if not open_plans:
        print("  none")

    pending = len(parked) + len(open_plans)
    if pending:
        print(f"\npending: {len(parked)} parked branches, {len(open_plans)} open plans")
    else:
        print("\nnothing pending — the drawer is empty; plan something new or stop")
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except subprocess.CalledProcessError as exc:
        print(
            f"git failed ({exc.returncode}): {exc.stderr.strip()}",
            file=sys.stderr,
        )
        code = 1
    raise SystemExit(code)
