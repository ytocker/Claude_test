"""
Main-menu concept `one-button`, round 2 — THEME A "THE DISPATCH SEAL".

The menu is Pip's courier badge: a struck brass-and-enamel dispatch seal hung
on a grosgrain ribbon a hand's width from the lens, with the whole sky thrown a
mile behind it and out of focus. START is the enamel field; the utilities are
sealing-wax tags strung on a cord below.

Round 1 was rejected as "too simple" and its thumbnail read as a coin, so the
whole build here is silhouette-first and technique-first:

  * SS=2 compose + ONE downscale, exactly like game/store_hub.py.
  * Every metal surface is a MULTI-STOP ramp whose penultimate stop is DARKER
    than its last — the shadow-terminator bounce that separates brass from
    gold plastic. A monotonic dark->light ramp is the plastic tell.
  * ONE hard raking key at 20 deg above horizontal from the upper left, warm;
    cool sky-bounce fill. Every bevel is lit per-angle by N.L against that key,
    which is why the rim, the lugs, the ring and the bead-mill all agree.
  * Patina (green-black) in the recesses, never pure black — the single change
    that reads as aged brass rather than yellow paint.
  * The coin read is killed by SILHOUETTE: rope-milled bead edge, four cardinal
    lugs, a suspension bar, a suspension ring, and a ribbon that runs off the
    top edge of the canvas. None of those are coin shapes and all of them
    survive a 90x160 greyscale.

Depth is bought with sharpness and saturation, not haze: the seal owns the only
hard specular edges and the only saturated colour. The background is the live
alpine_haze sky with ALL high-frequency detail removed, a baked large-scale
bokeh field and a veiling scrim over it, and a whisper of corner lens falloff
in front of everything.

Nothing here is imported by the game; it writes review PNGs under docs/ only.
Pure pygame, no numpy (absent on pygbag/WASM), no per-frame per-pixel loops.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game import biome as _biome
from game import parrot, sky_designs, store_data
from game.config import GROUND_Y, PARCEL_Y_OFFSET, H, W
from game.hud import _font
# The locked CONSTELLATION/lagoon primitive set, reused verbatim so this
# exploration is built out of the same DNA as the store hub it has to beat.
from game.store_hub import (SS, DW, DH, m, font, lerp_stops, vgrad_stops,
                            multistop_v, contact_shadow, _glyph_base,
                            _stamp_bold, gradient_text, plain_text, bevel_rim,
                            top_sheen, cabochon, cabochon_glass, _rim_light,
                            downscale)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "docs", "menu-v2", "one-button")

# ── the one light ─────────────────────────────────────────────────────────────
# A single hard key 20 deg above horizontal from the upper left. Deliberately
# low: raking light is what makes struck metal read, because every bevel then
# gets a bright top-left edge and a black bottom-right occlusion.
KEY_DEG = 200.0                     # screen-space bearing of the light SOURCE
KEY_V = (math.cos(math.radians(KEY_DEG)), math.sin(math.radians(KEY_DEG)))
KEY_WARM = (255, 236, 196)
FILL_COOL = (140, 170, 190)

# ── brass ─────────────────────────────────────────────────────────────────────
# FIVE stops, and the fourth is DARKER than the fifth. That single
# non-monotonic bounce at the shadow terminator is most of the difference
# between "gold plastic" and "brass": real metal throws light back at you out
# of its own dark side.
BRASS_STOPS = [
    (0.00, (255, 242, 206)),
    (0.28, (240, 198, 110)),
    (0.55, (196, 140, 52)),
    (0.82, (128, 84, 26)),
    (1.00, (150, 102, 34)),
]
BRASS_BRIGHT = BRASS_STOPS[0][1]
# Patina: green-black, never pure black. Aged brass keeps a verdigris cast in
# every recess the polishing wheel cannot reach.
PATINA = (28, 34, 28)
PATINA_DEEP = (30, 26, 20)
# The rope mill is the one zone a polishing wheel can never reach, so its beads
# are struck from a PATINATED ramp: near-ink with only a glint on each dome.
# That is what makes the whole mill band read as the dark leg of the seal's
# two-tone boundary instead of averaging out to mid brass.
MILL_STOPS = [
    (0.00, (176, 152, 104)),
    (0.30, (104, 86, 54)),
    (0.60, (56, 50, 36)),
    (0.85, (30, 32, 26)),
    (1.00, (44, 46, 34)),
]
# The outermost edge is the FIRST thing the wheel touches, so it stays polished
# all the way round even where the key does not reach it. Its ramp therefore
# has a high floor — which is also what keeps the seal's silhouette readable
# against a night sky, where the patina band and the sky are both near-ink.
EDGE_STOPS = [
    (0.00, (255, 248, 222)),
    (0.35, (246, 210, 130)),
    (0.70, (224, 176, 96)),
    (1.00, (214, 166, 92)),
]

# ── hard enamel, oxblood, fired flush and mirror-polished (cloisonne) ─────────
ENAMEL_HI = (126, 34, 34)           # dome centre
ENAMEL_LO = (52, 10, 14)            # dome rim
ENAMEL_BLOOM = (188, 68, 46)        # subsurface light, returned lower-right

# ── ribbon / cord / wax (flat, unlit — nothing but the seal is lit) ──────────
RIB_DARK = (24, 28, 38)
RIB_DARK_2 = (16, 19, 27)
RIB_OCHRE = (150, 116, 60)
# A courier ribbon is a two-tone weave: navy ground, broad putty centre band.
# Putty rather than another dark, because a dark ribbon on the dark top of the
# alpine_haze day sky disappears — and the ribbon running off the top edge is
# one of the four things doing the anti-coin work.
RIB_PUTTY = (196, 182, 152)
WAX_HI = (104, 44, 42)
WAX_LO = (62, 24, 26)
WAX_RIM = (228, 212, 184)
WAX_LABEL = (238, 228, 206)
CORD = (150, 132, 102)
CORD_DK = (74, 62, 44)

# ── geometry, authored at 360x640 ────────────────────────────────────────────
SEAL_C = (180, 332)
R_OUT = 100                  # planchet edge
R_MILL = 91                  # rope-mill bead centres
BEAD_R = 7.0
R_BEVEL = 80                 # the bright brass bevel: the two-tone light leg
R_ANN_IN = 58
R_TEXT = 68
R_FIELD = 55                 # enamel field
LUG_R = 116                  # lug tip radius — the silhouette breakers
LUG_HALF = 15
PIVOT = (180, 182)           # suspension ring centre == the swing pivot
RING_R = 15
BAR_RECT = pygame.Rect(128, 196, 104, 24)

PIP_C = (250, 112)
PIP_SCALE = 1.6

TAG_W, TAG_H = 76, 52
TAG_HIT_H = 58
TAG_CX = (48, 136, 224, 312)
CORD_Y0, CORD_SAG = 466, 44
TAGS = (("STORE", "store"), ("TOP 10", "top10"),
        ("SETTINGS", "settings"), ("PROFILE", "profile"))
LABEL_SIZE = 12

PHASES = [("day", 0.12), ("golden", 0.27), ("plum", 0.47), ("night", 0.70)]

SWING_FRAMES = 12
SWING_DEG = 1.2
SWEEP_DEG = 6.0


# =============================================================================
# measurement helpers (review-only)
# =============================================================================
def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = rgb[:3]
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def sample_mean(surf, points):
    acc, n = [0, 0, 0], 0
    w, h = surf.get_size()
    for x, y in points:
        x, y = int(x), int(y)
        if not (0 <= x < w and 0 <= y < h):
            continue
        c = surf.get_at((x, y))
        acc[0] += c[0]
        acc[1] += c[1]
        acc[2] += c[2]
        n += 1
    n = max(1, n)
    return tuple(v // n for v in acc)


def brightest(surf, rect):
    return _extreme(surf, rect, True)


def darkest(surf, rect):
    return _extreme(surf, rect, False)


def _extreme(surf, rect, hi):
    best_l = -1.0 if hi else 9.0
    best_c = (0, 0, 0)
    r = rect.clip(surf.get_rect())
    for yy in range(r.top, r.bottom):
        for xx in range(r.left, r.right):
            c = surf.get_at((xx, yy))[:3]
            l = luminance(c)
            if (l > best_l) if hi else (l < best_l):
                best_l, best_c = l, c
    return best_c


def ring_box(cx, cy, r, ang_deg, half=4):
    x = cx + r * math.cos(math.radians(ang_deg))
    y = cy + r * math.sin(math.radians(ang_deg))
    return pygame.Rect(int(x) - half, int(y) - half, half * 2 + 1,
                       half * 2 + 1)


# =============================================================================
# lighting primitives — every bevel on this screen is lit by the SAME key
# =============================================================================
def shade(ndotl, stops=BRASS_STOPS):
    """Sample a metal ramp from a surface-normal dot light. t runs the FULL
    ramp, so a bevel turned away from the key lands on the ramp's last stop —
    which is deliberately brighter than the one before it. Ambient is not a
    separate term here: it IS that bounce stop, because on real metal the
    shadow side is not ambient light, it is the environment reflected back."""
    t = 1.0 - max(0.0, min(1.0, ndotl))
    return lerp_stops(stops, t)


def lit_ring(surf, cx, cy, r, width, stops=BRASS_STOPS, alpha=255,
             normal_out=True, tint=None, gain=1.0):
    """A circular bevel lit per-angle: at each sample the outward (or inward)
    normal is dotted with the key, so the ring is bright where it faces the
    light and drops to the ramp's bounce where it faces away. Drawn as a dense
    run of small discs because pygame's thick arcs tear."""
    n = max(48, int(2 * math.pi * r / max(1.0, width * 0.34)))
    for i in range(n):
        a = 2 * math.pi * i / n
        nx, ny = math.cos(a), math.sin(a)
        if not normal_out:
            nx, ny = -nx, -ny
        c = shade((nx * KEY_V[0] + ny * KEY_V[1]) * gain, stops)
        if tint is not None:
            c = tuple(int(round(cc * 0.5 + tc * 0.5)) for cc, tc in zip(c, tint))
        pygame.draw.circle(surf, (*c, alpha),
                           (int(round(cx + r * nx)), int(round(cy + r * ny))),
                           max(1, int(round(width / 2))))


def ink_ring(surf, cx, cy, r, w, color, alpha):
    """A translucent keyline, drawn through a layer. pygame.draw OVERWRITES
    alpha on an SRCALPHA target, so a translucent stroke drawn straight onto
    the struck metal would punch a hole through it instead of tinting it."""
    pad = r + w + 2
    lay = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    pygame.draw.circle(lay, (*color, alpha), (pad, pad), r, w)
    surf.blit(lay, (cx - pad, cy - pad))


def brass_plate(size, span, stops=BRASS_STOPS):
    """A flat brass sheet whose value ramp runs ALONG the key axis. Built as one
    vertical multi-stop ramp and rotated so its bright end points up-left at the
    key bearing: a rotated linear ramp is still a linear ramp, so this costs one
    gradient bake and one rotate instead of any per-pixel work. Because the ramp
    spans exactly `size`, the inscribed disc sees the full ramp — including the
    bounce stop, which lands on the far rim where a real casting bounces."""
    a = 0.5 - span / (2.0 * size)
    b = 0.5 + span / (2.0 * size)
    # The ramp is remapped to span exactly the planchet and CLAMPED outside it,
    # so the bar and lugs keep struck-metal values instead of running off the
    # end of the gradient.
    g = vgrad_stops(size, size, 0, [(a + t * (b - a), c) for t, c in stops])
    rot = pygame.transform.rotate(g, 90.0 - (KEY_DEG - 180.0))
    out = pygame.Surface((size, size), pygame.SRCALPHA)
    out.blit(rot, ((size - rot.get_width()) // 2, (size - rot.get_height()) // 2))
    return out


def mask_to(surf, mask):
    """Keep only where `mask` is opaque (mask is a white silhouette)."""
    out = surf.copy()
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return out


# =============================================================================
# the rope mill — ONE bead sprite, blitted 44 times
# =============================================================================
def bead_sprite(r, stops=MILL_STOPS):
    """One milled bead: a struck hemisphere seated in a patina valley. A single
    directional key means every bead on the ring shades IDENTICALLY, so the
    whole mill is one sprite blitted round the rim — the strongest 'this is a
    medal, not a coin' cue at thumbnail size, for one bake."""
    pad = max(2, int(r * 0.55))
    size = int(r * 2 + pad * 2)
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    ox = int(-KEY_V[0] * r * 0.42)
    oy = int(-KEY_V[1] * r * 0.42)
    pygame.draw.circle(s, (*PATINA, 235), (c + ox, c + oy), int(r * 1.02))
    lx, ly = c + int(KEY_V[0] * r * 0.46), c + int(KEY_V[1] * r * 0.46)
    steps = 22
    for k in range(steps):
        t = k / (steps - 1)
        rad = int(round(r * 1.55 * (1.0 - t)))
        if rad <= 0:
            continue
        pygame.draw.circle(s, lerp_stops(stops, 1.0 - t), (lx, ly), rad)
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), int(r))
    body = s.copy()
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    seat = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(seat, (*PATINA, 210), (c - ox, c - oy), int(r * 1.06))
    cut = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(cut, (255, 255, 255, 255), (c, c), int(r * 1.02))
    seat.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out = pygame.Surface((size, size), pygame.SRCALPHA)
    out.blit(seat, (0, 0))
    out.blit(body, (0, 0))
    ink_ring(out, c, c, int(r), max(1, m(0.5)), PATINA_DEEP, 150)
    return out, c


# =============================================================================
# engraved arc type — incuse, so the light fringe sits BOTTOM-RIGHT
# =============================================================================
def arc_text(surf, cx, cy, r, text, f, span_deg, centre_deg, flip=False,
             dark=(26, 22, 16), light=(246, 214, 150)):
    """Type struck INTO the annulus. Each glyph is rotated to the tangent, and
    the bright copy is offset DOWN-RIGHT under the dark face: with the key up
    at the upper left, an incuse letter's far wall is the lit one, so the
    highlight has to fall opposite the raised-type convention."""
    widths = [f.size(ch)[0] for ch in text]
    n = len(text)
    arc_px = math.radians(span_deg) * r
    tot = sum(widths)
    track = (arc_px - tot) / max(1, n - 1)
    d = -1.0 if flip else 1.0
    a0 = centre_deg - d * math.degrees(arc_px / 2 / r)
    off = max(1, m(1.1))
    pos = 0.0
    for ch, wch in zip(text, widths):
        mid = pos + wch / 2.0
        ang = a0 + d * math.degrees(mid / r)
        px = cx + r * math.cos(math.radians(ang))
        py = cy + r * math.sin(math.radians(ang))
        rot = -(ang + 90.0) if not flip else -(ang - 90.0)
        base = _stamp_bold(f.render(ch, True, (255, 255, 255)), m(0.5))
        hi = base.copy()
        hi.fill((*light, 255), special_flags=pygame.BLEND_RGBA_MULT)
        dk = base.copy()
        dk.fill((*dark, 255), special_flags=pygame.BLEND_RGBA_MULT)
        hi = pygame.transform.rotate(hi, rot)
        dk = pygame.transform.rotate(dk, rot)
        rct = dk.get_rect(center=(int(px), int(py)))
        surf.blit(hi, (rct.x + off, rct.y + off))
        surf.blit(dk, rct.topleft)
        pos += wch + track


# =============================================================================
# THE SEAL — baked once at SS, then 12 swing rotations baked from that one bake
# =============================================================================
_seal_cache = {}


def _lug_points(ang_deg):
    """A cardinal lug: a capsule tab projecting past the planchet edge."""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    cx, cy = SEAL_C
    base_r, tip_r = R_OUT - 12, LUG_R - LUG_HALF
    pts = []
    for s in (1, -1):
        pts.append((m(cx + ux * base_r + px * LUG_HALF * s * 1.15),
                    m(cy + uy * base_r + py * LUG_HALF * s * 1.15)))
    return pts, (m(cx + ux * tip_r), m(cy + uy * tip_r)), m(LUG_HALF)


def _seal_mask(canvas):
    """White silhouette of everything that is BRASS: bar, stem, planchet, lugs."""
    mask = pygame.Surface(canvas, pygame.SRCALPHA)
    cx, cy = m(SEAL_C[0]), m(SEAL_C[1])
    for ang in (0, 90, 180, 270):
        pts, tip, rr = _lug_points(ang)
        pygame.draw.circle(mask, (255, 255, 255, 255), tip, rr)
        pygame.draw.polygon(mask, (255, 255, 255, 255),
                            [pts[0], pts[1],
                             (tip[0] + (pts[1][0] - pts[0][0]) // 2,
                              tip[1] + (pts[1][1] - pts[0][1]) // 2),
                             (tip[0] - (pts[1][0] - pts[0][0]) // 2,
                              tip[1] - (pts[1][1] - pts[0][1]) // 2)])
    br = pygame.Rect(m(BAR_RECT.x), m(BAR_RECT.y), m(BAR_RECT.w), m(BAR_RECT.h))
    pygame.draw.rect(mask, (255, 255, 255, 255), br, border_radius=m(6))
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(m(166), m(BAR_RECT.bottom - 3)),
                         (m(194), m(BAR_RECT.bottom - 3)),
                         (m(188), m(SEAL_C[1] - R_OUT + 8)),
                         (m(172), m(SEAL_C[1] - R_OUT + 8))])
    pygame.draw.circle(mask, (255, 255, 255, 255), (cx, cy), m(R_OUT))
    return mask


def build_seal_device():
    """The whole struck lockup at SS: brass body from ONE rotated ramp, patina
    valley, bead mill, lit bevels, incuse dispatch line, and the enamel field
    under glass. Returns (surface, pivot_in_surface)."""
    canvas = (DW, DH)
    surf = pygame.Surface(canvas, pygame.SRCALPHA)
    cx, cy = m(SEAL_C[0]), m(SEAL_C[1])

    mask = _seal_mask(canvas)
    plate_sz = m(300)
    plate = brass_plate(plate_sz, m(LUG_R * 2))
    sheet = pygame.Surface(canvas, pygame.SRCALPHA)
    sheet.blit(plate, (cx - plate_sz // 2, cy - plate_sz // 2))
    surf.blit(mask_to(sheet, mask), (0, 0))

    # lug rims + their seating shadow into the planchet
    for ang in (0, 90, 180, 270):
        _pts, tip, rr = _lug_points(ang)
        lit_ring(surf, tip[0], tip[1], rr - m(1.4), m(2.6))
        ink_ring(surf, tip[0], tip[1], rr, max(1, m(1.3)), PATINA_DEEP, 230)
        pygame.draw.circle(surf, (*PATINA_DEEP, 255), tip, int(rr * 0.44))
        lit_ring(surf, tip[0], tip[1], int(rr * 0.44), m(2.0),
                 normal_out=False, gain=1.2)

    # the suspension bar: struck plate, embossed, glossed, and stamped SKYBIT
    br = pygame.Rect(m(BAR_RECT.x), m(BAR_RECT.y), m(BAR_RECT.w), m(BAR_RECT.h))
    bevel_rim(surf, br, m(6), (*PATINA_DEEP, 255), (*BRASS_BRIGHT, 235), m(2.4))
    top_sheen(surf, br, m(6), m(9), peak=54)
    contact_shadow(surf, br, m(6), m(3), alpha=120)
    bf = font(13)
    bl = _stamp_bold(_glyph_base("SKYBIT", bf, m(2.4)), m(0.7))
    blr = bl.get_rect(center=(br.centerx, br.centery + m(0.4)))
    hi = bl.copy()
    hi.fill((250, 226, 168, 255), special_flags=pygame.BLEND_RGBA_MULT)
    dk = bl.copy()
    dk.fill((44, 30, 14, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hi, (blr.x + m(1), blr.y + m(1)))
    surf.blit(dk, blr.topleft)

    # planchet edge: a near-ink patina valley, the bead mill struck into it,
    # and ONE polished edge wire round the outside.
    pygame.draw.circle(surf, (*PATINA_DEEP, 255), (cx, cy), m(R_OUT), m(19))

    bead, bc = bead_sprite(m(BEAD_R))
    nbeads = 42
    for i in range(nbeads):
        a = 2 * math.pi * i / nbeads
        bx = cx + m(R_MILL) * math.cos(a)
        by = cy + m(R_MILL) * math.sin(a)
        surf.blit(bead, (int(bx) - bc, int(by) - bc))

    lit_ring(surf, cx, cy, m(R_OUT - 1.5), m(3.6), stops=EDGE_STOPS, gain=1.1)
    ink_ring(surf, cx, cy, m(R_OUT), max(1, m(1.2)), PATINA_DEEP, 235)

    # the bright brass bevel immediately inside the mill: the LIGHT leg of the
    # two-tone pair the seal-vs-sky boundary is built on.
    lit_ring(surf, cx, cy, m(R_BEVEL + 2.0), m(6.0), gain=1.3)
    ink_ring(surf, cx, cy, m(R_BEVEL - 2.0), max(1, m(1.2)), PATINA, 190)

    # ── the ONE annulus that carries all the ornament ────────────────────────
    tf = font(11)
    arc_text(surf, cx, cy, m(R_TEXT), "SKY POST · DISPATCH", tf,
             span_deg=158, centre_deg=-90.0)
    arc_text(surf, cx, cy, m(R_TEXT), "No. 001", tf,
             span_deg=58, centre_deg=90.0, flip=True)
    for ang in (0, 180):
        px = cx + m(R_TEXT) * math.cos(math.radians(ang))
        py = cy + m(R_TEXT) * math.sin(math.radians(ang))
        d = m(3.4)
        pygame.draw.polygon(surf, (246, 214, 150),
                            [(px + m(1.1), py - d + m(1.1)),
                             (px + d + m(1.1), py + m(1.1)),
                             (px + m(1.1), py + d + m(1.1)),
                             (px - d + m(1.1), py + m(1.1))])
        pygame.draw.polygon(surf, (26, 22, 16),
                            [(px, py - d), (px + d, py), (px, py + d),
                             (px - d, py)])

    # cool sky-bounce fill on the side turned away from the key. The key is
    # warm and the fill is cool, so the brass reads as metal under a real sky
    # rather than as one tinted material lit by one lamp.
    cool = pygame.Surface(canvas, pygame.SRCALPHA)
    nfill = 320
    for i in range(nfill):
        a = 2 * math.pi * i / nfill
        d = -(math.cos(a) * KEY_V[0] + math.sin(a) * KEY_V[1])
        if d <= 0.0:
            continue
        pygame.draw.circle(cool, (*FILL_COOL, int(36 * d ** 1.5)),
                           (int(cx + m(R_TEXT) * math.cos(a)),
                            int(cy + m(R_TEXT) * math.sin(a))), m(11))
    surf.blit(cool, (0, 0))

    # inner wall down into the enamel: an inward-facing bevel, so its lit side
    # is opposite the outer rim's — the read that says "this is a well".
    lit_ring(surf, cx, cy, m(R_ANN_IN + 1.4), m(4.2), normal_out=False,
             gain=1.15)
    ink_ring(surf, cx, cy, m(R_ANN_IN - 1.2), max(1, m(1.4)), PATINA, 220)

    # ── the enamel field: hard oxblood, fired flush, mirror-polished ─────────
    cabochon(surf, cx, cy, m(R_FIELD), glass_lo=ENAMEL_HI, glass_hi=ENAMEL_LO)

    sf = font(24)
    gradient_text(surf, "START", sf, (cx, cy + m(2)),
                  (255, 244, 214), (216, 158, 60),
                  keyline=(38, 8, 10), kw=m(1.1), shadow=True, tracking=m(2.5),
                  weight=m(1.2))

    cabochon_glass(surf, cx, cy, m(R_FIELD), tint=(250, 226, 226))

    # subsurface bloom: light that went THROUGH the glass and came back out of
    # the far side. Without it the field is a painted disc, not glass over
    # colour.
    bloom = pygame.Surface(canvas, pygame.SRCALPHA)
    br_r = m(R_FIELD)
    bxx = cx - int(KEY_V[0] * br_r * 0.46)
    byy = cy - int(KEY_V[1] * br_r * 0.46)
    for k in range(10, 0, -1):
        rr = int(br_r * 0.86 * k / 10)
        a = 34 * (1 - (k - 1) / 10) ** 1.6 / 255.0
        pygame.draw.circle(bloom, (*[int(c * a) for c in ENAMEL_BLOOM], 255),
                           (bxx, byy), rr)
    cut = pygame.Surface(canvas, pygame.SRCALPHA)
    pygame.draw.circle(cut, (255, 255, 255, 255), (cx, cy), m(R_FIELD - 2))
    bloom.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    return surf


def _crop_about_pivot(surf):
    """Re-frame the SS lockup so the suspension ring sits at the sprite centre:
    rotating about the centre is then rotating about the pivot, which is the
    only reason the 12 swing bakes can be plain pygame rotations."""
    px, py = m(PIVOT[0]), m(PIVOT[1])
    used = surf.get_bounding_rect()
    hw = max(abs(used.left - px), abs(used.right - px)) + m(3)
    hh = max(abs(used.top - py), abs(used.bottom - py)) + m(3)
    out = pygame.Surface((hw * 2, hh * 2), pygame.SRCALPHA)
    out.blit(surf, (hw - px, hh - py))
    return out


def seal_swing_frames():
    """12 pre-baked swing rotations at the FINAL 1x size. The runtime indexes
    this list per frame and blits — there is no runtime rotation anywhere, and
    each frame still passes through exactly ONE smoothscale from SS."""
    if "swing" in _seal_cache:
        return _seal_cache["swing"]
    big = _crop_about_pivot(build_seal_device())
    frames = []
    for i in range(SWING_FRAMES):
        ang = SWING_DEG * math.sin(2 * math.pi * i / SWING_FRAMES)
        rot = pygame.transform.rotate(big, ang) if ang else big
        w, hgt = rot.get_size()
        frames.append(pygame.transform.smoothscale(rot, (w // SS, hgt // SS)))
    _seal_cache["swing"] = frames
    return frames


def sweep_sprites():
    """The specular sweep: two pre-baked highlight arcs 12 deg apart, cross-faded
    per frame so the shine on the brass drifts +/-6 deg over ~9 s. Baked at SS
    with the rest of the metal, downscaled once."""
    if "sweep" in _seal_cache:
        return _seal_cache["sweep"]
    out = []
    size = m(R_OUT * 2 + 6)
    for sgn in (-1, 1):
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        spec = math.radians(KEY_DEG + sgn * SWEEP_DEG)
        n = 460
        for rr, wpx, k in ((R_BEVEL + 2.0, 6.0, 1.0),
                           (R_MILL, 9.0, 0.40),
                           (R_TEXT, 20.0, 0.30),
                           (R_ANN_IN + 1.4, 4.2, 0.62)):
            lay = pygame.Surface((size, size), pygame.SRCALPHA)
            for i in range(n):
                a = 2 * math.pi * i / n
                d = math.cos(a - spec)
                if d <= 0.0:
                    continue
                al = int(150 * (d ** 6) * k)
                if al <= 1:
                    continue
                pygame.draw.circle(lay, (*KEY_WARM, al),
                                   (int(c + m(rr) * math.cos(a)),
                                    int(c + m(rr) * math.sin(a))),
                                   max(1, m(wpx / 2)))
            s.blit(lay, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)
        hole = pygame.Surface((size, size), pygame.SRCALPHA)
        hole.fill((255, 255, 255, 255))
        pygame.draw.circle(hole, (0, 0, 0, 0), (c, c), m(R_FIELD + 1))
        s.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        out.append(pygame.transform.smoothscale(s, (size // SS, size // SS)))
    _seal_cache["sweep"] = out
    return out


# =============================================================================
# the hanger — ribbon, wax seal, suspension ring, Pip. Static: it hangs from
# the pivot, so it does NOT swing with the seal.
# =============================================================================
def _grosgrain(surf, quad, base, stripe=RIB_PUTTY, frac=0.38):
    """A flat two-tone grosgrain band: navy ground, broad putty centre stripe,
    ochre pinstripes at the stripe edges, and the woven rib running ACROSS the
    length. Deliberately unlit — nothing on this screen is lit but the seal."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = quad

    def cross(f):
        return ((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f),
                (x3 + (x2 - x3) * f, y3 + (y2 - y3) * f))

    pygame.draw.polygon(surf, base, quad)
    lo, hi = 0.5 - frac / 2, 0.5 + frac / 2
    (ax, ay), (bx, by) = cross(lo)
    (cx2, cy2), (dx, dy) = cross(hi)
    pygame.draw.polygon(surf, stripe, [(ax, ay), (cx2, cy2), (dx, dy),
                                       (bx, by)])
    rib_d = tuple(int(c * 0.74) for c in base[:3])
    rib_l = tuple(int(c * 0.86) for c in stripe[:3])
    steps = max(6, int(math.hypot(x3 - x0, y3 - y0) / m(3)))
    for i in range(steps):
        if i % 2:
            continue
        t = i / (steps - 1)
        for f0, f1, col in ((0.0, lo, rib_d), (lo, hi, rib_l),
                            (hi, 1.0, rib_d)):
            (px0, py0), (px1, py1) = cross(f0)
            (qx0, qy0), (qx1, qy1) = cross(f1)
            pygame.draw.line(surf, col,
                             (px0 + (px1 - px0) * t, py0 + (py1 - py0) * t),
                             (qx0 + (qx1 - qx0) * t, qy0 + (qy1 - qy0) * t),
                             m(1))
    for f in (lo, hi):
        (ax, ay), (bx, by) = cross(f)
        pygame.draw.line(surf, RIB_OCHRE, (ax, ay), (bx, by), m(1.8))
    pygame.draw.line(surf, RIB_DARK_2, (x0, y0), (x3, y3), m(1.6))
    pygame.draw.line(surf, RIB_DARK_2, (x1, y1), (x2, y2), m(1.6))


def _band(p0, p1, w0, w1):
    """Quad for a band from p0 to p1 with widths w0/w1, perpendicular to run."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    return [(m(p0[0] - nx * w0 / 2), m(p0[1] - ny * w0 / 2)),
            (m(p0[0] + nx * w0 / 2), m(p0[1] + ny * w0 / 2)),
            (m(p1[0] + nx * w1 / 2), m(p1[1] + ny * w1 / 2)),
            (m(p1[0] - nx * w1 / 2), m(p1[1] - ny * w1 / 2))]


def _swallowtail(surf, p, along, w, depth, base, stripe=RIB_PUTTY,
                 frac=0.38):
    """The forked ribbon end. A swallowtail is not a coin shape and not a
    rectangle — it is the cheapest silhouette signal that this is a ribbon."""
    dx, dy = along
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux

    def fork(half, col):
        pygame.draw.polygon(surf, col, [
            (m(p[0] - nx * half), m(p[1] - ny * half)),
            (m(p[0] + nx * half), m(p[1] + ny * half)),
            (m(p[0] + nx * half + ux * depth),
             m(p[1] + ny * half + uy * depth)),
            (m(p[0] + ux * depth * (0.42 + 0.58 * (1 - half / (w / 2)))),
             m(p[1] + uy * depth * (0.42 + 0.58 * (1 - half / (w / 2))))),
            (m(p[0] - nx * half + ux * depth),
             m(p[1] - ny * half + uy * depth)),
        ])

    fork(w / 2, base)
    fork(w * frac / 2, stripe)


def wax_blob(surf, cx, cy, rx, ry, seed=0, hi=WAX_HI, lo=WAX_LO, rim=True):
    """Poured sealing wax: an irregular pool of overlapping discs with a soft
    pale rim so the (unlit, low-saturation) shape still separates from a night
    sky. Flat by design — all the light in this scene belongs to the seal."""
    lobes = [(0.0, 0.0, 1.0), (0.62, -0.24, 0.52), (-0.58, 0.2, 0.55),
             (0.3, 0.44, 0.46), (-0.34, -0.42, 0.44), (0.05, -0.6, 0.4)]
    body = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for i, (fx, fy, fr) in enumerate(lobes):
        j = ((seed * 7 + i * 13) % 5 - 2) * 0.03
        pygame.draw.ellipse(body, (*lo, 255), pygame.Rect(
            int(cx + fx * rx - rx * fr * (1 + j)),
            int(cy + fy * ry - ry * fr * (1 + j)),
            int(2 * rx * fr * (1 + j)), int(2 * ry * fr * (1 + j))))
    inner = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for k in range(8, 0, -1):
        f = k / 8.0
        col = lerp_stops([(0.0, hi), (1.0, lo)], 1.0 - f)
        pygame.draw.ellipse(inner, (*col, 255), pygame.Rect(
            int(cx - rx * 0.92 * f), int(cy - ry * 0.92 * f),
            int(2 * rx * 0.92 * f), int(2 * ry * 0.92 * f)))
    keep = body.copy()
    keep.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    inner.blit(keep, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(inner, (0, 0))
    surf.blit(body, (0, 0))
    if rim:
        edge = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        for i, (fx, fy, fr) in enumerate(lobes):
            j = ((seed * 7 + i * 13) % 5 - 2) * 0.03
            pygame.draw.ellipse(edge, (*WAX_RIM, 230), pygame.Rect(
                int(cx + fx * rx - rx * fr * (1 + j)),
                int(cy + fy * ry - ry * fr * (1 + j)),
                int(2 * rx * fr * (1 + j)), int(2 * ry * fr * (1 + j))),
                max(1, m(1.2)))
        hole = body.copy()
        hole.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        shrunk = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        for i, (fx, fy, fr) in enumerate(lobes):
            j = ((seed * 7 + i * 13) % 5 - 2) * 0.03
            k = 0.90
            pygame.draw.ellipse(shrunk, (255, 255, 255, 255), pygame.Rect(
                int(cx + fx * rx - rx * fr * (1 + j) * k),
                int(cy + fy * ry - ry * fr * (1 + j) * k),
                int(2 * rx * fr * (1 + j) * k), int(2 * ry * fr * (1 + j) * k)))
        edge.blit(shrunk, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        surf.blit(edge, (0, 0))


_pip_cache = {}


def pip_sprite():
    """Pip at SS with the REAL equipped skin + parcel. Cached on
    (skin, parcel) — never at import — because the player can change either in
    the Store and come straight back to this screen."""
    store_data.load()
    key = (store_data.equipped("skin") or "skin_base",
           store_data.equipped("parcel"))
    if key in _pip_cache:
        return _pip_cache[key]
    skin, parcel_id = key
    s = PIP_SCALE * SS
    if skin == "skin_base":
        body = parrot._add_outline_scaled(
            parrot._build_frame_scaled(parrot._WING_ANGLES[0], s), s)
    else:
        base = parrot.get_skin_frame(skin, 0, 0.0)
        bw, bh = base.get_size()
        body = pygame.transform.smoothscale(base, (int(bw * s), int(bh * s)))
    parcel = parrot.get_parcel("normal", parcel_id)
    pw, ph = parcel.get_size()
    parcel = pygame.transform.smoothscale(parcel, (int(pw * s), int(ph * s)))
    bw, bh = body.get_size()
    pad = parcel.get_height()
    sheet = pygame.Surface((bw, bh + pad), pygame.SRCALPHA)
    sheet.blit(body, (0, 0))
    pr = parcel.get_rect(center=(bw // 2, bh // 2 + int(PARCEL_Y_OFFSET * s)))
    sheet.blit(parcel, pr.topleft)
    sheet.blit(_rim_light(sheet, color=KEY_WARM, alpha=95,
                          off=max(1, m(0.9))), (0, 0))
    _pip_cache[key] = (sheet, (bw // 2, bh // 2))
    return _pip_cache[key]


def pip_head(diameter):
    store_data.load()
    key = ("head", store_data.equipped("skin") or "skin_base", diameter)
    if key in _pip_cache:
        return _pip_cache[key]
    skin = key[1]
    if skin == "skin_base":
        src = parrot._add_outline_scaled(
            parrot._build_frame_scaled(parrot._WING_ANGLES[1], 3.0), 3.0)
    else:
        base = parrot.get_skin_frame(skin, 1, 0.0)
        src = pygame.transform.smoothscale(
            base, (base.get_width() * 3, base.get_height() * 3))
    box = pygame.Rect(33 * 3, 6 * 3, 32 * 3, 32 * 3).clip(src.get_rect())
    head = pygame.transform.smoothscale(src.subsurface(box).copy(),
                                        (diameter, diameter))
    _pip_cache[key] = head
    return head


def build_hanger_device():
    """Ribbon + wax + suspension ring + Pip, at SS. Baked once and blitted; it
    hangs from the pivot so it does not move when the seal swings."""
    surf = pygame.Surface((DW, DH), pygame.SRCALPHA)
    ring = (PIVOT[0], PIVOT[1])

    _grosgrain(surf, _band((124, -16), (164, 112), 62, 58), RIB_DARK)
    _grosgrain(surf, _band((180, 180), (206, 66), 46, 42), RIB_DARK_2)
    _swallowtail(surf, (206, 66), (0.22, -0.97), 42, 22, RIB_DARK_2)
    _grosgrain(surf, _band((164, 104), (180, 192), 58, 54), RIB_DARK)

    # the wax that seals the crossing
    wax_blob(surf, m(184), m(120), m(15), m(13), seed=3,
             hi=(150, 40, 36), lo=(88, 20, 22))

    # the ring is METAL and the ribbon threads it, so the ring reads OVER the
    # strands except where the strand wraps across its lower front
    lit_ring(surf, m(ring[0]), m(ring[1]), m(RING_R - 3.2), m(6.4), gain=1.2)
    ink_ring(surf, m(ring[0]), m(ring[1]), m(RING_R), max(1, m(1.1)),
             PATINA_DEEP, 220)
    ink_ring(surf, m(ring[0]), m(ring[1]), m(RING_R - 6.4), max(1, m(1.1)),
             PATINA, 210)
    pygame.draw.polygon(surf, RIB_DARK, _band((180, 176), (180, 198), 24, 24))
    pygame.draw.line(surf, RIB_DARK_2, (m(168), m(182)), (m(192), m(182)),
                     m(1.2))

    pip, anchor = pip_sprite()
    ppos = (m(PIP_C[0]) - anchor[0], m(PIP_C[1]) - anchor[1])

    # the hooked foot: he has just hung his badge on the ring
    leg = [(230, 150), (214, 166), (199, 180)]
    for wpx, col in ((4.2, (44, 32, 26)), (2.6, (150, 122, 84))):
        pygame.draw.lines(surf, col, False,
                          [(m(x), m(y)) for x, y in leg], max(1, m(wpx)))
    pygame.draw.arc(surf, (44, 32, 26),
                    pygame.Rect(m(188), m(170), m(20), m(20)),
                    math.radians(-40), math.radians(190), max(1, m(3.4)))
    pygame.draw.arc(surf, (170, 140, 96),
                    pygame.Rect(m(188.6), m(170.6), m(19), m(19)),
                    math.radians(20), math.radians(180), max(1, m(1.6)))
    surf.blit(pip, ppos)
    return surf


# =============================================================================
# background — sky demoted, bokeh + veil instead of a real blur
# =============================================================================
_BOKEH = [(-8, 96, 54), (72, 58, 34), (196, 34, 44), (312, 92, 60),
          (352, 208, 46), (26, 236, 40), (150, 176, 30), (300, 300, 52),
          (18, 402, 58), (338, 430, 44), (108, 520, 50), (250, 560, 38),
          (60, 610, 44), (196, 624, 34), (150, 6, 28)]


def cordy(x):
    t = (x - W / 2) / (W / 2)
    return CORD_Y0 + CORD_SAG * (1.0 - t * t)


def tag_rects():
    rects = []
    for cx in TAG_CX:
        cy = int(cordy(cx)) + 10 + TAG_H // 2
        rects.append(pygame.Rect(cx - TAG_W // 2, cy - TAG_HIT_H // 2,
                                 TAG_W, TAG_HIT_H))
    return rects


def start_rect():
    r = pygame.Rect(0, 0, R_OUT * 2, R_OUT * 2)
    r.center = SEAL_C
    return r


def build_base_device(phase):
    """Everything BEHIND the seal, composed at SS: the live alpine_haze sky with
    every high-frequency element removed, a baked bokeh field, a veiling scrim,
    the ribbon tails, the strung cord and its wax tags, and a whisper of corner
    lens falloff in front of the lot."""
    surf = pygame.Surface((DW, DH))
    pal = _biome.palette_for_phase(phase)
    if not sky_designs.render_active(surf, DW, DH, GROUND_Y * SS, pal, phase):
        raise RuntimeError("alpine_haze sky design is not active")

    # Defocus for one blit: large-scale bokeh + a veiling scrim, and NO
    # mountains, clouds or foreground at all. Removing the high-frequency
    # detail is what actually sells "thrown a mile behind and out of focus";
    # the discs just give the blur something to have blurred.
    hi = sample_mean(surf, [(DW // 2, int(DH * 0.12)), (DW // 4, int(DH * 0.2))])
    lo = sample_mean(surf, [(DW // 2, int(DH * 0.86)), (DW // 4, int(DH * 0.78))])
    veil_top = tuple(min(255, int(c * 0.55 + 255 * 0.45)) for c in hi)
    veil_bot = tuple(min(255, int(c * 0.62 + 255 * 0.38)) for c in lo)
    bok = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for bx, by, brd in _BOKEH:
        f = by / H
        col = tuple(int(a + (b - a) * f) for a, b in zip(veil_top, veil_bot))
        for k in range(7, 0, -1):
            rr = int(m(brd) * (0.55 + 0.45 * k / 7))
            a = int(24 * (1 - (k - 1) / 7) ** 1.5) + 4
            pygame.draw.circle(bok, (*col, a), (m(bx), m(by)), rr)
        pygame.draw.circle(bok, (*col, 12), (m(bx), m(by)), m(brd),
                           max(1, m(1.6)))
    surf.blit(bok, (0, 0))

    mid = tuple((a + b) // 2 for a, b in zip(veil_top, veil_bot))
    veil = multistop_v(DW, DH, [(0.0, veil_top), (0.42, mid), (0.58, mid),
                                (1.0, veil_bot)])
    veil.set_alpha(96)
    surf.blit(veil, (0, 0))

    # ribbon tails: they vanish behind the planchet and reappear below it, which
    # is the cheapest possible statement that the seal is a solid object in
    # front of something.
    rib = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for sgn, tip in ((-1, (100, 470)), (1, (260, 470))):
        top = (180 + sgn * 26, 214)
        _grosgrain(rib, _band(top, tip, 46, 52), RIB_DARK)
        _swallowtail(rib, tip, (sgn * 0.28, 0.96), 52, 26, RIB_DARK)
    surf.blit(rib, (0, 0))

    # contact shadow the seal casts onto the tails / veil
    sh = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for k in range(14, 0, -1):
        a = int(52 * (1 - (k - 1) / 14) ** 1.6)
        pygame.draw.circle(sh, (18, 14, 12, a),
                           (m(SEAL_C[0] + 5), m(SEAL_C[1] + 7)),
                           m(R_OUT) + m(k * 0.9))
    surf.blit(sh, (0, 0))

    # the strung cord + its wax tags
    pts = [(m(x), m(cordy(x))) for x in range(-4, W + 6, 6)]
    pygame.draw.lines(surf, CORD_DK, False,
                      [(x, y + m(1.4)) for x, y in pts], max(1, m(2.6)))
    pygame.draw.lines(surf, CORD, False, pts, max(1, m(1.8)))
    for hx in (100, 260):
        pygame.draw.circle(surf, CORD_DK, (m(hx), m(cordy(hx))), m(4.5))
        pygame.draw.circle(surf, CORD, (m(hx), m(cordy(hx))), m(3.2))

    lf = font(LABEL_SIZE)
    for i, ((label, _kind), cx) in enumerate(zip(TAGS, TAG_CX)):
        cy = cordy(cx) + 10 + TAG_H / 2
        pygame.draw.line(surf, CORD_DK, (m(cx), m(cordy(cx))),
                         (m(cx), m(cy - TAG_H * 0.36)), max(1, m(2.4)))
        wax_blob(surf, m(cx), m(cy), m(TAG_W / 2), m(TAG_H / 2), seed=i + 1)
        plain_text(surf, label, lf, (m(cx), m(cy)), WAX_LABEL,
                   shadow_a=170, tracking=m(0.6), weight=m(0.8),
                   keyline=(40, 14, 16), kw=m(0.8))

    # corner lens falloff — you are close to this object
    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    cxm, cym = DW / 2, DH / 2
    maxd = math.hypot(cxm, cym)
    for k in range(26):
        f = 1.0 - k / 26.0
        a = int(54 * f ** 2.2)
        if a <= 0:
            continue
        rr = int(maxd * (0.62 + 0.42 * k / 26.0))
        ring = pygame.Surface((DW, DH), pygame.SRCALPHA)
        pygame.draw.rect(ring, (10, 12, 20, a), ring.get_rect())
        hole = pygame.Surface((DW, DH), pygame.SRCALPHA)
        hole.fill((255, 255, 255, 255))
        pygame.draw.ellipse(hole, (0, 0, 0, 0),
                            pygame.Rect(int(cxm - rr), int(cym - rr * 1.15),
                                        int(rr * 2), int(rr * 2.3)))
        ring.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(ring, (0, 0))
    return surf


# =============================================================================
# frame assembly — the honest runtime path: 1 base blit + 1 seal + 2 sweep + 1
# hanger, all pre-baked, zero per-frame rasterisation.
# =============================================================================
_base_cache = {}


def base_1x(phase_key, phase):
    if phase_key not in _base_cache:
        _base_cache[phase_key] = downscale(build_base_device(phase))
    return _base_cache[phase_key]


_hanger_cache = {}


def hanger_1x():
    store_data.load()
    key = (store_data.equipped("skin") or "skin_base",
           store_data.equipped("parcel"))
    if key not in _hanger_cache:
        _hanger_cache[key] = downscale(build_hanger_device())
    return _hanger_cache[key]


def render_frame(phase_key, phase, t=0.0):
    base = base_1x(phase_key, phase)
    surf = base.copy()

    swing = seal_swing_frames()
    idx = int(round((0.25 * t * SWING_FRAMES) % SWING_FRAMES)) % SWING_FRAMES
    sp = swing[idx]
    surf.blit(sp, sp.get_rect(center=PIVOT))

    a = 0.5 + 0.5 * math.sin(2 * math.pi * t / 9.0)
    sa, sb = sweep_sprites()
    for spr, al in ((sa, int(255 * (1 - a))), (sb, int(255 * a))):
        spr.set_alpha(al)
        surf.blit(spr, spr.get_rect(center=SEAL_C))

    hang = hanger_1x()
    surf.blit(hang, (0, 0))
    return surf, base


# =============================================================================
# review sheet
# =============================================================================
CURRENT_PNG = os.path.join(REPO, "docs", "main-menu", "current_ingame.png")
R1_PNG = os.path.join(OUT, "round_1_day.png")


def detail_column(width):
    """Scale + detail views: the seal at 2x, the annulus macro, the swing
    filmstrip and the two specular bakes."""
    col = pygame.Surface((width, 1000), pygame.SRCALPHA)
    col.fill((0, 0, 0, 0))
    f = _font(15, True)
    fs = _font(12, True)
    y = 0

    frame, _b = render_frame("day", _biome.phase_for_time(0.12 * _biome.CYCLE_SECONDS))
    hero = frame.subsurface(pygame.Rect(52, 150, 256, 320)).copy()
    hero2 = pygame.transform.smoothscale(hero, (256 * 2, 320 * 2))
    col.blit(f.render("SEAL @ 2x  (200 px hero in a 360 px canvas)", True,
                      (222, 208, 178)), (0, y))
    y += 22
    view = pygame.transform.smoothscale(hero2, (width, int(width * 320 / 256)))
    col.blit(view, (0, y))
    pygame.draw.rect(col, (70, 70, 88),
                     pygame.Rect(0, y, view.get_width(), view.get_height()), 1)
    y += view.get_height() + 16

    col.blit(f.render("ANNULUS MACRO  mill / bevel / incuse line", True,
                      (222, 208, 178)), (0, y))
    y += 22
    macro = frame.subsurface(pygame.Rect(76, 228, 112, 84)).copy()
    macro = pygame.transform.scale(macro, (width, int(width * 84 / 112)))
    col.blit(macro, (0, y))
    pygame.draw.rect(col, (70, 70, 88),
                     pygame.Rect(0, y, macro.get_width(), macro.get_height()), 1)
    y += macro.get_height() + 16

    col.blit(f.render("SWING  12 pre-baked rotations (4 shown)", True,
                      (222, 208, 178)), (0, y))
    y += 22
    swing = seal_swing_frames()
    strip_w = width // 4
    cw, ch = 250, 240
    for k, i in enumerate((0, 3, 6, 9)):
        sp = swing[i]
        crop = pygame.Surface((cw, ch))
        crop.fill((26, 24, 30))
        crop.blit(sp, (cw // 2 - sp.get_width() // 2,
                       -(sp.get_height() // 2 - 30)))
        crop = pygame.transform.smoothscale(
            crop, (strip_w - 4, int((strip_w - 4) * ch / cw)))
        col.blit(crop, (k * strip_w, y))
        col.blit(fs.render(f"{i}", True, (150, 152, 168)),
                 (k * strip_w + 2, y + crop.get_height() - 14))
    y += int((strip_w - 4) * ch / cw) + 22

    col.blit(f.render("SPECULAR SWEEP  A / B  (+/-6 deg, ~9 s)", True,
                      (222, 208, 178)), (0, y))
    y += 22
    sa, sb = sweep_sprites()
    for k, spr in enumerate((sa, sb)):
        plate = pygame.Surface(spr.get_size())
        plate.fill((26, 24, 30))
        cp = spr.copy()
        cp.set_alpha(255)
        plate.blit(cp, (0, 0))
        sc = pygame.transform.smoothscale(plate, (width // 2 - 6,
                                                  width // 2 - 6))
        col.blit(sc, (k * (width // 2), y))
    y += width // 2 + 8
    return col.subsurface(pygame.Rect(0, 0, width, min(1000, y))).copy()


def build_sheet(frames, thumb_src):
    pad, gap = 22, 16
    head, cap = 74, 30
    side = 300
    current = (pygame.image.load(CURRENT_PNG).convert()
               if os.path.exists(CURRENT_PNG) else None)
    r1 = (pygame.image.load(R1_PNG).convert()
          if os.path.exists(R1_PNG) else None)
    refs = [(current, "CURRENT  live menu"), (r1, "ROUND 1  (rejected)")]
    refs = [r for r in refs if r[0] is not None]
    cols = 4 + len(refs)
    detail = detail_column(side)
    band = 214
    body_h = max(H + cap + band, detail.get_height())
    sheet_w = pad * 2 + W * cols + gap * (cols - 1) + gap + side
    sheet_h = head + body_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 26))

    sheet.blit(_font(31, True).render(
        "MAIN MENU v2  —  ONE-BUTTON  —  ROUND 2  —  THEME A: THE DISPATCH SEAL",
        True, (245, 226, 178)), (pad, 14))
    sheet.blit(_font(15, True).render(
        "a struck brass + oxblood-enamel courier seal on a ribbon, one hard raking key, "
        "sky thrown a mile back and defocused   ·   SS=2 compose + one downscale   ·   "
        "alpine_haze, four keyframes, 1x",
        True, (150, 152, 168)), (pad, 46))

    f_cap = _font(16, True)
    x = pad
    for img, label in refs:
        sheet.blit(img, (x, head))
        pygame.draw.rect(sheet, (70, 70, 88),
                         pygame.Rect(x - 1, head - 1, W + 2, H + 2), 1)
        sheet.blit(f_cap.render(label, True, (150, 152, 168)),
                   (x, head + H + 8))
        x += W + gap
    for (name, t), (frame, _bg) in zip(PHASES, frames):
        sheet.blit(frame, (x, head))
        pygame.draw.rect(sheet, (70, 70, 88),
                         pygame.Rect(x - 1, head - 1, W + 2, H + 2), 1)
        sheet.blit(f_cap.render(f"{name.upper()}   t={t:.2f}", True,
                                (208, 196, 168)), (x, head + H + 8))
        x += W + gap

    dx = x
    sheet.blit(detail, (dx, head))

    # the coin test, under the phase strip
    ty = head + H + cap + 6
    thumb = pygame.transform.grayscale(
        pygame.transform.smoothscale(thumb_src, (90, 160)))
    sheet.blit(f_cap.render("90x160 GREYSCALE — the coin test", True,
                            (208, 196, 168)), (pad, ty))
    sheet.blit(thumb, (pad, ty + 24))
    pygame.draw.rect(sheet, (70, 70, 88),
                     pygame.Rect(pad - 1, ty + 23, 92, 162), 1)
    f_note = _font(13, True)
    notes = [
        "SILHOUETTE, not surface:",
        " rope-milled bead edge,",
        " 4 cardinal lugs, a",
        " suspension bar + ring,",
        " ribbon off the top edge.",
        "",
        "Brass ramp is NON-",
        "MONOTONIC: stop 4 is",
        "darker than stop 5, so",
        "the far rim bounces.",
        "",
        "Patina (28,34,28) in the",
        "recesses — never black.",
        "",
        "All ornament lives in ONE",
        "annulus. Inside it: one",
        "oxblood dome + START.",
        "Outside it: nothing.",
        "",
        "No sparkles anywhere.",
    ]
    col_x, ny = pad + 112, ty + 24
    for line in notes:
        if ny > ty + 24 + 9 * 17:
            col_x, ny = pad + 112 + 210, ty + 24
        sheet.blit(f_note.render(line, True, (176, 178, 194)), (col_x, ny))
        ny += 17
    return sheet


# =============================================================================
def main():
    os.makedirs(OUT, exist_ok=True)
    frames = []
    for name, t in PHASES:
        phase = _biome.phase_for_time(t * _biome.CYCLE_SECONDS)
        fr = render_frame(name, phase, t=2.4)
        frames.append(fr)
        pygame.image.save(fr[0], os.path.join(OUT, f"round_2_{name}.png"))
    sheet = build_sheet(frames, frames[0][0])
    pygame.image.save(sheet, os.path.join(OUT, "round_2.png"))
    report(frames)


def report(frames):
    cx, cy = SEAL_C
    print("\n=== 1. SEAL-vs-SKY TWO-TONE PAIR (patina mill leg / brass edge+bevel leg)")
    print("    12 bearings, all clear of the four lugs. At each one: the DARKEST")
    print("    pixel in the mill band and the BRIGHTEST pixel on the polished")
    print("    edge wire + inner bevel, each against the background 8-16 px out.")
    bearings = [22, 52, 68, 112, 128, 158, 202, 232, 248, 292, 308, 338]
    worst_all = 99.0
    for (name, _t), (frame, base) in zip(PHASES, frames):
        worst, wat = 99.0, None
        for b in bearings:
            mill = darkest(frame, ring_box(cx, cy, R_MILL, b, 5))
            bev = brightest(frame, ring_box(cx, cy, (R_OUT + R_BEVEL) / 2, b,
                                            int((R_OUT - R_BEVEL) / 2)))
            sky = sample_mean(base, [(cx + rr * math.cos(math.radians(b)),
                                      cy + rr * math.sin(math.radians(b)))
                                     for rr in (R_OUT + 6, R_OUT + 10,
                                                R_OUT + 15)])
            mx = max(contrast(mill, sky), contrast(bev, sky))
            if mx < worst:
                worst, wat = mx, (b, mill, bev, sky, contrast(mill, sky),
                                  contrast(bev, sky))
        worst_all = min(worst_all, worst)
        b, mill, bev, sky, c1, c2 = wat
        print(f"  {name:7} worst bearing {b:3d} deg   mill {str(mill):>15}"
              f" ({c1:5.2f})   edge/bevel {str(bev):>15} ({c2:5.2f})"
              f"   bg {str(sky):>15}   max={worst:5.2f}")
    print(f"  WORST max(leg) over 12 bearings x 4 phases: {worst_all:5.2f}"
          f"  -> {'PASS' if worst_all >= 3.0 else 'FAIL'}")

    print("\n=== 2. START on the enamel, all phases (opaque seal = phase-proof)")
    fld = [(cx - 26, cy + 10), (cx + 26, cy + 10), (cx, cy + 16),
           (cx - 40, cy - 2), (cx + 40, cy - 2)]
    for (name, _t), (frame, _b) in zip(PHASES, frames):
        st = brightest(frame, pygame.Rect(cx - 46, cy - 8, 92, 22))
        under = sample_mean(frame, fld)
        print(f"  {name:7} START ink {str(st):>15}  enamel {str(under):>15}"
              f"  contrast={contrast(st, under):5.2f}")

    print("\n=== 3. TAG LABELS on their wax, all phases")
    rects = tag_rects()
    lfm = _font(LABEL_SIZE, True)
    for (name, _t), (frame, _b) in zip(PHASES, frames):
        row = []
        for r, (label, _k) in zip(rects, TAGS):
            lw = lfm.size(label)[0]
            box = pygame.Rect(0, 0, lw + 4, 15)
            box.center = r.center
            ink = brightest(frame, box)
            wax = darkest(frame, box)
            row.append(f"{label}={contrast(ink, wax):5.1f}")
        print(f"  {name:7} " + "   ".join(row))

    print("\n=== 3b. TAG SLAB vs SKY — the same two-tone logic (dark wax / pale rim)")
    for (name, _t), (frame, base) in zip(PHASES, frames):
        row = []
        for r, (label, _k) in zip(rects, TAGS):
            sky = sample_mean(base, [(r.centerx, r.top - 12),
                                     (r.left - 10, r.centery),
                                     (r.right + 10, r.centery)])
            wax = sample_mean(frame, [(r.centerx, r.top + 8),
                                      (r.centerx, r.bottom - 10)])
            box = r.inflate(4, 4)
            hole = pygame.Rect(0, 0, 66, 20)
            hole.center = r.center
            rim = (0, 0, 0)
            for side in (pygame.Rect(box.left, box.top, box.w, 10),
                         pygame.Rect(box.left, box.bottom - 10, box.w, 10),
                         pygame.Rect(box.left, box.top, 12, box.h),
                         pygame.Rect(box.right - 12, box.top, 12, box.h)):
                c = brightest(frame, side)
                if luminance(c) > luminance(rim):
                    rim = c
            legs = (contrast(wax, sky), contrast(rim, sky))
            row.append(f"{label}={max(legs):4.1f}")
        print(f"  {name:7} " + "   ".join(row))

    print("\n=== 3c. RIBBON vs SKY (navy ground / putty centre band)")
    for (name, _t), (frame, base) in zip(PHASES, frames):
        row = []
        for y, rx in ((26, 137), (64, 149), (96, 159), (150, 172)):
            box = pygame.Rect(rx - 9, y - 3, 19, 7)
            put = brightest(frame, box)
            nav = darkest(frame, pygame.Rect(rx - 26, y - 3, 53, 7))
            sky = sample_mean(base, [(rx - 46, y), (rx - 40, y), (300, y)])
            row.append(f"y{y}={max(contrast(put, sky), contrast(nav, sky)):4.1f}")
        print(f"  {name:7} " + "   ".join(row))

    print("\n=== 4. LABEL FIT (12 px bold, tracking 0.6)")
    lf = _font(LABEL_SIZE, True)
    for (label, _k), r in zip(TAGS, rects):
        w = lf.size(label)[0]
        print(f"  {label:9} {w:3d}px wide, cap h={lf.get_height()}px  in a "
              f"{TAG_W}x{TAG_H} wax slab  -> {(TAG_W - w) / 2:5.1f}px/side")
    print(f"  label size = {LABEL_SIZE} px (floor is 12)")

    print("\n=== 5. HIT RECTS")
    named = [("START", start_rect())] + [(l, r) for (l, _k), r
                                         in zip(TAGS, rects)]
    for nm, r in named:
        print(f"  {nm:9} {str(r):40} min-side={min(r.width, r.height)}px")
    ok = True
    for i in range(len(named)):
        for j in range(i + 1, len(named)):
            if named[i][1].colliderect(named[j][1]):
                ok = False
                print(f"  OVERLAP {named[i][0]} x {named[j][0]}")
    gaps = [rects[k + 1].left - rects[k].right for k in range(len(rects) - 1)]
    print(f"  pairwise disjoint: {ok}   tag gaps: {gaps}px   "
          f"margins: L={rects[0].left} R={W - rects[-1].right}")
    print(f"  lowest interactive edge: y={max(r.bottom for _n, r in named)} "
          f"(must be < 624)")

    print("\n=== 6. BRASS RAMP")
    print("  stops:", BRASS_STOPS)
    l4, l5 = luminance(BRASS_STOPS[3][1]), luminance(BRASS_STOPS[4][1])
    print(f"  stop4 L={l4:.4f}  stop5 L={l5:.4f}  "
          f"non-monotonic bounce present: {l5 > l4}")
    frame = frames[0][0]
    lit = brightest(frame, pygame.Rect(cx - 96, cy - 30, 26, 60))
    dark = sample_mean(frame, [(cx + 73, cy + 6), (cx + 73, cy - 6),
                               (cx + 70, cy + 14)])
    rim = sample_mean(frame, [(cx + 81, cy + 4), (cx + 81, cy - 4),
                              (cx + 80, cy + 10)])
    print(f"  lit annulus {str(lit)} L={luminance(lit):.3f}   shadow-side "
          f"annulus {str(dark)} L={luminance(dark):.3f}   far-rim bevel "
          f"{str(rim)} L={luminance(rim):.3f}")
    print(f"  far rim RE-BRIGHTENS out of the shadow side: "
          f"{luminance(rim) > luminance(dark)} "
          f"(+{100 * (luminance(rim) / max(1e-6, luminance(dark)) - 1):.0f}%)")

    print("\n=== 7. PIP")
    store_data.load()
    pip, anchor = pip_sprite()
    print(f"  equipped skin={store_data.equipped('skin') or 'skin_base'}  "
          f"parcel={store_data.equipped('parcel')}  (read live, cache key = "
          f"(skin, parcel))")
    print(f"  sprite {pip.get_width() // SS}x{pip.get_height() // SS} px at 1x, "
          f"scale={PIP_SCALE}, centre={PIP_C}, foot hooks the ring at {PIVOT}")

    print("\n=== 8. PIPELINE")
    sw = seal_swing_frames()
    print(f"  SS={SS}  device canvas {DW}x{DH} -> one smoothscale to {W}x{H}")
    print(f"  swing bakes: {len(sw)} (sizes {sw[0].get_size()}), zero runtime "
          f"rotation")
    print(f"  sweep bakes: {len(sweep_sprites())}, cross-faded by set_alpha")
    print(f"  per-frame cost: 1 base blit + 1 swing blit + 2 sweep blits + "
          f"1 hanger blit = 5 blits, no rasterisation")
    print("  numpy: not imported anywhere in this module")


if __name__ == "__main__":
    main()
