"""Render 5 candidate SHRINK power-up icons that intentionally riff on
the GROW witch-hat icon — same red velvet palette, but each candidate
explores a *dramatically* different mushroom silhouette and a *different
spot colour* so reviewers can pick which 'sibling' shape best reads
as a shrink / miniaturisation pickup:

  V1 stumpy     wide low Russula-style dome on a short fat stem
                — gold spots
  V2 tower      slim-tall body: small cone cap on a long slender stem
                — icy-blue spots
  V3 twin-bud   main cone cap + a smaller bud cap sprouting from the
                side of the stem (mushroom cluster)
                — cream spots (default, GROW-matching)
  V4 puffball   round ball cap, tiny stem (sphere with no point)
                — magenta-pink spots
  V5 pancake    very flat wide disc cap on a slim tall stem
                — teal-mint spots in a single ring across the disc

The output is a single comparison strip:
  Row 1 — REFERENCE  (existing GROW + existing SHRINK icons)
  Row 2 — CANDIDATES (V1..V5)
plus 2x zoom standalones per variant so the cap + spot detail is legible.

Run headless:

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_shrink_icon_variants.py
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from game.entities import (
    _get_grow_body_sprite, _get_shrink_body_sprite, _draw_grow_halo,
)
from game.draw import MUSH_CAP, MUSH_CAP2, MUSH_SPOT, MUSH_STEM


# ── Shared shrink-variant palette (red velvet — matches GROW so the cap ────
#     shape + spot colour are the only differentiators from grow).

SS = 5
VELVET_OUTLINE = ( 60,  15,  25)
VELVET_BODY    = MUSH_CAP                # (125, 30, 45)
VELVET_HI      = MUSH_CAP2               # (180, 60, 75)
VELVET_SHEEN   = (220, 130, 150, 130)
VELVET_RIM_HI  = (220, 120, 130)
STEM_OUTLINE   = (150, 120,  90)
STEM_HI        = (255, 250, 230)
HALO_RGB       = (180,  90, 110)

# Per-variant spot palettes — (rim, body, glint).
SPOT_GOLD     = ((190, 130,  40), (255, 200,  80), (255, 245, 200))
SPOT_ICE      = ((110, 160, 210), (200, 230, 255), (255, 255, 255))
SPOT_CREAM    = ((195, 165, 110), MUSH_SPOT,        (255, 250, 220))
SPOT_MAGENTA  = ((170,  60, 130), (240, 130, 200), (255, 230, 245))
SPOT_TEAL     = (( 60, 160, 130), (170, 230, 200), (240, 255, 245))


# ── Shared building blocks ──────────────────────────────────────────────────

def _shift(pts, ox, oy):
    return [(p[0] + ox, p[1] + oy) for p in pts]


def _stem_polygon(w, h):
    """Generic bulbed-ivory stem at supersample with a FLAT bottom edge —
    the bulb still flares mid-stem but the base is a horizontal line
    instead of tapering to a point, so the mushroom sits squarely on
    the world rather than balancing on a single tip. `(w, h)` are
    display px; the polygon auto-scales for slim/fat/short/tall stems."""
    pts = [
        (0.42 * w, 0.00 * h),      # top-left (narrow neck)
        (0.58 * w, 0.00 * h),
        (0.66 * w, 0.40 * h),      # waist-right
        (0.78 * w, 0.66 * h),      # mid bulb right
        (0.96 * w, 0.88 * h),      # flared base shoulder right
        (0.96 * w, 1.00 * h),      # flat base right (widest point)
        (0.04 * w, 1.00 * h),      # flat base left
        (0.04 * w, 0.88 * h),
        (0.22 * w, 0.66 * h),      # mid bulb left
        (0.34 * w, 0.40 * h),      # waist-left
    ]
    return [(int(x * SS), int(y * SS)) for (x, y) in pts]


def _draw_stem(big, stem_ox, stem_oy, stem_w, stem_h):
    pts = _stem_polygon(stem_w, stem_h)
    pts = _shift(pts, stem_ox, stem_oy)
    pygame.draw.polygon(big, MUSH_STEM,     pts)
    pygame.draw.polygon(big, STEM_OUTLINE,  pts, width=SS)
    # Vertical highlight streak — at 40% of stem width.
    hi_x = stem_ox + int(0.40 * stem_w * SS)
    pygame.draw.line(big, STEM_HI,
                     (hi_x, stem_oy + int(0.10 * stem_h * SS)),
                     (hi_x, stem_oy + int(0.78 * stem_h * SS)), SS)


def _draw_spot(big, x, y, r_body, spot_palette):
    rim, body, glint = spot_palette
    pygame.draw.circle(big, rim,   (x, y), int((r_body + 0.4) * SS))
    pygame.draw.circle(big, body,  (x, y), int(r_body * SS))
    pygame.draw.circle(big, glint, (x - SS // 2, y - SS // 2), max(1, SS // 2))


def _draw_velvet_sheen(big, body_poly, x_frac=0.20, y_frac=0.12,
                       w_frac=0.32, h_frac=0.40):
    sheen = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    xs = [p[0] for p in body_poly]
    ys = [p[1] for p in body_poly]
    bx0, by0 = min(xs), min(ys)
    bw, bh = max(xs) - bx0, max(ys) - by0
    pygame.draw.ellipse(sheen, VELVET_SHEEN,
                        pygame.Rect(bx0 + int(bw * x_frac),
                                    by0 + int(bh * y_frac),
                                    int(bw * w_frac),
                                    int(bh * h_frac)))
    mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), body_poly)
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))


def _draw_scalloped_rim(big, rim_x, rim_y, rim_w, count=5):
    curl_w = rim_w // count
    for i in range(count):
        center = (rim_x + i * curl_w + curl_w // 2, rim_y)
        pygame.draw.circle(big, VELVET_BODY,    center, curl_w // 2)
        pygame.draw.circle(big, VELVET_OUTLINE, center, curl_w // 2, SS)
        pygame.draw.circle(big, VELVET_RIM_HI,
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))


def _finalize(big, sprite_w, sprite_h):
    return pygame.transform.smoothscale(big, (sprite_w, sprite_h))


# ── VARIANT 1 ── STUMPY (wide low Russula dome + short fat stem) ───────────

def variant_stumpy():
    CAP_W, CAP_H = 30, 14
    STEM_W, STEM_H = 14, 10
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox = ((sprite_w - CAP_W) // 2) * SS
    cap_oy = 0
    stem_ox = ((sprite_w - STEM_W) // 2) * SS
    stem_oy = (CAP_H + 2) * SS

    _draw_stem(big, stem_ox, stem_oy, STEM_W, STEM_H)

    # Wide low half-dome. Drawn as a tall ellipse with the bottom half
    # masked out so only the top dome shows. Built on a private surface
    # so the rect-clip doesn't punch holes in the stem we just drew.
    dome = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    outer = pygame.Rect(cap_ox, cap_oy, CAP_W * SS, int(CAP_H * SS * 2))
    inner = outer.inflate(-SS * 2, -SS * 2)
    pygame.draw.ellipse(dome, VELVET_OUTLINE, outer)
    pygame.draw.ellipse(dome, VELVET_BODY,    inner)
    cutoff = cap_oy + int(CAP_H * SS * 0.95)
    pygame.draw.rect(dome, (0, 0, 0, 0),
                     pygame.Rect(0, cutoff, big.get_width(),
                                 big.get_height() - cutoff))
    big.blit(dome, (0, 0))

    # Highlight crescent — left-of-centre.
    pygame.draw.ellipse(big, VELVET_HI,
                        pygame.Rect(cap_ox + int(CAP_W * SS * 0.16),
                                    cap_oy + int(CAP_H * SS * 0.10),
                                    int(CAP_W * SS * 0.34),
                                    int(CAP_H * SS * 0.42)))

    # Sheen body polygon — half-ellipse outline points.
    dome_pts = []
    cx_px = cap_ox + (CAP_W * SS) // 2
    cy_px = cap_oy + int(CAP_H * SS * 0.92)
    for k in range(0, 21):
        t = k / 20.0
        a = math.pi * (1.0 - t)
        x = cx_px + int(math.cos(a) * (CAP_W * SS) * 0.48)
        y = cy_px - int(math.sin(a) * (CAP_H * SS) * 0.95)
        dome_pts.append((x, y))
    dome_pts.append((cap_ox + CAP_W * SS, cy_px))
    dome_pts.append((cap_ox, cy_px))
    _draw_velvet_sheen(big, dome_pts, x_frac=0.18, y_frac=0.08,
                        w_frac=0.30, h_frac=0.32)

    # No scallops — the wide low silhouette already reads distinctly.
    # Spots: 5 in a wide arc to fill the broad cap.
    for fx_frac, fy_frac in (
        (0.18, 0.55), (0.36, 0.32), (0.50, 0.24),
        (0.66, 0.36), (0.82, 0.58),
    ):
        fx = cap_ox + int(CAP_W * fx_frac * SS)
        fy = cap_oy + int(CAP_H * fy_frac * SS)
        _draw_spot(big, fx, fy, 2.0, SPOT_GOLD)

    return _finalize(big, sprite_w, sprite_h), CAP_H


# ── VARIANT 2 ── TOWER (slim tall cone cap on a long slender stem) ─────────

def variant_tower():
    CAP_W, CAP_H = 14, 18
    STEM_W, STEM_H = 9, 30
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox = ((sprite_w - CAP_W) // 2) * SS
    cap_oy = 0
    stem_ox = ((sprite_w - STEM_W) // 2) * SS
    stem_oy = (CAP_H + 2) * SS

    _draw_stem(big, stem_ox, stem_oy, STEM_W, STEM_H)

    # Narrow steeple cone — apex centred, walls steeper than GROW's.
    outline_pts = _shift([
        (CAP_W // 2 * SS, 0),
        (int(CAP_W * 0.88 * SS), int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.96 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.04 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.12 * SS), int(CAP_H * 0.78 * SS)),
    ], cap_ox, cap_oy)
    body_pts = _shift([
        (CAP_W // 2 * SS, 1 * SS),
        (int(CAP_W * 0.84 * SS), int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.92 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.08 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.16 * SS), int(CAP_H * 0.78 * SS)),
    ], cap_ox, cap_oy)
    hi_pts = _shift([
        (CAP_W // 2 * SS - 1 * SS,     1 * SS),
        (int(CAP_W * 0.28 * SS),       int(CAP_H * 0.55 * SS)),
        (int(CAP_W * 0.18 * SS),       int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.34 * SS),       int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.44 * SS),       int(CAP_H * 0.55 * SS)),
    ], cap_ox, cap_oy)
    pygame.draw.polygon(big, VELVET_OUTLINE, outline_pts)
    pygame.draw.polygon(big, VELVET_BODY,    body_pts)
    pygame.draw.polygon(big, VELVET_HI,      hi_pts)

    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS) + cap_ox
    rim_y = int(CAP_H * 0.93 * SS) + cap_oy
    _draw_scalloped_rim(big, rim_x, rim_y, rim_w, count=4)
    _draw_velvet_sheen(big, body_pts)

    # Spots: 3 stacked vertically (cap is too narrow for the 4-grid).
    for fx_frac, fy_frac in ((0.46, 0.28), (0.58, 0.50), (0.40, 0.72)):
        fx = cap_ox + int(CAP_W * fx_frac * SS)
        fy = cap_oy + int(CAP_H * fy_frac * SS)
        _draw_spot(big, fx, fy, 1.6, SPOT_ICE)

    return _finalize(big, sprite_w, sprite_h), CAP_H


# ── VARIANT 3 ── TWIN-BUD (main cone + side bud — mushroom cluster) ────────

def variant_twin_bud():
    CAP_W, CAP_H = 18, 20
    STEM_W, STEM_H = 18, 22
    sprite_w = max(CAP_W, STEM_W) + 12       # leave room for the side bud
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox = 1 * SS
    cap_oy = 0
    stem_ox = (2 + (CAP_W - STEM_W) // 2) * SS
    stem_oy = (CAP_H + 2) * SS

    _draw_stem(big, stem_ox, stem_oy, STEM_W, STEM_H)

    # ── Main cap (grow-style cone, narrower) ──
    outline_pts = _shift([
        (CAP_W // 2 * SS, 0),
        (int(CAP_W * 0.86 * SS), int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.95 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.05 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.14 * SS), int(CAP_H * 0.78 * SS)),
    ], cap_ox, cap_oy)
    body_pts = _shift([
        (CAP_W // 2 * SS, 1 * SS),
        (int(CAP_W * 0.82 * SS), int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.91 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.09 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.18 * SS), int(CAP_H * 0.78 * SS)),
    ], cap_ox, cap_oy)
    hi_pts = _shift([
        (CAP_W // 2 * SS - 1 * SS,     1 * SS),
        (int(CAP_W * 0.32 * SS),       int(CAP_H * 0.55 * SS)),
        (int(CAP_W * 0.22 * SS),       int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.34 * SS),       int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.42 * SS),       int(CAP_H * 0.55 * SS)),
    ], cap_ox, cap_oy)
    pygame.draw.polygon(big, VELVET_OUTLINE, outline_pts)
    pygame.draw.polygon(big, VELVET_BODY,    body_pts)
    pygame.draw.polygon(big, VELVET_HI,      hi_pts)

    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS) + cap_ox
    rim_y = int(CAP_H * 0.93 * SS) + cap_oy
    _draw_scalloped_rim(big, rim_x, rim_y, rim_w)
    _draw_velvet_sheen(big, body_pts)

    # ── Side bud: tiny mushroom emerging mid-stem to the right. ──
    BUD_W, BUD_H = 9, 11
    BUD_STEM_W, BUD_STEM_H = 5, 7
    bud_x_anchor = cap_ox + int((CAP_W + 4) * SS)
    bud_cap_oy   = int((CAP_H * 0.55) * SS)
    bud_stem_oy  = bud_cap_oy + BUD_H * SS

    # Bud stem
    bud_stem_pts = _stem_polygon(BUD_STEM_W, BUD_STEM_H)
    bud_stem_pts = _shift(bud_stem_pts,
                          bud_x_anchor + ((BUD_W - BUD_STEM_W) // 2) * SS,
                          bud_stem_oy)
    pygame.draw.polygon(big, MUSH_STEM,    bud_stem_pts)
    pygame.draw.polygon(big, STEM_OUTLINE, bud_stem_pts, width=SS)

    # Bud cap (mini grow-cone)
    bud_outline = _shift([
        (BUD_W // 2 * SS, 0),
        (int(BUD_W * 0.86 * SS), int(BUD_H * 0.78 * SS)),
        (int(BUD_W * 0.95 * SS), int(BUD_H * 0.92 * SS)),
        (int(BUD_W * 0.05 * SS), int(BUD_H * 0.92 * SS)),
        (int(BUD_W * 0.14 * SS), int(BUD_H * 0.78 * SS)),
    ], bud_x_anchor, bud_cap_oy)
    bud_body = _shift([
        (BUD_W // 2 * SS, 1 * SS),
        (int(BUD_W * 0.82 * SS), int(BUD_H * 0.78 * SS)),
        (int(BUD_W * 0.91 * SS), int(BUD_H * 0.90 * SS)),
        (int(BUD_W * 0.09 * SS), int(BUD_H * 0.90 * SS)),
        (int(BUD_W * 0.18 * SS), int(BUD_H * 0.78 * SS)),
    ], bud_x_anchor, bud_cap_oy)
    pygame.draw.polygon(big, VELVET_OUTLINE, bud_outline)
    pygame.draw.polygon(big, VELVET_BODY,    bud_body)

    # ── Spots: 3 on the main cap, 1 on the bud. ──
    for fx_frac, fy_frac in ((0.50, 0.18), (0.62, 0.45), (0.38, 0.65)):
        fx = cap_ox + int(CAP_W * fx_frac * SS)
        fy = cap_oy + int(CAP_H * fy_frac * SS)
        _draw_spot(big, fx, fy, 2.0, SPOT_CREAM)
    bud_spot_x = bud_x_anchor + int(BUD_W * 0.45 * SS)
    bud_spot_y = bud_cap_oy + int(BUD_H * 0.40 * SS)
    _draw_spot(big, bud_spot_x, bud_spot_y, 1.2, SPOT_CREAM)

    return _finalize(big, sprite_w, sprite_h), CAP_H


# ── VARIANT 4 ── PUFFBALL (round ball cap, tiny stem) ──────────────────────

def variant_puffball():
    CAP_W, CAP_H = 22, 22                  # square footprint → sphere
    STEM_W, STEM_H = 10, 12
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox = ((sprite_w - CAP_W) // 2) * SS
    cap_oy = 0
    stem_ox = ((sprite_w - STEM_W) // 2) * SS
    stem_oy = (CAP_H + 2) * SS

    _draw_stem(big, stem_ox, stem_oy, STEM_W, STEM_H)

    # Sphere: filled circle + outline + crescent highlight.
    cx = cap_ox + (CAP_W * SS) // 2
    cy = cap_oy + (CAP_H * SS) // 2
    r  = (CAP_W * SS) // 2 - SS
    pygame.draw.circle(big, VELVET_OUTLINE, (cx, cy), r + SS)
    pygame.draw.circle(big, VELVET_BODY,    (cx, cy), r)
    # Velvet inner darkening near the bottom for a hint of bulge.
    dark = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(dark, (60, 15, 25, 80),
                       (cx, cy + r // 3), r * 7 // 10)
    big.blit(dark, (0, 0))
    # Highlight kiss — top-left ellipse.
    pygame.draw.ellipse(big, VELVET_HI,
                        pygame.Rect(cx - r + r // 4,
                                    cy - r + r // 4,
                                    r,
                                    r * 2 // 3))
    pygame.draw.ellipse(big, (250, 220, 230),
                        pygame.Rect(cx - r + r // 3,
                                    cy - r + r // 4,
                                    r * 2 // 5,
                                    r // 3))

    # Spots: 4 in a wraparound ring (top + 2 sides + bottom-ish), to
    # sell the spherical curvature.
    for ang_deg, r_frac in (
        ( 250, 0.55),
        ( 320, 0.62),
        (  40, 0.62),
        ( 110, 0.55),
    ):
        a = math.radians(ang_deg)
        sx = cx + int(math.cos(a) * r * r_frac)
        sy = cy + int(math.sin(a) * r * r_frac)
        _draw_spot(big, sx, sy, 1.8, SPOT_MAGENTA)

    return _finalize(big, sprite_w, sprite_h), CAP_H


# ── VARIANT 5 ── PANCAKE (very flat wide disc cap on slim tall stem) ───────

def variant_pancake():
    CAP_W, CAP_H = 30, 8
    STEM_W, STEM_H = 14, 22
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox = ((sprite_w - CAP_W) // 2) * SS
    cap_oy = 0
    stem_ox = ((sprite_w - STEM_W) // 2) * SS
    stem_oy = (CAP_H + 2) * SS

    _draw_stem(big, stem_ox, stem_oy, STEM_W, STEM_H)

    # Disc: two stacked flat ellipses (deep velvet base + lighter top),
    # giving a hint of pancake thickness.
    outer = pygame.Rect(cap_ox, cap_oy, CAP_W * SS, CAP_H * SS)
    inner = outer.inflate(-SS * 2, -SS * 2)
    pygame.draw.ellipse(big, VELVET_OUTLINE, outer)
    pygame.draw.ellipse(big, VELVET_BODY,    inner)
    # Top crescent highlight stretched horizontally.
    pygame.draw.ellipse(big, VELVET_HI,
                        pygame.Rect(cap_ox + int(CAP_W * SS * 0.20),
                                    cap_oy + int(CAP_H * SS * 0.10),
                                    int(CAP_W * SS * 0.50),
                                    int(CAP_H * SS * 0.32)))
    # A second deeper red disc hint underneath for thickness.
    pygame.draw.ellipse(big, VELVET_OUTLINE,
                        pygame.Rect(cap_ox + SS,
                                    cap_oy + int(CAP_H * SS * 0.65),
                                    (CAP_W - 2) * SS,
                                    int(CAP_H * SS * 0.55)))

    # Spots: 4 cream-butter spots in a GROW-style scatter (asymmetric so
    # they don't read as a uniform grid). Cream colour + halo + glint
    # rendering matches the canonical GROW spot exactly.
    for fx_frac, fy_frac in (
        (0.18, 0.48),
        (0.40, 0.30),
        (0.62, 0.55),
        (0.82, 0.36),
    ):
        fx = cap_ox + int(CAP_W * fx_frac * SS)
        fy = cap_oy + int(CAP_H * fy_frac * SS)
        _draw_spot(big, fx, fy, 1.7, SPOT_CREAM)

    return _finalize(big, sprite_w, sprite_h), CAP_H


# ── Strip composition ──────────────────────────────────────────────────────

CELL_W, CELL_H = 96, 124
PAD = 6
TITLE_H = 24
ROW_GAP = 18
BG = (28, 38, 60)
BG_DEEP = (14, 18, 32)
LBL = (220, 230, 250)
TITLE_C = (200, 220, 255)


def _ref_cell(sprite, dx, dy, halo_color, halo_radius, label):
    cell = pygame.Surface((CELL_W, CELL_H)).convert()
    cell.fill(BG)
    cx, cy = CELL_W // 2, CELL_H // 2 - 8
    _draw_grow_halo(cell, cx, cy, pulse=1.2,
                    color_rgb=halo_color, radius=halo_radius, peak_y_off=-2)
    cell.blit(sprite, (cx + dx, cy + dy))
    font = pygame.font.SysFont(None, 15, bold=True)
    t = font.render(label, True, LBL)
    cell.blit(t, (CELL_W // 2 - t.get_width() // 2, CELL_H - 20))
    return cell


def _variant_cell(sprite, cap_h, label, sublabel):
    cell = pygame.Surface((CELL_W, CELL_H)).convert()
    cell.fill(BG)
    cx, cy = CELL_W // 2, CELL_H // 2 - 8
    _draw_grow_halo(cell, cx, cy, pulse=1.2,
                    color_rgb=HALO_RGB, radius=42, peak_y_off=-2)
    sprite_w, sprite_h = sprite.get_size()
    dx = -sprite_w // 2 + 1
    dy = -cap_h + 2
    cell.blit(sprite, (cx + dx, cy + dy))
    font = pygame.font.SysFont(None, 15, bold=True)
    font_s = pygame.font.SysFont(None, 12)
    t = font.render(label, True, LBL)
    s = font_s.render(sublabel, True, (170, 190, 220))
    cell.blit(t, (CELL_W // 2 - t.get_width() // 2, CELL_H - 28))
    cell.blit(s, (CELL_W // 2 - s.get_width() // 2, CELL_H - 14))
    return cell


def _row(title, cells, total_w):
    h = TITLE_H + CELL_H + PAD * 2
    row = pygame.Surface((total_w, h)).convert()
    row.fill(BG_DEEP)
    title_font = pygame.font.SysFont(None, 20, bold=True)
    title_surf = title_font.render(title, True, TITLE_C)
    row.blit(title_surf, (PAD + 2, 2))
    for i, cell in enumerate(cells):
        x = PAD + i * (CELL_W + PAD)
        row.blit(cell, (x, TITLE_H + PAD))
    return row


def main():
    out_dir = os.path.join(_REPO, "docs", "shrink_icon_variants")
    os.makedirs(out_dir, exist_ok=True)

    grow_sprite, grow_dx, grow_dy = _get_grow_body_sprite()
    shrink_sprite = _get_shrink_body_sprite()
    sw, sh = shrink_sprite.get_size()
    shrink_dx = -sw // 2
    shrink_dy = -sh // 2

    ref_cells = (
        _ref_cell(grow_sprite, grow_dx, grow_dy,
                  halo_color=(180, 90, 110), halo_radius=46,
                  label="GROW (reference)"),
        _ref_cell(shrink_sprite, shrink_dx, shrink_dy,
                  halo_color=(80, 220, 230), halo_radius=36,
                  label="SHRINK (current)"),
    )

    builders = (
        ("V1 stumpy",    "wide dome  ·  gold",       variant_stumpy),
        ("V2 tower",     "tall cone  ·  ice-blue",   variant_tower),
        ("V3 twin-bud",  "cap+bud  ·  cream",        variant_twin_bud),
        ("V4 puffball",  "round ball  ·  magenta",   variant_puffball),
        ("V5 pancake",   "flat disc  ·  cream (picked)", variant_pancake),
    )
    variant_cells = []
    variant_sprites = {}
    for label, sublabel, builder in builders:
        sprite, cap_h = builder()
        variant_cells.append(_variant_cell(sprite, cap_h, label, sublabel))
        variant_sprites[label] = sprite

    candidate_w = PAD + (CELL_W + PAD) * len(builders)
    ref_w       = PAD + (CELL_W + PAD) * len(ref_cells)
    total_w     = max(candidate_w, ref_w)

    row_ref  = _row("REFERENCE", ref_cells, total_w)
    row_cand = _row("CANDIDATES", variant_cells, total_w)

    strip = pygame.Surface((total_w,
                            row_ref.get_height() + ROW_GAP
                            + row_cand.get_height())).convert()
    strip.fill(BG_DEEP)
    strip.blit(row_ref,  (0, 0))
    strip.blit(row_cand, (0, row_ref.get_height() + ROW_GAP))

    strip_path = os.path.join(out_dir, "comparison_strip.png")
    pygame.image.save(strip, strip_path)
    print(f"wrote {strip_path}")

    # 2x zoom standalones — easier to evaluate cap detail + spot colours.
    for label, sprite in variant_sprites.items():
        slug = label.split(" ", 1)[1].replace("-", "_")
        big = pygame.Surface((160, 180)).convert()
        big.fill(BG)
        cx, cy = 80, 86
        _draw_grow_halo(big, cx, cy, pulse=1.2,
                        color_rgb=HALO_RGB, radius=58, peak_y_off=-2)
        sw, sh = sprite.get_size()
        scale = 2
        zoomed = pygame.transform.scale(sprite, (sw * scale, sh * scale))
        zsw, zsh = zoomed.get_size()
        big.blit(zoomed, (cx - zsw // 2, cy - zsh // 2 - 4))
        path = os.path.join(out_dir, f"{slug}_2x.png")
        pygame.image.save(big, path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
