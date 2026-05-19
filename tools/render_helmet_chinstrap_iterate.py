"""Iterate chinstrap designs for the side-view punk-mohawk helmet.

The helmet sits at anchor (+18, -18) in world coords relative to
bird center. Pip's chin (jaw bottom) is at world ~(+15, +2). The
strap must visibly wrap UNDER the chin so the player reads "the
helmet is held on" rather than "decorative loop in front of jaw".

Each variant function paints the dome + mohawk + decal verbatim
from the live helmet, then renders its own chinstrap design.
Re-edit CHINSTRAP_VARIANTS, re-run, look at 00_chinstrap.png,
critique, repeat.

Usage:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_helmet_chinstrap_iterate.py
"""

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

from tools.render_helmet_side_view_variants import (
    _half_dome, build_world, render_zoom, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_variants", "side_view_v2",
                    "chinstrap_iterate")
os.makedirs(_OUT, exist_ok=True)


# The user approved anchor (+18, -18) at the live drop=12 — dome
# center landed at world (bird.x + 18, bird.y - 24). Extending the
# helm surface vertically shifts surface centre down, which would
# drift the dome up unless we compensate. Recompute the anchor so
# the dome stays put when drop changes:
#
#   dome_in_surface_y = pad + hh/2 = 4 + 7.5 = 11.5
#   surface_center_y  = (pad*2 + hh + drop) / 2
#   anchor_y_needed   = dome_world_y - (dome_in_surface_y - surface_center_y)
#
# Old: drop=12 → surface_center_y=17.5, anchor_y_needed=-18 → dome at -24
# New: drop=DROP_PX → anchor_y_needed = -24 - (11.5 - (pad*2 + 15 + DROP_PX)/2)
ANCHOR_X = 18
DROP_PX = 28
ANCHOR_Y = int(-24 - (11.5 - (8 + 15 + DROP_PX) / 2))  # = -10 for DROP_PX=28
STRAP = (60, 60, 70)
BUCKLE = (200, 50, 50)


def _new_helm(s, drop=DROP_PX):
    hw = int(24 * s)
    hh = int(15 * s)
    pad = 4
    helm = pygame.Surface(
        (hw + pad * 2, hh + pad * 2 + drop), pygame.SRCALPHA)
    return helm, hw, hh, pad, drop


def _paint_dome(helm, hw, hh, pad, s):
    """Live helmet dome + mohawk + decal painting (verbatim)."""
    _half_dome(helm, hw, hh, pad, (10, 10, 18), (50, 50, 60))
    fin = [
        (pad + 3,           pad + 1),
        (pad + hw // 2 - 2, pad - 3),
        (pad + hw // 2 + 3, pad - 2),
        (pad + hw - 4,      pad + 2),
    ]
    pygame.draw.polygon(helm, (240, 240, 230), fin)
    pygame.draw.polygon(helm, (10, 10, 18), fin, 1)
    for sx in (pad + hw // 2 - 3, pad + hw // 2 + 2):
        spike = [(sx, pad - 2), (sx + 1, pad - 5), (sx + 2, pad - 2)]
        pygame.draw.polygon(helm, (240, 240, 230), spike)
        pygame.draw.polygon(helm, (10, 10, 18), spike, 1)
    pygame.draw.line(helm, (10, 10, 18),
                     (pad + hw // 2 - 2, pad + hh - 3),
                     (pad + hw // 2 + 2, pad + hh - 3), 1)
    pygame.draw.rect(helm, (200, 200, 210),
                     pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 2))
    sk_w = max(3, int(5 * s))
    sk_h = max(2, int(4 * s))
    sk = pygame.Rect(0, 0, sk_w, sk_h)
    sk.center = (pad + hw // 2 - 5, pad + hh - 4)
    pygame.draw.ellipse(helm, (240, 240, 230), sk)
    pygame.draw.ellipse(helm, (10, 10, 18), sk, 1)


def _anchor_and_blit(bird, surf, helm, cx, cy, flipped):
    s = bird.shrink_scale
    tilt = -bird.tilt_deg if flipped else bird.tilt_deg
    y_off = -ANCHOR_Y * s if flipped else ANCHOR_Y * s
    offset = pygame.math.Vector2(ANCHOR_X * s, y_off).rotate(-tilt)
    rotated = pygame.transform.rotate(helm, tilt)
    if flipped:
        rotated = pygame.transform.flip(rotated, False, True)
    r = rotated.get_rect(center=(int(cx + offset.x),
                                 int(cy + offset.y)))
    surf.blit(rotated, r.topleft)


# Pip's chin lands at world (bird.x + 15, bird.y + 2). With the
# dome's world position kept stable via the compensated ANCHOR_Y,
# the chin sits at helm-surface coords (13, 37) regardless of drop.
def _chin_buckle_xy(hw, hh, pad, drop):
    bx = 13
    by = 37
    return bx, by


# ── chinstrap variants ──────────────────────────────────────────────────────

def cs_a_v_two_strap(bird, surf, cx, cy, flipped):
    """A — TWO straps converging on a buckle UNDER the chin.
    Front strap (forward-temple → buckle) + back strap
    (rear-temple → buckle). Forms a V."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    pygame.draw.line(helm, STRAP, front_temple, (bx, by), 2)
    pygame.draw.line(helm, STRAP, rear_temple,  (bx, by), 2)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_b_single_loop(bird, surf, cx, cy, flipped):
    """B — Single strap looping under the chin. From front-temple
    drops straight, curves under the chin, comes back up to a
    visible end (no buckle) tucked into the rear of the dome. The
    rear segment is darker so it reads as "behind the head"."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    # Front strap (visible).
    pygame.draw.line(helm, STRAP, front_temple, (bx, by), 2)
    # Curve under the chin then back up to rear temple — drawn as a
    # darker tone to suggest "behind the head silhouette".
    DARK = (40, 40, 50)
    pygame.draw.line(helm, DARK, (bx, by), rear_temple, 2)
    # Tiny buckle dot at the chin.
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_c_y_strap(bird, surf, cx, cy, flipped):
    """C — Y-shaped strap. Two short straps from the rim merging
    into ONE thick strap that drops down to the chin buckle.
    Cleaner read than the symmetric V."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    # Both temple straps meet at a midpoint just under the jaw line.
    mid = ((front_temple[0] + rear_temple[0]) // 2,
           pad + hh + 6)
    pygame.draw.line(helm, STRAP, front_temple, mid, 2)
    pygame.draw.line(helm, STRAP, rear_temple,  mid, 2)
    # Single thick strap from mid → chin buckle.
    pygame.draw.line(helm, STRAP, mid, (bx, by), 3)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_d_back_diag_only(bird, surf, cx, cy, flipped):
    """D — ONE diagonal back strap from rear-temple down past jaw
    to a buckle UNDER the chin. Cleanest minimal read of "strap
    holding helmet on"."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    rear_temple = (pad + 3, pad + hh + 1)
    pygame.draw.line(helm, STRAP, rear_temple, (bx, by), 2)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_e_thick_v_with_pad(bird, surf, cx, cy, flipped):
    """E — Thick V straps + tiny chin-pad rectangle at the buckle so
    the strap reads as a real motorbike-style chinstrap with a
    visible pad pressing against the chin."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    pygame.draw.line(helm, STRAP, front_temple, (bx, by), 2)
    pygame.draw.line(helm, STRAP, rear_temple,  (bx, by), 2)
    # Chin pad — small rounded rect at the buckle.
    pad_rect = pygame.Rect(bx - 3, by - 2, 7, 4)
    pygame.draw.rect(helm, (40, 40, 50), pad_rect, border_radius=1)
    pygame.draw.rect(helm, BUCKLE, pad_rect, width=1, border_radius=1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_f_v_thicker_strap(bird, surf, cx, cy, flipped):
    """F — A with 3-px straps + 3-px buckle. More visible."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    pygame.draw.line(helm, STRAP, (pad + hw - 3, pad + hh + 1), (bx, by), 3)
    pygame.draw.line(helm, STRAP, (pad + 3,      pad + hh + 1), (bx, by), 3)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 3)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_g_v_brighter_strap(bird, surf, cx, cy, flipped):
    """G — A with a brighter strap colour (90, 90, 105) so the
    grey reads against Pip's red feathers."""
    bright = (95, 95, 110)
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    pygame.draw.line(helm, bright, (pad + hw - 3, pad + hh + 1), (bx, by), 2)
    pygame.draw.line(helm, bright, (pad + 3,      pad + hh + 1), (bx, by), 2)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_h_v_bone_strap(bird, surf, cx, cy, flipped):
    """H — Bone-white strap matching the mohawk palette. Highest
    contrast against Pip's red body."""
    bone = (240, 240, 230)
    outline = (10, 10, 18)
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_t = (pad + hw - 3, pad + hh + 1)
    rear_t  = (pad + 3,      pad + hh + 1)
    # Draw outline first (slightly thicker dark) then bone fill.
    pygame.draw.line(helm, outline, front_t, (bx, by), 3)
    pygame.draw.line(helm, outline, rear_t,  (bx, by), 3)
    pygame.draw.line(helm, bone,    front_t, (bx, by), 1)
    pygame.draw.line(helm, bone,    rear_t,  (bx, by), 1)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_i_v_compact_pad(bird, surf, cx, cy, flipped):
    """I — V straps + a SMALL (4×3) chin pad — refined E with
    tighter pad so it doesn't read as a beard."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    pygame.draw.line(helm, STRAP, (pad + hw - 3, pad + hh + 1), (bx, by), 2)
    pygame.draw.line(helm, STRAP, (pad + 3,      pad + hh + 1), (bx, by), 2)
    pad_rect = pygame.Rect(bx - 2, by - 1, 5, 3)
    pygame.draw.rect(helm, (40, 40, 50), pad_rect)
    pygame.draw.rect(helm, (200, 200, 210), pad_rect, width=1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_j_v_dark_strap_red_buckle(bird, surf, cx, cy, flipped):
    """J — Darker, near-black strap (30, 30, 40) so the line reads
    as a strap silhouette without competing with the helmet dome
    palette. Buckle stays red."""
    dark = (30, 30, 40)
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    pygame.draw.line(helm, dark, (pad + hw - 3, pad + hh + 1), (bx, by), 2)
    pygame.draw.line(helm, dark, (pad + 3,      pad + hh + 1), (bx, by), 2)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_k_single_front_2px(bird, surf, cx, cy, flipped):
    """K — Single FRONT-temple strap dropping past the cheek to a
    buckle under the chin. The only side-view-correct routing — the
    rear strap is hidden behind the head silhouette in real life."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    pygame.draw.line(helm, STRAP, front_temple, (bx, by), 2)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_l_single_front_3px(bird, surf, cx, cy, flipped):
    """L — K thickened to 3 px so the rope reads bolder."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    pygame.draw.line(helm, STRAP, front_temple, (bx, by), 3)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 3)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_m_front_plus_rear_stub(bird, surf, cx, cy, flipped):
    """M — Single FRONT strap + a tiny stub at the rear-temple
    suggesting "the helmet has straps on both sides, but only the
    front one is visible from this angle"."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    pygame.draw.line(helm, STRAP, front_temple, (bx, by), 2)
    # Tiny stub at rear-temple — 3 px of strap visible before it
    # disappears behind the head silhouette.
    pygame.draw.line(helm, STRAP, rear_temple,
                     (rear_temple[0] + 1, rear_temple[1] + 3), 2)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_n_front_with_pad(bird, surf, cx, cy, flipped):
    """N — Single FRONT strap + small chin pad rectangle at the
    buckle. The pad anchors the strap visually as a real clip."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    pygame.draw.line(helm, STRAP, front_temple, (bx, by), 2)
    pad_rect = pygame.Rect(bx - 2, by - 1, 5, 3)
    pygame.draw.rect(helm, (40, 40, 50), pad_rect)
    pygame.draw.rect(helm, (200, 200, 210), pad_rect, width=1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_o_front_chin_loop(bird, surf, cx, cy, flipped):
    """O — Front strap drops down then curves UNDER the chin (an
    'L' shape) — the curve under the chin makes the loop intent
    explicit without crossing Pip's face."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    # Drop down past the jaw — the strap clears Pip's face by
    # going further right (forward) before bending under.
    elbow = (front_temple[0] + 1, by - 4)
    pygame.draw.line(helm, STRAP, front_temple, elbow, 2)
    pygame.draw.line(helm, STRAP, elbow, (bx, by), 2)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def _draw_l_variant(helm, hw, hh, pad, drop, strap_col, buckle_col,
                     strap_w=3, buckle_r=2):
    """L base painter — single FRONT strap + buckle, parameterised."""
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    pygame.draw.line(helm, strap_col, front_temple, (bx, by), strap_w)
    pygame.draw.circle(helm, buckle_col, (bx, by), buckle_r)


def cs_l1_baseline(bird, surf, cx, cy, flipped):
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    _draw_l_variant(helm, hw, hh, pad, drop, STRAP, BUCKLE, 3, 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_l2_brighter(bird, surf, cx, cy, flipped):
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    _draw_l_variant(helm, hw, hh, pad, drop,
                    (90, 90, 105), BUCKLE, 3, 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_l3_big_buckle(bird, surf, cx, cy, flipped):
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    _draw_l_variant(helm, hw, hh, pad, drop, STRAP, BUCKLE, 3, 3)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_l4_bone_strap(bird, surf, cx, cy, flipped):
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    # Dark outline 3 px then bone-white 1 px down the centre.
    pygame.draw.line(helm, (10, 10, 18), front_temple, (bx, by), 3)
    pygame.draw.line(helm, (240, 240, 230), front_temple, (bx, by), 1)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_l5_outlined_dark(bird, surf, cx, cy, flipped):
    """L with a dark outline + lighter grey core — gives the strap
    a 3D rope feel without using bone palette."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    pygame.draw.line(helm, (15, 15, 22), front_temple, (bx, by), 3)
    pygame.draw.line(helm, (110, 110, 125), front_temple, (bx, by), 1)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 3)
    pygame.draw.circle(helm, (15, 15, 22), (bx, by), 3, 1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def _ear_junction_xy(hw, hh, pad, drop):
    """Y-strap junction at Pip's ear — world (+12, -6) maps to
    helm surface (10, 29) with the compensated anchor."""
    return 10, 29


def cs_y1_classic_skate(bird, surf, cx, cy, flipped):
    """Y1 — Classic skateboard chinstrap: two short straps from the
    rim converge at a side adjuster near the ear, then a single
    strap drops under the chin to a side-release buckle."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    jx, jy = _ear_junction_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    # Two short straps from rim → ear-level junction.
    pygame.draw.line(helm, STRAP, front_temple, (jx, jy), 2)
    pygame.draw.line(helm, STRAP, rear_temple,  (jx, jy), 2)
    # Single strap from junction → chin buckle.
    pygame.draw.line(helm, STRAP, (jx, jy), (bx, by), 2)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_y2_with_adjuster(bird, surf, cx, cy, flipped):
    """Y2 — Y1 + a small adjuster slider at the Y junction.
    Black rect with chrome edge = the plastic adjuster."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    jx, jy = _ear_junction_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    pygame.draw.line(helm, STRAP, front_temple, (jx, jy), 2)
    pygame.draw.line(helm, STRAP, rear_temple,  (jx, jy), 2)
    pygame.draw.line(helm, STRAP, (jx, jy), (bx, by), 2)
    # Adjuster — small black rectangle with chrome outline at the
    # junction point.
    adj = pygame.Rect(jx - 2, jy - 1, 4, 3)
    pygame.draw.rect(helm, (30, 30, 40), adj)
    pygame.draw.rect(helm, (200, 200, 210), adj, 1)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_y3_outlined(bird, surf, cx, cy, flipped):
    """Y3 — Y1 with the 3-px-outlined-rope style from L5 applied to
    each segment + side-release clip at the chin."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    jx, jy = _ear_junction_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    OUT  = (15, 15, 22)
    CORE = (110, 110, 125)
    # 3-px outlined straps + 1-px lighter core through the middle.
    for a, b in ((front_temple, (jx, jy)),
                 (rear_temple,  (jx, jy)),
                 ((jx, jy),     (bx, by))):
        pygame.draw.line(helm, OUT,  a, b, 3)
        pygame.draw.line(helm, CORE, a, b, 1)
    # Side-release clip — chunky 5×4 rectangle at the chin, two
    # halves split vertically (visible groove).
    clip = pygame.Rect(bx - 2, by - 2, 5, 4)
    pygame.draw.rect(helm, BUCKLE, clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT, (bx + 1, by - 2), (bx + 1, by + 1), 1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_y4_bright(bird, surf, cx, cy, flipped):
    """Y4 — Y1 but with the brighter (90, 90, 105) strap colour so
    the lines pop against Pip's red feathers."""
    bright = (95, 95, 110)
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    jx, jy = _ear_junction_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    pygame.draw.line(helm, bright, front_temple, (jx, jy), 2)
    pygame.draw.line(helm, bright, rear_temple,  (jx, jy), 2)
    pygame.draw.line(helm, bright, (jx, jy), (bx, by), 2)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_y5_y2_bright(bird, surf, cx, cy, flipped):
    """Y5 — Y2 + brighter strap colour. The skateboard chinstrap
    look with a visible adjuster AND high contrast straps."""
    bright = (95, 95, 110)
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    jx, jy = _ear_junction_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    pygame.draw.line(helm, bright, front_temple, (jx, jy), 2)
    pygame.draw.line(helm, bright, rear_temple,  (jx, jy), 2)
    pygame.draw.line(helm, bright, (jx, jy), (bx, by), 2)
    adj = pygame.Rect(jx - 2, jy - 1, 4, 3)
    pygame.draw.rect(helm, (30, 30, 40), adj)
    pygame.draw.rect(helm, (200, 200, 210), adj, 1)
    pygame.draw.circle(helm, BUCKLE, (bx, by), 2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_y6_full_kit(bird, surf, cx, cy, flipped):
    """Y6 — Full skate-helmet chinstrap kit: outlined Y straps +
    plastic adjuster slider at the ear junction + side-release
    clip at the chin. The complete real-life helmet hardware."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    jx, jy = _ear_junction_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    OUT  = (15, 15, 22)
    CORE = (110, 110, 125)
    for a, b in ((front_temple, (jx, jy)),
                 (rear_temple,  (jx, jy)),
                 ((jx, jy),     (bx, by))):
        pygame.draw.line(helm, OUT,  a, b, 3)
        pygame.draw.line(helm, CORE, a, b, 1)
    # Plastic adjuster slider at the Y junction.
    adj = pygame.Rect(jx - 2, jy - 1, 4, 3)
    pygame.draw.rect(helm, (30, 30, 40), adj)
    pygame.draw.rect(helm, (200, 200, 210), adj, 1)
    # Side-release clip at the chin — red rect with dark outline
    # and a vertical groove suggesting the two-half clip body.
    clip = pygame.Rect(bx - 2, by - 2, 5, 4)
    pygame.draw.rect(helm, BUCKLE, clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT, (bx + 1, by - 2), (bx + 1, by + 1), 1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_y7_thin_clean(bird, surf, cx, cy, flipped):
    """Y7 — Same skate-helmet kit but with 2-px straps (not
    outlined 3) — cleaner, less chunky look."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    jx, jy = _ear_junction_xy(hw, hh, pad, drop)
    front_temple = (pad + hw - 3, pad + hh + 1)
    rear_temple  = (pad + 3,      pad + hh + 1)
    OUT  = (15, 15, 22)
    pygame.draw.line(helm, OUT, front_temple, (jx, jy), 2)
    pygame.draw.line(helm, OUT, rear_temple,  (jx, jy), 2)
    pygame.draw.line(helm, OUT, (jx, jy), (bx, by), 2)
    # Adjuster slider.
    adj = pygame.Rect(jx - 2, jy - 1, 4, 3)
    pygame.draw.rect(helm, (30, 30, 40), adj)
    pygame.draw.rect(helm, (200, 200, 210), adj, 1)
    # Side-release clip.
    clip = pygame.Rect(bx - 2, by - 2, 5, 4)
    pygame.draw.rect(helm, BUCKLE, clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT, (bx + 1, by - 2), (bx + 1, by + 1), 1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def _side_anchor_xy(hw, hh, pad, drop):
    """Strap attachment points on the SIDE of the helmet, just above
    the ear. A real skate helmet rim covers the ear and straps come
    out near the back-side of the rim — NOT at the front of the
    brow. Two anchors close together so the V doesn't cross Pip's
    face."""
    rim_y = pad + hh + 1
    front_side = (pad + 8,         rim_y)   # ear-front
    rear_side  = (pad + 4,         rim_y)   # ear-back
    return front_side, rear_side


def cs_t1_tight_v(bird, surf, cx, cy, flipped):
    """T1 — Tight V with both anchors on the helmet's side panel
    (over the ear). Straps drop nearly vertically, no face cross."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    jx, jy = _ear_junction_xy(hw, hh, pad, drop)
    front_side, rear_side = _side_anchor_xy(hw, hh, pad, drop)
    OUT = (15, 15, 22)
    pygame.draw.line(helm, OUT, front_side, (jx, jy), 2)
    pygame.draw.line(helm, OUT, rear_side,  (jx, jy), 2)
    pygame.draw.line(helm, OUT, (jx, jy), (bx, by), 2)
    adj = pygame.Rect(jx - 2, jy - 1, 4, 3)
    pygame.draw.rect(helm, (30, 30, 40), adj)
    pygame.draw.rect(helm, (200, 200, 210), adj, 1)
    clip = pygame.Rect(bx - 2, by - 2, 5, 4)
    pygame.draw.rect(helm, (200, 50, 50), clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT, (bx + 1, by - 2), (bx + 1, by + 1), 1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_t2_tight_v_no_adjuster(bird, surf, cx, cy, flipped):
    """T2 — T1 without the adjuster slider (cleaner)."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    jx, jy = _ear_junction_xy(hw, hh, pad, drop)
    front_side, rear_side = _side_anchor_xy(hw, hh, pad, drop)
    OUT = (15, 15, 22)
    pygame.draw.line(helm, OUT, front_side, (jx, jy), 2)
    pygame.draw.line(helm, OUT, rear_side,  (jx, jy), 2)
    pygame.draw.line(helm, OUT, (jx, jy), (bx, by), 2)
    clip = pygame.Rect(bx - 2, by - 2, 5, 4)
    pygame.draw.rect(helm, (200, 50, 50), clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT, (bx + 1, by - 2), (bx + 1, by + 1), 1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_t3_single_side_strap(bird, surf, cx, cy, flipped):
    """T3 — Single strap from a side anchor (over the ear) dropping
    to the chin clip. The simplest "skate helmet chinstrap" read."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_side, rear_side = _side_anchor_xy(hw, hh, pad, drop)
    # Anchor mid-way between front and rear on the side rim.
    side = ((front_side[0] + rear_side[0]) // 2, front_side[1])
    OUT = (15, 15, 22)
    pygame.draw.line(helm, OUT, side, (bx, by), 2)
    clip = pygame.Rect(bx - 2, by - 2, 5, 4)
    pygame.draw.rect(helm, (200, 50, 50), clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT, (bx + 1, by - 2), (bx + 1, by + 1), 1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_t4_tight_v_lighter(bird, surf, cx, cy, flipped):
    """T4 — T2 with a slightly lighter strap (40, 40, 50) so the
    line doesn't read as harsh black against Pip's red feathers."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    jx, jy = _ear_junction_xy(hw, hh, pad, drop)
    front_side, rear_side = _side_anchor_xy(hw, hh, pad, drop)
    STR = (40, 40, 50)
    OUT = (15, 15, 22)
    pygame.draw.line(helm, STR, front_side, (jx, jy), 2)
    pygame.draw.line(helm, STR, rear_side,  (jx, jy), 2)
    pygame.draw.line(helm, STR, (jx, jy), (bx, by), 2)
    clip = pygame.Rect(bx - 2, by - 2, 5, 4)
    pygame.draw.rect(helm, (200, 50, 50), clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT, (bx + 1, by - 2), (bx + 1, by + 1), 1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_t5_curved_single(bird, surf, cx, cy, flipped):
    """T5 — Single strap from side anchor, curving forward via a
    midpoint near the lower jaw to the chin clip. Simulates the
    strap following the head's curvature."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    bx, by = _chin_buckle_xy(hw, hh, pad, drop)
    front_side, rear_side = _side_anchor_xy(hw, hh, pad, drop)
    side = ((front_side[0] + rear_side[0]) // 2, front_side[1])
    # Midpoint near the lower jaw — bias toward Pip's silhouette.
    mid = (side[0] + 1, side[1] + 8)
    OUT = (15, 15, 22)
    pygame.draw.line(helm, OUT, side, mid, 2)
    pygame.draw.line(helm, OUT, mid, (bx, by), 2)
    clip = pygame.Rect(bx - 2, by - 2, 5, 4)
    pygame.draw.rect(helm, (200, 50, 50), clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT, (bx + 1, by - 2), (bx + 1, by + 1), 1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def _single_strap_chinstrap(helm, hw, hh, pad, drop,
                            anchor, clip_centre,
                            strap_col=(15, 15, 22),
                            thick=2):
    """Single straight strap from helmet rim to chin clip + clip."""
    OUT     = (15, 15, 22)
    BUCKLE  = (200, 50, 50)
    pygame.draw.line(helm, strap_col, anchor, clip_centre, thick)
    clip = pygame.Rect(clip_centre[0] - 2, clip_centre[1] - 2, 5, 4)
    pygame.draw.rect(helm, BUCKLE, clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT,
                     (clip.x + 2, clip.y),
                     (clip.x + 2, clip.bottom - 1), 1)


def cs_g1_single_thin(bird, surf, cx, cy, flipped):
    """G1 — Single 2-px strap, dark, from rim to chin. Clean line
    overlaying Pip's face on the left of the sunglasses."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    _single_strap_chinstrap(helm, hw, hh, pad, drop,
                            anchor=(10, pad + hh + 1),
                            clip_centre=(13, 37), thick=2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_g2_single_thick(bird, surf, cx, cy, flipped):
    """G2 — Single 3-px strap. Thicker, more visible."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    _single_strap_chinstrap(helm, hw, hh, pad, drop,
                            anchor=(10, pad + hh + 1),
                            clip_centre=(13, 37), thick=3)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_g3_lighter_grey(bird, surf, cx, cy, flipped):
    """G3 — 2-px strap with lighter grey colour (90, 90, 105) so it
    pops against Pip's red feathers."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    _single_strap_chinstrap(helm, hw, hh, pad, drop,
                            anchor=(10, pad + hh + 1),
                            clip_centre=(13, 37),
                            strap_col=(90, 90, 105), thick=2)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_g4_outlined_strap(bird, surf, cx, cy, flipped):
    """G4 — Outlined strap: 3-px dark outline + 1-px lighter core
    so the strap has visible volume."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    OUT  = (15, 15, 22)
    CORE = (110, 110, 125)
    anchor = (10, pad + hh + 1)
    clip_centre = (13, 37)
    pygame.draw.line(helm, OUT,  anchor, clip_centre, 3)
    pygame.draw.line(helm, CORE, anchor, clip_centre, 1)
    BUCKLE = (200, 50, 50)
    clip = pygame.Rect(clip_centre[0] - 2, clip_centre[1] - 2, 5, 4)
    pygame.draw.rect(helm, BUCKLE, clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT,
                     (clip.x + 2, clip.y),
                     (clip.x + 2, clip.bottom - 1), 1)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_g5_thick_lighter(bird, surf, cx, cy, flipped):
    """G5 — 3-px strap in lighter grey. The boldest, most visible
    single-strap option."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    _single_strap_chinstrap(helm, hw, hh, pad, drop,
                            anchor=(10, pad + hh + 1),
                            clip_centre=(13, 37),
                            strap_col=(90, 90, 105), thick=3)
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def _bhsi_chinstrap(helm, front_anchor, rear_anchor, junction,
                    clip_centre, strap_col=(15, 15, 22), strap_w=2,
                    draw_adjuster=False):
    """BHSI-correct chinstrap: front strap visibly crosses the temple
    between the lens and the ear, rear strap drops behind the ear,
    both meet at a V-junction below+forward of the ear, single
    strap continues to buckle at the throat."""
    OUT     = (15, 15, 22)
    CHROME  = (200, 200, 210)
    BUCKLE  = (200, 50, 50)
    pygame.draw.line(helm, strap_col, front_anchor, junction, strap_w)
    pygame.draw.line(helm, strap_col, rear_anchor,  junction, strap_w)
    pygame.draw.line(helm, strap_col, junction, clip_centre, strap_w)
    if draw_adjuster:
        adj = pygame.Rect(junction[0] - 1, junction[1] - 1, 3, 2)
        pygame.draw.rect(helm, (30, 30, 40), adj)
        pygame.draw.rect(helm, CHROME, adj, 1)
    clip = pygame.Rect(clip_centre[0] - 2, clip_centre[1] - 2, 5, 4)
    pygame.draw.rect(helm, BUCKLE, clip)
    pygame.draw.rect(helm, OUT, clip, 1)
    pygame.draw.line(helm, OUT,
                     (clip.x + 2, clip.y),
                     (clip.x + 2, clip.bottom - 1), 1)


def cs_h1_bhsi_basic(bird, surf, cx, cy, flipped):
    """H1 — BHSI-correct anatomy. Front anchor above the eye, rear
    anchor at back of helmet, V-junction below+forward of ear,
    buckle at throat. Front strap crosses the temple between lens
    and ear."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    rim_y = pad + hh + 1
    _bhsi_chinstrap(
        helm,
        front_anchor=(11, rim_y),
        rear_anchor=(6, rim_y),
        junction=(9, 30),
        clip_centre=(13, 37),
        strap_w=2,
    )
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_h2_bhsi_thicker(bird, surf, cx, cy, flipped):
    """H2 — H1 with 3-px straps (more visible)."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    rim_y = pad + hh + 1
    _bhsi_chinstrap(
        helm,
        front_anchor=(11, rim_y),
        rear_anchor=(6, rim_y),
        junction=(9, 30),
        clip_centre=(13, 37),
        strap_w=3,
    )
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_h3_bhsi_with_adjuster(bird, surf, cx, cy, flipped):
    """H3 — H1 with a plastic adjuster slider at the V-junction."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    rim_y = pad + hh + 1
    _bhsi_chinstrap(
        helm,
        front_anchor=(11, rim_y),
        rear_anchor=(6, rim_y),
        junction=(9, 30),
        clip_centre=(13, 37),
        strap_w=2,
        draw_adjuster=True,
    )
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_h4_bhsi_lens_bite(bird, surf, cx, cy, flipped):
    """H4 — Front anchor moved 1 px right so the strap clearly
    crosses the back edge of the lens on its way to the V-junction."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    rim_y = pad + hh + 1
    _bhsi_chinstrap(
        helm,
        front_anchor=(12, rim_y),
        rear_anchor=(6, rim_y),
        junction=(9, 30),
        clip_centre=(13, 37),
        strap_w=2,
        draw_adjuster=True,
    )
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


def cs_h5_bhsi_lighter(bird, surf, cx, cy, flipped):
    """H5 — H3 with lighter grey strap (90,90,105) for visibility
    on Pip's red feathers."""
    helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
    _paint_dome(helm, hw, hh, pad, bird.shrink_scale)
    rim_y = pad + hh + 1
    _bhsi_chinstrap(
        helm,
        front_anchor=(11, rim_y),
        rear_anchor=(6, rim_y),
        junction=(9, 30),
        clip_centre=(13, 37),
        strap_col=(90, 90, 105),
        strap_w=2,
        draw_adjuster=True,
    )
    _anchor_and_blit(bird, surf, helm, cx, cy, flipped)


CHINSTRAP_VARIANTS = [
    ("H1_bhsi_basic",      cs_h1_bhsi_basic,
     "H1: BHSI-correct V — front strap crosses temple (lens↔ear)"),
    ("H2_bhsi_thicker",    cs_h2_bhsi_thicker,
     "H2: H1 with 3-px straps (more visible)"),
    ("H3_bhsi_adjuster",   cs_h3_bhsi_with_adjuster,
     "H3: H1 + plastic adjuster slider at V-junction"),
    ("H4_bhsi_lens_bite",  cs_h4_bhsi_lens_bite,
     "H4: H3 with front anchor +1 (strap crosses back of lens)"),
    ("H5_bhsi_lighter",    cs_h5_bhsi_lighter,
     "H5: H3 with lighter grey strap (90,90,105)"),
]


def main():
    saved = []
    for label, fn, caption in CHINSTRAP_VARIANTS:
        world = build_world()
        world.bird._draw_helmet = (
            lambda surf, cx, cy, flipped, b=world.bird, _fn=fn:
                _fn(b, surf, cx, cy, flipped)
        )
        zoom = render_zoom(world, zoom=6, crop=72)
        path = os.path.join(_OUT, f"cs_{label}.png")
        pygame.image.save(zoom, path)
        saved.append((label, caption, zoom))
        print(f"saved {path}")

    zoom_w, zoom_h = saved[0][2].get_size()
    band_h = 56
    gap = 12
    sheet_w = len(saved) * zoom_w + (len(saved) - 1) * gap + 24
    sheet_h = zoom_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, zoom) in enumerate(saved):
        x = 12 + idx * (zoom_w + gap)
        y = 12
        sheet.blit(zoom, (x, y))
        band = _label_band(zoom_w, label, caption, height=band_h)
        sheet.blit(band, (x, y + zoom_h))
    sheet_path = os.path.join(_OUT, "00_chinstrap.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")


if __name__ == "__main__":
    main()
