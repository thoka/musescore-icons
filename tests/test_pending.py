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


def test_plans_index_reads_the_table():
    rows = pending.plans_index()
    nums = [r["num"] for r in rows]
    assert "0001" in nums and "0006" in nums
    assert all(r["status"] in {"open", "done", "abandoned"} for r in rows)
    assert all(r["file"].endswith(".md") for r in rows)


def test_short_truncates_at_word_boundary():
    assert pending.short("one two three", limit=7) == "one two …"
    assert pending.short("tiny", limit=10) == "tiny"
