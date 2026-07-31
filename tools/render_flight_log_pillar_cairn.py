#!/usr/bin/env python3
"""
pillar-cairn  ·  flight_log  ·  round 2

The run read as a monument rather than a readout. Every pillar cleared is one
stone the player stacked on a night field; the cairn IS the score, so the
number on the plinth only confirms what the silhouette already said.

The composition argues by negative space. A 25-pillar run leaves ~56% of the
frame as untouched sky above the stack — the unreached remainder expressed as
room to build, never as a ghosted "could have been". A 180-pillar run pushes
that same stack to ~76% of the canvas and the sky closes in, so progress is
felt as the sky being eaten rather than as a bar being filled.

Ordinary pillars are thin slate courses; the five landmark zones are chunky
boulders wedged into the lamination, each structurally different (heat plume,
carved face, rime, ember slot, runnels) so the run's story is legible in
silhouette before any text is read. The death is a scarlet fork through the
last stone placed.

Run from the repo root:  python3 tools/render_flight_log_pillar_cairn.py
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.biome import palette_for_phase
from game.draw import lerp_color


# ── canvas + palette ─────────────────────────────────────────────────────────

W, H = 360, 640

BG = (8, 8, 20)
GOLD = (240, 192, 64)
SCARLET = (172, 40, 32)

STONE = (120, 96, 66)
STONE_ANCHOR = (148, 118, 82)
SEAM = (13, 10, 8)
HOT_CORAL = (236, 92, 72)

TEAL = (72, 196, 186)
EMBER = (255, 150, 52)
RIME = (226, 238, 250)
RUNNEL = (12, 12, 18)

# Base of the stack. Everything below this line is plinth, so the cairn and
# the engraved numeral never negotiate for the same pixels.
BASE_Y = 520
PLINTH_TOP = 520

FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
_FONTS = {}


def font(size):
    if size not in _FONTS:
        _FONTS[size] = pygame.font.Font(FONT_PATH, size)
    return _FONTS[size]


def dim(c, k):
    return (int(c[0] * k), int(c[1] * k), int(c[2] * k))


def text(surf, s, size, color, pos, anchor="topleft", alpha=255, track=0):
    f = font(size)
    if track:
        parts = [f.render(ch, True, color) for ch in s]
        tw = sum(p.get_width() for p in parts) + track * (len(s) - 1)
        img = pygame.Surface((max(1, tw), f.get_height()), pygame.SRCALPHA)
        x = 0
        for p in parts:
            img.blit(p, (x, 0))
            x += p.get_width() + track
    else:
        img = f.render(s, True, color)
    if alpha < 255:
        img.set_alpha(alpha)
    r = img.get_rect(**{anchor: pos})
    surf.blit(img, r)
    return r


# ── stone geometry ───────────────────────────────────────────────────────────

def chipped_rect(x, y, w, h, rng):
    """Rect corners knocked off at random so no two stones repeat. Chips are
    capped at a third of the short side, otherwise thin slate courses lose
    their whole face to the bevel."""
    cap = max(1, int(min(w, h) * 0.34))
    def chip():
        if rng.random() < 0.62:
            return rng.randint(1, max(1, cap)), rng.randint(1, max(1, cap))
        return 0, 0

    tl, tr, br, bl = chip(), chip(), chip(), chip()
    pts = []
    pts.append((x + tl[0], y))
    pts.append((x + w - tr[0], y))
    if tr != (0, 0):
        pts.append((x + w, y + tr[1]))
    pts.append((x + w, y + h - br[1]))
    if br != (0, 0):
        pts.append((x + w - br[0], y + h))
    pts.append((x + bl[0], y + h))
    if bl != (0, 0):
        pts.append((x, y + h - bl[1]))
    pts.append((x, y + tl[1]))
    return pts


def shift(pts, dx, dy):
    return [(px + dx, py + dy) for px, py in pts]


def draw_stone(surf, pts, body, rim, rim_w=2, top_rim=True, rise=None):
    """Rim light is drawn as the same silhouette offset one step toward the
    light and then re-covered by the body, so the highlight tracks every chip
    exactly instead of being a straight line pasted on a jagged edge."""
    if rise is None or rise >= 3.0:
        pygame.draw.polygon(surf, SEAM, shift(pts, 0, 1))
    if top_rim:
        pygame.draw.polygon(surf, dim(rim, 0.45), shift(pts, 0, -1))
    pygame.draw.polygon(surf, rim, shift(pts, -rim_w, 0))
    pygame.draw.polygon(surf, body, pts)


# ── landmark stones ──────────────────────────────────────────────────────────

def deco_geyser(surf, x, y, w, h, rng):
    """Heat bleeds off the top edge as a narrowing column that fades out well
    before the stack's crown, so it reads as escaping pressure, not a beam."""
    plume_h = 34
    plume = pygame.Surface((w + 24, plume_h), pygame.SRCALPHA)
    for j in range(plume_h):
        v = j / (plume_h - 1.0)          # 0 at the top of the plume
        a = int(96 * (v ** 1.6))
        if a <= 0:
            continue
        half = (w * 0.5 - 3) * (0.34 + 0.66 * v)
        off = math.sin((1 - v) * 5.2) * (1 - v) * 5.0
        cx = (w + 24) * 0.5 + off
        c = lerp_color(TEAL, (188, 250, 244), 1 - v)
        pygame.draw.line(plume, (*c, a), (cx - half, j), (cx + half, j), 1)
    surf.blit(plume, (x + w * 0.5 - (w + 24) * 0.5, y - plume_h + 3))

    for _ in range(4):
        px = x + rng.uniform(w * 0.25, w * 0.75)
        py = y - rng.uniform(6, 26)
        d = pygame.Surface((3, 3), pygame.SRCALPHA)
        pygame.draw.circle(d, (*TEAL, 150), (1, 1), 1)
        surf.blit(d, (px, py))

    pygame.draw.line(surf, dim(TEAL, 0.85), (x + 2, y), (x + w - 2, y), 1)


def deco_clown(surf, x, y, w, h, rng):
    cy = y + h * 0.44
    ex = w * 0.21
    for s in (-1, 1):
        pygame.draw.circle(surf, (18, 14, 12), (int(x + w * 0.5 + s * ex), int(cy) + 1), 3)
        pygame.draw.circle(surf, (238, 240, 244), (int(x + w * 0.5 + s * ex), int(cy)), 2)
    mw = w * 0.44
    my = y + h * 0.70
    pts = []
    for i in range(9):
        t = i / 8.0
        pts.append((x + w * 0.5 - mw * 0.5 + mw * t, my + math.sin(t * math.pi) * 4.2))
    pygame.draw.lines(surf, (16, 10, 10), False, [(px, py + 1) for px, py in pts], 3)
    # Warmer and lighter than the death scarlet, so a grin never reads as a crack.
    pygame.draw.lines(surf, (214, 92, 62), False, pts, 2)


def deco_snow(surf, x, y, w, h, rng):
    """Rime grows off the windward edges rather than sitting on top as a cap —
    the crust has to describe the shape it froze onto."""
    n = max(4, int(w / 7))
    for i in range(n):
        cx = x + 3 + (w - 6) * (i + rng.uniform(0.2, 0.8)) / n
        sp = rng.uniform(2.5, 5.5)
        pygame.draw.polygon(surf, RIME, [(cx - 2.2, y + 1), (cx, y - sp), (cx + 2.2, y + 1)])
    for s, ex in ((0, x), (1, x + w)):
        for i in range(3):
            fy = y + h * (0.25 + 0.25 * i) + rng.uniform(-1, 1)
            sp = rng.uniform(2.0, 4.0) * (-1 if s == 0 else 1)
            pygame.draw.polygon(surf, dim(RIME, 0.82),
                                [(ex, fy - 2), (ex + sp, fy), (ex, fy + 2)])
    pygame.draw.line(surf, dim(RIME, 0.55), (x + 2, y + 1), (x + w - 2, y + 1), 1)


def deco_lamp(surf, x, y, w, h, rng):
    cx, cy = x + w * 0.5, y + h * 0.52
    glow = pygame.Surface((60, 40), pygame.SRCALPHA)
    for r, a in ((22, 16), (16, 22), (11, 34), (7, 54)):
        pygame.draw.ellipse(glow, (*EMBER, a), (30 - r, 20 - r * 0.62, r * 2, r * 1.24))
    surf.blit(glow, (cx - 30, cy - 20), special_flags=pygame.BLEND_ADD)
    sw, sh = max(9, int(w * 0.30)), max(4, int(h * 0.30))
    pygame.draw.rect(surf, (72, 34, 10), (cx - sw / 2 - 1, cy - sh / 2 - 1, sw + 2, sh + 2))
    pygame.draw.rect(surf, EMBER, (cx - sw / 2, cy - sh / 2, sw, sh))
    pygame.draw.rect(surf, (255, 226, 160), (cx - sw / 2 + 1, cy - sh / 2 + 1, sw - 2, 1))


def deco_rain(surf, x, y, w, h, rng):
    n = max(4, int(w / 8))
    for i in range(n):
        rx = int(x + 4 + (w - 8) * (i + rng.uniform(0.15, 0.85)) / n)
        top = y + rng.uniform(0, h * 0.22)
        pygame.draw.line(surf, RUNNEL, (rx, top), (rx + rng.uniform(-1, 1), y + h), 2)
        pygame.draw.line(surf, (74, 86, 104), (rx - 1, top + 2), (rx - 1, y + h - 1), 1)
    pygame.draw.line(surf, (58, 68, 86), (x + 3, y + h - 1), (x + w - 3, y + h - 1), 1)


DECOS = {
    "geyser": deco_geyser,
    "clown": deco_clown,
    "snow": deco_snow,
    "lamp": deco_lamp,
    "rain": deco_rain,
}


# ── stack construction ───────────────────────────────────────────────────────

LM_RISE = 15
ANCHOR_RISE = 5
CAP_RISE = 17
MIN_RISE = 1.3


def build_blocks(spec):
    """One stone per pillar, bottom-up. Ordinary courses share whatever rise is
    left after the landmark boulders and the capstone take their fixed height,
    so a long run laminates instead of overflowing the frame."""
    rng = random.Random(spec["seed"])
    n = spec["pillars"]
    landmarks = spec["landmarks"]
    anchors = set(spec["anchors"])

    roles, weights = [], []
    for i in range(1, n + 1):
        if i == n:
            roles.append("cap")
        elif i in landmarks:
            roles.append("landmark")
        elif i in anchors:
            roles.append("anchor")
        else:
            roles.append("plain")
        # A handful of fatter courses keeps a 180-stone lamination from
        # striping into a machined pattern.
        weights.append(rng.uniform(0.55, 1.05) if rng.random() > 0.16
                       else rng.uniform(1.6, 2.4))

    fixed = sum(CAP_RISE if r == "cap" else LM_RISE if r == "landmark"
                else ANCHOR_RISE if r == "anchor" else 0 for r in roles)
    free = [w for w, r in zip(weights, roles) if r == "plain"]
    budget = spec["rise_total"] - fixed

    # A minimum course height keeps the thinnest slates from vanishing, but it
    # steals from the budget — so the scale is re-solved against whatever is
    # still floating above the floor until the crown lands where it was framed.
    scale = budget / max(1e-6, sum(free))
    for _ in range(16):
        n_floor = sum(1 for w in free if w * scale <= MIN_RISE)
        floating = sum(w for w in free if w * scale > MIN_RISE)
        if floating <= 0:
            break
        scale = (budget - MIN_RISE * n_floor) / floating

    blocks = []
    y = BASE_Y
    for i, (role, wt) in enumerate(zip(roles, weights), start=1):
        t = (i - 1) / max(1, n - 1)          # 0 at the base, 1 at the crown
        if role == "cap":
            rise = CAP_RISE
        elif role == "landmark":
            rise = LM_RISE
        elif role == "anchor":
            rise = ANCHOR_RISE
        else:
            rise = max(MIN_RISE, wt * scale)

        taper = spec["w_base"] + (spec["w_top"] - spec["w_base"]) * (t ** 0.86)
        crag = (math.sin(t * 11.0 + spec["seed"]) * 3.4
                + math.sin(t * 27.0 + spec["seed"] * 2.1) * 1.8)
        bw = taper + crag + rng.uniform(-2.4, 2.4)
        if role in ("landmark", "cap"):
            bw = max(bw, spec["w_top"] + 14)
        if role == "anchor":
            bw += 7

        # Stack line wanders a little so the monument reads hand-built, but is
        # capped at 6px total so it never looks like it is falling over.
        line = W * 0.5 + math.sin(t * 2.3 + 0.7) * 4.2 + math.sin(t * 5.1) * 1.8
        cx = line + rng.uniform(-4, 4)

        h = rise + (rng.uniform(4, 7) if role == "plain" else 4)
        h = min(h, 20)
        blocks.append(dict(role=role, idx=i, cx=cx, w=bw, rise=rise, h=h,
                           y=y, kind=landmarks.get(i)))
        y -= rise
    return blocks


def draw_stack(surf, spec, blocks):
    """Stones first, marks second. A landmark sitting thirty courses down would
    otherwise have its plume and its milestone numeral buried by everything the
    player stacked afterwards."""
    rng = random.Random(spec["seed"] + 991)
    for b in blocks:
        x = b["cx"] - b["w"] * 0.5
        y_top = b["y"] - b["h"]
        pts = chipped_rect(x, y_top, b["w"], b["h"], rng)

        if b["role"] == "anchor" or (b["role"] == "landmark" and b["idx"] in spec["anchors"]):
            body = STONE_ANCHOR
            rim = GOLD
            rw = 3
        elif b["role"] in ("landmark", "cap"):
            body = (130, 104, 72)
            rim = dim(GOLD, 0.82)
            rw = 2
        else:
            j = rng.randint(-8, 8)
            body = (STONE[0] + j, STONE[1] + j, STONE[2] + max(-4, j))
            rim = dim(GOLD, 0.70 + 0.22 * rng.random())
            rw = 2 if b["rise"] > 2.6 else 1

        draw_stone(surf, pts, body, rim, rim_w=rw, top_rim=b["rise"] > 2.2, rise=b["rise"])

    for b in blocks:
        # Marks live on the exposed lip of a course, not on its buried body.
        x = b["cx"] - b["w"] * 0.5
        face_top = b["y"] - b["rise"]
        if b["kind"]:
            DECOS[b["kind"]](surf, x, face_top, b["w"], b["rise"], rng)
        if b["role"] == "anchor" or (b["idx"] in spec["anchors"] and b["kind"]):
            text(surf, str(b["idx"]), 9, GOLD,
                 (x + b["w"] + 6, face_top + b["rise"] * 0.5), "midleft", alpha=200)


def draw_crack(surf, cap):
    """One fork, from a point inside the last stone out to its edges — the run
    ends on the stone the player was still placing."""
    x = cap["cx"] - cap["w"] * 0.5
    y_top = cap["y"] - cap["h"]
    fx, fy = cap["cx"] + cap["w"] * 0.06, y_top + cap["h"] * 0.52
    ends = [(x + 2, y_top + cap["h"] - 2), (x + cap["w"] - 2, y_top + 2)]
    stem = (fx - cap["w"] * 0.10, y_top)

    glow = pygame.Surface((int(cap["w"]) + 26, int(cap["h"]) + 26), pygame.SRCALPHA)
    ox, oy = x - 13, y_top - 13
    for wdt, a in ((6, 26), (4, 40)):
        pygame.draw.line(glow, (*SCARLET, a), (stem[0] - ox, stem[1] - oy), (fx - ox, fy - oy), wdt)
        for e in ends:
            pygame.draw.line(glow, (*SCARLET, a), (fx - ox, fy - oy), (e[0] - ox, e[1] - oy), wdt)
    surf.blit(glow, (ox, oy))

    pygame.draw.line(surf, SCARLET, stem, (fx, fy), 3)
    for e in ends:
        pygame.draw.line(surf, SCARLET, (fx, fy), e, 3)
    pygame.draw.line(surf, HOT_CORAL, stem, (fx, fy), 1)
    for e in ends:
        pygame.draw.line(surf, HOT_CORAL, (fx, fy), e, 1)


# ── phase band ───────────────────────────────────────────────────────────────

BAND_X, BAND_W = 26, 300
BAND_Y, BAND_H = 484, 22


def draw_phase_band(surf, phase, days_done):
    """The day cycle stays a horizon sliver behind the monument: dim, low, and
    narrow enough that it can only ever be read as sky, not as a gauge."""
    band = pygame.Surface((BAND_W, BAND_H), pygame.SRCALPHA)
    for i in range(BAND_W):
        p = i / (BAND_W - 1.0)
        pal = palette_for_phase(p)
        edge = min(1.0, min(i, BAND_W - 1 - i) / 34.0) ** 1.3
        for j in range(BAND_H):
            v = j / (BAND_H - 1.0)
            c = dim(lerp_color(pal["sky_top"], pal["sky_bot"], v), 0.50)
            a = int(190 * (math.sin(math.pi * (j + 0.5) / BAND_H) ** 0.85) * edge)
            band.set_at((i, j), (*c, a))
    surf.blit(band, (BAND_X, BAND_Y))

    mx = BAND_X + phase * BAND_W
    my = BAND_Y + BAND_H * 0.46
    marker = pygame.Surface((30, 30), pygame.SRCALPHA)
    for r, a in ((12, 20), (8, 34), (5, 70)):
        pygame.draw.circle(marker, (255, 226, 158, a), (15, 15), r)
    pygame.draw.circle(marker, (200, 168, 112), (15, 15), 3)
    surf.blit(marker, (mx - 15, my - 15))

    for d in range(days_done):
        pygame.draw.circle(surf, dim(GOLD, 0.8), (BAND_X + 4 + d * 6, BAND_Y - 6), 1)


# ── plinth ───────────────────────────────────────────────────────────────────

def engrave(surf, s, size, center, color):
    """Cut into the stone rather than sitting on it: shadow up-left, catch-light
    down-right, matching the gold rim light on every course above."""
    f = font(size)
    ink = f.render(s, True, color)
    box = ink.get_bounding_rect()
    core = ink.subsurface(box).copy()
    dark = core.copy()
    dark.fill((10, 8, 6), special_flags=pygame.BLEND_RGB_MULT)
    lit = core.copy()
    lit.fill((118, 92, 44), special_flags=pygame.BLEND_RGB_MIN)
    r = core.get_rect(center=center)
    surf.blit(dark, (r.x - 2, r.y - 2))
    surf.blit(lit, (r.x + 2, r.y + 3))
    surf.blit(core, r)
    return r


def draw_plinth(surf, spec):
    rng = random.Random(spec["seed"] + 77)
    x0, x1 = 10, W - 10
    pygame.draw.rect(surf, (26, 21, 15), (x0, PLINTH_TOP, x1 - x0, H - PLINTH_TOP))
    pygame.draw.rect(surf, (46, 37, 26), (x0, PLINTH_TOP, x1 - x0, 4))
    pygame.draw.rect(surf, GOLD, (x0, PLINTH_TOP, 3, H - PLINTH_TOP))
    pygame.draw.rect(surf, dim(GOLD, 0.5), (x0, PLINTH_TOP, x1 - x0, 1))
    pygame.draw.rect(surf, (12, 10, 8), (x1 - 2, PLINTH_TOP + 2, 2, H - PLINTH_TOP))

    for _ in range(90):
        px, py = rng.randint(x0 + 4, x1 - 4), rng.randint(PLINTH_TOP + 6, H - 2)
        surf.set_at((px, py), (rng.randint(30, 42), rng.randint(24, 34), rng.randint(17, 24)))
    for _ in range(5):
        py = rng.randint(PLINTH_TOP + 12, H - 8)
        pygame.draw.line(surf, (20, 16, 12), (x0 + rng.randint(6, 60), py),
                         (x1 - rng.randint(6, 60), py + rng.randint(-1, 1)), 1)

    text(surf, "PILLAR", 12, dim(GOLD, 0.72), (W // 2, PLINTH_TOP + 12), "center", track=4)
    engrave(surf, str(spec["pillars"]), 96, (W // 2, PLINTH_TOP + 60), GOLD)
    text(surf, "DAY %d  ·  %s" % (spec["day"], spec["time"]), 14, (168, 152, 126),
         (W // 2, H - 14), "center", track=1)


# ── panel ────────────────────────────────────────────────────────────────────

def render_panel(spec):
    surf = pygame.Surface((W, H))
    for y in range(H):
        v = y / (H - 1.0)
        surf.fill(lerp_color(BG, (16, 15, 30), v ** 1.4), (0, y, W, 1))

    rng = random.Random(spec["seed"] + 5)
    for _ in range(70):
        sx, sy = rng.randint(0, W - 1), rng.randint(0, BAND_Y - 10)
        a = rng.randint(22, 110)
        d = pygame.Surface((2, 2), pygame.SRCALPHA)
        pygame.draw.circle(d, (200, 214, 245, a), (1, 1), 1 if rng.random() < 0.82 else 1.4)
        surf.blit(d, (sx, sy))

    draw_phase_band(surf, spec["phase"], spec["day"] - 1)

    blocks = build_blocks(spec)
    draw_stack(surf, spec, blocks)
    draw_crack(surf, blocks[-1])

    # Day-complete ceiling: dashed rule at where a full-day run's crown would sit
    full_y = max(10, int(BASE_Y - spec["rise_total"] * 170 / max(1, spec["pillars"])))
    sky_rule = pygame.Surface((W - 32, 1), pygame.SRCALPHA)
    for ix in range(0, W - 32, 8):
        sky_rule.fill((180, 160, 100, 28), (ix, 0, 4, 1))
    surf.blit(sky_rule, (16, full_y))
    text(surf, "DAY COMPLETE", 8, (100, 86, 52), (W - 20, full_y - 6), "topright",
         alpha=80, track=1)

    cap = blocks[-1]
    ly = cap["y"] - cap["h"] * 0.5
    lx = cap["cx"] + cap["w"] * 0.5 + 10
    pygame.draw.line(surf, dim(SCARLET, 0.7), (lx - 8, ly), (lx - 2, ly), 1)
    text(surf, "CAUSE · " + spec["cause"], 10, (206, 78, 66), (lx, ly), "midleft", track=1)

    draw_plinth(surf, spec)
    return surf, blocks


# ── run data ─────────────────────────────────────────────────────────────────

RUN_A = dict(
    seed=25, pillars=25, phase=0.184, day=1, time="0:47", cause="GEYSER",
    landmarks={23: "geyser"}, anchors=(),
    rise_total=150, w_base=72, w_top=40,
    caption="RUN A · PILLAR 25 · DAY 1 · 0:47 · geyser zone entered",
)

RUN_B = dict(
    seed=180, pillars=180, phase=0.031, day=2, time="5:30", cause="SNOW",
    landmarks={34: "geyser", 50: "lamp", 65: "clown", 70: "rain", 139: "snow"},
    anchors=(50, 100, 150),
    rise_total=356, w_base=82, w_top=32,
    caption="RUN B · PILLAR 180 · DAY 2 · 5:30 · all 5 landmarks",
)


# ── sheet ────────────────────────────────────────────────────────────────────

HEAD = 56
CAPS = 40
SHEET_W, SHEET_H = 736, HEAD + H + CAPS

sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((8, 8, 20))

text(sheet, "PILLAR CAIRN  ·  ROUND 2", 21, GOLD, (16, 18), "topleft", track=1)
text(sheet, "flight log  ·  360×640  ·  procedural", 11, (120, 116, 140),
     (SHEET_W - 16, 26), "topright", track=1)
pygame.draw.line(sheet, (44, 40, 60), (16, HEAD - 6), (SHEET_W - 16, HEAD - 6), 1)

panels = []
for i, spec in enumerate((RUN_A, RUN_B)):
    p, blocks = render_panel(spec)
    x = 4 + i * (W + 8)
    sheet.blit(p, (x, HEAD))
    pygame.draw.rect(sheet, (40, 36, 54), (x - 1, HEAD - 1, W + 2, H + 2), 1)
    text(sheet, spec["caption"], 11, (176, 168, 150), (x + W // 2, HEAD + H + 18),
         "center", track=0)
    top = min(b["y"] - b["h"] for b in blocks)
    panels.append((spec, blocks, top))

OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "pillar_cairn")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "round_2.png")
pygame.image.save(sheet, OUT)

print("wrote %s  (%dx%d)" % (OUT, SHEET_W, SHEET_H))
for spec, blocks, top in panels:
    sky = top / H * 100.0
    print("  pillar %-4d stones=%-4d crown y=%.0f  sky above=%.1f%%  cairn height=%.1f%%"
          % (spec["pillars"], len(blocks), top, sky, (BASE_Y - top) / H * 100.0))
band_area = BAND_W * BAND_H / (W * H) * 100.0
print("  phase band = %.2f%% of panel area ; marker at x=%.0f / %.0f"
      % (band_area, BAND_X + RUN_A["phase"] * BAND_W, W))
