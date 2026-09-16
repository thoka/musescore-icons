"""Archiv-Schicht: schreibt deckgen ein Archiv, das Macro Deck lesen kann?

Geprueft wird gegen die Anatomie in docs/plans/0002-deck-generator.md, Anhang A
-- und, wo ein echter Export in samples/ liegt, gegen dessen Feldnamen.
"""

from __future__ import annotations

import hashlib
import json
import zipfile

import pytest
from PIL import Image

from deckgen import Button, Deck, change_folder, press_key


def build_deck() -> Deck:
    """Kleines Deck mit allem, was die Schicht kann: Icon, Aktion, Unterordner."""
    deck = Deck("Test", rows=2, columns=3)
    icon = deck.icons.add("kreis", Image.new("RGBA", (64, 64), (255, 0, 0, 255)))
    sub = deck.folder("Unten")
    deck.root.place(Button(label="1/16", icon=icon, background="#ef4444",
                           on_press=press_key("3")), x=0, y=0)
    deck.root.place(Button(label="mehr", on_press=change_folder(sub)), x=2, y=1)
    sub.place(Button(label="zurueck", on_press=change_folder(deck.root)), x=0, y=0)
    return deck


@pytest.fixture(scope="module")
def archive(tmp_path_factory):
    path = build_deck().write(tmp_path_factory.mktemp("deck") / "test.macroDeckFolder")
    with zipfile.ZipFile(path) as z:
        yield path, z


@pytest.fixture(scope="module")
def manifest(archive):
    return json.loads(archive[1].read("manifest.json"))


@pytest.fixture(scope="module")
def content(archive):
    return json.loads(archive[1].read("content.json"))


def sha256(blob: bytes) -> str:
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def test_manifest_checksums_and_sizes(archive, manifest):
    """Jeder Eintrag traegt die echte Summe und Groesse seiner Datei."""
    _, z = archive
    for entry in manifest["files"]:
        blob = z.read(entry["path"])
        assert entry["sha256"] == sha256(blob), entry["path"]
        assert entry["size"] == len(blob), entry["path"]


def test_manifest_counts(manifest):
    assert manifest["formatVersion"] == 2
    assert manifest["contents"]["folderCount"] == 2
    assert manifest["contents"]["widgetCount"] == 3
    assert manifest["contents"]["iconCount"] == 1


def test_only_integrations_that_need_listing(manifest):
    """app.macro-deck.deck ist eingebaut und steht bewusst nicht im Manifest."""
    assert [i["id"] for i in manifest["contents"]["integrations"]] == \
        ["app.macro-deck.keyboard"]


@pytest.mark.parametrize("size", ["master", "128", "256", "512"])
def test_icon_files_match_their_hashes(archive, content, size):
    _, z = archive
    icon = content["icons"][0]
    assert icon["fileContentHashes"][size] == sha256(z.read(f"icons/{icon['id']}/{size}.webp"))


def test_icon_master_is_1024(content):
    icon = content["icons"][0]
    assert (icon["width"], icon["height"]) == (1024, 1024)
    assert icon["availableSizes"] == [128, 256, 512]


def test_button_data_is_json_in_a_string(content):
    data = json.loads(content["folders"][0]["widgets"][0]["data"])
    assert data["label"] == "1/16"
    assert data["icon"]["type"] == "icon-pack"

    flows = json.loads(data["flows"])                  # noch eine Ebene JSON
    assert flows[0]["triggerId"] == "onShortPress"
    block = flows[0]["children"][0]
    assert block["blockType"] == "app.macro-deck.keyboard.press-key"
    combo = next(p for p in block["parameters"] if p["name"] == "combo")
    assert combo["value"] == {"modifiers": [], "key": "3"}


def test_subfolder_hangs_on_the_root(content):
    root, sub = content["folders"]
    assert root["parentId"] is None
    assert sub["parentId"] == root["id"]
    flows = json.loads(json.loads(sub["widgets"][0]["data"])["flows"])
    assert flows[0]["children"][0]["parameters"][0]["value"] == root["id"]


def test_two_runs_are_byte_identical(archive, tmp_path):
    """Feste Zeitstempel, abgeleitete GUIDs -- sonst kaempft jeder Lauf im Diff."""
    path, _ = archive
    again = build_deck().write(tmp_path / "again.macroDeckFolder")
    assert again.read_bytes() == path.read_bytes()


def test_place_outside_the_grid_is_refused():
    deck = Deck("Test", rows=2, columns=3)
    with pytest.raises(ValueError, match="ausserhalb"):
        deck.root.place(Button(label="x"), x=3, y=0)


def test_manifest_stays_under_macro_decks_64k_limit():
    """Macro Deck liest Manifeste nur bis 64 KiB (MaxManifestBytes im
    Importeur). 90 Icons -- 360 Eintraege -- passen nur, wenn das
    Manifest nicht eingerueckt ist; das Noten-Deck lag mit 89 Icons
    eingerueckt darueber und der Import lehnte das Archiv ab."""
    import uuid

    deck = build_deck()
    files = {f"icons/{uuid.UUID(int=0x400 + n)}/128.webp": b"x" * 2000
             for n in range(360)}
    assert len(deck._manifest_bytes(files)) <= 65536


# -- Abgleich mit einem echten Export ---------------------------------------

def press_key_block(content: dict) -> dict:
    for folder in content["folders"]:
        for widget in folder["widgets"]:
            for flow in json.loads(json.loads(widget["data"])["flows"]):
                for child in flow["children"]:
                    if child["blockType"].endswith("press-key"):
                        return child
    pytest.skip("kein press-key-Block gefunden")


def test_manifest_has_the_same_fields_as_the_export(sample, manifest):
    theirs = json.loads(sample.read("manifest.json"))
    assert set(theirs) == set(manifest)
    assert set(theirs["contents"]) == set(manifest["contents"])
    assert set(theirs["files"][0]) == set(manifest["files"][0])


def test_content_has_the_same_fields_as_the_export(sample, content):
    theirs = json.loads(sample.read("content.json"))
    assert set(theirs) == set(content)
    assert set(theirs["folders"][0]) == set(content["folders"][0])
    assert set(theirs["folders"][0]["widgets"][0]) == \
        set(content["folders"][0]["widgets"][0])
    assert set(theirs["icons"][0]) == set(content["icons"][0])


def test_flow_block_keeps_the_fields_the_importer_needs(sample, content):
    """Die Parameter-Beschreibungen des Exports laesst deckgen bewusst weg."""
    theirs = press_key_block(json.loads(sample.read("content.json")))
    ours = press_key_block(content)
    assert set(theirs) == set(ours)
    assert {p["name"] for p in theirs["parameters"]} == \
        {p["name"] for p in ours["parameters"]}
    assert {"name", "type", "value"} <= set(theirs["parameters"][0])
    assert {"name", "type", "value"} == set(ours["parameters"][0])
