---
name: release
description: Cut a release of the Macro Deck icon packs — rebuild the ZIPs, create the GitHub release with them as assets, refresh the overview page's file sizes. Use when the user asks to release, publish, or ship the packs (Release schneiden).
---

# Release

Releases are cut from `main`, after the merge brought the work in — the
release publishes what the site already shows.

1. `python3 make_packs.py --clean` — rebuild the ZIP packs.
2. `gh release create <tag> packs/*.zip` — attach every pack to the release.
3. `python3 make_pages.py` — refresh the file sizes on the overview page, then
   commit the regenerated `index.html`.

The download links on the overview page use
`/releases/latest/download/<pack>.zip`, so they keep working across releases
as long as the asset names stay the same.
