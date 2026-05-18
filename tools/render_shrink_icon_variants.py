"""Render 5 candidate SHRINK power-up icons that intentionally riff on
the GROW witch-hat icon.

All five candidates keep the GROW family DNA — velvet cone-style cap,
cream-butter ornaments in the 4-spot canonical layout, ivory bulbed
stem, soft velvet sheen, pulsing radial halo — but each explores a
different cap silhouette so reviewers can pick which "sibling" reads
best as a shrink/miniaturisation pickup:

  variant_1_stout         vertically compressed grow cone (40% shorter)
  variant_2_pixie_hood    grow cone with the tip curled sideways
                          (pixie / sleeping-cap silhouette)
  variant_3_domed         smooth half-dome cap (no point) with scallops
  variant_4_bell          bell-shaped cap, concave lower half
  variant_5_acorn         grow cone with an acorn-cup skirt at the stem

The output is a single comparison strip:
  Row 1 — REFERENCE: existing GROW + existing SHRINK icons
  Row 2 — CANDIDATES: V1..V5

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


# ── Shared shrink-variant palette (red velvet — matches GROW so the only ──
#     thing that distinguishes shrink from grow is the cap silhouette).

SS = 5
VELVET_OUTLINE = ( 60,  15,  25)        # = _GROW_VELVET_OUTLINE
VELVET_BODY    = MUSH_CAP                # = (125, 30, 45)
VELVET_HI      = MUSH_CAP2               # = (180, 60, 75)
VELVET_SHEEN   = (220, 130, 150, 130)   # = _GROW_VELVET_SHEEN
VELVET_RIM_HI  = (220, 120, 130)        # = _GROW_VELVET_RIM_HI
SPOT_HALO      = (195, 165, 110)        # = _GROW_SPOT_HALO
STEM_OUTLINE   = (150, 120,  90)        # = _GROW_STEM_OUTLINE
STEM_HI        = (255, 250, 230)        # = _GROW_STEM_HI
HALO_RGB       = (180,  90, 110)        # = _GROW_HALO_RGB

# Canonical 4-spot ornament layout — same fractions GROW uses.
ORNAMENT_SLOTS = (
    (0.50, 0.18),
    (0.62, 0.42),
    (0.40, 0.62),
    (0.70, 0.72),
)


# ── Shared building blocks ──────────────────────────────────────────────────

def _shift(pts, ox, oy):
    return [(p[0] + ox, p[1] + oy) for p in pts]


def _draw_stem(big, stem_ox, stem_oy):
    """Bulbed ivory stem — identical silhouette to GROW's stem."""
    stem_pts = [
        ( 8 * SS,  0 * SS),
        (12 * SS,  0 * SS),
        (13 * SS, 12 * SS),
        (15 * SS, 18 * SS),
        (10 * SS, 21 * SS),
        ( 5 * SS, 18 * SS),
        ( 7 * SS, 12 * SS),
    ]
    pts = _shift(stem_pts, stem_ox, stem_oy)
    pygame.draw.polygon(big, MUSH_STEM,     pts)
    pygame.draw.polygon(big, STEM_OUTLINE,  pts, width=SS)
    pygame.draw.line(big, STEM_HI,
                     (9 * SS + stem_ox,  2 * SS + stem_oy),
                     (9 * SS + stem_ox, 18 * SS + stem_oy), SS)


def _draw_spots(big, cap_w, cap_h, cap_ox, cap_oy, mask_poly=None):
    """Cream-butter spots in GROW's canonical 4-slot layout.
    `mask_poly` (if given) clips: skips any slot whose pixel sits outside
    the cap silhouette so a variant with a non-rectangular cap doesn't
    paint a spot in empty space."""
    if mask_poly is not None:
        mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), mask_poly)
    for fx_frac, fy_frac in ORNAMENT_SLOTS:
        fx = int(cap_w * fx_frac * SS) + cap_ox
        fy = int(cap_h * fy_frac * SS) + cap_oy
        if mask_poly is not None:
            if mask.get_at((fx, fy))[3] == 0:
                continue
        pygame.draw.circle(big, SPOT_HALO, (fx, fy), int(2.4 * SS))
        pygame.draw.circle(big, MUSH_SPOT, (fx, fy), int(2.0 * SS))
        pygame.draw.circle(big, (255, 255, 250),
                           (fx - SS // 2, fy - SS // 2), max(1, SS // 2))


def _draw_velvet_sheen(big, cap_body_poly):
    """Soft alpha ellipse masked to the cap polygon — same trick GROW uses."""
    sheen = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    xs = [p[0] for p in cap_body_poly]
    ys = [p[1] for p in cap_body_poly]
    bx0, by0 = min(xs), min(ys)
    bw, bh = max(xs) - bx0, max(ys) - by0
    pygame.draw.ellipse(sheen, VELVET_SHEEN,
                        pygame.Rect(bx0 + int(bw * 0.20),
                                    by0 + int(bh * 0.12),
                                    int(bw * 0.32),
                                    int(bh * 0.40)))
    mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), cap_body_poly)
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))


def _draw_scalloped_rim(big, rim_x, rim_y, rim_w, count=5):
    """Curled scalloped rim — same circles-along-the-base trick GROW uses."""
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


# ── VARIANT 1 ── STOUT (vertically compressed grow cone) ───────────────────

def variant_stout():
    CAP_W, CAP_H = 22, 14                  # was 22×24 — 42% shorter
    STEM_W, STEM_H = 20, 22
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox, cap_oy = 1 * SS, 0
    stem_ox, stem_oy = 2 * SS, (CAP_H + 2) * SS

    _draw_stem(big, stem_ox, stem_oy)

    outline_pts = _shift([
        (CAP_W // 2 * SS, 0),
        (int(CAP_W * 0.86 * SS), int(CAP_H * 0.70 * SS)),
        (int(CAP_W * 0.95 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.05 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.14 * SS), int(CAP_H * 0.70 * SS)),
    ], cap_ox, cap_oy)
    body_pts = _shift([
        (CAP_W // 2 * SS, 1 * SS),
        (int(CAP_W * 0.82 * SS), int(CAP_H * 0.70 * SS)),
        (int(CAP_W * 0.91 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.09 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.18 * SS), int(CAP_H * 0.70 * SS)),
    ], cap_ox, cap_oy)
    hi_pts = _shift([
        (CAP_W // 2 * SS - 1 * SS,     1 * SS),
        (int(CAP_W * 0.32 * SS),       int(CAP_H * 0.50 * SS)),
        (int(CAP_W * 0.22 * SS),       int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.34 * SS),       int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.42 * SS),       int(CAP_H * 0.50 * SS)),
    ], cap_ox, cap_oy)
    pygame.draw.polygon(big, VELVET_OUTLINE, outline_pts)
    pygame.draw.polygon(big, VELVET_BODY,    body_pts)
    pygame.draw.polygon(big, VELVET_HI,      hi_pts)

    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS) + cap_ox
    rim_y = int(CAP_H * 0.93 * SS) + cap_oy
    _draw_scalloped_rim(big, rim_x, rim_y, rim_w)
    _draw_velvet_sheen(big, body_pts)
    _draw_spots(big, CAP_W, CAP_H, cap_ox, cap_oy, mask_poly=body_pts)

    return _finalize(big, sprite_w, sprite_h), CAP_H


# ── VARIANT 2 ── PIXIE HOOD (cone with curled-sideways tip) ────────────────

def variant_pixie_hood():
    CAP_W, CAP_H = 22, 24
    STEM_W, STEM_H = 20, 22
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox, cap_oy = 1 * SS, 0
    stem_ox, stem_oy = 2 * SS, (CAP_H + 2) * SS

    _draw_stem(big, stem_ox, stem_oy)

    # Hood curves: tip starts at top-centre but bends to the right then
    # down. Left edge sweeps in a soft S; right edge has the curl.
    outline_pts = _shift([
        (int(CAP_W * 0.74 * SS), int(CAP_H * 0.02 * SS)),    # tip apex
        (int(CAP_W * 0.86 * SS), int(CAP_H * 0.22 * SS)),    # curl shoulder
        (int(CAP_W * 0.78 * SS), int(CAP_H * 0.32 * SS)),    # curl tuck
        (int(CAP_W * 0.94 * SS), int(CAP_H * 0.78 * SS)),    # right base
        (int(CAP_W * 0.96 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.05 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.10 * SS), int(CAP_H * 0.62 * SS)),
        (int(CAP_W * 0.30 * SS), int(CAP_H * 0.28 * SS)),
    ], cap_ox, cap_oy)
    body_pts = _shift([
        (int(CAP_W * 0.74 * SS), int(CAP_H * 0.04 * SS)),
        (int(CAP_W * 0.82 * SS), int(CAP_H * 0.22 * SS)),
        (int(CAP_W * 0.76 * SS), int(CAP_H * 0.32 * SS)),
        (int(CAP_W * 0.90 * SS), int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.92 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.08 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.14 * SS), int(CAP_H * 0.62 * SS)),
        (int(CAP_W * 0.32 * SS), int(CAP_H * 0.28 * SS)),
    ], cap_ox, cap_oy)
    hi_pts = _shift([
        (int(CAP_W * 0.40 * SS), int(CAP_H * 0.32 * SS)),
        (int(CAP_W * 0.30 * SS), int(CAP_H * 0.62 * SS)),
        (int(CAP_W * 0.20 * SS), int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.34 * SS), int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.46 * SS), int(CAP_H * 0.55 * SS)),
    ], cap_ox, cap_oy)
    pygame.draw.polygon(big, VELVET_OUTLINE, outline_pts)
    pygame.draw.polygon(big, VELVET_BODY,    body_pts)
    pygame.draw.polygon(big, VELVET_HI,      hi_pts)

    # Tiny rim-curl pom-pom at the curled tip — sells the "pixie hat" idea.
    pom_x = int(CAP_W * 0.86 * SS) + cap_ox
    pom_y = int(CAP_H * 0.32 * SS) + cap_oy
    pygame.draw.circle(big, MUSH_SPOT, (pom_x, pom_y), int(2.0 * SS))
    pygame.draw.circle(big, VELVET_OUTLINE, (pom_x, pom_y), int(2.0 * SS), SS)

    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS) + cap_ox
    rim_y = int(CAP_H * 0.93 * SS) + cap_oy
    _draw_scalloped_rim(big, rim_x, rim_y, rim_w)
    _draw_velvet_sheen(big, body_pts)
    _draw_spots(big, CAP_W, CAP_H, cap_ox, cap_oy, mask_poly=body_pts)

    return _finalize(big, sprite_w, sprite_h), CAP_H


# ── VARIANT 3 ── DOMED (smooth half-dome, no point) ────────────────────────

def variant_domed():
    CAP_W, CAP_H = 24, 18
    STEM_W, STEM_H = 20, 22
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox, cap_oy = 0 * SS, 0
    stem_ox, stem_oy = 2 * SS, (CAP_H + 2) * SS

    _draw_stem(big, stem_ox, stem_oy)

    # Cap is an ellipse-rectangle clipped to look like a half-dome.
    cap_rect_outer = pygame.Rect(cap_ox, cap_oy,
                                 CAP_W * SS, int(CAP_H * SS * 1.8))
    cap_rect_inner = cap_rect_outer.inflate(-SS * 2, -SS * 2)
    # Outline + body via a clipped ellipse (the top half).
    clip = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(clip, VELVET_OUTLINE, cap_rect_outer)
    pygame.draw.ellipse(clip, VELVET_BODY,    cap_rect_inner)
    # Knock out the bottom half so only the dome shows.
    bottom_cut = pygame.Rect(0, cap_oy + int(CAP_H * SS * 0.95),
                             big.get_width(), big.get_height())
    pygame.draw.rect(clip, (0, 0, 0, 0), bottom_cut)
    big.blit(clip, (0, 0))
    # Highlight crescent
    pygame.draw.ellipse(big, VELVET_HI,
                        pygame.Rect(cap_ox + int(CAP_W * SS * 0.20),
                                    cap_oy + int(CAP_H * SS * 0.18),
                                    int(CAP_W * SS * 0.30),
                                    int(CAP_H * SS * 0.45)))

    # Mask polygon for spots & sheen — approximate the dome.
    dome_pts = []
    cx_px = cap_ox + (CAP_W * SS) // 2
    cy_px = cap_oy + int(CAP_H * SS * 0.9)
    for k in range(0, 21):
        t = k / 20.0
        a = math.pi * (1.0 - t)
        x = cx_px + int(math.cos(a) * (CAP_W * SS) * 0.48)
        y = cy_px + int(math.sin(a) * (CAP_H * SS) * 0.92 * -1)
        dome_pts.append((x, y))
    dome_pts.append((cap_ox + CAP_W * SS, cy_px))
    dome_pts.append((cap_ox, cy_px))

    _draw_velvet_sheen(big, dome_pts)
    rim_w = int(CAP_W * 0.88 * SS)
    rim_x = int(CAP_W * 0.06 * SS) + cap_ox
    rim_y = cy_px
    _draw_scalloped_rim(big, rim_x, rim_y, rim_w, count=5)
    _draw_spots(big, CAP_W, CAP_H, cap_ox, cap_oy, mask_poly=dome_pts)

    return _finalize(big, sprite_w, sprite_h), CAP_H


# ── VARIANT 4 ── BELL (concave/bell-shaped cap) ────────────────────────────

def variant_bell():
    CAP_W, CAP_H = 22, 22
    STEM_W, STEM_H = 20, 22
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox, cap_oy = 1 * SS, 0
    stem_ox, stem_oy = 2 * SS, (CAP_H + 2) * SS

    _draw_stem(big, stem_ox, stem_oy)

    # Bell silhouette: gently rounded top, waist that pinches in just
    # above the rim flare. Built from a denser polygon than the cone.
    outline_pts = _shift([
        (int(CAP_W * 0.50 * SS), int(CAP_H * 0.02 * SS)),    # apex
        (int(CAP_W * 0.66 * SS), int(CAP_H * 0.10 * SS)),
        (int(CAP_W * 0.78 * SS), int(CAP_H * 0.26 * SS)),
        (int(CAP_W * 0.74 * SS), int(CAP_H * 0.52 * SS)),    # waist pinch
        (int(CAP_W * 0.62 * SS), int(CAP_H * 0.68 * SS)),
        (int(CAP_W * 0.92 * SS), int(CAP_H * 0.90 * SS)),    # rim flare
        (int(CAP_W * 0.08 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.38 * SS), int(CAP_H * 0.68 * SS)),
        (int(CAP_W * 0.26 * SS), int(CAP_H * 0.52 * SS)),
        (int(CAP_W * 0.22 * SS), int(CAP_H * 0.26 * SS)),
        (int(CAP_W * 0.34 * SS), int(CAP_H * 0.10 * SS)),
    ], cap_ox, cap_oy)
    body_pts = _shift([
        (int(CAP_W * 0.50 * SS), int(CAP_H * 0.05 * SS)),
        (int(CAP_W * 0.64 * SS), int(CAP_H * 0.12 * SS)),
        (int(CAP_W * 0.74 * SS), int(CAP_H * 0.28 * SS)),
        (int(CAP_W * 0.70 * SS), int(CAP_H * 0.50 * SS)),
        (int(CAP_W * 0.60 * SS), int(CAP_H * 0.66 * SS)),
        (int(CAP_W * 0.88 * SS), int(CAP_H * 0.88 * SS)),
        (int(CAP_W * 0.12 * SS), int(CAP_H * 0.88 * SS)),
        (int(CAP_W * 0.40 * SS), int(CAP_H * 0.66 * SS)),
        (int(CAP_W * 0.30 * SS), int(CAP_H * 0.50 * SS)),
        (int(CAP_W * 0.26 * SS), int(CAP_H * 0.28 * SS)),
        (int(CAP_W * 0.36 * SS), int(CAP_H * 0.12 * SS)),
    ], cap_ox, cap_oy)
    hi_pts = _shift([
        (int(CAP_W * 0.40 * SS), int(CAP_H * 0.12 * SS)),
        (int(CAP_W * 0.30 * SS), int(CAP_H * 0.28 * SS)),
        (int(CAP_W * 0.32 * SS), int(CAP_H * 0.50 * SS)),
        (int(CAP_W * 0.42 * SS), int(CAP_H * 0.66 * SS)),
        (int(CAP_W * 0.46 * SS), int(CAP_H * 0.30 * SS)),
    ], cap_ox, cap_oy)
    pygame.draw.polygon(big, VELVET_OUTLINE, outline_pts)
    pygame.draw.polygon(big, VELVET_BODY,    body_pts)
    pygame.draw.polygon(big, VELVET_HI,      hi_pts)

    rim_w = int(CAP_W * 0.84 * SS)
    rim_x = int(CAP_W * 0.08 * SS) + cap_ox
    rim_y = int(CAP_H * 0.91 * SS) + cap_oy
    _draw_scalloped_rim(big, rim_x, rim_y, rim_w)
    _draw_velvet_sheen(big, body_pts)
    _draw_spots(big, CAP_W, CAP_H, cap_ox, cap_oy, mask_poly=body_pts)

    return _finalize(big, sprite_w, sprite_h), CAP_H


# ── VARIANT 5 ── ACORN (cone with a cup-skirt at the stem) ─────────────────

def variant_acorn():
    CAP_W, CAP_H = 22, 24
    STEM_W, STEM_H = 20, 22
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox, cap_oy = 1 * SS, 0
    stem_ox, stem_oy = 2 * SS, (CAP_H + 2) * SS

    _draw_stem(big, stem_ox, stem_oy)

    # Same grow-style cone polygons, mostly verbatim — the distinguishing
    # detail is the acorn-cup skirt drawn AFTER the cap, ringing the
    # stem base.
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

    # Acorn-cup skirt: a flat-bottomed half-ellipse hugging the stem
    # immediately below the cap, in a slightly darker velvet shade so it
    # reads as a separate fungal collar.
    skirt_rect = pygame.Rect(
        cap_ox + int(CAP_W * 0.05 * SS),
        cap_oy + int(CAP_H * 0.85 * SS),
        int(CAP_W * 0.90 * SS),
        int(CAP_H * 0.30 * SS),
    )
    pygame.draw.ellipse(big, VELVET_OUTLINE, skirt_rect)
    pygame.draw.ellipse(big, VELVET_BODY,    skirt_rect.inflate(-SS * 2, -SS * 2))
    pygame.draw.ellipse(big, VELVET_HI,
                        skirt_rect.inflate(-SS * 4, -SS * 5).move(0, -SS))

    _draw_velvet_sheen(big, body_pts)
    _draw_spots(big, CAP_W, CAP_H, cap_ox, cap_oy, mask_poly=body_pts)

    return _finalize(big, sprite_w, sprite_h), CAP_H


# ── Strip composition ──────────────────────────────────────────────────────

CELL_W, CELL_H = 96, 112
PAD = 6
TITLE_H = 24
LABEL_H = 28
ROW_GAP = 18
BG = (28, 38, 60)
BG_DEEP = (14, 18, 32)
LBL = (220, 230, 250)
TITLE_C = (200, 220, 255)


def _ref_cell(sprite, dx, dy, halo_color, halo_radius, label):
    cell = pygame.Surface((CELL_W, CELL_H)).convert()
    cell.fill(BG)
    cx, cy = CELL_W // 2, CELL_H // 2 - 4
    _draw_grow_halo(cell, cx, cy, pulse=1.2,
                    color_rgb=halo_color, radius=halo_radius, peak_y_off=-2)
    cell.blit(sprite, (cx + dx, cy + dy))
    font = pygame.font.SysFont(None, 16, bold=True)
    t = font.render(label, True, LBL)
    cell.blit(t, (CELL_W // 2 - t.get_width() // 2, CELL_H - 20))
    return cell


def _variant_cell(sprite, cap_h, label):
    cell = pygame.Surface((CELL_W, CELL_H)).convert()
    cell.fill(BG)
    cx, cy = CELL_W // 2, CELL_H // 2 - 4
    _draw_grow_halo(cell, cx, cy, pulse=1.2,
                    color_rgb=HALO_RGB, radius=42, peak_y_off=-2)
    sprite_w, sprite_h = sprite.get_size()
    # Anchor: centre cap on (cx, cy) horizontally, tip near cy - cap_h/2 + 4.
    dx = -sprite_w // 2 + 1
    dy = -cap_h + 2
    cell.blit(sprite, (cx + dx, cy + dy))
    font = pygame.font.SysFont(None, 16, bold=True)
    t = font.render(label, True, LBL)
    cell.blit(t, (CELL_W // 2 - t.get_width() // 2, CELL_H - 20))
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
                  halo_color=HALO_RGB, halo_radius=36,
                  label="SHRINK (current)"),
    )

    builders = (
        ("V1 stout",       variant_stout),
        ("V2 pixie-hood",  variant_pixie_hood),
        ("V3 domed",       variant_domed),
        ("V4 bell",        variant_bell),
        ("V5 acorn",       variant_acorn),
    )
    variant_cells = []
    variant_sprites = {}
    for label, builder in builders:
        sprite, cap_h = builder()
        variant_cells.append(_variant_cell(sprite, cap_h, label))
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

    # Also save each candidate as a standalone large PNG (centered with halo)
    # so reviewers can zoom in.
    for label, sprite in variant_sprites.items():
        slug = label.split(" ", 1)[1].replace("-", "_")
        big = pygame.Surface((140, 160)).convert()
        big.fill(BG)
        cx, cy = 70, 76
        _draw_grow_halo(big, cx, cy, pulse=1.2,
                        color_rgb=HALO_RGB, radius=52, peak_y_off=-2)
        sw, sh = sprite.get_size()
        scale = 2
        zoomed = pygame.transform.scale(sprite, (sw * scale, sh * scale))
        zsw, zsh = zoomed.get_size()
        big.blit(zoomed, (cx - zsw // 2, cy - zsh // 2 - 2))
        path = os.path.join(out_dir, f"{slug}_2x.png")
        pygame.image.save(big, path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
