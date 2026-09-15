# 0005 — Macro Deck → MuseScore plugin bridge

Status: **open** · Written: 2026-09-15

## Einstieg

* **Stand** — Branch `plan/0004-board-layout` (unrelated work; 0005 files are
  extra). Present and uncommitted: `docs/musescore-fernsteuerung.md`,
  `docs/action-codes.md`, `tools/extract_actions.py`. MuseScore source clone at
  `.opencode/external/MuseScore` (v4.7.4, commit `7688c00`, ~794 MB,
  gitignored; re-clone command in `tools/extract_actions.py` docstring). No
  code for 0005 exists yet. Target host: MuseScore 4.7.4 on Windows 11 (WSL is
  the dev side only).
* **Nächster Schritt** — Schritt 1 (Probe-Plugin schreiben), Modell: Sonnet.
* **Lesen** — this file (Einstieg + Hintergrund + Schritt 1);
  `docs/musescore-fernsteuerung.md` §1.5, §4, §6. The `*.cpp/h` paths listed
  in *Hintergrund* only when a claim must be re-verified;
  `docs/action-codes.md` only as a lookup, never read whole.
* **Laufen lassen** — `python3 tools/extract_actions.py .opencode/external/MuseScore docs/action-codes.md`
  must print `548 actions` (rerun only after a MuseScore version bump);
  `.venv/bin/python -m pytest` is expected green (nothing in the generator was
  touched).
* **Offen** — commits need the user's go (0005 file + the three doc/tool files
  each on their own branch per convention); running MuseScore and Macro Deck
  only works on the Win11 host (user); `makeUri` for legacy plugin URIs not
  yet read; XHR/QProcess probe results pending (Schritt 2).

## Hintergrund: verifizierte Fakten (4.7.4, Quelltext)

The plugin engine is the **extensions** module. Legacy QML plugins (header
properties `menuPath`, `pluginType`, `requiresScore`, …) are loaded by
`src/framework/extensions/internal/legacy/extpluginsloader.cpp` and run by
`extpluginrunner.cpp`. New-style extensions use `manifest.json`
(fields documented in `src/framework/extensions/extensionstypes.h:189+`;
`type: macros|form|composite`, per-action `func`, default `main`).

1. **Plugin actions are first-class actions.** Every plugin action becomes a
   `UiAction` and is registered (`extensionsuiactions.cpp:49-70`,
   `extensionsactioncontroller.cpp:45-57` → `uiActionsRegister()->reg()` and
   `dispatcher()->reg()`). Therefore they
   - appear in the Shortcuts editor (it lists
     `uiactionsRegister()->actionList()`, see
     `src/framework/shortcuts/qml/Muse/Shortcuts/shortcutsmodel.cpp:102-107`),
   - pass the validation of `shortcuts.xml` imports (the register check
     accepts them), i. e. **they are bindable to F13–F24 keys like any
     built-in command**.
   This corrects the earlier claim in the Fernsteuerung report (§4, now fixed).
2. **Action code format** — `extensionstypes.h:156-187`: scheme `action` plus
   an `action` parameter → `action://<uri>?action=<func>`; legacy plugins get
   a single action with code `main` (`extpluginsloader.cpp:273-280`); the
   `<uri>` part comes from `makeUri(rootPath, path)` (`:161`,
   implementation not yet read — *Offen*). The Shortcuts editor **Export**
   writes the real codes, which is the empirical shortcut to get them.
3. **Shortcut context** — `extensionstypes.h:76-88`: default
   `project-opened`; a plugin with `requiresScore: false` gets `any`
   (`extpluginsloader.cpp:255-262`).
4. **A plugin can drive everything** — `PluginAPI::cmd(s)` maps a few MS3
   names and then dispatches **any** action code
   (`src/engraving/api/v1/qmlpluginapi.cpp:408-425`). Full score access via
   `curScore`, selection, cursor, `readScore`/`writeScore`
   (`qmlpluginapi.h:100-555`).
5. **A plugin can leave the sandbox** — `QProcess` (class `MsProcess :
   public QProcess`) is registered as a QML type
   (`qmlpluginapi.cpp:203`, `util.h:127`, `util.cpp:273-284`); QML can connect
   to its signals, so a spawned helper's stdout is a push channel into the
   plugin.

## Die vier Wege (grundlegende Überlegungen)

| Weg | Trigger-Kette | Komplexe Logik | Status |
|---|---|---|---|
| **A: Taste → Plugin-Aktion** | Macro Deck Keyboard-Integration → F13–F24 → `shortcuts.xml`-Eintrag → Plugin-Aktion → `cmd()`-Kette | im Plugin (QML/JS) | funktioniert heute, kein Fokus-Problem (Shortcut-Kontext) |
| **B: HTTP-Brücke** | Macro-Deck-C#-Plugin (oder „Programm ausführen“) POST → lokaler Queue-Server; Dock-Plugin polled per `Timer` + `XMLHttpRequest` → `cmd()` | im Plugin | Probe nötig (XHR im Plugin? Dock-Plugin resident?) |
| **C: QProcess-Brücke** | Macro Deck → helper process (z. B. Python/PowerShell) → stdout-Zeilen → `readyReadStandardOutput` → `cmd()` | im Plugin + Helper | Probe nötig (Signals in QML, Prozess-Lebensdauer) |
| **D: MCP** | Macro-Deck-C#-Plugin als MCP-Client → TCP 2212 (`rcontrol`) → Action-Code direkt | im Plugin (Trigger per Code) | Zukunft — erst wenn ein Release `rcontrol` ausliefert |

B bewegt keine Tasten und braucht keinen Fokus; A ist am wenigsten
invasiv und deckt den Großfall ab. C ist der Fallback, falls B an der
QML-Sandbox scheitert. D macht A/B/C für den Trigger überflüssig, nicht die
Plugin-Logik.

## Schritte

### Schritt 1 — Probe-Plugin schreiben

Modell: Sonnet (kleine, mechanische QML-Arbeit mit klarem Prüfplan).

Zwei Plugin-Varianten nach `docs/musescore-fernsteuerung.md` §2/§6 Fakten
bauen (Repo-Ordner `probes/0005/`):

1. `macros`-Plugin: `onRun` führt eine `cmd()`-Kette aus (z. B.
   `note-input`, drei Noten, `escape`) und schreibt eine Logzeile.
2. `dock`-Plugin (minimal, unsichtbar): `Timer` (250 ms) + `XMLHttpRequest`
   GET `http://127.0.0.1:54930/next`; bei Treffer `cmd(code)`; zusätzlich ein
   `QProcess`-Start eines `powershell`-Echo-Helfers und Auswertung von
   `readyReadStandardOutput`.

Dazu: Vorlage-`shortcuts.xml` mit Bindung `F13` → Plugin-Aktion (Code-Format
`action://<uri>?action=main`; echten Code empirisch aus dem Shortcuts-Editor-
Export übernehmen, sobald Schritt 2 ihn liefert).

Abhaken wenn: beide Dateien stehen, Anleitung im Plan verlinkt.

### Schritt 2 — Messung am Win11-Host

Modell: Sonnet (Auswertung der Logdateien); Ausführung nur durch den Nutzer.

Am Host: Plugins installieren (`%LOCALAPPDATA%\MuseScore\MuseScore4\Plugins`
bzw. Home → Plugins), Shortcuts-Editor prüfen (Aktion sichtbar? Code?),
`shortcuts.xml` importieren, F13 drücken, Log prüfen; beim Dock-Plugin XHR- und
QProcess-Pfade aus dem Log lesen.

Abhaken wenn: für A/B/C je ein PASS/FAIL + der echte Action-Code notiert sind
(hier im Plan).

### Schritt 3 — Weg-Entscheidung

Modell: Opus (Design-Schnitt mit allen Messdaten im Kontext).

Weg A/B/C (+ D als Ausblick) festlegen; daraus Schritt 4 schneiden und
weitere Pläne (Deck-Generator 0002) verdrahten.

### Schritt 4 — Implementierung

Modell: je nach Weg; Default Sonnet.

Kurzfristig unabhängig davon: `decks/*.py` um einen Generator-Zweig erweitern,
der die `shortcuts.xml` (F13–F24-Schema) aus den Deck-Definitionen erzeugt —
das zahlt auf jedem Weg ein.

## Messdaten

*(Schritt 2 trägt hier ein: Action-Codes, PASS/FAIL je Weg, Logauszüge.)*
