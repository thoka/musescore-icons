# MuseScore UI Icons

*[Deutsche Fassung: README-de.md](README-de.md)*

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

## Notes

* The names in the file system match the `IconCode::Code` values from MuseScore
  exactly – this makes it easy to map an icon to its place in the UI.
* Two names point to the same glyph (`TREMOLO_TWO_NOTES` /
  `TREMOLO_STYLE_DEFAULT`, `LYRICS` / `LEARN`); two identical files are written
  for those, and `manifest.json` lists them as `aliases`.
* `GRADUATION_CAP` (`U+F19D`) is defined in the enum but missing from the font,
  and is therefore skipped.
