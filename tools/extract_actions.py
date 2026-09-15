#!/usr/bin/env python3
"""Extract the MuseScore action list (code, title, description, shortcut
context, default keys) from a MuseScore source tree into a Markdown table.

The output is the reference document docs/action-codes.md. Regenerate it
whenever the pinned MuseScore version changes:

    git clone --depth 1 --branch v4.7.4 --single-branch \
        https://github.com/musescore/MuseScore /tmp/opencode/ms
    python3 tools/extract_actions.py /tmp/opencode/ms docs/action-codes.md

The UiAction definitions are read from the *uiactions.cpp files of every
applicable module; default key assignments come from the embedded
src/app/configs/data/shortcuts.xml. Module paths occasionally move between
MuseScore versions — adjust the FILES table below if a path disappears.

Standard library only. The source tree is not modified.
"""
import re
import sys
from pathlib import Path

FILES = [
    ("src/appshell/internal/applicationuiactions.cpp", "App-Fenster & Menüs"),
    ("src/notationscene/internal/notationuiactions.cpp", "Notation"),
    ("src/palette/internal/paletteuiactions.cpp", "Paletten"),
    ("src/playback/internal/playbackuiactions.cpp", "Wiedergabe & Mixer"),
    ("src/project/internal/projectuiactions.cpp", "Projekt & Dateien"),
    ("src/instrumentsscene/internal/instrumentsuiactions.cpp", "Instrumente"),
    ("src/framework/audio/main/internal/audiouiactions.cpp", "Audio"),
    ("src/framework/extensions/internal/extensionsuiactions.cpp", "Extensions"),
    ("src/framework/multiwindows/internal/multiwindowsuiactions.cpp", "Multiwindow"),
    ("src/framework/musesampler/internal/musesampleruiactions.cpp", "MuseSampler"),
    ("src/framework/ui/internal/navigationuiactions.cpp", "Tastaturnavigation"),
    ("src/framework/update/internal/updateuiactions.cpp", "Update"),
    ("src/framework/vst/internal/vstuiactions.cpp", "VST"),
    ("src/framework/workspace/internal/workspaceuiactions.cpp", "Workspaces"),
    ("src/framework/diagnostics/internal/diagnosticsactions.cpp", "Diagnose (Dev)"),
    ("src/framework/autobot/internal/autobotactions.cpp", "Autobot (Dev)"),
]

# German labels for the shortcut contexts that decide where an assigned key
# is active; anything not listed here is shown verbatim.
CTX_DE = {
    "any": "immer",
    "project-opened": "Partitur offen",
    "project-focused": "Partitur fokussiert",
    "not-project-focused": "außerhalb der Partitur",
    "disabled": "deaktiviert",
}

STR = r'"((?:[^"\\]|\\.)*)"'
TRANS_RE = re.compile(r'TranslatableString\((?:"[^"]*"\s*,\s*)?"((?:[^"\\]|\\.)*)"')
CONST_RE = re.compile(r'const ActionCode (\w+)\(' + STR)
CTXID_RE = re.compile(r'\b(?:muse::)?shortcuts::(CTX_\w+)|\b(?:mu::)?context::(CTX_\w+)\b')


def load_contexts(src):
    """Return (literals, aliases) for the shortcut-context constants.

    The constants are declared in the framework and aliased in the app;
    both places are parsed so that identifiers like CTX_NOTATION_OPENED
    resolve to their string value ("project-opened").
    """
    literals, aliases = {}, {}
    for header in ["src/framework/shortcuts/shortcutcontext.h",
                   "src/context/shortcutcontext.h"]:
        text = (src / header).read_text(encoding="utf-8")
        literals.update(dict(re.findall(
            r'(?:const std::string|static const std::string) (\w+)\(' + STR, text)))
        aliases.update(dict(re.findall(
            r'(\w+)\s*=\s*(?:muse::shortcuts|mu::context)::(\w+);', text)))
    return literals, aliases


def resolve_ctx(literals, aliases, name):
    seen = set()
    while name in aliases and name not in seen:
        seen.add(name)
        name = aliases[name]
    return literals.get(name, name)


def split_args(block):
    """Split a UiAction(...) argument list on top-level commas, honouring
    parentheses and string literals."""
    args, depth, cur, instr = [], 0, "", False
    i = 0
    while i < len(block):
        c = block[i]
        if instr:
            cur += c
            if c == "\\" and i + 1 < len(block):
                cur += block[i + 1]
                i += 2
                continue
            if c == '"':
                instr = False
        elif c == '"':
            instr = True
            cur += c
        elif c in "({[":
            depth += 1
            cur += c
        elif c in ")}]":
            depth -= 1
            cur += c
        elif c == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += c
        i += 1
    if cur.strip():
        args.append(cur.strip())
    return args


def extract_file(src, literals, aliases, path):
    """Return [(code, title, desc, scCtx), ...] for one *uiactions.cpp file.

    Each UiAction entry is located by paren balancing; the first argument is
    either a string literal or an ActionCode constant declared at the top of
    the file. Title and description are the TranslatableString arguments.
    """
    text = (src / path).read_text(encoding="utf-8")
    consts = dict(CONST_RE.findall(text))
    out = []
    for m in re.finditer(r'UiAction\(', text):
        start = m.end() - 1
        depth, i, instr = 0, start, False
        while i < len(text):
            c = text[i]
            if instr:
                if c == "\\":
                    i += 2
                    continue
                if c == '"':
                    instr = False
            elif c == '"':
                instr = True
            elif c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        args = split_args(text[start + 1:i])
        sm = re.fullmatch(STR, args[0])
        if sm:
            code = sm.group(1)
        elif re.fullmatch(r'\w+', args[0]) and args[0] in consts:
            code = consts[args[0]]
        else:
            continue
        trans = TRANS_RE.findall(text[start + 1:i])
        title = trans[0] if trans else ""
        desc = trans[1] if len(trans) > 1 and trans[1] != trans[0] else ""
        sc = ""
        for arg in args[1:]:
            cm = CTXID_RE.search(arg)
            if cm:
                sc = resolve_ctx(literals, aliases, cm.group(1) or cm.group(2))
                break
            sm = re.fullmatch(STR, arg)
            if sm and re.fullmatch(r'[a-z-]+', sm.group(1)):
                sc = sm.group(1)
                break
        # "&" marks the menu mnemonic and is not part of the visible name
        title = title.replace('&', '')
        desc = desc.replace('&', '')
        out.append((code, title, desc, sc))
    return out


def read_defaults(src):
    """Parse the embedded default-shortcuts file into {code: "seq1 seq2"}."""
    text = (src / "src/app/configs/data/shortcuts.xml").read_text(encoding="utf-8")
    defaults = {}
    for scm in re.finditer(r'<SC>(.*?)</SC>', text, re.S):
        km = re.search(r'<key>([^<]+)</key>', scm.group(1))
        seqs = re.findall(r'<seq>([^<]+)</seq>', scm.group(1))
        if km:
            defaults[km.group(1)] = " ".join(seqs)
    return defaults


def main():
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <musescore-src> <out.md>")
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    literals, aliases = load_contexts(src)
    defaults = read_defaults(src)

    total, lines = 0, []
    for path, group in FILES:
        actions = extract_file(src, literals, aliases, path)
        if not actions:
            continue
        seen, uniq = set(), []
        for a in actions:
            if a[0] not in seen:
                seen.add(a[0])
                uniq.append(a)
        total += len(uniq)
        lines.append(f"\n### {group} ({len(uniq)})\n")
        lines.append("| Code | Titel (EN) | Beschreibung (EN) | Aktiv wo | Vorbelegung |")
        lines.append("|---|---|---|---|---|")
        for code, title, desc, sc in sorted(uniq):
            key = defaults.get(code, "")
            lines.append(
                f"| `{code}` | {title.replace('|', chr(92) + '|')} "
                f"| {desc.replace('|', chr(92) + '|')} "
                f"| {CTX_DE.get(sc, sc)} | {key} |")

    header = f"""# MuseScore 4.7.4 — Action-Codes

*Aus dem Quelltext von [MuseScore v4.7.4](https://github.com/musescore/MuseScore/tree/v4.7.4)
extrahiert — dieselben Register, die der Shortcuts-Editor anbietet. Titel und
Beschreibungen sind die (englischen) UI-Texte; die deutsche Oberfläche zeigt
Übersetzungen. „Aktiv wo" ist der Shortcut-Kontext (`scCtx`): wo eine zugewiesene
Taste greift. „Vorbelegung" kommt aus der eingebetteten
`src/app/configs/data/shortcuts.xml`. {total} Aktionen.
Neu erzeugen: `tools/extract_actions.py`.*

Siehe auch: `docs/musescore-fernsteuerung.md` (wie diese Codes als Tasten
zugewiesen werden)."""
    out.write_text(header + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"{total} actions -> {out}")


if __name__ == "__main__":
    main()
