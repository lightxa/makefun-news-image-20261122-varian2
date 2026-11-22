#!/usr/bin/env python3
"""news-image-20261122 variant 2: "The World at a Glance" poster.

Draws a 1024x1024 poster of Sunday 22 November 2026 world news with
pure Python stdlib only (no PIL, no network) and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png. Fully deterministic: same bytes every run.

Stories (all verified as 22 November 2026):
  1. COP31, Antalya: final-deal package announced, approval session
     set for Sunday morning (Reuters, dateline 22 Nov 2026).
  2. Israel: Eisenkot's marathon coalition talks with Likud begin
     Sunday 22 Nov (invitation reported Sat 21 Nov; talks start Sun).
  3. Cricket, Wellington: Rishabh Pant 128, India pass 600 and lead
     New Zealand by 261 on day 4, Sunday 22 Nov (ESPNcricinfo live
     blog, updated 22 Nov 2026).
  4. Lebanon: 83rd Independence Day, Sunday 22 Nov (Trump sent a
     formal cable marking it on 22 Nov; President Aoun's eve-of-day
     speech demanded an end to Israeli occupation and Iranian
     interference).
  5. Football: Liverpool v Manchester United at Anfield, Premier
     League, Sunday 22 Nov 2026, 16:30 GMT (scheduled fixture).
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font 5x7
# Each glyph is 7 rows of 5 bits, written as strings of '#' and '.'.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px per char cell)."""
    return len(text) * 6 * scale - scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def rect(self, x, y, rw, rh, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + rw)
        y1 = min(self.h, y + rh)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i:i + 3] = color

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5) if abs(dy) <= r else 0
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, yy, color)

    def ring(self, cx, cy, r, thick, color):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= thick / 2.0:
                    self.set(xx, yy, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for s in range(steps + 1):
            x = round(x0 + dx * s / steps)
            y = round(y0 + dy * s / steps)
            for ty in range(-(thick // 2), thick // 2 + 1):
                for tx in range(-(thick // 2), thick // 2 + 1):
                    self.set(x + tx, y + ty, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for yy in range(cy - ry, cy + ry + 1):
            dy = (yy - cy) / ry if ry else 0
            if abs(dy) > 1:
                continue
            dx = int(rx * (1 - dy * dy) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, yy, color)

    def tri(self, x0, y0, x1, y1, x2, y2, color):
        minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
        miny, maxy = min(y0, y1, y2), max(y0, y1, y2)
        d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if d == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / d
                b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / d
                c = 1 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    self.set(xx, yy, color)

    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch)
        if rows is None:
            return
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == '1':
                    self.rect(x + rx * scale, y + ry * scale,
                              scale, scale, color)

    def text(self, x, y, s, scale, color):
        for ch in s:
            self.glyph(x, y, ch, scale, color)
            x += 6 * scale

    def text_centred(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


# ---------------------------------------------------------------- PNG encode
def png_bytes(canvas):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- colours
NAVY = bytes((14, 42, 71))
INK = bytes((16, 24, 40))
WHITE = bytes((255, 255, 255))
CREAM = bytes((243, 233, 210))
AMBER = bytes((245, 166, 35))
RED = bytes((200, 16, 46))
TEAL = bytes((14, 124, 123))
TEAL_DK = bytes((9, 90, 89))
SAND = bytes((232, 196, 104))
GREEN = bytes((22, 101, 52))
GREEN_LT = bytes((127, 176, 105))
PURPLE = bytes((91, 42, 134))
OCEAN = bytes((46, 134, 171))
OCEAN_LT = bytes((120, 180, 210))
SKY = bytes((214, 234, 248))


def panel(c, x, y, w, h, bg, border=None):
    c.rect(x, y, w, h, bg)
    if border is not None:
        c.rect(x, y, w, 4, border)
        c.rect(x, y + h - 4, w, 4, border)
        c.rect(x, y, 4, h, border)
        c.rect(x + w - 4, y, 4, h, border)


def draw_globe(c, cx, cy, r):
    """Stylised globe: ocean disc, latitude rings, land blobs, story dots."""
    c.disc(cx, cy, r, OCEAN)
    # latitude arcs (lighter, clipped by the disc via set bounds)
    for k, ry in enumerate((int(r * 0.85), int(r * 0.45), int(r * 0.10))):
        for xx in range(cx - r, cx + r + 1):
            dx = (xx - cx) / r
            if abs(dx) >= 1:
                continue
            half = int(r * (1 - dx * dx) ** 0.5)
            for yy in (cy - ry, cy + ry):
                if abs(yy - cy) <= half:
                    c.set(xx, yy, OCEAN_LT)
    # longitude ellipse arcs
    for rx in (int(r * 0.45), int(r * 0.85)):
        for t in range(0, 361, 2):
            import math
            a = math.radians(t)
            x = cx + int(rx * math.cos(a))
            y = cy + int(r * math.sin(a))
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                c.set(x, y, OCEAN_LT)
    # land masses as flat green blobs
    blobs = [
        (cx - 78, cy - 62, 52, 30), (cx - 30, cy - 78, 46, 26),
        (cx + 42, cy - 58, 58, 34), (cx + 88, cy - 6, 34, 52),
        (cx - 88, cy + 28, 40, 34), (cx - 6, cy + 34, 52, 30),
        (cx + 52, cy + 62, 44, 26), (cx - 34, cy + 84, 30, 16),
    ]
    for bx, by, brx, bry in blobs:
        c.ellipse(bx, by, brx, bry, GREEN_LT)
    # story location dots
    dots = [
        (cx - 52, cy - 70),   # Europe / Antalya
        (cx - 40, cy - 52),   # Middle East
        (cx + 96, cy + 44),   # New Zealand
        (cx - 46, cy - 44),   # Lebanon
        (cx - 74, cy - 78),   # Britain
    ]
    for dx, dy in dots:
        c.disc(dx, dy, 7, RED)
        c.ring(dx, dy, 7, 2, WHITE)


def draw_poster():
    c = Canvas(W, H, NAVY)

    # ---- top banner -------------------------------------------------
    c.rect(0, 0, W, 118, RED)
    c.rect(0, 118, W, 6, AMBER)
    c.text_centred(512, 18, "THE WORLD AT A GLANCE", 7, WHITE)
    c.text_centred(512, 76, "SUNDAY 22 NOVEMBER 2026", 5, AMBER)

    # ---- lead story: COP31 ------------------------------------------
    panel(c, 24, 140, 976, 118, TEAL, TEAL_DK)
    c.text(48, 156, "COP31 NEARS A FINAL DEAL", 5, WHITE)
    c.text(48, 196, "ANTALYA: NEW PACKAGE TO NEARLY 200 NATIONS", 3, CREAM)
    c.text(48, 222, "APPROVAL SESSION SET FOR SUNDAY MORNING", 3, CREAM)
    # small sun/globe icon on the lead panel
    c.disc(948, 199, 34, AMBER)
    c.ring(948, 199, 34, 3, WHITE)
    c.disc(948, 199, 18, TEAL_DK)

    # ---- centre globe ------------------------------------------------
    draw_globe(c, 512, 452, 148)
    c.text_centred(512, 616, "ONE DAY, FIVE STORIES", 3, WHITE)

    # ---- left panel: Israel -----------------------------------------
    panel(c, 24, 288, 300, 250, SAND)
    c.text(44, 306, "ISRAEL", 5, INK)
    c.text(44, 348, "COALITION", 4, INK)
    c.text(44, 380, "TALKS BEGIN", 4, INK)
    c.text(44, 412, "SUNDAY", 4, INK)
    c.text(44, 452, "EISENKOT INVITES", 3, INK)
    c.text(44, 478, "LIKUD TO TALKS", 3, INK)
    c.text(44, 504, "AFTER DEADLOCK", 3, INK)

    # ---- right panel: cricket ---------------------------------------
    panel(c, 700, 288, 300, 250, GREEN)
    c.text(720, 306, "PANT 128", 5, WHITE)
    c.text(720, 348, "INDIA PASS 600", 3, WHITE)
    c.text(720, 374, "IN WELLINGTON", 3, WHITE)
    c.text(720, 412, "LEAD BY 261", 3, CREAM)
    c.text(720, 438, "DAY 4 OF TEST", 3, CREAM)
    # cricket ball, bottom right corner
    c.disc(962, 502, 20, RED)
    c.ring(962, 502, 20, 2, WHITE)

    # ---- bottom left: Lebanon ---------------------------------------
    panel(c, 24, 660, 476, 240, CREAM)
    c.text(48, 678, "LEBANON TURNS 83", 4, RED)
    c.text(48, 716, "INDEPENDENCE DAY", 4, INK)
    c.text(48, 752, "PRESIDENT AOUN:", 3, INK)
    c.text(48, 778, "END THE OCCUPATION,", 3, INK)
    c.text(48, 804, "END THE MEDDLING", 3, INK)
    c.text(48, 830, "TRUMP SENDS A CABLE", 3, INK)
    c.text(48, 856, "MARKING THE DAY", 3, INK)
    # cedar tree, right of the heading
    c.tri(462, 690, 440, 748, 484, 748, GREEN)
    c.tri(462, 722, 436, 790, 488, 790, GREEN)
    c.rect(458, 790, 8, 22, bytes((120, 72, 20)))

    # ---- bottom right: football -------------------------------------
    panel(c, 524, 660, 476, 240, PURPLE)
    c.text(548, 678, "ANFIELD TODAY", 4, WHITE)
    c.text(548, 716, "LIVERPOOL V MAN UTD", 3, AMBER)
    c.text(548, 752, "PREMIER LEAGUE,", 3, WHITE)
    c.text(548, 778, "SUNDAY, 4.30PM", 3, WHITE)
    c.text(548, 804, "TWO OF ENGLAND'S", 3, WHITE)
    c.text(548, 830, "BIGGEST CLUBS MEET", 3, WHITE)
    c.text(548, 856, "AT ANFIELD", 3, WHITE)
    # football, top right corner
    c.disc(956, 700, 22, WHITE)
    c.disc(956, 700, 8, INK)
    c.ring(956, 700, 22, 2, AMBER)

    # ---- footer ------------------------------------------------------
    c.rect(0, 924, W, 100, INK)
    c.text_centred(512, 946, "FIVE STORIES FROM ONE SUNDAY", 4, WHITE)
    c.text_centred(512, 982, "COP31 - ISRAEL - CRICKET - LEBANON - FOOTBALL", 3, AMBER)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw_poster())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
