"""Render 5 HELMET designs that all match the chosen skateboard.

The skateboard palette is FIXED (live deck in game/entities.py:
_draw_skateboard). Every helmet variant draws using ONLY those exact
RGB values, so the kit stays matched. The variants differ in shape
and decal layout only.

Shared palette (every helmet uses these — no others):
  BLACK       = (10, 10, 18)      deck fill / skull + bone outlines
  CHROME      = (200, 200, 210)   deck outline / rim band
  SLATE_DK    = (50, 50, 60)      wheel outer / highlight
  SLATE       = (60, 60, 70)      trucks / chinstrap
  BONE        = (240, 240, 230)   deck skull body / mohawk / decals
  CROSSBONE   = (235, 235, 225)   deck crossbones / decals
  CREAM       = (245, 240, 230)   wheel face / accents
  RED         = (200, 50, 50)     wheel bullseye / buckle / accent

Variants:
  variant_1_bone_mohawk     — current LIVE helmet. Bone-fin mohawk +
                              skull on front + red buckle.
  variant_2_skull_crown     — dominant LARGE bone skull occupying the
                              dome front; no mohawk. Skull-as-logo,
                              echoing the deck's centred skull.
  variant_3_chrome_stripe   — thick chrome stripe front-to-back along
                              the dome centreline (no fin); tiny skull
                              on the front. Echoes the deck's chrome
                              outline as a band.
  variant_4_crossbones_x    — bold bone-white crossbones X across the
                              dome top (mirroring the deck's diagonals)
                              + small skull at the intersection.
  variant_5_red_bullseye    — bone skull on the front backed by a red
                              ring (mirroring the deck's wheel bullseye)
                              + chrome buckle. Red moves from buckle to
                              backing-accent.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python tools/render_skateboard_matching_helmets.py
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

from game.config import W, SHRINK_SCALE
from tools.render_skateboard_variants import render_base


# ─── shared palette — these are the ONLY colours allowed ───────────────────

BLACK     = (10, 10, 18)
CHROME    = (200, 200, 210)
SLATE_DK  = (50, 50, 60)
SLATE     = (60, 60, 70)
BONE      = (240, 240, 230)
CROSSBONE = (235, 235, 225)
CREAM     = (245, 240, 230)
RED       = (200, 50, 50)


# ─── anchor + blit helpers ─────────────────────────────────────────────────

def _helmet_anchor(bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    offset = pygame.math.Vector2(15 * s, -11 * s)
    offset = offset.rotate(-bird.tilt_deg)
    return bird.x + offset.x, bird.y + offset.y, s, bird.tilt_deg


def _blit_at(scene, surf, bx, by, tilt):
    rotated = pygame.transform.rotate(surf, tilt)
    r = rotated.get_rect(center=(int(bx), int(by)))
    scene.blit(rotated, r.topleft)


# ─── shared helmet surface + skull primitive ───────────────────────────────

HELMET_W, HELMET_H, HELMET_PAD, STRAP_DROP = 24, 15, 4, 12


def _helmet_surface(s):
    hw = int(HELMET_W * s)
    hh = int(HELMET_H * s)
    pad = HELMET_PAD
    drop = int(STRAP_DROP * s)
    surf = pygame.Surface(
        (hw + pad * 2, hh + pad * 2 + drop), pygame.SRCALPHA)
    return surf, hw, hh, pad, drop


def _draw_dome(surf, hw, hh, pad):
    """Black dome + dark-slate gloss highlight + 3 vents on top + chrome
    rim band. Shared across every variant so the silhouette is identical."""
    pygame.draw.ellipse(surf, BLACK,
                        pygame.Rect(pad, pad, hw, hh * 2))
    pygame.draw.ellipse(surf, SLATE_DK,
                        pygame.Rect(pad + 3, pad + 1,
                                    max(2, hw - 8), max(2, hh - 4)))
    vent_y = pad + hh // 2 - 2
    for vx_frac in (0.30, 0.50, 0.70):
        vx = pad + int(hw * vx_frac)
        pygame.draw.line(surf, BLACK,
                         (vx - 1, vent_y), (vx + 1, vent_y), 1)
    pygame.draw.ellipse(surf, CHROME,
                        pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 3))


def _draw_chinstrap(surf, hw, hh, pad, drop, buckle_col=RED):
    """Slate chinstrap to a buckle dot (defaults to red wheel-centre)."""
    left_shoulder  = (pad + 3,      pad + hh + 1)
    right_shoulder = (pad + hw - 3, pad + hh + 1)
    buckle = (pad + hw // 2, pad + hh + drop - 2)
    pygame.draw.line(surf, SLATE, left_shoulder,  buckle, 2)
    pygame.draw.line(surf, SLATE, right_shoulder, buckle, 2)
    pygame.draw.circle(surf, buckle_col, buckle, 2)


def _draw_skull(surf, cx, cy, s, *, w_mul=1.0, h_mul=1.0,
                fg=BONE, outline=BLACK):
    """Small skull ellipse with eye sockets — same shape vocabulary as
    the deck's centred skull."""
    sk_w = max(4, int(7 * s * w_mul))
    sk_h = max(3, int(5 * s * h_mul))
    sk = pygame.Rect(0, 0, sk_w, sk_h)
    sk.center = (cx, cy)
    pygame.draw.ellipse(surf, fg, sk)
    pygame.draw.ellipse(surf, outline, sk, 1)
    pygame.draw.circle(surf, outline, (sk.centerx - 1, sk.centery), 1)
    pygame.draw.circle(surf, outline, (sk.centerx + 1, sk.centery), 1)


# ─── V1 — Bone Mohawk (the current live helmet) ────────────────────────────

def helmet_v1_bone_mohawk(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_dome(surf, hw, hh, pad)
    cx_s = pad + hw // 2
    fin_top_y, fin_base_y = pad - 3, pad + 2
    fin_pts = [(cx_s - hw // 4, fin_base_y),
               (cx_s - hw // 5, fin_top_y),
               (cx_s + hw // 5, fin_top_y),
               (cx_s + hw // 4, fin_base_y)]
    pygame.draw.polygon(surf, BONE, fin_pts)
    pygame.draw.polygon(surf, BLACK, fin_pts, 1)
    _draw_skull(surf, cx_s, pad + hh - 4, s)
    _draw_chinstrap(surf, hw, hh, pad, drop)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── V2 — Skull Crown (large bone skull dominating the dome) ───────────────

def helmet_v2_skull_crown(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_dome(surf, hw, hh, pad)
    cx_s = pad + hw // 2
    # LARGE skull occupying ~70% of the dome front. No mohawk — the
    # skull itself is the visual centrepiece, echoing the deck where
    # the skull is the dominant logo.
    _draw_skull(surf, cx_s, pad + hh - 5, s, w_mul=1.7, h_mul=1.5)
    _draw_chinstrap(surf, hw, hh, pad, drop)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── V3 — Chrome Stripe (chrome band front-to-back, no mohawk) ─────────────

def helmet_v3_chrome_stripe(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_dome(surf, hw, hh, pad)
    cx_s = pad + hw // 2
    # Chrome stripe down the dome centreline — same chrome as the deck
    # outline, echoed across the helmet as a band.
    stripe_w = max(2, int(3 * s))
    pygame.draw.rect(surf, CHROME,
                     pygame.Rect(cx_s - stripe_w // 2, pad + 1,
                                 stripe_w, hh - 2))
    # Tiny skull on the front (centred horizontally on the stripe).
    _draw_skull(surf, cx_s, pad + hh - 4, s, w_mul=0.85, h_mul=0.85)
    _draw_chinstrap(surf, hw, hh, pad, drop)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── V4 — Crossbones X (deck diagonals mirrored across the dome) ───────────

def helmet_v4_crossbones_x(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_dome(surf, hw, hh, pad)
    # Crossbones X across the dome — same off-white as the deck
    # crossbones, same diagonal layout.
    pygame.draw.line(surf, CROSSBONE,
                     (pad + 4, pad + 2),
                     (pad + hw - 4, pad + hh - 3),
                     max(1, int(1.5 * s)))
    pygame.draw.line(surf, CROSSBONE,
                     (pad + 4, pad + hh - 3),
                     (pad + hw - 4, pad + 2),
                     max(1, int(1.5 * s)))
    # Tiny skull where the diagonals cross.
    cx_s = pad + hw // 2
    _draw_skull(surf, cx_s, pad + hh // 2 - 1, s,
                w_mul=0.85, h_mul=0.85)
    _draw_chinstrap(surf, hw, hh, pad, drop)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── V5 — Red Bullseye (skull backed by a red ring, echoing wheels) ────────

def helmet_v5_red_bullseye(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_dome(surf, hw, hh, pad)
    cx_s = pad + hw // 2
    skull_cy = pad + hh - 4
    # Red bullseye behind the skull — echoes the deck's wheel bullseye
    # at the helmet's focal point.
    bullseye_r = max(4, int(5 * s))
    pygame.draw.circle(surf, RED, (cx_s, skull_cy), bullseye_r)
    pygame.draw.circle(surf, BLACK, (cx_s, skull_cy), bullseye_r, 1)
    # Bone skull centred on the bullseye.
    _draw_skull(surf, cx_s, skull_cy, s)
    # Buckle moves to chrome since the red accent is now on the dome.
    _draw_chinstrap(surf, hw, hh, pad, drop, buckle_col=CHROME)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── driver ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("variant_1_bone_mohawk.png",    helmet_v1_bone_mohawk),
    ("variant_2_skull_crown.png",    helmet_v2_skull_crown),
    ("variant_3_chrome_stripe.png",  helmet_v3_chrome_stripe),
    ("variant_4_crossbones_x.png",   helmet_v4_crossbones_x),
    ("variant_5_red_bullseye.png",   helmet_v5_red_bullseye),
]


def _render_zoom(helmet_drawer, zoom=8):
    """Render JUST the helmet (no parrot, no deck) on a transparent
    canvas at zero tilt, then scale up so the design reads at a glance."""
    from game.entities import Bird
    canvas_w, canvas_h = 60, 50
    canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    dummy = Bird()
    dummy.x = canvas_w // 2 - 15
    dummy.y = canvas_h // 2 + 11
    dummy.vy = 0
    dummy.frame_t = 0.6
    helmet_drawer(canvas, dummy)
    return pygame.transform.scale(canvas,
                                  (canvas_w * zoom, canvas_h * zoom))


def _blit_inset(scene, zoomed):
    inset_w, inset_h = zoomed.get_size()
    pad = 4
    rect = pygame.Rect(W - inset_w - 14, 14, inset_w + pad * 2,
                       inset_h + pad * 2)
    pygame.draw.rect(scene, (245, 240, 220), rect, border_radius=4)
    pygame.draw.rect(scene, (15, 15, 15), rect, 3, border_radius=4)
    scene.blit(zoomed, (rect.x + pad, rect.y + pad))


def render_variant(helmet_drawer):
    """Pip + the LIVE skull deck + the variant helmet, plus an 8× zoom
    inset of the helmet alone so the design detail is unambiguous."""
    scene, bird = render_base()
    bird._draw_helmet = lambda surf, cx, cy, flipped: helmet_drawer(surf, bird)
    bird.draw(scene, 0, 0)
    zoomed = _render_zoom(helmet_drawer)
    _blit_inset(scene, zoomed)
    return scene


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots",
                           "skateboard_variants", "matching_helmets")
    os.makedirs(out_dir, exist_ok=True)
    for fname, drawer in VARIANTS:
        frame = render_variant(drawer)
        out = os.path.join(out_dir, fname)
        pygame.image.save(frame, out)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
