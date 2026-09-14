"""Komposition: sitzt das Icon im Rahmen, und sagen beide Backends dasselbe?

Der Vergleich der Backends braucht den Browser aus dem Playwright-Cache; fehlt
er, entfaellt dieser Teil. Die Geometrie prueft sich auch ohne.
"""

from __future__ import annotations

import pytest

from deckgen.compose import (DOT_SPACING, Composition, Glyph, dot_dx, dots,
                             ink_side)

SIZE = 256
MARGIN = 0.08          # Vorgabe von Composition


def ink(image, threshold: int = 127):
    """Alpha-Bounding-Box in Pixeln, Kanten einschliesslich."""
    mask = image.getchannel("A").point(lambda a: 255 if a > threshold else 0)
    box = mask.getbbox()
    return None if box is None else (box[0], box[1], box[2] - 1, box[3] - 1)


def test_fit_fills_the_area_inside_the_margin(glyphs):
    box = ink(Composition([Glyph("NOTE_8TH")]).to_image(glyphs, SIZE))
    assert max(box[2] - box[0], box[3] - box[1]) + 1 == \
        pytest.approx(SIZE * (1.0 - 2.0 * MARGIN), abs=2)
    # und mittig: die Raender links/rechts bzw. oben/unten sind gleich breit
    assert box[0] == pytest.approx(SIZE - 1 - box[2], abs=2)
    assert box[1] == pytest.approx(SIZE - 1 - box[3], abs=2)


def test_em_keeps_a_small_glyph_small(glyphs):
    """Im Modus em bleibt klein, was ins Em-Quadrat passt -- fit zieht es gross."""
    fit = ink(Composition([Glyph("NOTE_HEAD_QUARTER")]).to_image(glyphs, SIZE))
    em = ink(Composition([Glyph("NOTE_HEAD_QUARTER")], mode="em").to_image(glyphs, SIZE))
    assert em[3] - em[1] < fit[3] - fit[1]


def test_margin_zero_touches_the_edges(glyphs):
    box = ink(Composition([Glyph("NOTE_16TH")], margin=0.0).to_image(glyphs, SIZE))
    assert box[1] <= 1
    assert box[3] >= SIZE - 2


def test_dots_sit_in_a_row_at_the_measured_spacing():
    row = dots(3, dx=0.8, dy=0.1)
    assert [d.dx for d in row] == [0.8, 0.8 + DOT_SPACING, 0.8 + 2 * DOT_SPACING]
    assert {d.dy for d in row} == {0.1}


def test_dots_widen_the_icon(glyphs):
    def ratio(comp):
        box = ink(comp.to_image(glyphs, SIZE))
        return (box[2] - box[0]) / (box[3] - box[1])

    assert ratio(Composition([Glyph("NOTE_QUARTER"), *dots(2, dx=0.82)])) > \
        ratio(Composition([Glyph("NOTE_QUARTER")]))


def test_flow_lays_layers_side_by_side(glyphs):
    """Drei Achtel nebeneinander sind breiter als hoch -- uebereinander nicht."""
    layers = [Glyph("NOTE_8TH"), Glyph("NOTE_8TH"), Glyph("NOTE_8TH")]
    stacked = ink(Composition(layers).to_image(glyphs, SIZE))
    flowed = ink(Composition(layers, flow=True).to_image(glyphs, SIZE))
    assert stacked[2] - stacked[0] < stacked[3] - stacked[1]
    assert flowed[2] - flowed[0] > flowed[3] - flowed[1]


def test_svg_has_one_element_per_layer(glyphs):
    svg = Composition([Glyph("NOTE_8TH"), *dots(2)]).to_svg(glyphs, SIZE)
    assert svg.count("<path") == 1
    assert svg.count("<circle") == 2
    assert f'width="{SIZE}"' in svg
    assert "viewBox=" in svg


def test_unknown_glyph_is_named_in_the_error(glyphs):
    with pytest.raises(KeyError, match="GIBT_ES_NICHT"):
        Composition([Glyph("GIBT_ES_NICHT")]).to_image(glyphs, 32)


# -- Freihaltung und gemeinsame Skala ----------------------------------------

def test_clear_x_measures_each_glyphs_own_ink(glyphs):
    """The seat follows the ink at dot height: the quarter's stem, the 8th's
    earlier head, and behind the 16th's flag."""
    r = glyphs.renderer
    upem = r.upem
    radius = 0.10 * upem                       # dot radius 0.05 + clearance
    quarter = r.clear_x(glyphs._glyph("NOTE_QUARTER"), 0, radius)
    stem = r.bounds(glyphs._glyph("NOTE_QUARTER").glyph_name)[2]
    assert quarter == pytest.approx(stem + radius, abs=12)
    assert r.clear_x(glyphs._glyph("NOTE_8TH"), 0, radius) < 0.7 * upem
    flag = r.clear_x(glyphs._glyph("NOTE_16TH"), 0, radius)
    assert flag > r.bounds(glyphs._glyph("NOTE_16TH").glyph_name)[2]


def test_dot_dx_bumps_against_reach_not_floor(glyphs):
    """Ohne min_x sitzt der Punkt direkt hinter der gemessenen Tinte."""
    dx = dot_dx(glyphs, "NOTE_8TH")
    assert dx == pytest.approx(glyphs.renderer.clear_x(
        glyphs._glyph("NOTE_8TH"), 0.0, 0.10 * glyphs.renderer.upem) / 1024,
        abs=0.01)


def test_ink_side_is_the_fit_edge_length(glyphs):
    eighth = Glyph("NOTE_8TH")
    x0, y0, x1, y1 = glyphs.renderer.bounds(glyphs._glyph("NOTE_8TH").glyph_name)
    assert ink_side(glyphs, Composition([eighth])) == pytest.approx(y1 - y0)


def test_fixed_side_shares_one_scale(glyphs):
    """With the side fixed in advance every icon renders at the same scale --
    the noteheads keep the size the font gives them."""
    whole = ink(Composition([Glyph("NOTE_WHOLE")], side=1500)
                .to_image(glyphs, 256))
    quarter = ink(Composition([Glyph("NOTE_QUARTER")], side=1500)
                  .to_image(glyphs, 256))
    assert abs((whole[2] - whole[0]) - (quarter[2] - quarter[0])) <= 1
    assert quarter[3] - quarter[1] > quarter[2] - quarter[0]


def test_anchor_note_leaves_the_dots_to_the_right(glyphs):
    """anchor="note" centres the glyph; the dots extend to the right instead
    of pushing the note aside."""
    layers = [Glyph("NOTE_QUARTER"), *dots(2, dx=0.83)]
    union = ink(Composition(layers, side=1500).to_image(glyphs, 256))
    note = ink(Composition(layers, side=1500, anchor="note")
               .to_image(glyphs, 256))
    assert abs((union[0] + union[2]) / 2 - 127.5) <= 1
    assert note[0] > union[0] + 10
    assert abs((note[1] + note[3]) / 2 - 127.5) <= 1


# -- Punkt 3 der Verifikation aus Plan 0002 ---------------------------------

@pytest.fixture(scope="module")
def backend_boxes(browser, glyphs, tmp_path_factory):
    """Alle Faelle aus tools/compare_backends.py einmal ueber beide Wege messen.

    Der Browser startet dabei genau einmal, nicht je Fall.
    """
    import compare_backends as cb

    out = tmp_path_factory.mktemp("svg")
    (out / "blank.html").write_text("<!doctype html><meta charset=utf-8>",
                                    encoding="utf-8")
    names = list(cb.CASES)
    png = []
    for name in names:
        comp = cb.CASES[name]
        (out / f"{name}.svg").write_text(comp.to_svg(glyphs, SIZE), encoding="utf-8")
        png.append(cb.image_box(comp.to_image(glyphs, SIZE), 127))
    return dict(zip(names, zip(png, cb.svg_boxes(out, names, SIZE, 127))))


def case_names():
    import compare_backends as cb
    return list(cb.CASES)


@pytest.mark.parametrize("case", case_names())
def test_both_backends_hit_the_same_box(backend_boxes, case):
    """Pillow-Bild und gerastertes SVG treffen dieselbe Flaeche (+/- 1 px)."""
    png, svg = backend_boxes[case]
    assert png is not None and svg is not None
    assert max(abs(a - b) for a, b in zip(png, svg)) <= 1
