# MuseScore fernsteuern: Tasten zuweisen für Macro Deck

*Stand: 14.09.2026. Untersucht gegen MuseScore Studio 4.7.5 (veröffentlicht
08.09.2026) und den Entwicklungszweig `main` von MuseScore bzw.
[muse_framework](https://github.com/musescore/muse_framework) (Sep 2026) sowie
den Hauptzweig von [Macro Deck 3](https://github.com/Macro-Deck-App/Macro-Deck).*

Zielumgebung in diesem Projekt: **MuseScore Studio 4.7.4 läuft auf dem
Windows-11-Host** (64-bit, x86_64), die Entwicklung — und damit die Generatoren
dieses Repositories — läuft im WSL. Für den Tastenweg heißt das: Die Sendeseite
(Macro Deck bzw. dessen Keyboard-Integration) muss auf der Windows-Seite laufen,
die Shortcut-Datei ist vom WSL aus aber direkt erreichbar (Abschnitt 1.2).
Die Befunde gelten für 4.7.4 wie für 4.7.5 — beide nutzen dasselbe
Shortcut-Modul.

Ziel: Jeder MuseScore-Befehl soll auf eine Taste einer Macro-Deck-Oberfläche
gelegt werden. Die Taste muss kein physisch existierender Tastaturknopf sein —
sie muss nur von Macro Deck gesendet und von MuseScore angenommen werden
können. Dieser Bericht sammelt die Wege, die MuseScore dafür bietet, und
empfiehlt einen für dieses Repository.

## Überblick

| Weg | Status in 4.7.5 | Jeder Befehl? | Macro-Deck-Anbindung | Bewertung |
|---|---|---|---|---|
| Tastaturkürzel (`shortcuts.xml`) | vorhanden | ja — alle Befehle im Shortcuts-Editor | eingebaute Keyboard-Integration sendet Tasten | **Hauptweg**, funktioniert heute |
| MIDI-Mappings (Einstellungen) | vorhanden | nein — feste Aktionsliste | nur über ein MIDI-Plugin | Nische, für Pads Hardware |
| MCP-Server (`rcontrol`, TCP 2212) | noch nicht ausgeliefert, auf `main` | ja — jedes registrierte Kommando als Tool | kleines C#-Plugin als MCP-Client | **Zukunftsweg**, beobachten |
| OSC-Fernsteuerung | entfernt (MU2/3 hatten sie) | — | — | tot in MU4 |
| QML-Plugins | vorhanden | nein | — | keine Tasten zuweisbar |
| Kommandozeile | vorhanden | nein (nur Konvertierung/Export) | — | ungeeignet |
| Accessibility/UI-Automation | OS-abhängig | ja | externes Werkzeug | Notbehelf |

## 1. Tastaturkürzel — der Hauptweg

### 1.1 Mechanik

MuseScore führt intern eine Liste von *Aktionen* (Action-Codes wie
`note-input`, `copy`, `toggle-play`), und jede Aktion kann mit einer oder
mehreren *Tastenfolgen* belegt werden (Qt-`QKeySequence`-Syntax, z. B.
`Ctrl+R`, `F13`, `Ctrl+Shift+F13`). Definiert wird das im Shortcuts-Editor
(**Bearbeiten → Einstellungen → Shortcuts**): Eintrag wählen, *Definieren…*,
Tasten drücken, *Speichern*. Die [Handbuch-Seite](https://handbook.musescore.org/customization/keyboard-shortcuts.html)
beschreibt auch **Export** und **Import** von Shortcut-Listen.

### 1.2 Wo die Shortcuts liegen

Die Datei heißt `shortcuts.xml` und liegt im Benutzer-Datenordner:

| OS | Pfad |
|---|---|
| Linux | `~/.local/share/MuseScore/MuseScore4/shortcuts.xml` |
| Windows | `%LOCALAPPDATA%\MuseScore\MuseScore4\shortcuts.xml` |
| macOS | `~/Library/Application Support/MuseScore/MuseScore4/shortcuts.xml` |

Aus dem WSL heraus ist die Windows-Datei über
`/mnt/c/Users/<Benutzer>/AppData/Local/MuseScore/MuseScore4/shortcuts.xml`
erreichbar — der Generator kann sie also direkt dorthin schreiben (bzw. eine
Kopie zum Import über den Editor ablegen). Schreiben nur, solange MuseScore
geschlossen ist; gelesen wird beim Start.

Die Standardbelegung kommt aus einer eingebetteten Datei; die Nutzerdatei
enthält die Abweichungen. Format (aus
`framework/shortcuts/internal/shortcutsregister.cpp`, identisch in 4.7.5):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Shortcuts>
    <SC>
        <key>toggle-play</key>          <!-- Action-Code -->
        <seq>Ctrl+F13</seq>             <!-- Tastenfolge, Qt-Syntax -->
    </SC>
    <SC>
        <key>note-input</key>
        <seq>F14</seq>
        <seq>F15</seq>                  <!-- mehrere Folgen erlaubt -->
    </SC>
</Shortcuts>
```

Weitere Tags: `<std>` (int, Qt-Standardkürzel) und `<autorepeat>`. Wichtig aus
dem Code:

* Der Eintrag unter `<key>` ist der **Action-Code**, nicht die Taste — bei MU3
  war das anders (`<key>` = Taste, `<action>` = Code).
* Beim Einlesen wird jeder Action-Code gegen das Aktionenregister geprüft;
  **unbekannte Codes werden still verworfen** (Warnung im Log). Bindings für
  Befehle, die in einer Version fehlen oder umbenannt wurden, verschwinden
  also einfach.
* Die Datei wird beim Ändern im Editor geschrieben; direktes Bearbeiten
  funktioniert bei geschlossenem MuseScore (das Einlesen passiert beim Start).

### 1.3 Tasten, die keine Tastatur hat

Der Editor-Dialog *Definieren…* nimmt nur Tasten auf, die man physisch drücken
kann. Für alles andere bleibt der Weg über **Import** bzw. direktes Bearbeiten
der `shortcuts.xml`. Die Tastenfolgen sind Qt-`QKeySequence`-Strings, und Qt
kennt mehr Tasten als eine Tastatur liefert:

* **F13–F24** — der praktische Fall. Qt definiert `Qt::Key_F13` bis
  `Qt::Key_F24`; Windows hat dafür Virtual-Key-Codes (0x7C–0x87), X11
  Keysyms `F13`–`F35`. Damit ergeben 12 Tasten × Modifikatoren
  (nichts/Strg/Alt/Shift und Kombinationen) **rund 96 kollisionsfreie Slots** —
  genug, um einem Deck jeden gewünschten Befehl zuzuordnen, ohne irgendeine
  MuseScore-Vorbelegung zu treffen.
* Media-Tasten (`Media Next`, `Media Play` …) — Qt kennt sie, aber sie sind auf
  den meisten Systemen global belegt und für Befehle unbrauchbar.
* Grenzen: `QKeySequence` fasst maximal vier Anschläge pro Folge; auf macOS
  sind F13–F20 sicher erreichbar, F21–F24 hängen von der Synthese ab (auf dem
  Zielgerät testen).

Konkret für dieses Repository: Deck-Definition und Shortcut-Bindung aus einer
Quelle generieren — `decks/*.py` kennt die Befehle je Taste sowieso; ein
zweiter Generator-Zweig schreibt daraus die `shortcuts.xml` zum Import in
MuseScore. Schema-Empfehlung: `F13`–`F24` belegen, bei Bedarf mit
Modifikatoren ernennen (z. B. `Ctrl+F13`, `Shift+F13` …).

### 1.4 Action-Codes finden

* Der Shortcuts-Editor listet **alle** Befehle mit Namen; **Export** schreibt
  die aktuellen Einträge samt Action-Codes als `shortcuts.xml`.
* Aus dem Quelltext extrahierte Referenz: **`docs/action-codes.md`** —
  548 Aktionen mit Code, Titel, Beschreibung, Shortcut-Kontext und
  Vorbelegung (erzeugt von `tools/extract_actions.py`).
* Im Quelltext stehen die Aktionen in den `*_uiactions`-Dateien des
  MuseScore-Repositories bzw. (nach der Umstellung auf das neue
  Kommandosystem, siehe Abschnitt 3) im `rcommand`-Register des Frameworks.
* Das Handbuch führt eine Anhangsseite *All keyboard shortcuts* (Namen +
  Vorbelegung, aber ohne Action-Codes).

### 1.5 Reichen Tastatur-Events für so viele Kommandos?

Ja. Die 548 Einträge in `docs/action-codes.md` sind das vollständige Register
inklusive Dev-/Diagnosebefehlen; ein Deck kuratiert daraus, was auf Tasten
soll. Slots sind kein Engpass: `F13`–`F24` ergeben rund 96 kollisionsfreie
Kombinationen, dazu kommen unbenutzte Modifikatorkombos auf weiteren Tasten
(eine `QKeySequence` darf bis zu vier Anschläge haben). Die realistische
Grenze liegt beim Bedienbaren — auf einem Deck will man nur zehner- bis
niedrig-hunderter Zahlen an direkt erreichbaren Tasten, und Ordnung kommt über
Deck-Ordner/Seiten, nicht über mehr Slots. Wirklich unbegrenzt wäre erst der
MCP-Weg (Abschnitt 3), der Kommandos direkt aufruft und keine Tasten-Slots
verbraucht.

## 2. Macro Deck 3 als Sendeseite

Macro Deck 3 bringt eine **eingebaute Keyboard-Integration** mit
(`app.macro-deck.keyboard`, Quelltext:
`host/src/MacroDeckHost.Integrations/Keyboard/`):

* **Aktionen:** Taste drücken (*Press key*), Text tippen (*Type text*),
  *Tastenfolge ausführen* (*Run sequence*: Kombos, Text, Verzögerungen,
  Wiederholungen), *Taste runter* / *Taste hoch*.
* **KeyCode-Enum:** A–Z, 0–9, **F1–F24**, Enter/Esc/Backspace/Tab/…, Pfeile,
  Numpad, Media-Tasten. F13–F24 sind also erste Klasse.
* **Modifier:** `Control`, `Shift`, `Alt`, `Meta` (jeweils links/rechts
  unterscheidbar).
* **Ziel:** Eine Aktion kann einen Prozessnamen mitgeben und drei Modi —
  `WhenFocused` (Standard), `FocusThenSend` (Fenster fokusieren, dann senden)
  und `Background` (in den Hintergrund senden, ohne Fokuswechsel). Damit kann
  ein Deck MuseScore steuern, ohne ihm den Fokus zu klauen. Auf Windows heißt
  der MuseScore-Prozess `MuseScore4.exe`.
* **Plattformen:** Windows `SendInput` (+ `PostMessage` für Hintergrund), Linux
  X11/XTest (`XKeysymToKeycode` + `XTestFakeKeyEvent`), macOS CGEvents mit
  Accessibility-Berechtigung. Hintergrundsenden ist plattformabhängig — unter
  Windows vielversprechend, aber ob ein Qt-Programm wie MuseScore auf
  `PostMessage`-Tasten ohne Fokus reagiert, ist im Einzelfall zu prüfen; wenn
  nicht, bleibt `FocusThenSend`.

Für unsere Zielumgebung gilt: **Macro Deck (Host) muss auf der
Windows-Seite laufen**, nicht im WSL — nur dort injiziert die Keyboard-
Integration Tasten in Windows-Programme. Das Deck-Bediengerät (Tablet/Handy)
verbindet sich wie üblich übers Netz mit dem Windows-Host. F13–F24 sind unter
Windows layoutunabhängige Virtual-Key-Codes; eine deutsche Tastaturbelegung
spielt für sie keine Rolle.

Das SDK erlaubt eigenen Plugins zudem Parametertypen `Hotkey`,
`KeyboardSequence` und `KeyboardCombo` — ein MuseScore-spezifisches Plugin
(„Sendet Tastenfolge X an MuseScore“) wäre trivial, aber die eingebaute
Keyboard-Integration reicht für den Tastenweg aus.

Hinweis zur Version: Der Pilot in `README.md` beschreibt ein Tauri-Beta von
Macro Deck 3. Der Hauptzweig ist inzwischen eine .NET-Fassung mit dem
C#-SDK aus `docs.macro-deck.app`; die obigen Angaben beziehen sich auf diesen
Stand. Vor dem Ausbau prüfen, welche Fassung auf dem Zielsystem läuft und ob
deren Keyboard-Integration F13–F24 und Prozessziel mitbringt.

## 3. MCP — der Zukunftsweg

Im `muse_framework` (seit Mitte 2026 von MuseScore/Audacity gemeinsam
entwickelt, auf `main`, **nach** 4.7.5 — daher frühestens in einer späteren
Version) entsteht das Modul `framework/rcontrol`: ein **MCP-Server**
(„MuseMCP“, Model Context Protocol, JSON-RPC über TCP, Standardport **2212**):

* `tools/list` liefert **jedes registrierte Kommando** als MCP-Tool — Name ist
  der Kommando-Pfad mit `/` → `_`, dazu Titel und Beschreibung.
* `tools/call <name>` dispatched das Kommando direkt im Prozess. Argumente
  sind noch nicht implementiert (TODO im Code) — es gehen nur arglose
  Kommandos.
* Kein Authentifizierung; der Server lauscht auf allen Interfaces. Für den
  Produktionseinsatz bleibt abzuwarten, wie das gebunden/abschaltbar sein
  wird.

Damit gäbe es einen **direkten** Weg: jedes MuseScore-Kommando per Action-Code
über TCP aufrufen, ohne Tasten, ohne Shortcut-Datei. Für Macro Deck hieße das
ein kleines C#-Plugin (TCP-Client, `tools/list` cachen, eine Aktion „MuseScore:
Kommando X“). Sobald eine MuseScore-Version mit `rcontrol` ausgeliefert ist,
lohnt sich eine Neubewertung — der Tastenweg bleibt so lange stehen, und für
Ältere MuseScore-Versionen braucht man ihn ohnehin.

Mit demselben Umbau kommen `rcommand` (neues zentrales
Kommandoregister — auch die MIDI-Mappings dispatchen dann `command://`-Codes)
und `shortcuts_v2`; ein Modul `automation` ist angelegt, hat aber noch keine
Funktion.

## 4. Was sonst untersucht wurde

* **OSC-Fernsteuerung:** MuseScore 2/3 konnten per OSC gesteuert werden; MU4
  hat die Funktion nicht (Issue [#9807](https://github.com/musescore/MuseScore/issues/9807):
  „This feature is not present in MU4.0 anyway and the UI for it is hidden“).
  Ein Überrest des Einstellungs-UI (`RemoteControlSection.qml`, Checkbox +
  Portfeld) liegt unverdrahtet im Quelltext. Kein OSC in 4.7.5.
* **MIDI-Mappings** (Einstellungen → MIDI-Mappings, in 4.7.5 vorhanden):
  MIDI-Noten/Controller → Aktion; gespeichert wird ein Action-Code, dispatched
  wird er direkt (Framework-Modul `midiremote`, inkl. MMC-Dekodierung für
  Transportsteuerung per SysEx). Die Auswahl im Dialog ist eine feste Liste
  (Playback, Notenwerte u. a.; [Issue #20998](https://github.com/musescore/MuseScore/issues/20998)
  dokumentiert die Erweiterbarkeit), nicht der volle Befehlsvorrat. Für Macro
  Deck nur über ein MIDI-fähiges Plugin — gegen den Tastenweg spricht nichts
  außer dem Aufwand.
* **QML-Plugins:** Korrektur gegenüber früheren Fassungen dieses Berichts —
  Plugin-Aktionen sind **doch shortcut-bindbar**. Die Extensions-Engine
  registriert jede Plugin-Aktion als UiAction mit Shortcut-Kontext
  (`project-opened`, bei `requiresScore: false` sogar `any`); sie erscheint
  damit im Shortcuts-Editor und akzeptiert `shortcuts.xml`-Bindungen. Der
  Action-Code hat das Format `action://<plugin-uri>?action=main`; im
  Plugin-QML dispatcht `cmd(code)` **jeden** Action-Code, und `QProcess`
  erlaubt das Starten externer Helferprozesse. Einzelheiten und Ausbaustufen:
  Abschnitt 6 und Plan `docs/plans/0005-macrodeck-plugin-bruecke.md`.
* **Kommandozeile** (`mscore …`) konvertiert/exportiert Dateien; interaktive
  Steuerung eines laufenden Programms fehlt.
* **Ableton Link** (ab 4.2) synchronisiert Tempo, keine Befehle.
* **Testflow/autobot** treibt die App als Integrationstestframework an (über
  Navigation und Aktionssystem) — intern gedacht, kein Nutzer-Fernsteuerweg.
* **Accessibility/UI-Automation** (AT-SPI, UIA, AppleScript) könnte Menübefehle
  ohne Tastatur auslösen — als Notbehelf notiert, aber deutlich spröder als
  der Tastenweg.

## 5. Empfehlung für dieses Repository

1. **Jetzt:** Den Tastenweg benutzen. Aus den Deck-Definitionen
   (`decks/*.py`) eine `shortcuts.xml` generieren lassen, die jeden
   Deck-Befehl auf einen kollisionsfreien Slot mappt (Schema `F13`–`F24`, bei
   Bedarf `Ctrl`/`Shift`/`Alt` davor), und die Macro-Deck-Buttons über die
   eingebaute Keyboard-Integration dieselben Tastenfolgen senden lassen
   (Modus `FocusThenSend` oder `Background` mit Prozessname `MuseScore4.exe`).
   Der Generator schreibt die Datei direkt nach
   `/mnt/c/.../MuseScore4/shortcuts.xml` (WSL-Zugriff, siehe 1.2) oder legt
   sie als Import-Datei ab; der Macro-Deck-Host läuft auf Windows.
2. **Dokumentieren:** Pro Deck-Taste den zugehörigen Action-Code mit ablegen,
   damit Bindings und Icons auseinanderhalten bleiben, wenn MuseScore Codes
   ändert.
3. **Beobachten:** Das Erscheinen von `rcontrol`/MCP in einem MuseScore-Release
   (Framework-`main` hat es seit Sommer 2026). Dann ggf. Umschwenken auf ein
   MCP-Plugin — der Shortcut-Umweg entfällt, und die Action-Codes werden direkt
   adressiert.

## 6. Eigene Plugin-Mechanismen von außen auslösen

Macro Deck kann mehr als Tasten senden. Die Frage: Können wir **komplexere
Mechanismen als MuseScore-Plugin** bauen (QML/JS mit vollem Score-Zugriff und
`cmd()` für jeden Action-Code) und sie von **außen** — aber auf dem
Win11-Host — auslösen? Vier Weege, alle im Plugin-Quelltext von 4.7.4
verankert:

* **A — Taste → Plugin-Aktion (heute):** Die Plugin-Aktion wird wie ein
  Built-in im Shortcuts-Editor geführt und per `shortcuts.xml` auf F13–F24
  gelegt; Macro Deck sendet die Taste. Die komplexe Logik läuft komplett in
  MuseScore. Kein Fokus-Problem, kein Zusatzprozess.
* **B — HTTP-Brücke:** Ein Dock-Plugin lebt dauerhaft und pollt mit
  `Timer` + `XMLHttpRequest` eine lokale Queue (`http://127.0.0.1:<port>`);
  Macro Deck schreibt per C#-Plugin (oder „Programm ausführen“) hinein. Keine
  Tasten, kein Fokuswechsel. Offen: XHR aus dem Plugin heraus, Residenz von
  Dock-Plugins.
* **C — QProcess-Brücke:** Das Plugin startet einen Helferprozess
  (`QProcess`-Typ im QML-Namespace) und liest dessen stdout als
  Kommando-Kanal; der Helfer verbindet sich zu Macro Deck. Fallback, falls B
  an der QML-Sandbox scheitert.
* **D — MCP (Zukunft):** Liefert ein Release `rcontrol` aus, ruft Macro Deck
  jeden Action-Code direkt über TCP 2212 auf — auch Plugin-Codes. Die
  Tasten-/Brücken-Trigger entfallen; die Plugin-Logik bleibt.

Die Feinschritte (Probe-Plugins, Messplan am Host, Entscheidung) stehen im
Plan `docs/plans/0005-macrodeck-plugin-bruecke.md`.

## Quellen

* Handbuch: [Keyboard shortcuts](https://handbook.musescore.org/customization/keyboard-shortcuts.html),
  [Preferences](https://handbook.musescore.org/customization/preferences.html),
  [Revert to factory settings](https://handbook.musescore.org/support/revert-to-factory-settings.html) (Datenpfade)
* `muse_framework` (`main`, Sep 2026): `framework/shortcuts/internal/shortcutsregister.cpp`
  (XML-Format, Speicherpfad, Verwerfen unbekannter Codes),
  `framework/rcontrol/mcp/` (MuseMCP-Server, TCP-Transport Port 2212,
  Kommandos als Tools), `framework/rcommand/` (Kommandoregister),
  `framework/shortcuts_v2/`, `framework/automation/` (Skelett)
* MuseScore 4.7.5: `src/framework/shortcuts/internal/…` (dieselben
  XML-Tags), `src/framework/` ohne `rcontrol` — MCP noch nicht ausgeliefert
* Plugin-Engine (Extensions) in 4.7.4: `src/framework/extensions/extensionstypes.h`
  (Action-Code-Format, Shortcut-Kontexte, Manifest-Felder),
  `internal/extensionsactioncontroller.cpp` + `internal/extensionsuiactions.cpp`
  (Plugin-Aktionen als UiActions), `internal/legacy/extpluginsloader.cpp`
  (QML-Header-Parsing, `requiresScore`), `src/engraving/api/v1/qmlpluginapi.cpp`
  (`cmd()`, `QProcess`-Typ), `src/framework/shortcuts/qml/Muse/Shortcuts/shortcutsmodel.cpp`
  (Shortcuts-Editor listet alle registrierten UiActions)
* Macro Deck 3 (`Macro-Deck-App/Macro-Deck`, `main`):
  `host/src/MacroDeckHost.Integrations/Keyboard/` (Aktionen, `KeyCode`
  F1–F24, `KeyModifier`, `KeyboardTarget`, Linux/Windows/macOS-Provider),
  SDK-Doku [Actions](https://docs.macro-deck.app/features/actions/)
* Issues: [musescore/MuseScore#9807](https://github.com/musescore/MuseScore/issues/9807)
  (OSC in MU4 nicht vorhanden),
  [#31671](https://github.com/musescore/MuseScore/issues/31671) (MIDI-Mappings
  in 4.6.5), [#20998](https://github.com/musescore/MuseScore/issues/20998)
  (MIDI-Mappings-Aktionen)
