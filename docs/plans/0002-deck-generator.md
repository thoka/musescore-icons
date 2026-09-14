# Deck-Generator: vollständige Macro-Deck-Ordner erzeugen

## Einstieg

* **Status**: branch `plan/0002-deck-generator`. Steps 1–4 done and accepted
  on the device (2026-09-14); 140 tests green. Step 5 was re-scoped by the
  user the same day and moved to plan 0003 (`0003-workbench.md`) — this plan
  keeps only the original brief above, deferred.
* **Next step**: step 6, integration and documentation — after plan 0003
  lands; its text already names the generators, not a builder.
* **Read**: whatever step 6 touches — both READMEs, `AGENTS.md`,
  `make_pages.py`.
* **Run**: `.venv/bin/python -m pytest` — 140 tests green.
* **Open**: whether step 6 waits for plan 0003 or runs first — the user
  decides.

> **Für die umsetzende Session**: Alles unter *Entschieden* und in den Anhängen
> wurde im Piloten von Plan 0001 am Gerät verifiziert — gemessen, importiert,
> gegengeprüft. Es muss nicht neu recherchiert werden.

## Kontext

Plan 0001 sollte Icons liefern; der Pilot hat gezeigt, dass das der falsche
Liefergegenstand ist. Ein Icon-Pack füllt die Bibliothek, danach muss **jede
Taste einzeln im Raster zugeordnet** werden — bei einer Matrix aus Dauern und
Punktierungen ist das die eigentliche Arbeit, und sie bleibt am Menschen hängen.

Der Gegenbeweis liegt vor: Ein von Hand gebautes `.macroDeckFolder` wurde von
Macro Deck 3 importiert und funktionierte. In dieser einen Datei stecken Icons,
Beschriftungen, Farben, Positionen **und** Tastenkürzel. Das Ziel ist deshalb
nicht mehr ein Icon-Satz, sondern ein **Deck-Generator**: aus Glyphen und einem
Rhythmus-Gedanken entsteht ein fertiger Ordner, der einmal importiert wird.

Die Anatomie des Formats steht in Anhang A, die Befunde des Piloten in Anhang B.

---

## Entschieden (nicht neu diskutieren)

1. **Bibliothek, keine Konfigurationssprache.** Decks entstehen aus Python-Code
   gegen eine Bibliothek. Eine Matrix *ist* eine Schleife; in YAML gegossen wäre
   sie nur eine schlechtere Schleife. Kein YAML (neue Abhängigkeit), kein TOML
   (die Standardbibliothek kann es nur lesen, nicht schreiben). **JSON** kommt
   erst dann, wenn die Builder-Seite ein Rezept hin- und herschicken muss —
   Browser und `json` sprechen es von sich aus.
2. **SVG ist die Icon-Quelle**, bestätigt am Tablet-Client. Damit entfällt die
   Frage nach der Kantenlänge.
3. **Das Archiv trägt aber WebP** (Anhang A). Der Komponist braucht deshalb
   **zwei Backends aus demselben Layer-Modell**: SVG-Text für Vorschau,
   Icon-Packs und die Webseite, PIL-Bild für die WebP-Dateien im Archiv. Ein
   SVG-Rasterizer in Python wäre eine neue Abhängigkeit und ist unnötig — die
   Glyphen lassen sich mit Pillow direkt zeichnen, wie `musescore_icons.py` es
   längst tut.
4. **Drei Schichten, klar getrennt**: Komposition (weiß nichts von Macro Deck) —
   Archiv (weiß nichts von Glyphen) — Generatoren (verbinden beides). Die
   Webseite wird später ein weiterer Generator, kein Sonderweg.
5. **Namen sind kein Problem mehr.** In einem erzeugten Archiv setzen wir
   `icons[].name` selbst. Das „unbekannt" aus dem Drag-Weg betrifft uns nicht.

---

## Schritt 1 — Archiv-Schicht

Neues Paket `deckgen/`, Modul `deckgen/archive.py`. Schreibt ein
`.macroDeckFolder` nach Anhang A.

* Primitiven: `Folder(name, rows, columns)`, `Button(label, icon, background,
  label_position, icon_display, on_press)`, `IconLibrary.add(name, image)`,
  `folder.place(button, x, y, w=1, h=1)`, `folder.write(path)`.
* `IconLibrary.add` nimmt ein PIL-Bild, schreibt `master.webp` (1024) sowie
  128/256/512, rechnet die SHA-256-Summen und legt den Icon-Datensatz an.
* Manifest und `content.json` werden vollständig selbst erzeugt; ZIP-Schreiben
  mit festen Zeitstempeln wie in `make_packs.py:write_pack`, damit ein
  unveränderter Lauf ein bitgleiches Archiv ergibt.
* `deckgen/actions.py`: `PressKey(key, modifiers=(), target="MuseScore4",
  repeat=1)` erzeugt den `flows`-Block.
* **Gemessen**: Ein `flows`-Parameter braucht nur `name`, `type` und `value`.
  Ein Archiv, aus dem alle 102 Beschreibungsfelder entfernt wurden, liess sich
  importieren und die Taste loeste weiter aus. `press_key` ist damit ein paar
  Zeilen statt einer Vorlagensammlung.

### Stand: erledigt

* [x] `deckgen/actions.py` — `press_key` und `change_folder`, Auslöser
      `onShortPress`, Integrationsliste fürs Manifest (`app.macro-deck.deck`
      steht bewusst nicht darin, es ist eingebaut).
* [x] `deckgen/archive.py` — `Deck`, `Folder`, `Button`, `IconLibrary`;
      schreibt `manifest.json`, `content.json` und die WebP-Stufen.
* [x] `deckgen/glyphs.py` — Glyph als PIL-Bild oder SVG, über
      `musescore_icons.Renderer`.
* [x] **Strukturvergleich** eines erzeugten Archivs gegen den echten Export:
      Manifest, `contents`, Datei-Einträge, Ordner, Widget, Icon, Flow und Block
      haben dieselben Felder. Einziger Unterschied sind die weggelassenen
      Parameter-Beschreibungen — genau die, die der Importeur nicht braucht.
* [x] **Prüfsummen** stimmen, und zwei Läufe ergeben ein **bitgleiches** Archiv
      (feste Zeitstempel, GUIDs über `uuid5` aus den Namen abgeleitet).
* [x] **Abnahme am Gerät**: `packs/deckgen-smoke.macroDeckFolder` importiert und
      funktioniert — zwei Ordner, Navigation hin und zurück, drei Dauern-Tasten
      lösen in MuseScore aus. Die Archiv-Schicht ist damit fertig.

## Schritt 2 — Komposition: Glyphen zu Icons

`deckgen/compose.py` plus `deckgen/glyphs.py`. Das Layer-Modell aus Plan 0001,
Schritt 4, aber ohne Webseite drumherum.

* Layer: `Glyph(name, color, scale, dx, dy)` in **Em-Einheiten**, dazu
  `Shape` (Kreis/Rechteck, für Punktierungen) und `Text` (Ziffern, Tuplets).
* Box-Modus `em` oder `fit` plus Margin — dieselbe Semantik wie
  `musescore_icons.py --mode`.
* **Flow-Modus**: Layer nebeneinander statt übereinander, Abstand nach
  BBox-Breite plus Lücke (nicht nach Advance — der ist bei fast allen Glyphen
  1024 und risse Löcher). Das ist die Grundlage für Rhythmusfolgen.
* Zwei Backends, ein Modell: `to_svg()` und `to_image(size)`.
* Pfaddaten für das SVG-Backend: Unterkommando `glyphs` in `musescore_icons.py`,
  das `icons/glyphs.json` schreibt (Plan 0001, Schritt 3 — unverändert gültig,
  inklusive Leland als späterer Quelle für Pausen und SMuFL-Zeichen).

### Stand: Komposition steht und ist gegengemessen (Text-Layer offen)

* [x] `deckgen/compose.py` — `Composition` mit Layern in Em-Koordinaten:
      `Glyph` (Name, Farbe, `scale`, `dx`, `dy`) und `Dot` (Radius), dazu
      `dots(n)` für Punktierungen im gemessenen Abstand von 0.125 em.
* [x] Box-Modi `fit` und `em` mit Margin über die Vereinigungs-Bounding-Box
      aller Layer — erst komponieren, dann skalieren.
* [x] **Flow-Modus**: Layer nebeneinander, Abstand nach Tintenbreite plus Lücke.
      Das ist die Grundlage für die Rhythmusfolgen aus Schritt 4.
* [x] Beide Backends aus einem Modell: `to_image()` (Pillow, für die
      WebP-Stufen) und `to_svg()` (Pfade direkt aus fontTools).
* [x] **Abgleich der Backends** — `tools/compare_backends.py` rendert elf
      Rezepte über beide Wege und vergleicht die Alpha-Bounding-Boxen
      (Verifikation, Punkt 3). Das SVG rastert der Headless-Chrome aus Plan
      0001, Schritt 0: ein lokaler HTTP-Server liefert die Dateien aus (über
      `file://` verweigert `getImageData` die Auskunft), der Browser zeichnet
      sie ins Canvas und misst die Box. **Ergebnis: alle elf Fälle innerhalb
      1 px**, bei 256, 512 und 1024 px Kantenlänge — beide Box-Modi,
      Skalierung, Verschiebung, Punkte und Flow. Als Test liegt derselbe
      Vergleich in `tests/test_compose.py`; ohne Browser wird er übersprungen.
* [ ] `Text`-Layer (Ziffern, etwa die 3 einer Triole) — noch nicht gebaut.
* [ ] `rotate` und `mirror` aus Plan 0001 — bewusst weggelassen, bis eine Zelle
      sie braucht.

Beim Umsetzen dazugelernt:

* `icons/glyphs.json` wird für den **Python**-Weg nicht gebraucht: fontTools
  liefert die Pfade direkt, Pillow zeichnet die Glyphen. Die Datei gehört damit
  zu Schritt 5, wo der Browser sie zieht, weil er keine Font parsen soll — nicht
  zu Schritt 2.
* Skaliert wird um die **Mitte des Em-Quadrats**, nicht um den Ursprung: so
  bleibt ein verkleinerter Layer dort sitzen, wo er im Entwurf steht.
* Der Abstand der Punkte stammt aus der Messung in Plan 0001, Anhang A
  (`NOTE_DOTTED` → `_2` → `_3`: 927, 1055, 1151 Em-Einheiten).
* Der Vergleich braucht Fälle, in denen der geprüfte Rechenweg überhaupt
  sichtbar wird: `dx`/`dy` verschiebt einen **einzelnen** Layer nicht im Bild,
  weil der Ausschnitt einfach mitwandert, und der Zweig `em` greift nur bei
  einem Glyph, der ins Em-Quadrat passt (`NOTE_HEAD_QUARTER`, nicht
  `NOTE_QUARTER`).

## Schritt 3 — Erster Generator: Dauer × Punktierung

`decks/rhythm.py` — ein gewöhnliches Python-Skript, das die Bibliothek benutzt.

* Achse 1: Notendauern von ganz bis 1/32. Achse 2: 0 bis 2 Punkte.
* Jede Zelle: komponiertes Icon, Beschriftung, Hintergrundfarbe nach Dauer,
  Aktion `PressKey` mit dem MuseScore-Kürzel.
* Ergebnis ist ein importierbares `.macroDeckFolder`, das der Nutzer am Gerät
  abnimmt. **Erst danach** geht es weiter — wie im Piloten entscheidet das
  Gerät, nicht die Theorie.

### Stand: erledigt — zweifach abgenommen

* [x] `decks/rhythm.py` — 6 Spalten (ganz bis 1/32) × 3 Zeilen (0 bis 2 Punkte)
      = 18 Tasten, jede mit komponiertem Icon, Farbe nach Dauer und
      Tastenfolge. `--labels` schreibt die Dauer zusätzlich als Text,
      `--svg ORDNER` legt dieselben Icons als SVG ab.
* [x] `packs/rhythmus.macroDeckFolder` erzeugt: 74 Dateien, alle Prüfsummen des
      Manifests stimmen, Raster lückenlos belegt, zwei Läufe **bitgleich**.
* [x] `tests/test_rhythm.py` — Raster, Tastenfolge je Zelle (Dauer zuerst,
      Punktierung danach), Icons, Beschriftungen, Zielprozess, Bitgleichheit.
* [x] **Abnahme am Gerät** (2026-09-14): importiert, Tasten in MuseScore
      ausgelöst, Notenbild geprüft — **funktioniert**. Ein Befund: ab 1/16
      überlappen die Punktierungen mit der Fahne.
* [x] **Befund behoben** (2026-09-14): Punktsitz je Note gemessen —
      `Renderer.clear_x` (Kerning auf kleinem Raster: Tinte um den
      Punktradius dilatieren, verbotenen Bereich auf der Punkthöhe ablesen),
      `compose.dot_dx` setzt den Punkt dahinter. Der 8tel-Kopf endet bei
      0.54 em, sein Punkt rückt von 0.82 auf 0.65; 16tel/32tel hinter die
      Fahne (≈0.99/1.0). Dazu **gemeinsame Skala** für alle Zellen
      (`Composition(side=..., anchor="note")` statt Zellen-fit): die
      Notenkoepfe bleiben so gross, wie die Font sie zeichnet (~456
      Einheiten), die Punkte bleiben Rechtsanhang. 67 Tests.
* [x] **Zweitimport am Gerät** (2026-09-14): Punkte frei der Fahne, Koepfe
      gleich gross — abgenommen.

Dabei geklärt, weil es sich nur am Gerät entscheidet:

* **Double dotting.** MuseScore ships no default shortcut for it.
  Acceptance result: `:` (Shift+`.` on a German keyboard) did **not** arrive
  at the device; `,` — a plain key, no modifier — did. The shortcut now sits
  on `,` and the third row sends exactly that. Still open is whether a
  shift shortcut could be reached via `modifiers: ["shift"]` with
  `key: "."`; this deck no longer needs one.
* **Beschriftung.** Der echte Export kennt nur `labelPosition: "center"`, also
  Text **über** dem Icon. Am Gerät geprüft: lesbar.
* **Größenverhältnis.** Erste Abnahme akzeptierte den Zellen-fit; der
  Nutzer wollte danach gleiche Notenkoepfe ("Verhaeltnisse wie in der Font"),
  deshalb jetzt gemeinsame Skala ueber alle Zellen mit Note-Anker — die
  erste Abnahme galt nur den Ueberlappungen, der Zuschnitt faellt unter die
  Zweitimport-Frage.

## Schritt 4 — Notations-Schicht und Rhythmus-Patterns

**Modell: Sonnet** — Parser und Generator gegen die stehende Bibliothek. Opus
nur, falls die ABC-Teilmenge neu zugeschnitten werden muss.

Die Zwischendarstellung ist der Grund, warum diese Schicht existiert: Aus
*einer* Analyse fallen **Bild und Tastenfolge**.

```
"c8 c8 c4"  ->  [{dur:8}, {dur:8}, {dur:4}]  ->  Icon:   drei Glyphen im Flow
                    (Zwischendarstellung)     ->  Aktion: Tastenfolge an MuseScore
```

* `deckgen/notation.py`: Ereignisliste als Zwischendarstellung, dazu ein Parser
  für die **Rhythmus-Teilmenge von ABC** (Dauern, Punkte, Pausen, Bindebögen,
  Tuplets, Taktstriche). ABC deshalb, weil es die Notation ist, die auch
  HedgeDoc rendert (abcjs) — der Nutzer schreibt sie ohnehin.
* Aus derselben Liste: Icon über den Flow-Modus, Aktion als Folge von
  `PressKey` (Dauerntaste, dann Notentaste).
* Zweiter Generator `decks/patterns.py` mit einer Handvoll typischer Figuren.

### Stand: done — accepted on the device, one deliberate leftover (Text layer)

* [x] `deckgen/notation.py` — the rhythm subset of ABC into an event list:
      notes a-g (`c8` = an eighth; a bare letter = a quarter), rests `z`
      with the same value syntax, dotting up to two dots (`.` singly, `,`
      as the double-dot command — the device binding from step 3), ties
      (validated: same letter, the next event no rest), n-lets `(3`..`(9`
      over the next n events, barlines `|` as structure markers. Anything
      else: a `ParseError` naming the spot.
* [x] One list, two outputs: `composition()` lays the glyphs out in flow
      mode (rests map to `REST`/`REST_8TH` — the font has nothing finer;
      n-let notes run at scale 0.85 with the font's digit
      `TUPLET_NUMBER_ONLY` above the group; the tie glyph `NOTE_TIE`
      hangs between the notes); `actions()` types the figure into note
      entry — Ctrl+n, then per event the duration key, the dot key, the
      note key or `0` for a rest. Ties send no key: MuseScore ships no
      default and none is proven on the device.
* [x] `decks/patterns.py` — 12 figures ("Halbe" through "Taktende"), one
      button each, grid 4x3, one shared scale across the deck (step 3's
      lesson), `--labels`/`--svg` as in `decks/rhythm.py`.
      `packs/figuren.macroDeckFolder` written: 12 buttons, 12 icons, two
      runs bit-identical (test).
* [x] `tests/test_notation.py`, `tests/test_patterns.py` — the plan
      example as the normative parse case, the subset's rejections, the
      layer and key tables, grid and wiring per button (expected keys
      rebuilt by hand, not through `notation.actions`), bit-identity,
      shared frame. 138 tests in all.
* [x] **Device acceptance** — import `packs/figuren.macroDeckFolder`,
      fire a triplet (Ctrl+3), a sextuplet (Ctrl+6) and a rest (0) in
      MuseScore, look at the icons (triplet digit, rests hanging high —
      a fact of the font). **Accepted 2026-09-14**: the re-import with the
      display fix (zoom 100, label size 8 at the bottom) works, the
      shortcuts fire — "works, good enough" is the user's verdict, no
      correction needed.
* [ ] The `Text` layer from step 2 stays open — the triplet digit
      borrows `TUPLET_NUMBER_ONLY`; n-lets beyond 3 go without a number.
      Leftover by choice, non-blocking.

First device feedback (2026-09-14): the label sits on the notes and is too
dominant (it only points to the definition), and the notes are too small on
the button. Measured cause: the shared frame is driven by the widest figure
("Sechzehntel", 6.86 em — note head ≈ 7 px on a 128 stage), and the button
shows the icon at the export's default `icon_zoom: 70`. The fix is decided
with the user; nothing is trimmed or wrapped — the icons keep showing every
event. For the record: the WebP ladder stays as measured (rendered once at
1024, 128/256/512 derived by LANCZOS; which stage the client serves is the
app's choice).

* [x] `deckgen/notation.py` — tuplet notes back to scale 1.0: `TUPLET_SCALE`
      and its branch in `composition()` go away, all notes render equal;
      `TUPLET_NUMBER_ONLY` stays the group marker. The sextuplet (≈4.95 em
      at scale 1.0) stays under the width driver (6.86 em), so equal
      scaling costs no size.
* [x] `decks/patterns.py` — the display levers as named constants **and**
      argparse flags, so device iterations need no commits: `--zoom`
      (default 100, was the implicit 70; Button.icon_zoom), `--font-size`
      (default 8, was 14), `--label-position` (default `"bottom"`, was
      "center").
* [x] `tests/test_notation.py` — the two scale-0.85 assertions become 1.0;
      `tests/test_patterns.py` gains a wiring test that `font_size`,
      `label_position` and `zoom` land in the button data (read like the
      target-process test), plus one that the levers are `build()`
      parameters.
* [x] Plan update and `packs/figuren.macroDeckFolder` regenerated in the
      same commit (12 buttons, measured: zoom 100, fontSize 8,
      labelPosition "bottom"); re-import on the device decides the values
      — if the combination collides (zoom 100 label band) or "bottom" is
      dropped, the user's tuned export file supplies the real values.

## Schritt 5 — Builder-Seite als weiterer Generator

### Stand: zurückgestellt — das Thema zieht um

The user re-scoped this step on 2026-09-14: Python only for now. The board
system that came out of the discussion — menu strip, region routines, the
workbench deck — has its own, short plan: `0003-workbench.md`. The builder
page stays a possible later step: hand-written `builder.html`, dark theme,
fed by `icons/manifest.json` and `icons/glyphs.json` (the `glyphs`
subcommand for it is unbuilt so far), exporting SVG/ZIP or — if the browser
WebP path (`canvas.toBlob('image/webp')`) proves out — a whole
`.macroDeckFolder`; single cells remain draggable (Anhang B).

## Schritt 6 — Integration und Dokumentation

**Modell: Sonnet** — beschreiben, was steht.

* **Beide READMEs** um den Generator ergänzen (Regel aus `AGENTS.md`).
* `AGENTS.md`: `deckgen/` ist Bibliothek, `decks/` sind Generatoren, `samples/`
  enthält unversionierte Exporte vom Gerät.
* `make_pages.py`: Hinweis auf die Generatoren in der Kopfleiste.

### Stand: offen

---

## Betroffene Dateien

| Datei | Art |
|---|---|
| `deckgen/archive.py`, `actions.py`, `compose.py`, `glyphs.py`, `notation.py` | neu — die Bibliothek |
| `decks/rhythm.py`, `decks/patterns.py` | neu — Generatoren |
| `tools/compare_backends.py` | neu — misst beide Backends gegeneinander |
| `musescore_icons.py` | Unterkommando `glyphs`, `fetch` um Leland erweitert |
| `icons/glyphs.json` | neu, generiert |
| `builder.html` | neu — Schritt 5 |
| `README.md`, `README-de.md`, `AGENTS.md`, `make_pages.py` | Ergänzungen |

## Verifikation

Alles, was ohne Gerät nachprüfbar ist, liegt als Test in `tests/` und läuft mit
`.venv/bin/python -m pytest` — Punkt 1 bis 3 dieser Liste sind dort abgedeckt
(`test_archive.py`, `test_compose.py`, `test_rhythm.py`). Punkt 4 bleibt beim
Menschen.

1. Round-Trip: erzeugtes Archiv importieren, Tasten zählen, Icons ansehen.
2. Bitgleichheit: zweimal erzeugen ergibt dasselbe Archiv.
3. Icon-Vergleich: komponiertes SVG gegen das PIL-Bild derselben Zelle — gleiche
   Alpha-Bounding-Box (±1 px). Exakte Gleichheit ist kein Ziel, die
   Kantenglättung unterscheidet sich.
4. Gerät: Deck importieren, eine Taste in MuseScore auslösen, Dauer prüfen.
5. Seiten wie bisher mit `tools/check_page.py` gegen lokal **und** live.

## Risiken

* **Formatversion 2, App im Beta-Stand** (`3.0.0-beta.4`). Ein Formatwechsel
  bricht den Generator. Gegenmittel: Anhang A hält den gemessenen Stand fest,
  und `samples/` bewahrt einen echten Export zum Abgleich.
* **`flows`-Metadaten** könnten Pflicht sein (Schritt 1).
* **WebP aus Pillow** muss der App genügen — Farbraum und Alpha prüfen.
* **ABC-Teilmenge** wächst leicht ins Uferlose. Nur Rhythmus, keine Tonhöhen,
  bis ein Deck damit steht.
* **Verovio** (echter Notensatz mit Leland, SVG-Ausgabe) ist der Ausbauweg,
  wenn Glyphenreihen nicht mehr reichen — bewusst **nicht** eingeplant: mehrere
  MB WASM, und auf einer 1×1-Taste sind Notenlinien vermutlich unleserlich.

---

# Anhang A — Anatomie eines `.macroDeckFolder` (gemessen)

Aus einem Export von Macro Deck `3.0.0-beta.4`, in `samples/` abgelegt:

```
manifest.json    formatVersion 2, kind "Folder", appVersion, createdAt,
                 includesSecrets, contents{...}, encryption null,
                 files[] mit {path, sha256: "sha256:<hex>", size}
content.json     kind, profile, folders[], widgets[], icons[], scripts[],
                 secrets[], variables[]
icons/<guid>/    master.webp, 128.webp, 256.webp, 512.webp
```

* **Keine Signatur.** Ein von Hand gebautes Archiv mit selbst gerechneten
  SHA-256-Summen wurde importiert und funktionierte.
* `folders[0]`: `id`, `name`, `parentId`, `order`, `rows`, `columns`,
  `backgroundColor`, `widgetSpacing`, `widgetBorderRadius`, `createdAt`.
* `widgets[]`: `id`, `type: "ActionButton"`, `positionX`, `positionY`, `width`,
  `height`, `isPinned`, `data` — und `data` ist **JSON in einem String**:

  ```json
  { "label": "1/16",
    "icon": { "type": "icon-pack", "reference": "<icon-guid>" },
    "iconDisplay": { "fit": "contain", "zoom": 70, "offsetX": 0,
                     "offsetY": 0, "opacity": 100 },
    "backgroundColor": "#ef4444", "fontSize": 14, "textAlign": "center",
    "labelPosition": "center", "border": { "style": "off" },
    "stateMode": false,
    "flows": "<wieder JSON in einem String>" }
  ```

* `flows`: Liste von Auslösern (`triggerId: "onShortPress"`) mit `children` aus
  Aktionsblöcken. Ein Tastendruck an MuseScore:

  ```json
  { "blockType": "app.macro-deck.keyboard.press-key",
    "integrationId": "app.macro-deck.keyboard", "actionId": "press-key",
    "parameters": [ { "name": "combo",
                      "value": { "modifiers": [], "key": "3" } },
                    { "name": "repeat", "value": 1 },
                    { "name": "targetProcess", "value": "MuseScore4" },
                    { "name": "targetMode", "value": "focus-send" } ] }
  ```

  Im Export tragen die Parameter zusätzlich ihre komplette Beschreibung
  (`label`, `description`, `required`, `min`, `max`, …). Ob der Importeur das
  braucht, ist der Messpunkt aus Schritt 1.
* `icons[]`: `id`, `name`, `width`, `height`, `isAnimated`, `frameCount`,
  `sourceContentHash`, `fileContentHashes{master,128,256,512}`, `checksum`,
  `originalFileName`, `originalFormat` (`"Svg"`), `availableSizes`.
  Die Quelldatei selbst liegt **nicht** im Archiv — nur die WebP-Stufen.
* **Navigation**: `app.macro-deck.deck.change-folder` mit dem Parameter
  `folderId` (`type: "dynamic-choice"`). Unterordner haengen ueber `parentId`
  am Elternordner, `order` gibt die Reihenfolge, und **jeder Ordner hat sein
  eigenes Raster** (`rows`/`columns`) — eine Matrix darf pro Seite anders gross
  sein. Die Integration `app.macro-deck.deck` erscheint **nicht** in der
  Integrationsliste des Manifests; sie ist eingebaut.
* MuseScore-Kürzel: `3` ist 1/16 (aus dem Export belegt). Das übrige Schema
  (1 = 1/64 … 7 = ganze Note, `.` setzt den Punkt) folgt der MuseScore-Doku und
  ist beim Umsetzen zu prüfen.

# Anhang B — Was der Pilot bewiesen hat (Plan 0001, Schritt 2)

* `.zip` wird von „Install From File" angenommen; `.macroPack` aus der Doku
  kennt die App nicht. Pack-Archive sind `macrodeckiconpack`,
  `streamdeckiconpack`, `tpi`, `zip`.
* **SVG** ist als Icon-Format akzeptiert und sieht auf dem Tablet-Client am
  besten aus.
* Macro Deck 3 ist eine **Tauri**-App: Drops liefern der Oberfläche nur
  **Dateipfade**. Ein gezogenes `<img>` funktioniert (der Browser materialisiert
  es), ein gezogener Link nicht, auch nicht mit `DownloadURL`.
* Ein gezogenes, im Browser erzeugtes Bild kommt **ohne Namen** an; über den
  Pack-Weg bleibt der Name erhalten. In einem erzeugten Archiv setzen wir ihn
  ohnehin selbst.
* Ein Drag trägt **eine** Datei. Macro Decks eigene Ziele nehmen mehrere
  (`[multiple]="true"`, auch Ordner und Pack-Archive).

# Anhang C — Quellen

* Macro Deck (Quelltext, Tauri + Angular + .NET-Host):
  <https://github.com/Macro-Deck-App/Macro-Deck>
  * Drop-Weiterleitung: `ui/bootstrapper/src/bridge.rs` (`forward_drag_drop`)
  * akzeptierte Endungen: `ui/angular/.../domain/icon-drop.util.ts`
  * Archivformate: `host/src/MacroDeckHost.Application/Portable/`
  * HTTP-API: `host/src/MacroDeckHost/Api/Controllers/` (u. a.
    `ProfilesController`, `IconsController`, `FoldersController`)
* ABC-Notation und abcjs: <https://docs.abcjs.net/overview/abc-notation>
* Verovio (Notensatz nach SVG, Leland): <https://www.verovio.org/>
* Leland (SMuFL-Font, SIL OFL 1.1): <https://github.com/MuseScoreFonts/Leland>
