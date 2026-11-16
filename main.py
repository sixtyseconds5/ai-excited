#!/usr/bin/env python3
"""Golden koi leaps from a porcelain teacup into the stars.

Stdlib-only rasterizer: no third-party imports at all (the grader runs
bare python:3.13). It paints a 1024x683 night scene pixel by pixel --
indigo sky, scattered stars, a glowing moon, a porcelain teacup with
rising steam, and a golden koi arcing out of the cup with a tiny paper
boat riding on its back -- then writes it out as a PNG with a
pure-Python encoder (zlib + struct, filter 0 scanlines).

Run:  python3 main.py   ->  writes entry.png next to this file.
The picture is deterministic: same bytes on every run.
"""

import math
import random
import struct
import zlib

W, H = 1024, 683
OUT = "entry.png"

# Deterministic dice, so the stars land in the same places every run.
rng = random.Random(20261117)

# The canvas: one flat bytearray, 3 bytes (RGB) per pixel.
canvas = bytearray(W * H * 3)


def _idx(x, y):
    return (y * W + x) * 3


def put(x, y, r, g, b):
    """Set one pixel, silently ignoring anything off-canvas."""
    if 0 <= x < W and 0 <= y < H:
        i = _idx(x, y)
        canvas[i] = r
        canvas[i + 1] = g
        canvas[i + 2] = b


def blend(x, y, r, g, b, a):
    """Paint a colour over the canvas with opacity a (0..1)."""
    if not (0 <= x < W and 0 <= y < H) or a <= 0:
        return
    if a >= 1:
        put(x, y, r, g, b)
        return
    i = _idx(x, y)
    canvas[i] = int(canvas[i] * (1 - a) + r * a)
    canvas[i + 1] = int(canvas[i + 1] * (1 - a) + g * a)
    canvas[i + 2] = int(canvas[i + 2] * (1 - a) + b * a)


def disc(cx, cy, rad, colour, alpha=1.0):
    """Filled circle, centre (cx, cy), radius rad."""
    r, g, b = colour
    x0 = max(0, int(cx - rad))
    x1 = min(W - 1, int(cx + rad) + 1)
    y0 = max(0, int(cy - rad))
    y1 = min(H - 1, int(cy + rad) + 1)
    rr = rad * rad
    for y in range(y0, y1 + 1):
        dy = y - cy
        for x in range(x0, x1 + 1):
            dx = x - cx
            if dx * dx + dy * dy <= rr:
                blend(x, y, r, g, b, alpha)


def ellipse(cx, cy, rx, ry, colour, alpha=1.0):
    """Filled ellipse."""
    r, g, b = colour
    x0 = max(0, int(cx - rx))
    x1 = min(W - 1, int(cx + rx) + 1)
    y0 = max(0, int(cy - ry))
    y1 = min(H - 1, int(cy + ry) + 1)
    for y in range(y0, y1 + 1):
        dy = (y - cy) / ry
        for x in range(x0, x1 + 1):
            dx = (x - cx) / rx
            if dx * dx + dy * dy <= 1.0:
                blend(x, y, r, g, b, alpha)


def thick_line(x0, y0, x1, y1, width, colour, alpha=1.0):
    """A line drawn as a chain of overlapping discs."""
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 1.5) + 2
    for s in range(steps + 1):
        t = s / steps
        disc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, width / 2.0,
             colour, alpha)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- sky
TOP = (10, 12, 46)       # deep indigo, top of the frame
MID = (28, 32, 86)       # violet-blue, middle
LOW = (58, 64, 110)      # dusty blue-violet, horizon glow
for _y in range(H):
    if _y < H * 0.55:
        _c = lerp(TOP, MID, _y / (H * 0.55))
    else:
        _c = lerp(MID, LOW, (_y - H * 0.55) / (H * 0.45))
    _row = _y * W * 3
    for _x in range(W):
        _i = _row + _x * 3
        canvas[_i], canvas[_i + 1], canvas[_i + 2] = _c

# Stars: deterministic scatter, brighter ones get a little cross flare.
for _ in range(240):
    _sx = rng.uniform(0, W)
    _sy = rng.uniform(0, H * 0.72)
    _br = rng.uniform(0.45, 1.0)
    _sz = rng.choice([1, 1, 1, 2, 2, 3])
    _warm = rng.random() < 0.25
    _col = (255, 236, 190) if _warm else (225, 232, 255)
    disc(_sx, _sy, _sz, _col, _br)
    if _sz >= 2 and rng.random() < 0.5:
        thick_line(_sx - 5, _sy, _sx + 5, _sy, 1, _col, _br * 0.6)
        thick_line(_sx, _sy - 5, _sx, _sy + 5, 1, _col, _br * 0.6)

# A few tiny four-point sparkles, low in the sky near the leap.
for _sx, _sy, _s in [(700, 120, 7), (880, 260, 5), (150, 200, 6),
                     (950, 90, 6), (420, 90, 5)]:
    thick_line(_sx - _s, _sy, _sx + _s, _sy, 1, (255, 244, 200), 0.9)
    thick_line(_sx, _sy - _s, _sx, _sy + _s, 1, (255, 244, 200), 0.9)
    disc(_sx, _sy, 2, (255, 250, 220), 1.0)

# Glowing moon, upper right, with a soft halo.
for _r, _a in [(120, 0.05), (95, 0.08), (72, 0.13)]:
    disc(838, 118, _r, (232, 228, 255), _a)
disc(838, 118, 52, (244, 240, 255), 1.0)
disc(874, 92, 44, (16, 18, 52), 1.0)  # crescent bite, off to one side
disc(822, 132, 7, (214, 210, 240), 0.8)  # crater shade
disc(848, 138, 5, (214, 210, 240), 0.8)


# ------------------------------------------------------- water + cup
# Dark water band along the bottom, with pale streaks of reflection.
for _y in range(600, H):
    _t = (_y - 600) / (H - 600)
    _c = lerp((16, 20, 48), (8, 10, 26), _t)
    for _x in range(W):
        _i = (_y * W + _x) * 3
        canvas[_i], canvas[_i + 1], canvas[_i + 2] = _c
for _ in range(46):
    _sx = rng.uniform(20, W - 20)
    _sy = rng.uniform(606, 672)
    _ln = rng.uniform(14, 70)
    thick_line(_sx, _sy, _sx + _ln, _sy, 1,
               (150, 170, 220), rng.uniform(0.08, 0.28))

# Saucer: wide flat ellipse under the cup, porcelain white with a
# blue rim ring.
ellipse(300, 596, 190, 26, (226, 228, 238), 1.0)
ellipse(300, 592, 190, 26, (242, 244, 250), 1.0)
ellipse(300, 592, 168, 20, (58, 96, 168), 1.0)
ellipse(300, 592, 158, 17, (240, 242, 248), 1.0)

# The cup itself: a tapered body (stacked ellipses), white porcelain
# with a cobalt band and a little willow sprig painted on.
for _k in range(0, 96):
    _t = _k / 95.0
    _cy = 588 - _k
    _rx = 118 - 34 * _t          # narrower toward the base
    _shade = 1.0 - 0.24 * _t
    _col = (int(244 * _shade), int(245 * _shade), int(250 * _shade))
    ellipse(300, _cy, _rx, 7, _col, 1.0)
ellipse(300, 492, 84, 10, (250, 251, 255), 1.0)   # open rim
ellipse(300, 492, 76, 7, (38, 52, 96), 1.0)      # tea inside the rim
ellipse(300, 492, 68, 5, (58, 40, 26), 1.0)      # dark tea surface
# Cobalt band around the belly, with a dotted ring.
for _k in range(0, 22):
    _cy = 548 - _k
    _rx = 112 - 8 * (_k / 21.0)
    ellipse(300, _cy, _rx, 7, (44, 82, 158), 1.0)
for _a in range(0, 360, 12):
    _rad = math.radians(_a)
    disc(300 + 106 * math.cos(_rad), 537 + 6 * math.sin(_rad),
         2, (240, 242, 248), 1.0)
# Willow sprig: a thin stem with leaves on the cup's front.
thick_line(268, 566, 292, 528, 2, (44, 82, 158), 1.0)
for _lx, _ly in [(272, 556), (282, 544), (290, 534), (276, 566)]:
    ellipse(_lx, _ly, 7, 3, (44, 82, 158), 1.0)
# Handle: a ring of discs arcing out to the right of the cup.
for _s in range(41):
    _t = _s / 40.0
    _ang = math.pi * (0.15 + 0.7 * _t)
    _hx = 300 + 118 + 34 * math.cos(_ang - math.pi / 2) + 26 * _t
    _hy = 540 - 34 * math.sin(_ang) + 8 * _t
    disc(_hx, _hy, 7, (238, 240, 248), 1.0)
    disc(_hx, _hy, 4, (200, 204, 218), 1.0)

# Steam: three wavy ribbons rising from the tea, fading as they climb
# and dissolving into the stars.
for _base, _amp, _ph in [(272, 14, 0.0), (300, 18, 2.1), (328, 14, 4.2)]:
    _pts = []
    for _s in range(41):
        _t = _s / 40.0
        _y = 488 - _t * 210
        _x = _base + _amp * math.sin(_t * 5.2 + _ph) * (0.4 + _t)
        _pts.append((_x, _y))
    for _s in range(40):
        _a = 0.34 * (1 - _s / 40.0)
        thick_line(_pts[_s][0], _pts[_s][1], _pts[_s + 1][0],
                   _pts[_s + 1][1], 7 - _s * 0.1,
                   (214, 220, 240), _a)


# ------------------------------------------------------------- the koi
# The leap: a quadratic Bezier from the cup's rim, up over the stars,
# and back down toward the water on the right.
P0 = (296.0, 500.0)
P1 = (560.0, 130.0)
P2 = (800.0, 470.0)


def bez(t):
    x = (1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * P1[0] + t * t * P2[0]
    y = (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * P1[1] + t * t * P2[1]
    return x, y


# Body: overlapping discs along the arc, fat at the head, tapering to
# the tail; gold on top, pale cream along the belly.
for _s in range(121):
    _t = _s / 120.0
    _x, _y = bez(_t)
    _r = 44 - 26 * _t
    _gold = lerp((214, 128, 20), (255, 196, 60), 1 - _t * 0.55)
    disc(_x, _y, _r, _gold, 1.0)
    disc(_x, _y + _r * 0.34, _r * 0.62, (255, 238, 196), 0.85)
# Back ridge: a darker gold spine line following the arc.
for _s in range(0, 121, 2):
    _t = _s / 120.0
    _x, _y = bez(_t)
    _r = 44 - 26 * _t
    disc(_x, _y - _r * 0.62, 3, (172, 96, 12), 0.9)
# Scales: faint arcs stamped along the flank.
for _s in range(8, 112, 9):
    _t = _s / 120.0
    _x, _y = bez(_t)
    _r = 44 - 26 * _t
    for _k in range(7):
        _ang = math.pi * (0.08 + 0.11 * _k)
        disc(_x + _r * 0.55 * math.cos(_ang),
             _y + _r * 0.55 * math.sin(_ang), 2,
             (190, 110, 16), 0.55)
# Head: the koi's face at the start of the arc, eye bright, mouth open.
_hx, _hy = bez(0.02)
disc(_hx, _hy, 40, (248, 170, 44), 1.0)
disc(_hx - 16, _hy - 12, 8, (255, 255, 255), 1.0)
disc(_hx - 16, _hy - 12, 4, (20, 16, 10), 1.0)
disc(_hx - 15, _hy - 13, 1, (255, 255, 255), 1.0)
disc(_hx + 26, _hy + 14, 9, (120, 60, 10), 1.0)   # open mouth
# Pectoral fin, swept back along the body.
for _s in range(21):
    _t = _s / 20.0
    disc(_hx + 30 + _t * 34, _hy + 26 + _t * 22, 10 - _t * 5,
         (232, 148, 32), 0.95)
# Tail: a flowing double fan at the end of the arc.
_tx, _ty = bez(0.985)
for _fan, _spread in [(-1, 1), (1, 1)]:
    for _s in range(26):
        _t = _s / 25.0
        disc(_tx + _t * 66, _ty + _fan * _t * 52 * _spread,
             15 - _t * 9, (246, 176, 52), 0.95)
        disc(_tx + _t * 66, _ty + _fan * _t * 52 * _spread,
             8 - _t * 4, (255, 214, 110), 0.7)

# --------------------------------------------------- paper boat rider
# A tiny folded paper boat rides the koi's back, mid-leap.
_bx, _by = bez(0.46)
_br = 44 - 26 * 0.46
_boat_y = _by - _br * 0.72
for _dx, _dy, _c in [(-26, 0, (250, 250, 252)), (0, -16, (226, 228, 236)),
                     (26, 0, (250, 250, 252)), (0, 10, (210, 212, 222))]:
    disc(_bx + _dx, _boat_y + _dy, 9, _c, 1.0)
thick_line(_bx - 24, _boat_y, _bx + 24, _boat_y, 4,
           (238, 240, 246), 1.0)
thick_line(_bx, _boat_y, _bx, _boat_y - 26, 2, (120, 96, 70), 1.0)
for _s in range(11):  # little red flag
    disc(_bx + 2 + _s, _boat_y - 26 + _s * 0.5, 4 - _s * 0.3,
         (214, 64, 48), 1.0)

# Splash: droplets bursting from the rim where the koi left the tea.
for _ in range(26):
    _ang = rng.uniform(-0.4, math.pi + 0.4)
    _dist = rng.uniform(8, 74)
    _dx = 300 + _dist * math.cos(_ang)
    _dy = 492 - abs(_dist * math.sin(_ang)) * 0.9 - rng.uniform(0, 26)
    disc(_dx, _dy, rng.uniform(1.5, 4.5),
         (200, 216, 248), rng.uniform(0.5, 1.0))
for _r, _a in [(120, 0.5), (132, 0.3), (144, 0.18)]:
    for _s in range(31):
        _ang = math.pi * (1.05 + 0.9 * _s / 30.0)
        disc(300 + _r * math.cos(_ang), 492 + _r * 0.32 * math.sin(_ang),
             2, (190, 208, 244), _a)

# Vignette: gently darken the corners so the leap reads at small size.
for _y in range(H):
    for _x in range(W):
        _dx = (_x - W / 2) / (W / 2)
        _dy = (_y - H / 2) / (H / 2)
        _d = _dx * _dx + _dy * _dy
        if _d > 1.15:
            _f = max(0.0, 1.0 - (_d - 1.15) * 0.55)
            _i = _idx(_x, _y)
            canvas[_i] = int(canvas[_i] * _f)
            canvas[_i + 1] = int(canvas[_i + 1] * _f)
            canvas[_i + 2] = int(canvas[_i + 2] * _f)


# ------------------------------------------------------- PNG encoder
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    """Write the canvas as a 24-bit RGB PNG, filter 0 scanlines."""
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter type: None
        raw += canvas[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


if __name__ == "__main__":
    import hashlib
    import os

    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, OUT)
    size = write_png(out_path)
    digest = hashlib.sha256(open(out_path, "rb").read()).hexdigest()
    print(f"wrote {OUT} {W}x{H} {size} bytes sha256={digest}")
