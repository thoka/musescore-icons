---
name: merge-to-main
description: Squash-merge the current working branch into main as one summarized commit behind a tag, then delete the branch. Use when the user asks to merge to main or bring the branch's work into main — this is the user's only approval-gated step.
---

# Merge to main

Work runs on a branch, never on `main`; the user gates exactly one step:
bringing the branch into `main`. `main` is what GitHub Pages serves, so the
squash commit goes live on push.

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

       git switch main
       git merge --squash plan/0002-deck-generator
       git commit

   The commit message summarizes the branch's work — what was built and why,
   in the repo's short imperative style.
4. **Delete the branch.**

       git branch -D plan/0002-deck-generator

   Plain `-d` refuses after a squash, because the ancestry never merged;
   `-D` is safe here, the tag holds the commits.
5. **Push if the work should go live.** `git push origin main <tag>` — until
   then the squash sits locally.
