# MuseScore UI-Icons

*[English version: README.md](README.md) &middot; [Uebersichtsseite](https://thoka.github.io/musescore-icons/)*

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

## ZIP-Pakete

`make_packs.py` buendelt jeden Ordner, der Icons enthaelt, in ein eigenes
Archiv unter `packs/`. Der Archivname besteht aus allen Pfadelementen,
verbunden mit Punkten:

```bash
python3 make_packs.py                       # packs/icons.128px.edit-tools.zip, …
python3 make_packs.py --clean               # alte Archive vorher loeschen
python3 make_packs.py --root icons-light --suffixes .svg
python3 make_packs.py --flat --dry-run      # Dateien in der ZIP-Wurzel / nur anzeigen
```

Im Archiv liegen die Dateien in einem gleichnamigen Ordner, damit sich mehrere
Pakete nebeneinander auspacken lassen. Das Skript braucht nur die
Standardbibliothek und schreibt feste Zeitstempel – ein unveraenderter
Icon-Satz ergibt also bitgleiche Archive. `packs/` wird nicht eingecheckt.

## Macro-Deck-Icon-Pakete (Pilot)

`make_deck.py` buendelt eine Auswahl von Icons zu einem Icon-Pack fuer
[Macro Deck 3](https://macro-deck.app). Das Pack hat die flache Struktur, die
die App erwartet – Manifest, Pack-Icon und die Icon-Dateien nebeneinander in der
Archivwurzel:

```
ExtensionManifest.json      type, name, author, packageId, version …
ExtensionIcon.png           das Pack-Icon (immer PNG, 256 px)
PLAY.png  STOP.png  NOTE_8TH.png …
```

```bash
python3 make_deck.py --pilot                       # die drei Testvarianten
python3 make_deck.py --icons PLAY,STOP,NOTE_8TH    # eigene Auswahl, PNG 256 px
python3 make_deck.py --icons-file meine-icons.txt --format svg
```

| Option | Bedeutung |
|---|---|
| `--pilot` | alle drei Testvarianten auf einmal bauen (PNG 256, PNG 128, SVG) |
| `--icons PLAY,STOP` | Icon-Namen, kommagetrennt (Aliase funktionieren auch) |
| `--icons-file <Datei>` | ein Icon-Name je Zeile, `#` leitet einen Kommentar ein |
| `-s, --size 256` | Kantenlaenge in Pixel (Standard: 256) |
| `-f, --format png \| svg` | Dateiformat der Icons im Pack |
| `-c, --color white` | Icon-Farbe – weiss als Standard, weil Macro-Deck-Tasten dunkel sind |
| `--name`, `--author`, `--version`, `--package-id` | Manifest-Felder (`packageId` ist standardmaessig `Autor.PackName`) |
| `-o, --out packs` | Zielordner (Standard: `packs/`, nicht eingecheckt) |
| `--keep-dir` | das entpackte Pack-Verzeichnis neben den Archiven behalten |

Die Icons werden **frisch aus der Font gerendert**, nicht aus `icons/` kopiert:
ein 256-px-Icon muss echte 256 px haben, sonst waere die Groessenfrage unten mit
einer hochskalierten 128-px-Datei beantwortet. Jede Variante wird doppelt
geschrieben, als `.zip` und als bitgleiche `.macroPack`-Kopie – welches von
beiden der Import-Dialog annimmt, ist eine der offenen Fragen.

### Offene Fragen – am Geraet zu beantworten

Der Pilot existiert, um herauszufinden, was Macro Deck 3 tatsaechlich frisst.
Das kann nur ein Test an echter Hardware klaeren (Plugins-Tab → *Install From
File* → im Dateidialog *Macro Deck icon pack* auswaehlen):

| # | Frage | Stand |
|---|---|---|
| 1 | Nimmt „Install From File“ das `.zip` oder nur `.macroPack`? | offen |
| 2 | Werden **SVG**-Dateien in einem Icon-Pack akzeptiert? Dokumentiert ist SVG nur fuer *Plugin*-Icons. | offen |
| 3 | Welche Kantenlaenge sieht auf dem Geraet gut aus? 512 px macht [Probleme](https://github.com/Macro-Deck-App/Macro-Deck/issues/590), ~256 px gelten als sicher. | offen |
| 4 | Laesst sich ein Pack **per URL** direkt von der Uebersichtsseite ziehen? Wenn ja, kann die Seite Packs ausliefern statt nur Downloads anzubieten. | offen |

Die Antworten bestimmen die Export-Voreinstellungen des Icon-Builders, siehe
[`docs/plans/0001-glyph-composer.md`](docs/plans/0001-glyph-composer.md).

## Uebersichtsseite (GitHub Pages)

`make_pages.py` erzeugt aus `icons/manifest.json` die `index.html` im
Wurzelverzeichnis: eine Kategorie-Uebersicht mit Vorschau-Icons, Zahlen und
Download-Links auf die ZIP-Pakete des neuesten GitHub-Releases.

```bash
python3 make_pages.py                       # schreibt index.html
python3 make_pages.py --tag v1.0.0          # auf ein festes Release verlinken
python3 make_pages.py --preview 12          # nur die ersten 12 Icons je Kategorie
```

Standardmaessig zeigt die Seite alle Icons einer Kategorie; `--preview N`
begrenzt auf die ersten N. Beide Seiten nutzen ein einziges dunkles Thema
(weiss auf grau) und stellen die schwarzen PNGs invertiert, also weiss, dar.

Die Seite liegt unter <https://thoka.github.io/musescore-icons/> und verlinkt
die vollstaendige, durchsuchbare Galerie in `icons/index.html`. Die leere Datei
`.nojekyll` im Wurzelverzeichnis ist noetig – ohne sie wuerde GitHub Pages die
`_unnamed/`-Ordner unterschlagen.

## Releases

Die ZIP-Pakete haengen an einem GitHub-Release, damit die Download-Links stabil
bleiben:

```bash
python3 make_packs.py --clean
gh release create v1.0.0 packs/*.zip --title "…" --notes "…"
```

`https://github.com/thoka/musescore-icons/releases/latest/download/icons.128px.edit-tools.zip`
zeigt immer auf das neueste Release. Nach einem neuen Release `make_pages.py`
erneut laufen lassen, damit die Dateigroessen auf der Uebersichtsseite stimmen.

## Hinweise

* Die Namen im Dateisystem entsprechen exakt den `IconCode::Code`-Werten aus
  MuseScore – so lässt sich ein Icon direkt einer UI-Stelle zuordnen.
* Zwei Namen zeigen auf denselben Glyph (`TREMOLO_TWO_NOTES` /
  `TREMOLO_STYLE_DEFAULT`, `LYRICS` / `LEARN`); dafür werden zwei identische
  Dateien geschrieben, in `manifest.json` stehen sie als `aliases`.
* `GRADUATION_CAP` (`U+F19D`) ist im Enum definiert, in der Font aber nicht
  vorhanden, und wird deshalb übersprungen.
