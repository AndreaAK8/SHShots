"""Tests for scripts/annotate.py — AK's locked annotation style (v2, 2026-06-12):
red #EA3329, rounded-corner boxes, tapered arrow (thin tail -> triangular head),
optional sensitive-region blur, rounded screenshot corners."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from PIL import Image

from annotate import AK_RED, annotate, blur_regions, crop_browser_chrome, round_corners

WHITE = (255, 255, 255)


def _blank(w=400, h=300):
    return Image.new("RGB", (w, h), WHITE)


def test_ak_red_is_the_sampled_color():
    assert AK_RED == (234, 51, 41)  # #EA3329 sampled from AK's reference image


def test_box_has_red_edges_but_rounded_corners():
    img = annotate(_blank(), boxes=[(50, 40, 120, 60)])
    assert img.getpixel((110, 40)) == AK_RED         # top edge mid: on stroke
    assert img.getpixel((50, 70)) == AK_RED          # left edge mid: on stroke
    assert img.getpixel((50, 40)) == WHITE           # sharp corner pixel: rounded away
    assert img.getpixel((110, 70)) == WHITE          # interior untouched


def test_arrow_right_tapered():
    # Arrow pointing RIGHT at (200, 150) — AK's reference: thin tail, fat head
    img = annotate(_blank(), arrows=[(200, 150, "right")])
    assert img.getpixel((197, 150)) == AK_RED        # inside head
    assert img.getpixel((150, 150)) == AK_RED        # along stem
    assert img.getpixel((210, 150)) == WHITE         # past the tip untouched
    # taper: stem is thinner at tail than head is tall
    assert img.getpixel((145, 138)) == WHITE         # above thin tail: white
    assert img.getpixel((185, 138)) == AK_RED        # head is tall here


def test_arrow_left_supported():
    img = annotate(_blank(), arrows=[(200, 150, "left")])
    assert img.getpixel((203, 150)) == AK_RED        # inside head
    assert img.getpixel((255, 150)) == AK_RED        # along stem (tail right)
    assert img.getpixel((190, 150)) == WHITE


def test_blur_regions_smudges_only_the_region():
    img = _blank()
    for x in range(100, 140):                        # sharp black block
        for y in range(100, 140):
            img.putpixel((x, y), (0, 0, 0))
    out = blur_regions(img, [(90, 90, 60, 60)])
    assert out.getpixel((100, 100)) != (0, 0, 0)     # edge no longer sharp black
    assert out.getpixel((120, 120)) != WHITE         # but darkness remains
    assert out.getpixel((300, 200)) == WHITE         # outside region untouched


def test_round_corners_makes_corners_transparent():
    out = round_corners(_blank(), radius=20)
    assert out.mode == "RGBA"
    assert out.getpixel((0, 0))[3] == 0              # corner fully transparent
    assert out.getpixel((200, 150))[3] == 255        # center opaque
    assert out.getpixel((200, 0))[3] == 255          # edge midpoints opaque


def test_crop_browser_chrome_retina():
    img = _blank(w=2880, h=1800)
    out = crop_browser_chrome(img, window_width_points=1440)
    assert out.size == (2880, 1800 - 174)


def test_crop_browser_chrome_non_retina():
    img = _blank(w=1440, h=900)
    out = crop_browser_chrome(img, window_width_points=1440)
    assert out.size == (1440, 900 - 87)
