"""
deckgen.archive -- ein vollstaendiges .macroDeckFolder schreiben.

Aufbau des Archivs (gemessen an einem Export von Macro Deck 3.0.0-beta.4,
Einzelheiten in docs/plans/0002-deck-generator.md, Anhang A):

    manifest.json     Formatangaben, Inhaltszaehler, Datei-Liste mit sha256
    content.json      Ordner, Tasten, Icons
    icons/<guid>/     master.webp (1024) + 128/256/512.webp

Signiert wird nichts -- die Pruefsummen im Manifest genuegen. Das Manifest
bleibt komprimiert (ein Zeilenumbruch pro Feld wuerde bei groesseren Decks
ueber Macro Decks Manifest-Limit von 64 KiB steigen, dann lehnt der Import
das Archiv ab).

Beispiel:
    deck = Deck("Rhythmus")
    icon = deck.icons.add("note-8th", bild)
    deck.root.place(Button(icon=icon, on_press=press_key("4")), x=0, y=0)
    deck.write("packs/rhythmus.macroDeckFolder")
"""

from __future__ import annotations

import hashlib
import io
import json
import uuid
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from .actions import INTEGRATIONS, SHORT_PRESS, Action

FORMAT_VERSION = 2
APP_VERSION = "3.0.0-beta.4"          # Stand, gegen den entwickelt wurde
ICON_SIZES = (128, 256, 512)
MASTER_SIZE = 1024
# Feste Zeitstempel und abgeleitete GUIDs -- damit zwei Laeufe dasselbe Archiv
# ergeben. Der Importeur schreibt GUIDs ohnehin um (PortableGuidRemapper).
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
CREATED_AT = "2026-01-01T00:00:00.0000000Z"


def _guid(kind: str, key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"deckgen:{kind}:{key}"))


def _sha256(blob: bytes) -> str:
    return "sha256:" + hashlib.sha256(blob).hexdigest()


@dataclass
class Icon:
    """Ein Icon in der Bibliothek des Archivs, in allen noetigen Groessen."""

    id: str
    name: str
    files: dict[str, bytes]           # "master" | "128" | "256" | "512" -> WebP
    width: int
    height: int
    source_hash: str
    original_file_name: str
    original_format: str

    def record(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "isAnimated": False,
            "frameCount": None,
            "sourceContentHash": self.source_hash,
            "fileContentHashes": {k: _sha256(v) for k, v in self.files.items()},
            "checksum": None,
            "originalFileName": self.original_file_name,
            "originalFormat": self.original_format,
            "availableSizes": list(ICON_SIZES),
        }


class IconLibrary:
    """Nimmt Bilder entgegen und legt sie als WebP-Stufen ab."""

    def __init__(self) -> None:
        self.icons: list[Icon] = []

    def add(self, name: str, image, original_file_name: str | None = None,
            original_format: str = "Png") -> Icon:
        from PIL import Image

        master = image if image.size == (MASTER_SIZE, MASTER_SIZE) else \
            image.resize((MASTER_SIZE, MASTER_SIZE), Image.LANCZOS)
        files = {"master": _webp(master)}
        for size in ICON_SIZES:
            files[str(size)] = _webp(master.resize((size, size), Image.LANCZOS))

        icon = Icon(
            id=_guid("icon", name),
            name=name,
            files=files,
            width=MASTER_SIZE,
            height=MASTER_SIZE,
            source_hash=_sha256(files["master"]),
            original_file_name=original_file_name or f"{name}.png",
            original_format=original_format,
        )
        self.icons.append(icon)
        return icon


def _webp(image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, "WEBP", lossless=True, quality=100)
    return buf.getvalue()


@dataclass
class Button:
    """Eine Taste. Was nicht gesetzt wird, laesst die App auf ihrem Standard."""

    label: str = ""
    icon: Icon | None = None
    background: str | None = None
    on_press: Action | list[Action] | None = None
    font_size: int = 14
    text_align: str = "center"
    label_position: str = "center"
    icon_zoom: int = 70
    icon_fit: str = "contain"
    icon_opacity: int = 100

    def data(self, key: str) -> str:
        data: dict = {"label": self.label, "stateMode": False}
        if self.icon is not None:
            data["icon"] = {"type": "icon-pack", "reference": self.icon.id}
            data["iconDisplay"] = {"fit": self.icon_fit, "zoom": self.icon_zoom,
                                   "offsetX": 0, "offsetY": 0,
                                   "opacity": self.icon_opacity}
        data["fontSize"] = self.font_size
        data["textAlign"] = self.text_align
        data["labelPosition"] = self.label_position
        data["border"] = {"style": "off"}
        if self.background is not None:
            data["backgroundColor"] = self.background

        actions = self.on_press if isinstance(self.on_press, list) else \
            ([] if self.on_press is None else [self.on_press])
        flows = [dict(SHORT_PRESS,
                      children=[a.block(f"{key}:{i}") for i, a in enumerate(actions)])] \
            if actions else []
        data["flows"] = json.dumps(flows, ensure_ascii=False)
        # "data" ist im Archiv selbst wieder JSON in einem String.
        return json.dumps(data, ensure_ascii=False)


@dataclass
class Placement:
    button: Button
    x: int
    y: int
    w: int = 1
    h: int = 1


@dataclass
class Folder:
    """Eine Deck-Seite: ein Raster voller Tasten."""

    name: str
    rows: int = 5
    columns: int = 6
    parent: "Folder | None" = None
    order: int = 0
    placements: list[Placement] = field(default_factory=list)

    @property
    def id(self) -> str:
        return _guid("folder", self.name)

    def place(self, button: Button, x: int, y: int, w: int = 1, h: int = 1) -> Button:
        if not (0 <= x < self.columns and 0 <= y < self.rows):
            raise ValueError(f"{self.name}: Position ({x},{y}) liegt ausserhalb "
                             f"des Rasters {self.columns}x{self.rows}")
        self.placements.append(Placement(button, x, y, w, h))
        return button

    def record(self) -> dict:
        widgets = []
        for i, p in enumerate(self.placements):
            key = f"{self.name}:{p.x}:{p.y}"
            widgets.append({
                "id": _guid("widget", key),
                "type": "ActionButton",
                "positionX": p.x,
                "positionY": p.y,
                "width": p.w,
                "height": p.h,
                "data": p.button.data(key),
                "isPinned": False,
            })
        return {
            "id": self.id,
            "name": self.name,
            "parentId": self.parent.id if self.parent else None,
            "order": self.order,
            "rows": self.rows,
            "columns": self.columns,
            "backgroundColor": None,
            "widgetSpacing": None,
            "widgetBorderRadius": None,
            "createdAt": CREATED_AT,
            "widgets": widgets,
        }


class Deck:
    """Wurzelordner, Unterordner und Icon-Bibliothek -- zusammen ein Archiv."""

    def __init__(self, name: str, rows: int = 5, columns: int = 6):
        self.root = Folder(name, rows, columns)
        self.folders = [self.root]
        self.icons = IconLibrary()

    def folder(self, name: str, rows: int | None = None,
               columns: int | None = None, parent: Folder | None = None) -> Folder:
        parent = parent or self.root
        sub = Folder(name, rows or parent.rows, columns or parent.columns,
                     parent=parent,
                     order=sum(1 for f in self.folders if f.parent is parent))
        self.folders.append(sub)
        return sub

    def _integrations(self) -> list[dict]:
        used: dict[str, dict] = {}
        for folder in self.folders:
            for p in folder.placements:
                actions = p.button.on_press
                actions = actions if isinstance(actions, list) else \
                    ([] if actions is None else [actions])
                for a in actions:
                    if a.integration_id in INTEGRATIONS:
                        used[a.integration_id] = INTEGRATIONS[a.integration_id]
        return [used[k] for k in sorted(used)]

    def manifest(self, files: dict[str, bytes]) -> dict:
        return {
            "formatVersion": FORMAT_VERSION,
            "kind": "Folder",
            "appVersion": APP_VERSION,
            "createdAt": CREATED_AT,
            "includesSecrets": False,
            "contents": {
                "name": self.root.name,
                "folderCount": len(self.folders),
                "widgetCount": sum(len(f.placements) for f in self.folders),
                "iconCount": len(self.icons.icons),
                "scriptCount": 0,
                "secretCount": 0,
                "variableCount": 0,
                "integrations": self._integrations(),
            },
            "encryption": None,
            "files": [{"path": name, "sha256": _sha256(blob), "size": len(blob)}
                      for name, blob in sorted(files.items())],
        }

    def _manifest_bytes(self, files: dict[str, bytes]) -> bytes:
        # Macro Deck liest Manifeste nur bis 64 KiB (PortableArchive.MaxManifestBytes);
        # eingerueckt wuerde das Noten-Deck mit ~350 Eintraegen darueber liegen.
        return json.dumps(self.manifest(files), ensure_ascii=False).encode()

    def write(self, path: str | Path) -> Path:
        path = Path(path)
        content = {
            "kind": "Folder",
            "profile": None,
            "folders": [f.record() for f in self.folders],
            "widgets": None,
            "icons": [i.record() for i in self.icons.icons],
            "scripts": [],
            "secrets": [],
            "variables": [],
        }
        files: dict[str, bytes] = {
            "content.json": json.dumps(content, ensure_ascii=False, indent=2).encode()
        }
        for icon in self.icons.icons:
            for label, blob in icon.files.items():
                files[f"icons/{icon.id}/{label}.webp"] = blob

        files["manifest.json"] = self._manifest_bytes(files)

        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for name in sorted(files):
                info = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                zf.writestr(info, files[name])
        return path
