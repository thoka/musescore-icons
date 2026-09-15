# Taktarten: Tastenkürzel auf dem Gerät (Plan 0006)

Die Taktarten-Spalte (zweite Spalte von **Noten** und **Eingeben** im
Workbench-Deck) setzt die im Stück üblichen Taktarten. MuseScore hat
keinen Befehl mit Standard-Kürzel dafür — die Kürzel werden auf dem
Gerät selbst zugewiesen und über eine Importdatei verteilt.

## Die Zuordnung

| Taste | Taktart | Button |
|---|---|---|
| `Ctrl+Alt+5` | 2/4 | `TIME_SIGNATURES`, decks/workbench.py |
| `Ctrl+Alt+6` | C | dito |
| `Ctrl+Alt+7` | ¢ (alla breve) | dito |
| `Ctrl+Alt+8` | 6/8 | dito |
| `Ctrl+Alt+9` | 12/8 | dito |

**Stand: Vorschlag.** Die Buttons senden genau diese Tasten, bis die
Importdatei etwas anderes sagt — dann wandert die Zuordnung hierher und
in `TIME_SIGNATURES` um.

Warum diese Tasten: `Ctrl+Alt+0..4` belegen die Stimmen, `Alt+0..9` die
Intervalle (`docs/action-codes.md`) — 5..9 bleibt frei. Kein Shift: auf
der deutschen Tastatur erreicht ein Shift-Zeichen MuseScore über Macro
Deck nicht zuverlässig (das `:`-Lehrstück, decks/rhythm.py).

## Wie die Kürzel zugewiesen werden

1. In MuseScore die Taktarten aus der Palette auf eine Partitur ziehen
   (einmal je Taktart) — oder die Palettenzelle direkt verwenden.
2. Rechtsklick auf die Palettenzelle → **Tastenkürzel zuweisen** und
   die Taste aus der Tabelle setzen.
3. **Bearbeiten → Einstellungen → Tastenkürzel → Exportieren** — die
   Datei landet als `musescore/shortcuts.xml` im Repository und wird
   auf anderen Maschinen über **Importieren** eingespielt.

Die Datei ist noch nicht da; sobald sie kommt, wird sie fest
eingebunden und diese Seite folgt ihr. Der Effekt der Tasten in
MuseScore ist wie bei Transport und Bearbeiten das Urteil des Geräts.
