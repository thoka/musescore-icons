# Deck-Generator: vollständige Macro-Deck-Ordner erzeugen

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
* **Zu klären, mit Messung**: Wie viel Parameter-Beiwerk braucht ein `flows`-
  Eintrag wirklich? Im Export steht die komplette Parameter-Beschreibung der
  Integration (Label, Beschreibung, Validierung, Defaults). Test: aus dem
  Round-Trip-Archiv alles bis auf `name` und `value` entfernen und erneut
  importieren. Geht es durch, wird `PressKey` ein Dreizeiler; sonst braucht es
  je Aktion eine Vorlage, die aus einem Export stammt.

### Stand: offen

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

### Stand: offen

## Schritt 3 — Erster Generator: Dauer × Punktierung

`decks/rhythm.py` — ein gewöhnliches Python-Skript, das die Bibliothek benutzt.

* Achse 1: Notendauern von ganz bis 1/32. Achse 2: 0 bis 2 Punkte.
* Jede Zelle: komponiertes Icon, Beschriftung, Hintergrundfarbe nach Dauer,
  Aktion `PressKey` mit dem MuseScore-Kürzel.
* Ergebnis ist ein importierbares `.macroDeckFolder`, das der Nutzer am Gerät
  abnimmt. **Erst danach** geht es weiter — wie im Piloten entscheidet das
  Gerät, nicht die Theorie.

### Stand: offen

## Schritt 4 — Notations-Schicht und Rhythmus-Patterns

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

### Stand: offen

## Schritt 5 — Builder-Seite als weiterer Generator

Die Seite aus Plan 0001 wird die Oberfläche derselben Primitiven, nicht eine
zweite Implementierung.

* `builder.html`, handgeschrieben, dunkles Thema, speist sich aus
  `icons/manifest.json` und `icons/glyphs.json`.
* Erzeugt dasselbe Rezept als **JSON**; der Export im Browser schreibt entweder
  Icons (SVG, ZIP) oder — sobald der WebP-Weg im Browser steht
  (`canvas.toBlob('image/webp')`) — gleich ein `.macroDeckFolder`.
* Einzelne Zellen bleiben per Drag direkt auf eine Taste ziehbar (bewiesen,
  Anhang B); für ganze Decks ist der Import die bessere Antwort.

### Stand: offen

## Schritt 6 — Integration und Dokumentation

* **Beide READMEs** um den Generator ergänzen (Regel aus `AGENTS.md`).
* `AGENTS.md`: `deckgen/` ist Bibliothek, `decks/` sind Generatoren, `samples/`
  enthält unversionierte Exporte vom Gerät.
* `make_pages.py`: Hinweis auf den Generator und den Builder in der Kopfleiste.

### Stand: offen

---

## Betroffene Dateien

| Datei | Art |
|---|---|
| `deckgen/archive.py`, `actions.py`, `compose.py`, `glyphs.py`, `notation.py` | neu — die Bibliothek |
| `decks/rhythm.py`, `decks/patterns.py` | neu — Generatoren |
| `musescore_icons.py` | Unterkommando `glyphs`, `fetch` um Leland erweitert |
| `icons/glyphs.json` | neu, generiert |
| `builder.html` | neu — Schritt 5 |
| `README.md`, `README-de.md`, `AGENTS.md`, `make_pages.py` | Ergänzungen |

## Verifikation

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
