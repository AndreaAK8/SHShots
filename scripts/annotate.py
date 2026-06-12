"""Annotate BackOffice screenshots in AK's locked style.

Style (sampled from AK's reference image, 2026-06-12):
- Color: #EA3329 for every mark — no other colors, no variations.
- Boxes: sharp-corner rectangle outline, 3px stroke (scaled on Retina).
- Arrows: solid tapered arrow with triangular head, pointing LEFT at the
  target element, horizontal stem trailing to the right.

Usage from the skill:
    python3 scripts/annotate.py shot.png --box 50,40,120,60 --arrow 200,150
    (coordinates in IMAGE PIXELS; multiply page coords by 2 on Retina)
"""
import argparse

from PIL import Image, ImageDraw

AK_RED = (234, 51, 41)  # #EA3329

_HEAD_LEN = 20    # arrow head length, px (at 1x; pass scale=2 on Retina)
_HEAD_HALF = 10   # half-height of the arrow head
_STEM_LEN = 60    # stem length behind the head
_STEM_HALF = 3    # half-thickness of the stem
_STROKE = 3       # box border width


def annotate(img, boxes=None, arrows=None, scale=1):
    """Draw AK-style boxes and arrows on a PIL image (mutates and returns it).

    boxes:  list of (x, y, w, h) rectangles in image pixels.
    arrows: list of (tip_x, tip_y) — arrow points LEFT at that pixel.
    scale:  2 on Retina captures so stroke/arrow sizes match the 1x look.
    """
    draw = ImageDraw.Draw(img)
    for (x, y, w, h) in boxes or []:
        draw.rectangle([x, y, x + w, y + h], outline=AK_RED, width=_STROKE * scale)
    for (tx, ty) in arrows or []:
        head = _HEAD_LEN * scale
        half = _HEAD_HALF * scale
        stem = _STEM_LEN * scale
        s_half = _STEM_HALF * scale
        # Triangular head: tip at (tx, ty), base to the right
        draw.polygon([(tx, ty), (tx + head, ty - half), (tx + head, ty + half)],
                     fill=AK_RED)
        # Stem trailing right from the head base
        draw.rectangle([tx + head, ty - s_half, tx + head + stem, ty + s_half],
                       fill=AK_RED)
    return img


def crop_browser_chrome(img, window_width_points):
    """Strip Chrome's tab bar + omnibox + bookmarks row from the top.

    Browser chrome is 87 points tall; detect Retina by comparing the PNG's
    pixel width to the window's point width (2x pixels => Retina).
    """
    scale = max(1, round(img.width / window_width_points))
    offset = 87 * scale
    return img.crop((0, offset, img.width, img.height))


def _parse_csv_ints(value):
    return tuple(int(v) for v in value.split(","))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", help="PNG to annotate (modified in place unless --out)")
    p.add_argument("--box", action="append", default=[], type=_parse_csv_ints,
                   metavar="X,Y,W,H", help="rectangle in image pixels (repeatable)")
    p.add_argument("--arrow", action="append", default=[], type=_parse_csv_ints,
                   metavar="TIP_X,TIP_Y", help="left-pointing arrow tip (repeatable)")
    p.add_argument("--crop-chrome", type=int, metavar="WINDOW_WIDTH_POINTS",
                   help="strip browser chrome; pass the window width in points")
    p.add_argument("--scale", type=int, default=2,
                   help="pixel scale of the capture (2=Retina default, 1=external)")
    p.add_argument("--out", help="output path (default: overwrite input)")
    args = p.parse_args()

    img = Image.open(args.image).convert("RGB")
    if args.crop_chrome:
        img = crop_browser_chrome(img, args.crop_chrome)
    img = annotate(img, boxes=args.box, arrows=args.arrow, scale=args.scale)
    img.save(args.out or args.image)
    print(f"annotated -> {args.out or args.image}")


if __name__ == "__main__":
    main()
