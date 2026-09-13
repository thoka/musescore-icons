# MuseScore UI-Icons

Holt die Icon-Font der MuseScore-Studio-Oberfläche und rendert **für jeden Glyph
ein eigenes Icon** – als PNG (beliebige Größen) und optional als SVG,
thematisch in Unterordner sortiert.

## Quellen

| Datei | Herkunft |
|---|---|
| `fonts/MusescoreIcon.ttf` | [`musescore/muse_framework`](https://github.com/musescore/muse_framework) → `framework/ui/data/MusescoreIcon.ttf` |
| `fonts/iconcodes.h` | dasselbe Repo → `framework/ui/view/iconcodes.h` (liefert die sprechenden Namen wie `PLAY`, `NOTE_8TH`) |

Seit MuseScore Studio 4.6 liegt das UI-Framework im ausgelagerten Submodul
`muse_framework`, nicht mehr im Hauptrepo.

Die Font steht unter GPL-3.0 (MuseScore Limited). Die erzeugten Icons sind
abgeleitete Werke – bei Weitergabe gilt dieselbe Lizenz.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt     # fonttools, pillow
```

## Benutzung

```bash
.venv/bin/python musescore_icons.py all              # Download + Rendern (128 px)
.venv/bin/python musescore_icons.py fetch            # nur Font + Namen laden
.venv/bin/python musescore_icons.py render --sizes 16,24,32,48,128 --svg
.venv/bin/python musescore_icons.py list             # Glyphen + Kategorien anzeigen
```

Wichtige Optionen von `render` / `all`:

| Option | Bedeutung |
|---|---|
| `-s, --sizes 24,128` | PNG-Kantenlängen in Pixel (mehrere möglich) |
| `-c, --color "#ffffff"` | Icon-Farbe – z. B. Weiß für dunkle Oberflächen |
| `-b, --background white` | Hintergrund (Standard: transparent) |
| `-m, --margin 0.08` | Rand als Anteil der Kantenlänge |
| `--mode fit \| em` | `fit`: jeder Glyph füllt das Icon aus (Standard). `em`: Größenverhältnisse wie im Font-Design, Überstände werden nur so weit verkleinert, dass nichts abgeschnitten wird |
| `--svg` | zusätzlich saubere Vektor-SVGs (Konturen direkt aus der Font) |
| `--flat` | alles in einen Ordner statt thematisch sortiert |
| `--no-aliases` | keine Kopien für Zweitnamen desselben Codepoints |
| `--no-gallery` | keine `index.html` erzeugen |
| `--ref <tag>` | anderen Stand des Repos laden, z. B. `--ref v4.6.0` |

## Ergebnis

```
icons/
├── 128px/
│   ├── transport-playback/   PLAY.png, STOP.png, METRONOME.png …
│   ├── notes-rests-beams/    NOTE_8TH.png, TUPLET_NUMBER_ONLY.png …
│   ├── …
│   └── _unnamed/             U+F3A3.png …
├── svg/                      gleiche Struktur
├── index.html                durchsuchbare Galerie (Klick kopiert den Namen)
└── manifest.json             Name, Codepoint, Kategorie, Aliase, Dateien
```

Stand heute enthält die Font **553 Glyphen**; 397 davon haben über
`iconcodes.h` einen sprechenden Namen, der Rest landet mit seinem Codepoint
(`U+F3A3.png`) im Ordner `_unnamed` – das sind Icons, die in der Font schon
vorhanden, im Enum aber noch nicht eingetragen sind.

### Thematische Ordner

`transport-playback`, `notes-rests-beams`, `pitch-accidentals-keys`,
`articulations-ornaments`, `dynamics-expression`, `guitar-fretboard`,
`score-elements`, `layout-breaks-frames`, `lines`, `text-typography`,
`arrows-navigation`, `view-zoom`, `file-cloud-online`, `edit-tools`,
`audio-waveform`, `app-ui-status`, `shapes-misc`, `_unnamed`.

Die Zuordnung steckt in `CATEGORY_RULES` in `musescore_icons.py`: eine
geordnete Liste aus Ordnername + Regex-Mustern für den Icon-Namen, die erste
passende Regel gewinnt. Eigene Themen lassen sich dort in wenigen Zeilen
ergänzen; `list` zeigt sofort, wie sich die Verteilung ändert.

## Hinweise

* Die Namen im Dateisystem entsprechen exakt den `IconCode::Code`-Werten aus
  MuseScore – so lässt sich ein Icon direkt einer UI-Stelle zuordnen.
* Zwei Namen zeigen auf denselben Glyph (`TREMOLO_TWO_NOTES` /
  `TREMOLO_STYLE_DEFAULT`, `LYRICS` / `LEARN`); dafür werden zwei identische
  Dateien geschrieben, in `manifest.json` stehen sie als `aliases`.
* `GRADUATION_CAP` (`U+F19D`) ist im Enum definiert, in der Font aber nicht
  vorhanden, und wird deshalb übersprungen.
