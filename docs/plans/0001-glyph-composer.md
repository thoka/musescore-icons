# Glyph-Composer: Macro-Deck-Icons aus MuseScore-Glyphen

> **Für die umsetzende Session**: Dieser Plan ist als vollständige Bestellung
> gedacht. Alles hier Aufgeschriebene wurde in der Planungssession verifiziert
> (gemessen, abgerufen, nachgeschlagen) — es muss **nicht** neu recherchiert
> werden. Quellen stehen im Anhang.

## Kontext

`musescore-icons` rendert bisher **jeden Glyph einzeln** als PNG/SVG in fester
Farbe (schwarz auf transparent) und veröffentlicht das Ergebnis als GitHub-Pages
-Galerie plus ZIP-Release. Für den eigentlichen Zweck — **umfangreiche Macro
Decks für MuseScore** (Zielgerät: Macro Deck 3) — reicht das nicht:

* Icons müssen **frei koloriert** werden (Vorder-/Hintergrund, inkl. echter
  Transparenz).
* Icons müssen aus **mehreren Glyphen zusammengesetzt** werden.
* Ganze **Matrizen** sollen automatisch entstehen: Notendauer × Punktierung,
  Rhythmusfolgen usw.

Ergebnis soll ein Werkzeug auf der bestehenden Pages-Seite sein, das solche
Decks erzeugt und als Macro-Deck-Icon-Pack exportiert.

**Machbarkeit ist geklärt: ja.** Die Begründung steht in Anhang A; die
entscheidenden Punkte sind das gemeinsame Em-Quadrat aller Glyphen (upem 1024,
Advance fast durchgehend 1024) und die bereits funktionierende Auslieferung der
Font über GitHub Pages.

---

## Schritt 0 — Werkzeuge für visuelles Selbst-Feedback

**Zweck**: Der Agent soll das Ergebnis selbst *sehen*, statt Markup zu raten.
In der bisherigen Arbeit an diesem Repo war genau das die Lücke — CSS-Fehler
(überlaufende Icons, invertierter Hover-Hintergrund) fielen erst dem Menschen
auf.

**Gute Nachricht, bereits geprüft**: Auf dieser Maschine (Arch Linux unter WSL2)
liegt ein vollständig lauffähiger Headless-Browser im Playwright-Cache — **keine
Installation nötig**:

```
~/.cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell
→ "Google Chrome for Testing 149.0.7827.55", ldd: 0 fehlende Bibliotheken
```

Ebenfalls vorhanden: `chromium-1228` (voller Browser) und `firefox-1532`.
Node, npm und `uv` kommen aus **mise** und stehen in `mise.toml`, sind hier also
aktiv: `mise exec -- node --version` → v24.20.0, npm 11.19.0, uv 0.11.14. pnpm
ist global vorhanden, aber nicht eingetragen (siehe `AGENTS.md`, *Local
toolchain*) — npm genügt. **Achtung**: Die Maschine ist **Arch**, nicht Debian —
`playwright install-deps` und `apt`/`dpkg` funktionieren nicht und werden nicht
gebraucht.

Umzusetzen:

1. `tools/shot.sh` — Wrapper um den Headless-Chrome: Argumente URL + Zielpfad,
   Flags `--screenshot=<out>`, `--window-size=1280,900`, `--hide-scrollbars`,
   `--force-device-scale-factor=2`, `--virtual-time-budget=3000` (wartet auf
   Layout/Fonts). Binary per Glob `~/.cache/ms-playwright/chromium_headless_shell-*/`
   suchen, sonst `chromium-*/chrome-linux64/chrome --headless=new`.
2. `tools/check_page.py` — Playwright-Skript für das, was ein Screenshot nicht
   zeigt: Konsolenfehler, fehlgeschlagene Requests (404 auf Icons!), gezielte
   Selektor-Screenshots, und später Canvas-Pixel-Auslesen zum Vergleich mit dem
   Python-Renderer. Dafür `requirements-dev.txt` mit `playwright` anlegen und in
   `.venv` installieren — die Browser-Binaries sind schon da, es lädt also nur
   das Python-Paket. Falls Playwright eine andere Revision als 1228 erwartet und
   nachladen will: `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` und stattdessen
   `chrome-headless-shell` über `channel`/`executable_path` einhängen.
3. Lokaler Server zum Testen vor dem Push: `python3 -m http.server 8000` im
   Repo-Wurzelverzeichnis (Pages ist rein statisch, der lokale Server ist also
   repräsentativ).
4. **Abnahme von Schritt 0**: Screenshot von `http://localhost:8000/` *und* von
   `https://thoka.github.io/musescore-icons/` in den Scratchpad schreiben und
   mit dem Read-Tool ansehen. Erst wenn beide Bilder sichtbar sind, weitermachen.
5. Screenshots gehören **nicht** ins Repo — in den Scratchpad schreiben; falls
   doch ein Ordner im Repo genutzt wird, `shots/` in `.gitignore`.

### Stand: erledigt

* [x] `tools/shot.sh` — findet die `chrome-headless-shell` per Glob im
      Playwright-Cache, fällt auf `chromium-*/chrome-linux64/chrome
      --headless=new` zurück und bricht ab, wenn die Zieldatei leer bleibt.
* [x] `requirements-dev.txt` (`playwright>=1.49`) in `.venv` installiert, mit
      `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`.
* [x] `tools/check_page.py` — Konsolenfehler, fehlgeschlagene Requests,
      HTTP ≥ 400, Screenshots ganzer Seiten und einzelner Elemente, `--js` für
      spätere Canvas-Vergleiche. Exitcode 1 bei Befunden.
* [x] Lokaler Server (`python3 -m http.server 8000`) geprüft.
* [x] **Abnahme**: Screenshots von `http://localhost:8000/` und von
      `https://thoka.github.io/musescore-icons/` erzeugt und angesehen — beide
      Seiten identisch; dazu die Galerie `/icons/` lokal und live.
      `check_page.py` meldet für beide Seiten **0** Konsolenfehler und **0**
      fehlgeschlagene Requests (553 `<img>` auf der Übersicht).
* [x] Negativtest: Seite mit `console.error` und fehlendem Bild wird als
      3 Konsolenfehler + 1 fehlgeschlagener Request (HTTP 404) gemeldet,
      Exitcode 1.

Beim Umsetzen dazugelernt:

* Playwright 1.62 erwartet Browser-Revision **1234**, im Cache liegt **1228**.
  Der im Plan vorgesehene Ausweg greift: `executable_path` auf die vorhandene
  `chrome-headless-shell`, kein Nachladen. `playwright install` wird nie
  gebraucht.
* `Locator.screenshot(timeout=…)` allein wirkt nicht — ohne
  `page.set_default_timeout()` wartet ein Selektor weiter 30 s.
* Ein Selektor, der nichts trifft, ist ein Befund der Seite und wird als
  Konsolenfehler gezählt, statt das Werkzeug mit einem Traceback zu beenden.

---

## Schritt 1 — Plan im Repo ablegen (Nachverfolgbarkeit)

Diesen Plan als `docs/plans/0001-glyph-composer.md` ins Repo committen, bevor Code
entsteht, damit spätere Sessions und Dritte den Auftrag nachvollziehen können.
In `AGENTS.md` einen Verweis darauf aufnehmen. Fortschritt wird in derselben
Datei abgehakt (Checkliste je Stufe), nicht in einer separaten Notiz.

### Stand: hinfällig — war schon erledigt, bevor die Umsetzung begann

Der Schritt wurde nicht abgearbeitet, weil es nichts mehr zu tun gab:

* [x] Der Plan liegt seit `cc64c0b` („Add numbered plans folder with the glyph
      composer plan") im Repo, mit seiner Zeile in `docs/plans/README.md`.
* [x] `AGENTS.md` verweist im Abschnitt *Plans* auf `docs/plans/` und auf
      `docs/plans/README.md`, wo dieser Plan indiziert ist. Ein zusätzlicher
      Verweis auf genau diese Datei wäre eine zweite Stelle zum Pflegen —
      absichtlich weggelassen.
* [x] Die Checkliste je Stufe steht in dieser Datei (siehe Schritt 0), nicht
      in einer separaten Notiz.

Zu tun bleibt nur der Abschluss: den Status in `docs/plans/README.md` von
`open` auf `done` setzen, wenn die letzte Stufe fertig ist.

---

## Schritt 2 — Pilot zuerst (klein, entscheidet den Rest)

Der Nutzer hat das ausdrücklich so gewollt: *„in einem Piloten müssten wir
prüfen, was sich alles direkt in den Import aus der Website ziehen lässt."*
Also **vor** jedem Export-Code klären, was Macro Deck 3 tatsächlich frisst.

* `make_deck.py` (Erstfassung, ~60 Zeilen, stdlib + PIL fürs Umskalieren) baut
  aus einer Liste von Icon-Namen ein Pack-Verzeichnis:
  `ExtensionManifest.json` + `ExtensionIcon.png` + flache Icon-Dateien
  (Struktur siehe Anhang B). ZIP-Schreiben per vorhandener Logik
  `make_packs.py:write_pack`.
* Drei Testvarianten mit denselben ~10 Icons: **PNG 256 px**, **PNG 128 px**,
  **SVG**; jeweils als `.zip` und als nach `.macroPack` umbenannte Kopie.
* Zu beantworten (nur der Mensch kann das, Gerät nötig):
  1. Nimmt „Install From File" das ZIP oder nur `.macroPack`?
  2. Werden **SVG**-Dateien in einem Icon-Pack akzeptiert? (Dokumentiert ist
     SVG nur für *Plugin*-Icons, nicht für Icon-Packs — offener Punkt.)
  3. Welche Kantenlänge sieht auf dem Gerät gut aus? (512 px sind laut Issue
     #590 problematisch, ~256 px gelten als sicher.)
  4. Lässt sich ein Pack **per URL** direkt von der Pages-Seite ziehen? Wenn
     ja, kann die Seite Packs ausliefern statt nur Downloads anzubieten.
* Ergebnisse in beiden READMEs festhalten; sie bestimmen die Export-Presets in
  Schritt 5.

### Stand: gebaut — der Geraetetest bleibt beim Menschen

* [x] `make_deck.py` baut aus einer Namensliste ein Pack-Verzeichnis
      (`ExtensionManifest.json`, `ExtensionIcon.png`, flache Icon-Dateien) und
      schreibt es als `.zip` **und** als `.macroPack`-Kopie. Gezippt wird mit
      `make_packs.py:write_pack` (flach, feste Zeitstempel).
* [x] `--pilot` erzeugt die drei Varianten mit denselben 10 Icons — `PLAY`,
      `STOP`, `LOOP`, `METRONOME`, `UNDO`, `REDO`, `NOTE_QUARTER`, `NOTE_8TH`,
      `REST`, `SHARP`: `packs/macrodeck-png256`, `-png128`, `-svg`, je
      `.zip` + `.macroPack` (33,5 KB / 18,4 KB / 8,6 KB).
* [x] Sichtprüfung: Kontaktbogen beider PNG-Varianten auf dunklem Grund
      angesehen — weiss auf transparent, nichts abgeschnitten, 256 px sichtbar
      schaerfer als 128 px.
* [x] Die vier offenen Fragen stehen als Tabelle mit Stand `offen` in beiden
      READMEs; die Antworten gehoeren dort hinein, nicht in eine neue Datei.
* [x] **Geraetetest** am Macro Deck 3: Fragen 1, 2 und 4 beantwortet, die
      Tabelle in beiden READMEs steht. Frage 3 (Kantenlaenge) bleibt offen —
      getestet wurde das SVG-Pack, die PNG-Varianten warten noch auf dem Geraet.

### Ergebnis des Geraetetests

* **Frage 1 — Import**: `.zip` wird von „Install From File" angenommen.
  `.macroPack`, die Endung aus der Doku, kennt die App gar nicht; ihre Liste
  (`domain/icon-drop.util.ts`) lautet `macrodeckiconpack`, `streamdeckiconpack`,
  `tpi`, `zip`. `make_deck.py` schreibt seitdem nur noch das `.zip`.
* **Frage 2 — SVG**: ja. Das SVG-Pack importiert; `svg` steht in den
  `ICON_DROP_EXTENSIONS` neben `png`, `jpg`, `gif`, `webp`, `lottie`, `ico`,
  `icns`. Der Vorbehalt aus *Risiken* ist damit erledigt.
* **Frage 4 — per URL ziehen**: nein, aber mit einer wichtigen Ausnahme.
  Macro Deck 3 ist eine **Tauri**-App: die Rust-Shell reicht
  `WindowEvent::DragDrop` nur als **Dateipfade** weiter (`forward_drag_drop` →
  `paths`), und im Quelltext steht ausdruecklich „Tauri owns WebView
  drag-and-drop and swallows the HTML5 drop event". Ein gezogenes `<img>`
  funktioniert deshalb (der Browser legt die Bytes in eine temporaere Datei und
  gibt deren Pfad weiter), ein gezogener Link nicht — auch nicht mit dem
  Chromium-Format `DownloadURL`, das mit einer Testseite in `packs/` geprueft
  wurde. Packs gehen also den Weg herunterladen → *Install From File*.

Folgen fuer die spaeteren Stufen:

* **Schritt 4/5**: Jedes erzeugte Icon in der Vorschau muss ein echtes `<img>`
  mit Bilddaten sein — **bestaetigt**: PNG und SVG ziehen sowohl vom Server als
  auch aus einer `blob:`-URL, ein im Browser erzeugtes Icon laesst sich also
  direkt auf eine Taste ziehen. Das ist der Hauptweg fuer die Matrix: die Zellen
  muessen ohnehin einzeln an ihren Platz.
* **Name oder Bild — nie beides bei erzeugten Icons.** Der Dateiname eines
  gezogenen Bildes stammt aus seiner URL, der Inhalt aus einem erneuten Abruf
  dieser URL, der **am Service Worker vorbei** uebers Netz geht (mit einer
  Testseite geprueft: der Name `NOTE_8TH_dot1.png` kam an, das Bild nicht, und
  im Server-Log stand der 404 des Drags). `blob:`/`data:` liefern das Bild, aber
  keinen Namen — Macro Deck nennt das Icon dann „unbekannt". Der Service-Worker-
  Trick ist damit tot. Folge fuer Schritt 5: Wer Namen braucht, nimmt den
  ZIP-Export; der Direkt-Drag ist fuer einzelne Zellen gedacht, deren Name auf
  der Taste ohnehin nicht sichtbar ist.
* **Ein Drag = eine Datei.** Mehrere Dateien kann eine Webseite nicht in einem
  Zug uebergeben. Macro Deck selbst koennte es (`[multiple]="true"` am
  Icon-Picker und an der Icon-Packs-Seite, inkl. Ordnern und Pack-Archiven) —
  fuer viele Icons auf einmal bleibt also der Weg ZIP herunterladen, entpacken,
  Ordner oder Mehrfachauswahl aus dem Dateimanager ziehen.
* **Schritt 5**: Als Pack-Export genuegt ein `.zip` mit flacher Struktur; eine
  zweite Endung ist unnoetig. SVG ist als Icon-Format bestaetigt, ein
  PNG-Preset bleibt trotzdem Standard, solange Frage 3 offen ist.

Beim Umsetzen dazugelernt:

* Der Plan sah PIL nur zum **Umskalieren** der vorhandenen 128-px-PNGs vor. Das
  haette Frage 3 verfaelscht: ein aus 128 px hochgerechnetes „256er" beweist
  nichts ueber die Schaerfe auf dem Geraet. `make_deck.py` rendert deshalb
  frisch ueber `musescore_icons.Renderer` — derselbe Code, der `icons/` erzeugt,
  nur mit freier Groesse und Farbe. Damit haengt `make_deck.py` an fontTools +
  Pillow statt an der Standardbibliothek; in `AGENTS.md` vermerkt.
* Standardfarbe ist **weiss**, nicht das Schwarz der Galerie: Macro-Deck-Tasten
  sind dunkel, schwarze Icons waeren dort unsichtbar.
* `ExtensionIcon.png` bleibt auch in der SVG-Variante ein PNG — das Pack-Icon
  zeigt die Store-Liste an, nicht das Geraet.

---

## Schritt 3 — Glyph-Daten erzeugen

**Entscheidung: Pfaddaten statt Webfont.** Ein generiertes `icons/glyphs.json`
speist Canvas (`Path2D`) *und* SVG-Export aus einer Quelle, ist pixelgenau
steuerbar und umgeht Font-Ladezustände sowie browserabhängiges `fillText`.
Volumen: 571 KB rohe Pfaddaten für 555 Glyphen (~220 KB gzip) — vertretbar für
eine Werkzeugseite, Leland wird erst bei Bedarf nachgeladen.

* Neues Unterkommando `glyphs` in `musescore_icons.py`. Wiederverwenden statt
  neu schreiben (Zeilennummern siehe Anhang C): `Renderer`-Klasse mit
  `glyphset`/`hmtx`/`upem`, `SVGPathPen` (schon für den SVG-Export benutzt),
  `BoundsPen`, `load_glyphs`, `CATEGORY_RULES`.
* Ausgabe `icons/glyphs.json`:
  ```json
  { "meta": { "font": "MusescoreIcon", "upem": 1024 },
    "glyphs": { "NOTE_8TH": { "code": "U+F369", "category": "notes-rests-beams",
                              "adv": 1024, "bbox": [102,-205,922,1270],
                              "d": "M820 832Q913 699 ..." } } }
  ```
  Pfade in **Font-Einheiten** und in Font-Orientierung (y nach oben) — die
  bestehenden Einzel-SVGs kippen das per `<g transform="scale(1,-1)">`, das
  bleibt so.
* `fetch` um **Leland** erweitern: `fonts/Leland.otf` + `fonts/OFL.txt` aus
  `MuseScoreFonts/Leland`. Daraus `icons/glyphs-leland.json` mit einer
  **kuratierten Teilmenge** (Leland hat ~3000 Glyphen, das wäre zu groß):
  Namenspräfixe `note*`, `rest*`, `augmentationDot`, `flag*`, `timeSig*`,
  `articulation*`, `dynamic*`, `notehead*`. Die Glyphnamen der `post`-Tabelle
  sind bei Leland die kanonischen SMuFL-Namen — keine zusätzliche
  `glyphnames.json` nötig.
* `LICENSE` (GPL-3.0, war bisher offen) ergänzen; OFL-Hinweis für Leland in
  beide READMEs. Wichtig und geprüft: Die OFL beschränkt nur die Font-Software,
  **nicht** die damit gerenderten Bilder — die Icons bleiben frei nutzbar.

---

## Schritt 4 — Builder-Seite `builder.html`

Statische, **handgeschriebene** Seite (kein Generator), weil sie ihre Daten zur
Laufzeit aus `manifest.json` / `glyphs*.json` zieht. Dunkles Thema der
bestehenden Seiten (weiß auf grau); `filter:invert` entfällt hier, da Farben
frei wählbar sind.

* **Layer-Modell**: pro Layer `font` (musescore|leland), `glyph`, `color`
  (inkl. Alpha; „transparent" = Alpha 0), `scale`, `dx`/`dy` **in Em-Einheiten**,
  `rotate`, `mirror`. Zusätzlich Nicht-Glyph-Layer: `shape` (Kreis/Rechteck —
  für Punktierungen) und `text` (Ziffern, z. B. Triolen-3).
* **Hintergrund**: Farbe mit Alpha, Form (keine/Quadrat/abgerundet/Kreis),
  Radius, Rand. Vorschau auf Schachbrettmuster, damit Transparenz sichtbar ist.
* **Box-Modus**: `em` (gemeinsames Em-Quadrat) oder `fit` (auf die Vereinigungs-
  Bounding-Box **aller** Layer skaliert) plus Margin — exakt die Semantik, die
  `musescore_icons.py` schon als `--mode em|fit` und `--margin` hat. Reihenfolge
  ist zwingend: erst in Em-Einheiten komponieren, **dann** die Gesamt-BBox
  skalieren (Glyphen ragen über das Em-Quadrat hinaus, siehe Anhang A).
* **Flow-Modus** für Rhythmen: Layer nebeneinander statt übereinander, Abstand
  nach BBox-Breite + Lücke (nicht nach Advance — der ist bei fast allen Glyphen
  1024 und erzeugt große Löcher).
* Glyph-Picker mit Suche über Namen und Codepoint, gespeist aus `manifest.json`
  (enthält bereits `name`, `code`, `category`, `aliases`).
* Rezept als JSON speichern/laden (Datei-Download + `localStorage`).

---

## Schritt 5 — Matrix & Export

* **N Achsen** (nicht nur Zeilen × Spalten), jede Achse eine Liste benannter
  Varianten; eine Variante überschreibt Layer-Felder, fügt Layer hinzu oder
  entfernt sie. Zelle = Basis-Rezept + je eine Variante pro Achse
  (Kreuzprodukt). Live-Vorschau als Raster.
* Namensschema als Vorlage, z. B. `note-{dauer}-dot{punkt}`.
* **ZIP-Export ohne Fremdbibliothek**: ZIP-Writer in JS, nur „stored" (PNGs
  sind bereits deflate-komprimiert) — ~70 Zeilen inkl. CRC32-Tabelle, kein CDN.
* Export-Ziele: PNG in wählbaren Größen (**Default 256 px**), SVG, und das
  Macro-Deck-Pack-Layout gemäß den Pilot-Ergebnissen aus Schritt 2.

Rezept-Skizze (Format beim Umsetzen finalisieren):

```json
{ "version": 1,
  "box": { "size": 256, "mode": "fit", "margin": 0.08 },
  "background": { "color": "#00000000", "shape": "rounded", "radius": 0.12 },
  "layers": [
    { "font": "musescore", "glyph": "NOTE_8TH", "color": "#ffffff" },
    { "shape": "circle", "color": "#ffffff", "r": 0.05, "dx": 0.85, "dy": -0.1 }
  ],
  "axes": [
    { "name": "dauer", "variants": [
      { "label": "4", "set": { "layers.0.glyph": "NOTE_QUARTER" } },
      { "label": "8", "set": { "layers.0.glyph": "NOTE_8TH" } } ] },
    { "name": "punkt", "variants": [
      { "label": "0", "drop": [1] },
      { "label": "1" },
      { "label": "2", "repeat": { "layer": 1, "n": 2, "dx": 0.125 } } ] } ],
  "naming": "note-{dauer}-dot{punkt}" }
```

`dx: 0.125` ist kein geratener Wert: der Punktabstand der Font beträgt ~128
Em-Einheiten (gemessen, Anhang A).

---

## Schritt 6 — Integration & Doku

* `make_pages.py`: Link „Icon builder" in die Kopfleiste der Übersichtsseite.
* **Beide READMEs** pflegen (Regel aus `AGENTS.md`): Builder, Rezeptformat,
  Leland/OFL, Pilot-Ergebnisse.
* `AGENTS.md` ergänzen: `builder.html` ist handgeschrieben (Ausnahme zur Regel
  „`index.html` nie von Hand"), `glyphs*.json` sind generiert, `tools/` ist
  Entwickler-Werkzeug und wird nicht ausgeliefert.

---

## Betroffene Dateien

| Datei | Art |
|---|---|
| `docs/plans/0001-glyph-composer.md` | neu — dieser Plan, Schritt 1 |
| `tools/shot.sh`, `tools/check_page.py`, `requirements-dev.txt` | neu — Schritt 0 |
| `make_deck.py` | neu — Pilot-Pack, später Macro-Deck-Export |
| `musescore_icons.py` | Unterkommando `glyphs`, `fetch` um Leland erweitert |
| `builder.html` | neu — die eigentliche Anwendung |
| `icons/glyphs.json`, `icons/glyphs-leland.json` | neu, generiert |
| `fonts/Leland.otf`, `fonts/OFL.txt`, `LICENSE` | neu |
| `make_pages.py`, `README.md`, `README-de.md`, `AGENTS.md`, `.gitignore` | Ergänzungen |

## Verifikation

1. **Schritt 0 zuerst abnehmen**: Screenshots von lokal und live erzeugen und
   mit dem Read-Tool ansehen.
2. `python3 -m http.server 8000`, `builder.html` öffnen; `tools/check_page.py`
   meldet **null** Konsolenfehler und **null** fehlgeschlagene Requests.
3. **Referenzvergleich gegen den Python-Renderer**: `NOTE_8TH`, Modus `fit`,
   Margin 0.08, schwarz auf transparent, 128 px im Browser exportieren und
   gegen `icons/128px/notes-rests-beams/NOTE_8TH.png` halten. Kriterium:
   gleiche Alpha-Bounding-Box (±1 px), Deckungsgrad innerhalb ~2 % — PIL und
   Canvas kantenglätten nicht identisch, exakte Gleichheit ist kein Ziel.
4. Transparenz: Export mit Hintergrund-Alpha 0 öffnen, Alpha-Kanal außerhalb
   der Glyphen muss 0 sein.
5. Matrix: Dauer (ganz…32tel) × Punktierung (0–3) erzeugen, ZIP entpacken,
   Dateinamen und Anzahl (= Achsenprodukt) prüfen.
6. Nach jedem Push die **Live-Seite** screenshotten, nicht nur die lokale.
7. Import des Packs in Macro Deck 3 auf dem Zielgerät — der einzige Schritt,
   den nur der Mensch ausführen kann.

## Risiken

* ~~**SVG in Icon-Packs ist unbestätigt** — deshalb Pilot vor Export-Code.~~
  Erledigt: der Pilot hat SVG am Gerät bestätigt (Schritt 2).
* `glyphs.json` wächst mit Leland → kuratierte Teilmenge, Nachladen erst bei
  Auswahl der Leland-Quelle.
* Leland-Glyphnamen sind SMuFL-technisch (`restQuarter`), nicht sprechend wie
  die UI-Namen — der Picker braucht Gruppierung nach Bereich.
* Playwright-Python könnte eine andere Browser-Revision als die vorhandene
  1228 erwarten → `executable_path` explizit setzen statt neu laden.

---

# Anhang A — Gemessene Font-Fakten

Alles mit `fontTools` gegen `fonts/MusescoreIcon.ttf` gemessen:

* **upem 1024**, 556 Glyphen in der Font, 553 im Manifest, 397 davon benannt.
* Advance **fast durchgehend 1024** → gemeinsames Em-Quadrat, Überlagern ist
  ohne Ausrichtungsheuristik korrekt.

| Glyph | adv | bbox (x0,y0,x1,y1) |
|---|---|---|
| `NOTE_WHOLE` | 1024 | 282, -204, 742, 130 |
| `NOTE_HALF` | 1024 | 283, -205, 742, 1228 |
| `NOTE_QUARTER` | 1024 | 283, -205, 742, 1228 |
| `NOTE_8TH` | 1024 | 102, -205, 922, 1270 |
| `NOTE_16TH` | 1024 | 100, -205, 924, 1265 |
| `NOTE_DOTTED` | 1024 | 97, -205, 927, 1228 |
| `NOTE_DOTTED_2` | 1024 | 97, -204, 1055, 1229 |
| `NOTE_DOTTED_3` | 1024 | 1, -204, 1151, 1229 |
| `DOT_ABOVE_LINE` | 1024 | 64, 480, 960, 1024 |
| `REST` | 1024 | 336, -42, 690, 1064 |
| `REST_8TH` | 924 | 256, 64, 768, 960 |
| `TUPLET_NUMBER_ONLY` | 1024 | 231, 127, 759, 871 |

Daraus folgt:

1. **Notenköpfe liegen deckungsgleich** (`NOTE_HALF`/`NOTE_QUARTER` identisch
   x 283–742); `NOTE_8TH` ergänzt nur die Fahne. Ein Punkt-Layer sitzt damit
   über *alle* Dauern hinweg an derselben Stelle richtig.
2. **Punktabstand ≈ 128 Em-Einheiten** (927 → 1055 → 1151 bei 1/2/3 Punkten).
3. **Glyphen überschreiten das Em-Quadrat** (y bis 1270, x bis 1151) → erst
   komponieren, dann die Vereinigungs-BBox skalieren.
4. **Die Matrix braucht die Komposition wirklich**: `NOTE_DOTTED`, `_2`, `_3`,
   `_4` sind ausschließlich **Viertelnoten** mit 1–4 Punkten. Punktierte
   Achtel/16tel existieren nicht als Glyph.
5. **Grenze der UI-Font**: Noten von ganz bis 1024tel, aber nur **zwei
   Pausen** (`REST`, `REST_8TH`) → deshalb Leland.

Weitere geprüfte Fakten:

* Einzel-SVGs haben pro Glyph eine **eigene, enge viewBox**
  (`viewBox="-365.98 -1410.48 1755.95 1755.95"` bei `NOTE_8TH`) und ein
  `<g transform="scale(1,-1)">`. Sie sind daher **nicht** direkt stapelbar —
  Grund für `glyphs.json` in Font-Koordinaten.
* Pfad-`fill` ist einfarbig `#000000` → Umfärben ist ein Attribut.
* Rohe Pfaddaten aller 555 SVGs: **571 KB**.
* `https://thoka.github.io/musescore-icons/fonts/MusescoreIcon.ttf` liefert
  **HTTP 200, 177.572 Bytes, `content-type: font/ttf`**, same-origin → als
  Webfont *oder* zum Parsen nutzbar, ohne CORS-Problem.

# Anhang B — Macro Deck: Pack-Format (recherchiert)

* Icon-Pack = **flache** Struktur im Wurzelverzeichnis:
  ```
  ExtensionManifest.json
  ExtensionIcon.png
  MyIcon1.png
  SomeotherIcon.png
  ```
* `ExtensionManifest.json`-Felder: `type: "IconPack"`, `name` (nach Einreichung
  unveränderlich), `author`, `repository`, `packageId` (Format
  `DeinName.PackName`, keine Leer-/Sonderzeichen, unveränderlich), `version`
  (SemVer), `target-macro-deck-version`.
* **Lokaler Import**: Plugins-Tab → „Install From File" → im Dateidialog rechts
  „Macro Deck icon pack" auswählen.
* **Store-Einreichung**: Fork von `Macro-Deck-App/Macro-Deck-Extensions`,
  GitHub-Action „Add/Update Extension", Pull Request, Moderation.
* **Größe**: 512 px verursachen dokumentierte Probleme (Issue #590: Ordner-
  wechsel bricht bei vielen 512er-Icons); ~256–350 px gelten als unproblematisch
  → Default 256 px.
* **SVG**: für Icon-Packs **nicht dokumentiert** (belegt nur für Plugin-Icons).
  Der Nutzer geht davon aus, dass Macro Deck 3 SVG kann → im Piloten prüfen.
* Referenz-Pack zum Abgucken: `morbeckp/macro-deck-iconpack` (flache PNGs +
  `ExtensionManifest.json`).

# Anhang C — Repo-Wissen für die Umsetzung

Wiederverwendbare Stellen (Stand dieser Planung):

* `musescore_icons.py`
  * `Renderer` ab ~Z. 267: `BoundsPen` (Z. 267), `hmtx` (Z. 276),
    `glyphset` (Z. 277), `upem`; `svg()` ab Z. 330 nutzt bereits `SVGPathPen`
    (Z. 331) — das ist die Vorlage für den Pfad-Export.
  * `write_gallery` ab Z. 367 (Galerie-HTML, dunkles Thema, `cell_min`-Logik).
  * `CATEGORY_RULES` ab ~Z. 47 — geordnete Regex-Liste, erste Regel gewinnt.
  * `main()` ab Z. 566, Subparser ab Z. 595 (`fetch`, `render`, `all`, `list`).
* `make_packs.py`: `pack_name()` (Pfadelemente → Punktnamen), `write_pack()`
  (deterministisches ZIP, feste Zeitstempel `(1980,1,1,0,0,0)`), `human()`.
* `make_pages.py`: `detect_repo()` (owner/name aus `git remote`),
  `group_by_category()`, `render()`, `STYLE` (Farb-Tokens des dunklen Themas).
* `icons/manifest.json`: `meta` (font, source, upem, mode, margin, sizes,
  color, background, glyph_count, named_count) + `icons[]` mit `name`,
  `codepoint`, `glyph_name`, `category`, `named`, `aliases`, `files`, `code`.

Konventionen aus `AGENTS.md`, die gelten:

* **README.md (EN) und README-de.md (DE) immer im selben Commit ändern**,
  gleiche Gliederung, Querlinks erhalten.
* Code-Kommentare/Docstrings/argparse-Hilfen **deutsch**; Commit-Messages und
  Agentenregeln **englisch**.
* `icons/` ist generiert, wird aber committet. `packs/` ist generiert und
  **nicht** committet. `index.html` und `icons/index.html` sind generiert —
  nie von Hand editieren, immer den Generator ändern und neu laufen lassen.
* `.nojekyll` im Wurzelverzeichnis muss bleiben (sonst verwirft Pages die
  `_unnamed/`-Ordner).
* `make_packs.py` bleibt stdlib-only; `musescore_icons.py` nutzt nur
  fontTools + Pillow.
* Beide erzeugten Seiten: ein einziges dunkles Thema, `filter:invert(1)` nur
  auf dem `<img>` (nicht auf einem Element mit Hintergrund), Icon-Boxen nie mit
  fester Pixelbreite (`width:100%` + `max-width`).

# Anhang D — Quellen

* Leland (SMuFL-Notationsfont von MuseScore, **SIL OFL 1.1**):
  <https://github.com/MuseScoreFonts/Leland> — die OFL beschränkt die
  Font-Software, nicht die gerenderten Bilder.
* Macro Deck Extension Store / Pack-Struktur und Einreichung:
  <https://github.com/Macro-Deck-App/Macro-Deck-Extensions>
* Icon-Packs erstellen (Übersicht): <https://macro-deck.app/create_submit_iconpacks>
* Beispiel-Pack: <https://github.com/morbeckp/macro-deck-iconpack>
* Größenproblem ab 512 px: <https://github.com/Macro-Deck-App/Macro-Deck/issues/590>
* Import-Probleme/Format: <https://github.com/Macro-Deck-App/Macro-Deck/issues/613>
* Quell-Repo der UI-Font: <https://github.com/musescore/muse_framework>
