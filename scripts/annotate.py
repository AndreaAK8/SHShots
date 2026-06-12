"""Annotate BackOffice screenshots in AK's locked style (v2, 2026-06-12).

Style (sampled from AK's reference images):
- Color: #EA3329 for every mark — no other colors, no variations.
- Boxes: ROUNDED-corner rectangle outline, 4px stroke (scaled on Retina).
- Arrows: tapered — thin tail widening into a solid triangular head
  (like AK's Download-button reference). Direction left or right.
- Blur: optional gaussian smudge over sensitive regions (emails, phones).
- Finish: rounded screenshot corners (transparent), like AK's reference.

Usage from the skill:
    python3 scripts/annotate.py shot.png \
        --box 50,40,120,60 --arrow 200,150,right \
        --blur 1340,380,720,800 --round 24
    (coordinates in IMAGE PIXELS; multiply page coords by 2 on Retina)
"""
import argparse

from PIL import Image, ImageDraw, ImageFilter

AK_RED = (234, 51, 41)  # #EA3329

_HEAD_LEN = 16    # arrow head length, px (at 1x; pass scale=2 on Retina)
_HEAD_HALF = 13   # half-height of the arrow head (wide, blunt head like AK's ref)
_STEM_LEN = 55    # stem length behind the head
_STEM_HALF = 5    # stem half-thickness where it meets the head
_TAIL_HALF = 2    # stem half-thickness at the tail (the taper)
_STROKE = 4       # box border width
_RADIUS = 8       # box corner radius


_SS = 4  # supersampling factor — PIL draws hard (jaggy) edges; draw at 4x
         # on a transparent overlay, downscale with LANCZOS, then composite.


def annotate(img, boxes=None, arrows=None, scale=1):
    """Draw AK-style boxes and arrows on a PIL image (returns RGB image).

    boxes:  list of (x, y, w, h) rectangles in image pixels.
    arrows: list of (tip_x, tip_y) or (tip_x, tip_y, "left"|"right") —
            the arrow POINTS toward that pixel. Default direction: right.
    scale:  2 on Retina captures so stroke/arrow sizes match the 1x look.

    All marks are rendered antialiased (supersampled overlay) — AK flagged
    jaggy arrow edges on 2026-06-12.
    """
    overlay = Image.new("RGBA", (img.width * _SS, img.height * _SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    s = scale * _SS
    red = AK_RED + (255,)
    for (x, y, w, h) in boxes or []:
        draw.rounded_rectangle(
            [x * _SS, y * _SS, (x + w) * _SS, (y + h) * _SS],
            radius=_RADIUS * s, outline=red, width=_STROKE * s)
    for arrow in arrows or []:
        tx, ty = arrow[0] * _SS, arrow[1] * _SS
        direction = arrow[2] if len(arrow) > 2 else "right"
        sign = -1 if direction == "right" else 1   # which side the tail is on
        base_x = tx + sign * _HEAD_LEN * s
        tail_x = base_x + sign * _STEM_LEN * s
        half = _HEAD_HALF * s
        s_half = _STEM_HALF * s
        t_half = _TAIL_HALF * s
        draw.polygon([
            (tx, ty),                       # tip
            (base_x, ty - half),            # head corner (top)
            (base_x, ty - s_half),          # head base meets stem (top)
            (tail_x, ty - t_half),          # thin tail (top)
            (tail_x, ty + t_half),          # thin tail (bottom)
            (base_x, ty + s_half),          # stem meets head (bottom)
            (base_x, ty + half),            # head corner (bottom)
        ], fill=red)
    overlay = overlay.resize(img.size, Image.LANCZOS)
    out = img.convert("RGBA")
    out.alpha_composite(overlay)
    out = out.convert("RGB")
    # keep mutate-and-return contract for callers holding the original
    img.paste(out)
    return img


def blur_regions(img, regions, strength=8):
    """Smudge sensitive regions (emails, phone numbers) beyond readability."""
    for (x, y, w, h) in regions:
        patch = img.crop((x, y, x + w, y + h)).filter(
            ImageFilter.GaussianBlur(radius=strength))
        img.paste(patch, (x, y))
    return img


def round_corners(img, radius=24):
    """Round the screenshot's corners (returns RGBA with transparent corners)."""
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.width - 1, img.height - 1],
                                           radius=radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def crop_browser_chrome(img, window_width_points):
    """Strip Chrome's tab bar + omnibox + bookmarks row from the top.

    Browser chrome is 87 points tall; detect Retina by comparing the PNG's
    pixel width to the window's point width (2x pixels => Retina).
    """
    scale = max(1, round(img.width / window_width_points))
    offset = 87 * scale
    return img.crop((0, offset, img.width, img.height))


def _parse_box(value):
    return tuple(int(v) for v in value.split(","))


def _parse_arrow(value):
    parts = value.split(",")
    if len(parts) == 2:
        return (int(parts[0]), int(parts[1]))
    return (int(parts[0]), int(parts[1]), parts[2].strip())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", help="PNG to annotate (modified in place unless --out)")
    p.add_argument("--box", action="append", default=[], type=_parse_box,
                   metavar="X,Y,W,H", help="rounded rectangle (repeatable)")
    p.add_argument("--arrow", action="append", default=[], type=_parse_arrow,
                   metavar="TIP_X,TIP_Y[,left|right]",
                   help="tapered arrow pointing at the tip (repeatable)")
    p.add_argument("--blur", action="append", default=[], type=_parse_box,
                   metavar="X,Y,W,H", help="blur a sensitive region (repeatable)")
    p.add_argument("--crop-chrome", type=int, metavar="WINDOW_WIDTH_POINTS",
                   help="strip browser chrome; pass the window width in points")
    p.add_argument("--round", type=int, default=0, metavar="RADIUS",
                   help="round the screenshot corners (e.g. 24)")
    p.add_argument("--scale", type=int, default=2,
                   help="pixel scale of the capture (2=Retina default, 1=external)")
    p.add_argument("--out", help="output path (default: overwrite input)")
    args = p.parse_args()

    img = Image.open(args.image).convert("RGB")
    if args.crop_chrome:
        img = crop_browser_chrome(img, args.crop_chrome)
    img = blur_regions(img, args.blur)
    img = annotate(img, boxes=args.box, arrows=args.arrow, scale=args.scale)
    if args.round:
        img = round_corners(img, args.round)
    img.save(args.out or args.image)
    print(f"annotated -> {args.out or args.image}")


if __name__ == "__main__":
    main()
