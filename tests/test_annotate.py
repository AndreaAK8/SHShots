"""Tests for scripts/annotate.py — AK's locked annotation style:
red #EA3329, ~3px sharp-corner rectangles, solid tapered arrow."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from PIL import Image

from annotate import AK_RED, annotate, crop_browser_chrome

WHITE = (255, 255, 255)


def _blank(w=400, h=300):
    return Image.new("RGB", (w, h), WHITE)


def test_ak_red_is_the_sampled_color():
    assert AK_RED == (234, 51, 41)  # #EA3329 sampled from AK's reference image


def test_box_draws_red_border_and_leaves_inside_untouched():
    img = annotate(_blank(), boxes=[(50, 40, 120, 60)])
    assert img.getpixel((50, 40)) == AK_RED          # top-left corner on stroke
    assert img.getpixel((110, 40)) == AK_RED         # top edge
    assert img.getpixel((50, 70)) == AK_RED          # left edge
    assert img.getpixel((110, 70)) == WHITE          # interior untouched


def test_arrow_paints_red_at_tip_and_along_stem():
    # Arrow pointing left at (200, 150), like AK's sample (tail to the right)
    img = annotate(_blank(), arrows=[(200, 150)])
    assert img.getpixel((203, 150)) == AK_RED        # near tip
    assert img.getpixel((255, 150)) == AK_RED        # along stem
    assert img.getpixel((190, 150)) == WHITE         # in front of tip untouched


def test_crop_browser_chrome_retina():
    # Retina: image pixels = 2x window points -> strip 174 px of browser chrome
    img = _blank(w=2880, h=1800)
    out = crop_browser_chrome(img, window_width_points=1440)
    assert out.size == (2880, 1800 - 174)


def test_crop_browser_chrome_non_retina():
    img = _blank(w=1440, h=900)
    out = crop_browser_chrome(img, window_width_points=1440)
    assert out.size == (1440, 900 - 87)
