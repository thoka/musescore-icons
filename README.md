# MuseScore UI Icons

*[Deutsche Fassung: README-de.md](README-de.md) &middot; [Overview page](https://thoka.github.io/musescore-icons/)*

Fetches the icon font of the MuseScore Studio user interface and renders
**every glyph as a separate icon** – as PNG (any size) and optionally as SVG,
sorted into thematic subfolders.

## Sources

| File | Origin |
|---|---|
| `fonts/MusescoreIcon.ttf` | [`musescore/muse_framework`](https://github.com/musescore/muse_framework) → `framework/ui/data/MusescoreIcon.ttf` |
| `fonts/iconcodes.h` | same repository → `framework/ui/view/iconcodes.h` (provides the speaking names such as `PLAY`, `NOTE_8TH`) |

Since MuseScore Studio 4.6 the UI framework lives in the separate submodule
`muse_framework`, no longer in the main repository.

The font is licensed under GPL-3.0 (MuseScore Limited). The generated icons are
derivative works – the same license applies when redistributing them.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt     # fonttools, pillow
```

## Usage

```bash
.venv/bin/python musescore_icons.py all              # download + render (128 px)
.venv/bin/python musescore_icons.py fetch            # only fetch font + names
.venv/bin/python musescore_icons.py render --sizes 16,24,32,48,128 --svg
.venv/bin/python musescore_icons.py list             # show glyphs + categories
```

Important options of `render` / `all`:

| Option | Meaning |
|---|---|
| `-s, --sizes 24,128` | PNG edge lengths in pixels (several possible) |
| `-c, --color "#ffffff"` | icon color – e.g. white for dark interfaces |
| `-b, --background white` | background (default: transparent) |
| `-m, --margin 0.08` | margin as a fraction of the edge length |
| `--mode fit \| em` | `fit`: every glyph fills the icon (default). `em`: size relations as designed in the font, overhangs are scaled down only as far as needed so nothing gets cut off |
| `--svg` | additionally export clean vector SVGs (outlines taken straight from the font) |
| `--flat` | everything into one folder instead of thematically sorted |
| `--no-aliases` | no copies for secondary names of the same codepoint |
| `--no-gallery` | do not generate `index.html` |
| `--ref <tag>` | load a different state of the repository, e.g. `--ref v4.6.0` |

## Result

```
icons/
├── 128px/
│   ├── transport-playback/   PLAY.png, STOP.png, METRONOME.png …
│   ├── notes-rests-beams/    NOTE_8TH.png, TUPLET_NUMBER_ONLY.png …
│   ├── …
│   └── _unnamed/             U+F3A3.png …
├── svg/                      same structure
├── index.html                searchable gallery (a click copies the name)
└── manifest.json             name, codepoint, category, aliases, files
```

As of today the font contains **553 glyphs**; 397 of them have a speaking name
via `iconcodes.h`, the rest ends up with its codepoint (`U+F3A3.png`) in the
folder `_unnamed` – these are icons that already exist in the font but are not
yet listed in the enum.

### Thematic folders

`transport-playback`, `notes-rests-beams`, `pitch-accidentals-keys`,
`articulations-ornaments`, `dynamics-expression`, `guitar-fretboard`,
`score-elements`, `layout-breaks-frames`, `lines`, `text-typography`,
`arrows-navigation`, `view-zoom`, `file-cloud-online`, `edit-tools`,
`audio-waveform`, `app-ui-status`, `shapes-misc`, `_unnamed`.

The assignment lives in `CATEGORY_RULES` in `musescore_icons.py`: an ordered
list of folder name + regex patterns matched against the icon name, the first
matching rule wins. Own themes can be added there in a few lines; `list`
immediately shows how the distribution changes.

## ZIP packs

`make_packs.py` bundles every folder that contains icons into its own archive
under `packs/`. The archive name is made up of all path elements joined by
dots:

```bash
python3 make_packs.py                       # packs/icons.128px.edit-tools.zip, …
python3 make_packs.py --clean               # delete old archives beforehand
python3 make_packs.py --root icons-light --suffixes .svg
python3 make_packs.py --flat --dry-run      # files at the zip root / preview only
```

Inside the archive the files live in a folder of the same name, so several
packs can be unpacked next to each other without colliding. The script only
uses the standard library and writes with fixed timestamps, so an unchanged
icon set produces byte-identical archives. `packs/` is not checked into git.

## Macro Deck icon packs (pilot)

`make_deck.py` bundles a selection of icons into an icon pack for
[Macro Deck 3](https://macro-deck.app). The pack uses the flat structure the app
expects – manifest, pack icon and the icon files side by side in the archive
root:

```
ExtensionManifest.json      type, name, author, packageId, version …
ExtensionIcon.png           the pack icon (always PNG, 256 px)
PLAY.png  STOP.png  NOTE_8TH.png …
```

```bash
python3 make_deck.py --pilot                       # the three test variants
python3 make_deck.py --icons PLAY,STOP,NOTE_8TH    # own selection, PNG 256 px
python3 make_deck.py --icons-file my-icons.txt --format svg
```

| Option | Meaning |
|---|---|
| `--pilot` | build all three test variants (PNG 256, PNG 128, SVG) at once |
| `--icons PLAY,STOP` | icon names, comma separated (aliases work too) |
| `--icons-file <file>` | one icon name per line, `#` starts a comment |
| `-s, --size 256` | edge length in pixels (default: 256) |
| `-f, --format png \| svg` | file format of the icons inside the pack |
| `-c, --color white` | icon color – white by default, because Macro Deck keys are dark |
| `--name`, `--author`, `--version`, `--package-id` | manifest fields (`packageId` defaults to `author.PackName`) |
| `-o, --out packs` | output folder (default: `packs/`, not checked in) |
| `--keep-dir` | keep the unpacked pack folder next to the archives |

The icons are rendered **fresh from the font**, not copied out of `icons/`: a
256 px icon has to be genuinely 256 px, otherwise the size question below would
be answered with an upscaled 128 px file. Every variant is written twice, as
`.zip` and as a byte-identical `.macroPack` copy – which of the two the import
dialog accepts is one of the open questions.

### Open questions – to be answered on the device

The pilot exists to find out what Macro Deck 3 actually swallows. Only a test
on real hardware can answer this (Plugins tab → *Install From File* → pick
*Macro Deck icon pack* in the file dialog):

| # | Question | Status |
|---|---|---|
| 1 | Does “Install From File” take the `.zip`, or only `.macroPack`? | open |
| 2 | Are **SVG** files accepted in an icon pack? SVG is documented for *plugin* icons only. | open |
| 3 | Which edge length looks good on the device? 512 px causes [problems](https://github.com/Macro-Deck-App/Macro-Deck/issues/590), ~256 px is considered safe. | open |
| 4 | Can a pack be pulled **by URL** straight from the overview page? If so, the page could serve packs instead of only offering downloads. | open |

The answers decide the export presets of the icon builder, see
[`docs/plans/0001-glyph-composer.md`](docs/plans/0001-glyph-composer.md).

## Overview page (GitHub Pages)

`make_pages.py` generates the root `index.html` from `icons/manifest.json`: a
category overview with preview icons, counts and download links pointing at the
ZIP packs of the latest GitHub release.

```bash
python3 make_pages.py                       # writes index.html
python3 make_pages.py --tag v1.0.0          # link to a fixed release instead of latest
python3 make_pages.py --preview 12          # show only the first 12 icons per category
```

By default every icon of a category is shown; `--preview N` limits it to the
first N. Both pages use one dark theme (white on grey) and display the black
PNGs inverted, i.e. white.

The page is live at <https://thoka.github.io/musescore-icons/> and links to the
full searchable gallery at `icons/index.html`. The empty `.nojekyll` file at the
repository root is required — without it GitHub Pages would drop the
`_unnamed/` folders.

## Releases

The ZIP packs are attached to a GitHub release, so the download links stay
stable:

```bash
python3 make_packs.py --clean
gh release create v1.0.0 packs/*.zip --title "…" --notes "…"
```

`https://github.com/thoka/musescore-icons/releases/latest/download/icons.128px.edit-tools.zip`
always points at the newest release. After publishing a new release, run
`make_pages.py` again so the file sizes on the overview page match.

## Notes

* The names in the file system match the `IconCode::Code` values from MuseScore
  exactly – this makes it easy to map an icon to its place in the UI.
* Two names point to the same glyph (`TREMOLO_TWO_NOTES` /
  `TREMOLO_STYLE_DEFAULT`, `LYRICS` / `LEARN`); two identical files are written
  for those, and `manifest.json` lists them as `aliases`.
* `GRADUATION_CAP` (`U+F19D`) is defined in the enum but missing from the font,
  and is therefore skipped.
