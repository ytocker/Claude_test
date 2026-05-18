"""Render 5 full-Pip skull-set variants — Pip + matched helmet + skull deck.

User picked the skull deck (variant 12). The first pass of this file
had two issues:
  1. The helmet read as a coloured blob, not a helmet — no chinstrap,
     no vents, easily mistaken for a hat. The tricorn variant was
     literally a hat.
  2. Even after a partial anchor fix the helmet sat above Pip's head
     instead of on it.

This iteration fixes both:

ANCHORS (derived from actual sprite geometry):
  • Helmet centre: (+15, -11) from Pip's centre. +15 is the head
                   x-centre (parrot head ellipse at sprite (47,21)
                   per game/parrot.py:149, same anchor the proven
                   triple-mode top-hat uses in
                   game/dollar_parrot_hat.py:34-35). y=-11 sits the
                   dome on the crown with the rim band just under
                   the eye-line.
  • Deck centre:   (0, +19) from Pip's centre — deck top at his body
                   bottom (slight overlap reads as STANDING on it).
Both rotate with bird.tilt_deg so helmet + board bank with Pip and
carry the 3-tap backflip spin.

OBVIOUSLY A HELMET (not a hat). Shared `_draw_helmet_base` primitive
gives every variant:
  • a wrap-the-temples dome with glossy highlight,
  • a darker rim band that separates dome from face,
  • 3 dark air vents across the dome top — strongest "helmet" cue
    at this scale apart from the strap,
  • a 2-strap CHINSTRAP descending to a buckle dot below the rim —
    the killer "helmet not hat" identifier.
No brims anywhere.

THE 5 VARIANTS share the primitive; only decals/extras differ:

  variant_1_matching_black   — all-black dome with white skull decal
                               on the front. Monochrome matching set.
  variant_2_classic_red      — bright red skater dome with white skull
                               on the front, gold buckle. Pop of colour.
  variant_3_spiked_punk      — black dome with 3 silver spikes rising
                               from the centreline, chrome rim, silver
                               buckle.
  variant_4_bandana_wrap     — black helmet base FIRST so vents + rim +
                               chinstrap stay visible, then a red
                               bandana wraps across the dome's upper
                               third with knot trailing back + skull.
  variant_5_skull_mohawk     — black dome with a 4-point white bone-fin
                               mohawk running the centreline + tiny
                               skull on the front. Replaces the
                               previous pirate tricorn (which had a
                               brim → read as hat).

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_skateboard_skull_set.py
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

from game.config import SHRINK_SCALE
from tools.render_skateboard_gameplay import render_gameplay_base


# ─── anchors derived from the actual parrot sprite geometry ────────────────

def _helmet_anchor(bird):
    """Place the helmet ON Pip's head — anchored at the head's actual
    x-centre, not above Pip's body centre.

    The parrot head ellipse is at sprite (47, 21) (game/parrot.py:149),
    which maps to world (+15, -9) from Pip's centre. The proven
    triple-mode top-hat (game/dollar_parrot_hat.py:34-35) uses the same
    head x-centre. Y = -11 places the surface centre 3 px below the
    crown highlight so the rim band lands just under the eye-line and
    the chinstrap trails across the cheek. Rotation by -tilt keeps the
    helmet banking with Pip and carries the backflip spin."""
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    offset = pygame.math.Vector2(15 * s, -11 * s)
    offset = offset.rotate(-bird.tilt_deg)
    return bird.x + offset.x, bird.y + offset.y, s, bird.tilt_deg


def _board_anchor_standing(bird):
    """Place the deck so its top is at Pip's body bottom (+16 from
    centre) — Pip reads as STANDING on it, not floating above."""
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    offset = pygame.math.Vector2(0, 19 * s)
    offset = offset.rotate(-bird.tilt_deg)
    return bird.x + offset.x, bird.y + offset.y, s, bird.tilt_deg


def _blit_at(scene, surf, bx, by, tilt):
    rotated = pygame.transform.rotate(surf, tilt)
    r = rotated.get_rect(center=(int(bx), int(by)))
    scene.blit(rotated, r.topleft)


# ─── shared skull deck (variant 12 art) positioned tight against Pip ───────

def draw_skull_deck_tight(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    board_w = int(34 * s)
    deck_h = max(4, int(7 * s))
    pad = 10
    surf = pygame.Surface(
        (board_w + pad * 2, deck_h * 5 + pad * 2), pygame.SRCALPHA)
    cx, cy = surf.get_width() // 2, surf.get_height() // 2 - 2

    deck = pygame.Rect(0, 0, board_w, deck_h)
    deck.center = (cx, cy)
    # Black deck with thin chrome outline.
    pygame.draw.rect(surf, (200, 200, 210), deck, border_radius=3)
    pygame.draw.rect(surf, (10, 10, 18), deck.inflate(-2, -2),
                     border_radius=2)
    # White crossbones — two diagonals across the deck.
    pygame.draw.line(surf, (235, 235, 225),
                     (deck.left + 4, deck.top + 1),
                     (deck.right - 4, deck.bottom - 1), 1)
    pygame.draw.line(surf, (235, 235, 225),
                     (deck.left + 4, deck.bottom - 1),
                     (deck.right - 4, deck.top + 1), 1)
    # White skull dome (small ellipse + two dark eye sockets).
    sk_w, sk_h = max(5, int(7 * s)), max(3, int(5 * s))
    sk_rect = pygame.Rect(0, 0, sk_w, sk_h)
    sk_rect.center = (cx, deck.centery - 1)
    pygame.draw.ellipse(surf, (240, 240, 230), sk_rect)
    pygame.draw.ellipse(surf, (10, 10, 18), sk_rect, 1)
    eye_y = sk_rect.centery - 1
    pygame.draw.circle(surf, (10, 10, 18), (sk_rect.centerx - 1, eye_y), 1)
    pygame.draw.circle(surf, (10, 10, 18), (sk_rect.centerx + 1, eye_y), 1)
    # Trucks + white wheels with red bullseye.
    truck_h = max(1, int(2 * s))
    wheel_r = max(2, int(3 * s))
    spin = bird.frame_t * 4.0
    for sign in (-1, 1):
        tx = cx + sign * int(board_w * 0.32) - 3
        pygame.draw.rect(surf, (60, 60, 70),
                         (tx, deck.bottom, 6, truck_h))
        wx = cx + sign * int(board_w * 0.32)
        wy = deck.bottom + truck_h + wheel_r
        pygame.draw.circle(surf, (50, 50, 60), (wx, wy), wheel_r + 1)
        pygame.draw.circle(surf, (245, 240, 230), (wx, wy), wheel_r)
        pygame.draw.circle(surf, (200, 50, 50), (wx, wy), 1)
        sx = wx + int(math.cos(spin + sign * 1.0) * wheel_r * 0.6)
        sy = wy + int(math.sin(spin + sign * 1.0) * wheel_r * 0.6)
        pygame.draw.line(surf, (180, 50, 50), (wx, wy), (sx, sy), 1)

    bx, by, _s, tilt = _board_anchor_standing(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── 5 helmet variants ─────────────────────────────────────────────────────
# All variants share `_draw_helmet_base` so the dome + rim + vents +
# CHIN STRAP read the same way. The strap is the killer "this is a
# helmet, not a hat" cue at this scale. No brims anywhere.

# Helmet surface layout (in surface coords). Surface is intentionally
# tall — the chinstrap trails well below the rim so straps stay inside
# the surface after rotation and land on Pip's cheek/jaw in world space.
HELMET_W   = 24   # dome width
HELMET_H   = 15   # dome height (top half of the ellipse)
HELMET_PAD = 4    # margin around the dome
STRAP_DROP = 12   # how far the straps trail below the rim


def _helmet_surface(s):
    """Tall enough that rotated chinstraps stay inside the surface."""
    hw = int(HELMET_W * s)
    hh = int(HELMET_H * s)
    pad = HELMET_PAD
    drop = int(STRAP_DROP * s)
    surf = pygame.Surface(
        (hw + pad * 2, hh + pad * 2 + drop), pygame.SRCALPHA)
    return surf, hw, hh, pad, drop


def _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col, hi_col, rim_col,
                      *, vent_col=(15, 15, 18),
                      strap_col=(40, 40, 50),
                      buckle_col=(180, 180, 190)):
    """Shared dome + highlight + rim + vents + chinstrap. The combination
    of vents (top of dome) and a clearly visible chinstrap (trailing
    below the rim) makes the silhouette read unambiguously as a HELMET
    rather than a hat at game scale."""
    # Dome ellipse — top half visible, bottom half clipped by the rim.
    dome_rect = pygame.Rect(pad, pad, hw, hh * 2)
    pygame.draw.ellipse(surf, dome_col, dome_rect)
    # Glossy highlight on the front-top.
    pygame.draw.ellipse(surf, hi_col,
                        pygame.Rect(pad + 3, pad + 1,
                                    max(2, hw - 8), max(2, hh - 4)))
    # Air vents — three short dark slits across the dome top. The strongest
    # "helmet not hat" cue at this scale apart from the strap.
    vent_y = pad + hh // 2 - 2
    for vx_frac in (0.30, 0.50, 0.70):
        vx = pad + int(hw * vx_frac)
        pygame.draw.line(surf, vent_col, (vx - 1, vent_y), (vx + 1, vent_y), 1)
    # Rim band — separates dome from face.
    rim_rect = pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 3)
    pygame.draw.ellipse(surf, rim_col, rim_rect)
    # Chinstrap — two short straps from the rim shoulders angling inward
    # to a buckle below. After tilt rotation these land on Pip's cheek/jaw.
    left_shoulder  = (pad + 3,      pad + hh + 1)
    right_shoulder = (pad + hw - 3, pad + hh + 1)
    buckle = (pad + hw // 2, pad + hh + drop - 2)
    pygame.draw.line(surf, strap_col, left_shoulder,  buckle, 2)
    pygame.draw.line(surf, strap_col, right_shoulder, buckle, 2)
    pygame.draw.circle(surf, buckle_col, buckle, 2)


def _add_skull_emblem(surf, cx, cy, s, fg=(245, 245, 235),
                      socket=(20, 20, 25)):
    sk_w = max(4, int(7 * s))
    sk_h = max(3, int(5 * s))
    sk_rect = pygame.Rect(0, 0, sk_w, sk_h)
    sk_rect.center = (cx, cy)
    pygame.draw.ellipse(surf, fg, sk_rect)
    pygame.draw.ellipse(surf, socket, sk_rect, 1)
    eye_y = sk_rect.centery
    pygame.draw.circle(surf, socket, (sk_rect.centerx - 1, eye_y), 1)
    pygame.draw.circle(surf, socket, (sk_rect.centerx + 1, eye_y), 1)


# ── V1: Matching all-black helmet, white skull on the front ───────────────

def helmet_v1_matching(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(18, 18, 22),
                      hi_col=(55, 55, 65),
                      rim_col=(8, 8, 12),
                      strap_col=(40, 40, 50))
    _add_skull_emblem(surf, pad + hw // 2, pad + hh - 4, s,
                      fg=(245, 240, 230), socket=(15, 15, 18))
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ── V2: Classic red skater dome, white skull on the front ─────────────────

def helmet_v2_classic_red(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(210, 50, 60),
                      hi_col=(255, 150, 160),
                      rim_col=(120, 25, 35),
                      strap_col=(50, 30, 30),
                      buckle_col=(210, 180, 80))
    _add_skull_emblem(surf, pad + hw // 2, pad + hh - 4, s,
                      fg=(245, 245, 235), socket=(120, 20, 30))
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ── V3: Black dome with 3 silver spikes + studded chinstrap ───────────────

def helmet_v3_spiked(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(18, 18, 22),
                      hi_col=(55, 55, 65),
                      rim_col=(200, 200, 210),     # chrome rim
                      strap_col=(35, 35, 45),
                      buckle_col=(200, 200, 210))  # silver buckle
    # Three silver spikes rising from the dome centreline. The shared
    # dome is drawn already; spikes overlay it.
    spike_xs = (pad + hw // 4, pad + hw // 2, pad + 3 * hw // 4)
    spike_base_y = pad + 1
    for sx in spike_xs:
        pygame.draw.polygon(surf, (200, 200, 210),
                            [(sx - 2, spike_base_y),
                             (sx + 2, spike_base_y),
                             (sx,     spike_base_y - 4)])
        pygame.draw.polygon(surf, (60, 60, 70),
                            [(sx - 2, spike_base_y),
                             (sx + 2, spike_base_y),
                             (sx,     spike_base_y - 4)], 1)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ── V4: Black helmet under a red bandana wrap (helmet still visible) ──────

def helmet_v4_bandana(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    # Draw the base helmet first so vents + rim + chinstrap are present.
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(18, 18, 22),
                      hi_col=(55, 55, 65),
                      rim_col=(8, 8, 12),
                      strap_col=(40, 40, 50))
    # Red bandana band wraps across the upper third of the dome. Air
    # vents sit ABOVE the band; rim + chinstrap stay visible BELOW it,
    # so the helmet identity is preserved.
    band_top = pad + 1
    band_h = max(2, hh // 3)
    band_rect = pygame.Rect(pad - 1, band_top, hw + 2, band_h)
    pygame.draw.rect(surf, (200, 40, 40), band_rect)
    pygame.draw.line(surf, (255, 130, 110),
                     (pad, band_top + 1),
                     (pad + hw, band_top + 1), 1)
    # Knot + tail trailing left (the back of Pip).
    knot_x = pad - 1
    knot_y = band_top + band_h // 2
    pygame.draw.circle(surf, (180, 30, 30), (knot_x, knot_y), 2)
    pygame.draw.line(surf, (200, 40, 40),
                     (knot_x - 1, knot_y),
                     (knot_x - 5, knot_y + 3), 2)
    # Tiny skull on the bandana front.
    _add_skull_emblem(surf, pad + hw // 2, knot_y, s,
                      fg=(245, 240, 230), socket=(110, 20, 25))
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ── V5: Black helmet with a white bone-mohawk fin down the centreline ─────

def helmet_v5_skull_mohawk(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(18, 18, 22),
                      hi_col=(55, 55, 65),
                      rim_col=(8, 8, 12),
                      strap_col=(40, 40, 50))
    # Bone-mohawk fin running the dome centreline — a wedge polygon
    # that rises 3 px above the dome, narrowing forward like a real
    # mohawk crest. Drawn last so it sits on top of the dome + vents.
    fin_top_y = pad - 3
    fin_base_y = pad + 2
    cx_s = pad + hw // 2
    fin_pts = [
        (cx_s - hw // 4, fin_base_y),       # rear base
        (cx_s - hw // 5, fin_top_y),        # rear top
        (cx_s + hw // 5, fin_top_y),        # front top
        (cx_s + hw // 4, fin_base_y),       # front base
    ]
    pygame.draw.polygon(surf, (240, 235, 220), fin_pts)
    pygame.draw.polygon(surf, (140, 130, 110), fin_pts, 1)
    # Tiny skull on the front of the dome.
    _add_skull_emblem(surf, pad + hw // 2, pad + hh - 4, s,
                      fg=(240, 235, 220), socket=(15, 15, 18))
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── driver ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("variant_1_matching_black.png", helmet_v1_matching),
    ("variant_2_classic_red.png",    helmet_v2_classic_red),
    ("variant_3_spiked_punk.png",    helmet_v3_spiked),
    ("variant_4_bandana_wrap.png",   helmet_v4_bandana),
    ("variant_5_skull_mohawk.png",   helmet_v5_skull_mohawk),
]


def render_variant(helmet_drawer):
    base, bird = render_gameplay_base()
    # Override the built-in helmet + skateboard so we control both
    # anchor positions. Bird.draw still handles the body sprite.
    bird._draw_helmet = lambda surf, cx, cy, flipped: helmet_drawer(surf, bird)
    bird._draw_skateboard = lambda surf, cx, cy, flipped: draw_skull_deck_tight(surf, bird)
    bird.draw(base, 0, 0)
    return base


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots",
                           "skateboard_variants", "skull_full_set")
    os.makedirs(out_dir, exist_ok=True)
    for fname, drawer in VARIANTS:
        frame = render_variant(drawer)
        out = os.path.join(out_dir, fname)
        pygame.image.save(frame, out)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
