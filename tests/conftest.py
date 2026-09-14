"""Gemeinsame Fixtures.

Font laden und Icons rendern kostet Zeit, aendert sich aber innerhalb eines
Laufs nicht -- deshalb haengen beide an der Session.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))          # compare_backends, check_page
sys.path.insert(0, str(REPO / "decks"))          # die Generatoren sind Skripte

SAMPLE = REPO / "samples" / "Home.macroDeckFolder"


@pytest.fixture(scope="session")
def glyphs():
    from deckgen.glyphs import Glyphs
    return Glyphs()


@pytest.fixture(scope="session")
def sample():
    """Ein echter Export der App -- liegt in samples/ und ist nicht versioniert."""
    if not SAMPLE.exists():
        pytest.skip(f"kein echter Export in {SAMPLE}")
    import zipfile
    with zipfile.ZipFile(SAMPLE) as z:
        yield z


def browser_available() -> bool:
    """Chrome aus dem Playwright-Cache -- ohne ihn entfaellt der SVG-Vergleich."""
    try:
        import playwright.sync_api  # noqa: F401

        from check_page import find_browser
        find_browser()
    except Exception:
        return False
    return True


@pytest.fixture(scope="session")
def browser():
    """Bremse fuer alles, was rastern muss: ohne Chrome wird uebersprungen."""
    if not browser_available():
        pytest.skip("kein Playwright-Chrome vorhanden")
