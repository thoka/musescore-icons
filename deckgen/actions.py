"""
deckgen.actions -- Aktionsbloecke fuer die flows einer Taste.

Die Form stammt aus einem echten Export (siehe docs/plans/0002-deck-generator.md,
Anhang A). Gemessen: ein Parameter braucht nur "name", "type" und "value" -- die
Beschreibungsfelder, die die Oberflaeche mitschreibt, laesst der Importeur weg.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

# Auslöser einer Taste. Bisher nur der kurze Druck; weitere Trigger tragen
# denselben Aufbau.
SHORT_PRESS = {
    "triggerId": "onShortPress",
    "triggerType": "onShortPress",
    "triggerLabel": "Kurzer Druck",
}

# Integrationen, die im Manifest aufgefuehrt werden muessen. "app.macro-deck.deck"
# steht bewusst nicht hier -- im Export fehlt es, es ist eingebaut.
INTEGRATIONS = {
    "app.macro-deck.keyboard": {
        "id": "app.macro-deck.keyboard",
        "name": "Tastatur",
        "version": "1.0.0",
        "requiresConfiguration": False,
    },
}


@dataclass
class Action:
    """Ein Aktionsblock im Flow einer Taste."""

    block_type: str
    integration_id: str
    action_id: str
    label: str
    parameters: list[tuple[str, str, object]] = field(default_factory=list)
    color: str = "#3b82f6"

    def block(self, key: str) -> dict:
        # Die Oberflaeche vergibt hier mal "block-<zeit>-<zufall>", mal eine GUID;
        # beides wird angenommen. Aus dem Schluessel abgeleitet bleibt es stabil.
        return {
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"deckgen:block:{key}")),
            "type": "action",
            "blockType": self.block_type,
            "label": self.label,
            "color": self.color,
            "integrationId": self.integration_id,
            "actionId": self.action_id,
            "parameters": [
                {"name": name, "type": type_, "value": value}
                for name, type_, value in self.parameters
            ],
        }


def press_key(key: str, modifiers: tuple[str, ...] = (), repeat: int = 1,
              repeat_delay: int = 0, target_process: str = "MuseScore4",
              target_mode: str = "focus-send") -> Action:
    """Tastendruck an ein Programm schicken -- das Arbeitspferd fuer MuseScore."""
    return Action(
        block_type="app.macro-deck.keyboard.press-key",
        integration_id="app.macro-deck.keyboard",
        action_id="press-key",
        label="Taste/Kombination drücken",
        parameters=[
            ("combo", "keyboard-combo", {"modifiers": list(modifiers), "key": key}),
            ("repeat", "number", repeat),
            ("repeatDelay", "duration", repeat_delay),
            ("targetProcess", "autocomplete", target_process),
            ("targetMode", "choice", target_mode),
        ],
    )


def change_folder(folder) -> Action:
    """Zu einem anderen Ordner wechseln -- die Navigation zwischen Decks."""
    folder_id = getattr(folder, "id", folder)
    return Action(
        block_type="app.macro-deck.deck.change-folder",
        integration_id="app.macro-deck.deck",
        action_id="change-folder",
        label="Ordner wechseln zu",
        parameters=[("folderId", "dynamic-choice", folder_id)],
    )
