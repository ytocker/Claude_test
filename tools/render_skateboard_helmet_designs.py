"""Render 5 SKATEBOARD helmet-sprite design variants.

Same gallery format as `render_skateboard_board_designs.py`: each
helmet is shown on Pip mid-flight (so you can read it at game scale,
~24 px wide), plus a 6× zoom inset in the upper-right corner so the
design details read clearly.

The 5 helmets pair thematically with the 5 deck designs in
`render_skateboard_board_designs.py` so a chosen helmet can be matched
with a chosen deck:

  variant_1_classic_skater   — matte cherry dome with two grip-tape
                               stripes mirroring the classic_wood deck,
                               cream chinstrap, dark rim.
  variant_2_red_pro_stripe   — bright red dome with white centre stripe
                               (matches red_pro deck stripe), dark
                               chinstrap, gold buckle.
  variant_3_neon_cyber       — dark teal dome with cyan top band and
                               magenta accent line + magenta under-glow
                               halo + glowing pink chinstrap. Synthwave
                               twin to the neon_cyber deck.
  variant_4_sunset_gradient  — sunset gradient dome (yellow → orange →
                               magenta), pinstripe across the middle,
                               white chinstrap with a yellow buckle —
                               matches the sunset_fishtail wheels.
  variant_5_lime_cruiser     — bright lime plastic dome with a white
                               highlight blob, white chinstrap, grey
                               buckle. Matches the penny cruiser deck.

All five share `_draw_helmet_base`: dome + glossy highlight + rim band
+ 3 air vents + 2-strap chinstrap to a buckle dot — the chinstrap and
vents are the strongest "helmet, not hat" cues at this scale.

Anchor lives ON Pip's head (derived from the actual head ellipse at
sprite (47, 21), game/parrot.py:149 — same anchor the proven
triple-mode top-hat uses in game/dollar_parrot_hat.py:34-35).

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python tools/render_skateboard_helmet_designs.py
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


# ─── anchor + blit helpers ─────────────────────────────────────────────────

def _helmet_anchor(bird):
    """Anchor at the head x-centre (+15) so the helmet sits ON Pip's
    head, not above his body centre. y = -11 puts the surface centre
    3 px below the crown highlight; the rim band lands just under the
    eye-line and the chinstrap trails across the cheek. Rotates with
    bird.tilt_deg so the helmet banks with Pip during flaps and the
    3-tap backflip spin."""
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    offset = pygame.math.Vector2(15 * s, -11 * s)
    offset = offset.rotate(-bird.tilt_deg)
    return bird.x + offset.x, bird.y + offset.y, s, bird.tilt_deg


def _blit_at(surf, helmet_surf, bx, by, tilt):
    rotated = pygame.transform.rotate(helmet_surf, tilt)
    r = rotated.get_rect(center=(int(bx), int(by)))
    surf.blit(rotated, r.topleft)


# ─── shared helmet primitive ───────────────────────────────────────────────
# Dome + glossy highlight + rim band + 3 air vents across the dome top +
# a 2-strap chinstrap descending to a buckle dot. Combination of vents
# (top) and chinstrap (bottom) is what reads unambiguously as "helmet".

HELMET_W   = 24
HELMET_H   = 15
HELMET_PAD = 4
STRAP_DROP = 12


def _helmet_surface(s):
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
    dome_rect = pygame.Rect(pad, pad, hw, hh * 2)
    pygame.draw.ellipse(surf, dome_col, dome_rect)
    pygame.draw.ellipse(surf, hi_col,
                        pygame.Rect(pad + 3, pad + 1,
                                    max(2, hw - 8), max(2, hh - 4)))
    vent_y = pad + hh // 2 - 2
    for vx_frac in (0.30, 0.50, 0.70):
        vx = pad + int(hw * vx_frac)
        pygame.draw.line(surf, vent_col, (vx - 1, vent_y), (vx + 1, vent_y), 1)
    rim_rect = pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 3)
    pygame.draw.ellipse(surf, rim_col, rim_rect)
    left_shoulder  = (pad + 3,      pad + hh + 1)
    right_shoulder = (pad + hw - 3, pad + hh + 1)
    buckle = (pad + hw // 2, pad + hh + drop - 2)
    pygame.draw.line(surf, strap_col, left_shoulder,  buckle, 2)
    pygame.draw.line(surf, strap_col, right_shoulder, buckle, 2)
    pygame.draw.circle(surf, buckle_col, buckle, 2)


# ─── 5 helmet designs ──────────────────────────────────────────────────────

# ── V1 — Classic Skater (matte cherry, grip-tape stripes) ─────────────────

def helmet_v1_classic_skater(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(120, 70, 40),
                      hi_col=(190, 130, 80),
                      rim_col=(50, 25, 18),
                      strap_col=(80, 60, 40),
                      buckle_col=(220, 195, 140))
    # Two grip-tape style stripes wrapping across the dome top — the
    # signature mirror of the classic_wood deck's grip tape.
    stripe_col = (35, 30, 25)
    sy1 = pad + 2
    sy2 = pad + 4
    pygame.draw.line(surf, stripe_col,
                     (pad + 4, sy1), (pad + hw - 4, sy1), 1)
    pygame.draw.line(surf, stripe_col,
                     (pad + 4, sy2), (pad + hw - 4, sy2), 1)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ── V2 — Red Pro Stripe (bright red dome with white centre stripe) ────────

def helmet_v2_red_pro_stripe(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(220, 55, 55),
                      hi_col=(255, 140, 140),
                      rim_col=(110, 20, 20),
                      strap_col=(30, 25, 25),
                      buckle_col=(220, 180, 80))
    # White centre stripe down the dome — front-to-back across the crown.
    pygame.draw.line(surf, (250, 245, 235),
                     (pad + hw // 2, pad + 1),
                     (pad + hw // 2, pad + hh - 2),
                     max(1, int(2 * s)))
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ── V3 — Neon Cyber (cyan + magenta with under-glow halo) ─────────────────

def helmet_v3_neon_cyber(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    # Magenta under-glow halo BEFORE the helmet draws — sits behind the
    # dome like the deck's under-glow.
    glow_w = hw + 16
    glow_h = hh + 6
    glow = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
    for r in range(glow_w // 2, 0, -2):
        a = int(70 * (r / (glow_w // 2)))
        pygame.draw.ellipse(glow, (255, 60, 200, a),
                            (glow_w // 2 - r, glow_h // 2 - r // 2,
                             r * 2, max(1, r)))
    surf.blit(glow, (pad + hw // 2 - glow_w // 2,
                     pad + hh - glow_h // 2),
              special_flags=pygame.BLEND_RGBA_ADD)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(15, 60, 90),
                      hi_col=(60, 200, 230),
                      rim_col=(180, 190, 200),
                      strap_col=(80, 30, 80),
                      buckle_col=(255, 100, 220))
    # Magenta accent line across the dome centreline (matches the deck
    # accent stripe).
    pygame.draw.line(surf, (255, 100, 220),
                     (pad + 2, pad + hh // 2 + 1),
                     (pad + hw - 2, pad + hh // 2 + 1),
                     max(1, int(s)))
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ── V4 — Sunset Gradient (yellow → orange → magenta dome) ─────────────────

def helmet_v4_sunset_gradient(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    # Build a gradient ellipse manually by drawing horizontal lines
    # masked by the dome ellipse, top→bottom: yellow → orange → magenta.
    dome_rect = pygame.Rect(pad, pad, hw, hh * 2)
    # Outline (deep purple).
    pygame.draw.ellipse(surf, (80, 20, 60), dome_rect)
    grad_layer = pygame.Surface((surf.get_width(), surf.get_height()),
                                pygame.SRCALPHA)
    inner = dome_rect.inflate(-2, -2)
    for y in range(inner.top, inner.top + hh):
        t = (y - inner.top) / max(1, hh - 1)
        col = (
            255,
            int(220 + (90 - 220) * t),
            int(80 + (190 - 80) * t),
        )
        pygame.draw.line(grad_layer, col,
                         (inner.left, y), (inner.right, y))
    mask = pygame.Surface(grad_layer.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), inner)
    grad_layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad_layer, (0, 0))
    # Glossy highlight (lighter peach top-left).
    pygame.draw.ellipse(surf, (255, 240, 200),
                        pygame.Rect(pad + 3, pad + 1,
                                    max(2, hw - 8), max(2, hh - 5)))
    # Pinstripe across the middle (matches the deck pinstripe).
    pygame.draw.line(surf, (255, 250, 230),
                     (pad + 3, pad + hh // 2 + 1),
                     (pad + hw - 3, pad + hh // 2 + 1),
                     max(1, int(s)))
    # Vents (drawn AFTER gradient so they read on the lighter top).
    vent_y = pad + hh // 2 - 2
    for vx_frac in (0.30, 0.50, 0.70):
        vx = pad + int(hw * vx_frac)
        pygame.draw.line(surf, (80, 20, 60),
                         (vx - 1, vent_y), (vx + 1, vent_y), 1)
    # Rim, chinstrap, buckle — borrow the primitive's tail end.
    rim_rect = pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 3)
    pygame.draw.ellipse(surf, (90, 30, 60), rim_rect)
    left_shoulder  = (pad + 3,      pad + hh + 1)
    right_shoulder = (pad + hw - 3, pad + hh + 1)
    buckle = (pad + hw // 2, pad + hh + drop - 2)
    pygame.draw.line(surf, (250, 245, 235), left_shoulder,  buckle, 2)
    pygame.draw.line(surf, (250, 245, 235), right_shoulder, buckle, 2)
    pygame.draw.circle(surf, (255, 220, 60), buckle, 2)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ── V5 — Lime Cruiser (bright lime plastic to match the penny deck) ───────

def helmet_v5_lime_cruiser(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(140, 230, 80),
                      hi_col=(220, 255, 180),
                      rim_col=(60, 130, 30),
                      strap_col=(235, 235, 230),
                      buckle_col=(120, 140, 100))
    # Plastic highlight blob top-left — same cue as the cruiser deck.
    pygame.draw.ellipse(surf, (255, 255, 240),
                        pygame.Rect(pad + 3, pad + 1,
                                    max(3, hw // 3),
                                    max(2, hh // 3)))
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── zoom inset (same approach as render_skateboard_board_designs) ─────────

def _render_zoom(drawer, zoom=6):
    """Render the helmet on a clean transparent canvas with a dummy bird
    centred and zero tilt, then scale up. The board isn't drawn — this
    isolates the helmet design for inspection."""
    from game.entities import Bird
    canvas_w, canvas_h = 80, 60
    canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    dummy = Bird()
    # Anchor at +15/-11 from bird centre, so place bird so the helmet
    # lands in the upper-middle of the canvas.
    dummy.x = canvas_w // 2 - 15
    dummy.y = canvas_h // 2 + 11
    dummy.vy = 0  # Bird.tilt_deg derives from vy → 0 vy → 0 tilt
    dummy.frame_t = 0.6
    drawer(canvas, dummy)
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


# ─── driver ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("variant_1_classic_skater.png",   helmet_v1_classic_skater),
    ("variant_2_red_pro_stripe.png",   helmet_v2_red_pro_stripe),
    ("variant_3_neon_cyber.png",       helmet_v3_neon_cyber),
    ("variant_4_sunset_gradient.png",  helmet_v4_sunset_gradient),
    ("variant_5_lime_cruiser.png",     helmet_v5_lime_cruiser),
]


def render_variant(drawer):
    base_scene, bird = render_base()
    # Substitute the variant helmet for Bird._draw_helmet so Pip + board
    # + variant helmet all composite together. Bird.draw calls
    # _draw_helmet(surf, cx, cy, flipped); our drawer is bird-aware so we
    # discard those args and pass through.
    bird._draw_helmet = lambda surf, cx, cy, flipped: drawer(surf, bird)
    bird.draw(base_scene, 0, 0)
    zoomed = _render_zoom(drawer)
    _blit_inset(base_scene, zoomed)
    return base_scene


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots",
                           "skateboard_variants", "helmet_designs")
    os.makedirs(out_dir, exist_ok=True)
    for fname, drawer in VARIANTS:
        frame = render_variant(drawer)
        out = os.path.join(out_dir, fname)
        pygame.image.save(frame, out)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
