---
name: merge-to-main
description: Squash-merge the current working branch into a target branch (main, or alpha while the project is unstable) as one summarized commit behind a tag, then delete the branch. Use when a branch's work is brought in — when the user asks for a merge, or when finished work collects on alpha (no confirmation needed there). The merge to main is the user's only approval-gated step.
---

# Merge to main

Work runs on a branch, never on a target branch; the user gates exactly one
step: bringing the branch in. The procedure below is the same for both
targets:

* **`main`** is the publish gate — GitHub Pages serves it, so the squash
  commit goes live on push. A plan merging here has its status `done` already.
* **`alpha`** collects finished but unproven work while the project is
  unstable. Same gate, same procedure; pushing `alpha` never goes live. A plan
  may arrive `open` and be continued from `alpha` on a new branch.

1. **Check the gate.** Nothing unfinished crosses: failing tests, an
   unfinished page, a generated file that no longer matches its generator
   (`index.html` vs `make_pages.py`, `icons/` vs `musescore_icons.py`). Run
   `.venv/bin/python -m pytest`. If the merge touches pages, verify against a
   local `python3 -m http.server` first — the site is static, so the local
   server is representative. If this closes a plan, its status in
   `docs/plans/README.md` is already `done` — tick it on the branch first if
   not.
2. **Tag the branch tip.** The tag is what keeps the individual commits
   findable once the branch is deleted — a squash orphans them without it:

        git tag merge/plan/0002-deck-generator

   The name is `merge/` plus the branch name. No leading slash (git refs
   cannot start with one); the prefix keeps tag and branch unambiguous while
   both exist.
3. **Squash-merge.**

        git switch alpha
        git merge --squash plan/0002-deck-generator
        git commit

   The commit message summarizes the branch's work — what was built and why,
   in the repo's short imperative style.
4. **Delete the branch.**

        git branch -D plan/0002-deck-generator

   Plain `-d` refuses after a squash, because the ancestry never merged;
   `-D` is safe here, the tag holds the commits.
5. **Push.** `git push origin <target> <tag>`. To `alpha` this is always
   safe — it is not served by GitHub Pages. Pushing `main` publishes, so
   only do it when the work should go live.
