import pending


def test_entries_colon_and_continuation():
    block = (
        "* **Stand**: branch `plan/0006-rhythm-entry`. All three steps in,\n"
        "  each committed: the library and the deck. 187 tests green.\n"
        "* **Next step**: none in code — the import file\n"
        "  arrives from the user.\n"
        "* **Open**: the device judgement still pending.\n"
    )
    e = pending.entry_entries(block)
    assert e["Stand"].startswith("branch `plan/0006-rhythm-entry`")
    assert "187 tests green" in e["Stand"]
    assert e["Next step"] == "none in code — the import file arrives from the user."
    assert e["Open"] == "the device judgement still pending."


def test_entries_dash_separator():
    block = "* **Stand** — Branch `plan/0004-board-layout` (unrelated work).\n"
    e = pending.entry_entries(block)
    assert e["Stand"] == "Branch `plan/0004-board-layout` (unrelated work)."


def test_next_step_labels():
    assert pending.next_step_key({"Next step": "x", "Stand": "y"}) == "Next step"
    assert pending.next_step_key({"Nächster Schritt": "x"}) == "Nächster Schritt"
    assert pending.next_step_key({"Stand": "y", "Status": "z"}) is None


def test_entry_block_sections():
    text = "# Title\n\n## Entry\n\n* **Stand**: one.\n\n## Context\n\nbody\n"
    block = pending.entry_block(text)
    assert "Stand" in block and "Context" not in block


def test_read_frontmatter():
    text = "---\nTitle: t\nStatus: open\nWritten: 2026-09-16\n---\n\n# Title\n"
    meta = pending.read_frontmatter(text)
    assert meta["Title"] == "t" and meta["Status"] == "open"
    assert pending.read_frontmatter("# No frontmatter\n") == {}
    assert pending.read_frontmatter("---\nnot: [closed\n---\n") == {}


def test_plans_index_reads_frontmatter():
    rows = pending.plans_index()
    by_num = {r["num"]: r for r in rows}
    assert "0001" in by_num and "0009" in by_num
    assert by_num["0001"]["status"] == "done"
    assert by_num["0001"]["title"] == "Glyph composer: macro deck icons from MuseScore glyphs"
    assert all(r["status"] in {"open", "done", "abandoned"} for r in rows)
    assert all(r["file"].endswith(".md") for r in rows)


def test_index_table_and_markers():
    rows = [
        {
            "num": "0001",
            "title": "Example",
            "file": "0001-example.md",
            "status": "done",
            "written": "2026-09-16",
        }
    ]
    readme = (
        "prose\n\n<!-- table:begin -->\n\n| old |\n\n<!-- table:end -->\n\nmore prose\n"
    )
    out = pending.replace_table(readme, pending.index_table(rows))
    assert out.startswith("prose\n\n<!-- table:begin -->\n\n| # | Plan |")
    assert "| 0001 | [Example](0001-example.md) | done | 2026-09-16 |" in out
    assert out.endswith("more prose\n")
    assert "| old |" not in out


def test_replace_table_needs_markers():
    try:
        pending.replace_table("no markers here", "| x |")
    except SystemExit as exc:
        assert "table:begin" in str(exc)
    else:
        raise AssertionError("missing markers must exit")


def test_short_truncates_at_word_boundary():
    assert pending.short("one two three", limit=7) == "one two …"
    assert pending.short("tiny", limit=10) == "tiny"
