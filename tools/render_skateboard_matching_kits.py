"""Render 5 MATCHING KIT variants — coordinated helmet + skateboard sets.

Each kit is a complete outfit: the helmet and the deck share colors,
accents, and theme so they read as one set, not two random pieces.
Pip is rendered mid-flight wearing the full kit at game scale.

Kits:

  kit_1_skull        — black + chrome + white skull. Punk skater.
                       (This is the current LIVE kit.)
  kit_2_flame        — black + red/orange flame + chrome + orange.
                       Hot-rod, fire-themed.
  kit_3_neon_cyber   — dark teal + cyan + magenta + glow halos.
                       Synthwave / cyberpunk.
  kit_4_royal_gold   — deep purple + gold accents + crown emblem.
                       Regal monarch.
  kit_5_sunset_80s   — yellow → orange → magenta gradient + white
                       pinstripe + yellow accents. 80s neon-sunset.

Same gallery pattern as render_skateboard_board_designs.py: render the
scene with Pip wearing the kit, plus a 6× zoom inset cropped to the
kit so the helmet + deck details read clearly.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python tools/render_skateboard_matching_kits.py
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

from game.config import W, SHRINK_SCALE, PARCEL_Y_OFFSET
from tools.render_skateboard_variants import render_base


# ─── shared anchors ─────────────────────────────────────────────────────────

def _helmet_anchor(bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    offset = pygame.math.Vector2(15 * s, -11 * s)
    offset = offset.rotate(-bird.tilt_deg)
    return bird.x + offset.x, bird.y + offset.y, s, bird.tilt_deg


def _board_anchor(bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    offset = pygame.math.Vector2(0, PARCEL_Y_OFFSET * s + 4 * s)
    offset = offset.rotate(-bird.tilt_deg)
    return bird.x + offset.x, bird.y + offset.y, s, bird.tilt_deg


def _blit_at(scene, surf, bx, by, tilt):
    rotated = pygame.transform.rotate(surf, tilt)
    r = rotated.get_rect(center=(int(bx), int(by)))
    scene.blit(rotated, r.topleft)


# ─── shared helmet primitive ────────────────────────────────────────────────

HELMET_W, HELMET_H, HELMET_PAD, STRAP_DROP = 24, 15, 4, 12


def _helmet_surface(s):
    hw = int(HELMET_W * s)
    hh = int(HELMET_H * s)
    pad = HELMET_PAD
    drop = int(STRAP_DROP * s)
    surf = pygame.Surface(
        (hw + pad * 2, hh + pad * 2 + drop), pygame.SRCALPHA)
    return surf, hw, hh, pad, drop


def _draw_helmet_base(surf, hw, hh, pad, drop, *,
                      dome_col, hi_col, rim_col, vent_col=(15, 15, 18),
                      strap_col=(40, 40, 50), buckle_col=(180, 180, 190)):
    pygame.draw.ellipse(surf, dome_col,
                        pygame.Rect(pad, pad, hw, hh * 2))
    pygame.draw.ellipse(surf, hi_col,
                        pygame.Rect(pad + 3, pad + 1,
                                    max(2, hw - 8), max(2, hh - 4)))
    vent_y = pad + hh // 2 - 2
    for vx_frac in (0.30, 0.50, 0.70):
        vx = pad + int(hw * vx_frac)
        pygame.draw.line(surf, vent_col, (vx - 1, vent_y), (vx + 1, vent_y), 1)
    pygame.draw.ellipse(surf, rim_col,
                        pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 3))
    left_shoulder  = (pad + 3,      pad + hh + 1)
    right_shoulder = (pad + hw - 3, pad + hh + 1)
    buckle = (pad + hw // 2, pad + hh + drop - 2)
    pygame.draw.line(surf, strap_col, left_shoulder,  buckle, 2)
    pygame.draw.line(surf, strap_col, right_shoulder, buckle, 2)
    pygame.draw.circle(surf, buckle_col, buckle, 2)


def _board_surface(s, board_w=34, deck_h_min=4, deck_h_mult=7):
    bw = int(board_w * s)
    dh = max(deck_h_min, int(deck_h_mult * s))
    pad = 10
    surf = pygame.Surface(
        (bw + pad * 2, dh * 5 + pad * 2), pygame.SRCALPHA)
    bsx = surf.get_width() // 2
    bsy = surf.get_height() // 2 - 2
    deck = pygame.Rect(0, 0, bw, dh)
    deck.center = (bsx, bsy)
    return surf, bw, dh, pad, bsx, bsy, deck


def _wheels_trucks(surf, cx, deck, s, bird, *,
                   truck_col, wheel_outer, wheel_inner, wheel_dot,
                   spoke_col):
    truck_h = max(1, int(2 * s))
    wheel_r = max(2, int(3 * s))
    spin = bird.frame_t * 4.0
    for sign in (-1, 1):
        tx = cx + sign * int(deck.width * 0.32) - 3
        pygame.draw.rect(surf, truck_col,
                         (tx, deck.bottom, 6, truck_h))
        wx = cx + sign * int(deck.width * 0.32)
        wy = deck.bottom + truck_h + wheel_r
        pygame.draw.circle(surf, wheel_outer, (wx, wy), wheel_r + 1)
        pygame.draw.circle(surf, wheel_inner, (wx, wy), wheel_r)
        pygame.draw.circle(surf, wheel_dot, (wx, wy), 1)
        sx = wx + int(math.cos(spin + sign * 1.0) * wheel_r * 0.6)
        sy = wy + int(math.sin(spin + sign * 1.0) * wheel_r * 0.6)
        pygame.draw.line(surf, spoke_col, (wx, wy), (sx, sy), 1)


# ─── KIT 1 — Skull (black + chrome + white skull) ──────────────────────────

def kit_1_skull_helmet(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(18, 18, 22),
                      hi_col=(55, 55, 65),
                      rim_col=(8, 8, 12),
                      strap_col=(40, 40, 50),
                      buckle_col=(180, 180, 190))
    cx_s = pad + hw // 2
    fin_top_y, fin_base_y = pad - 3, pad + 2
    pygame.draw.polygon(surf, (240, 235, 220),
                        [(cx_s - hw // 4, fin_base_y),
                         (cx_s - hw // 5, fin_top_y),
                         (cx_s + hw // 5, fin_top_y),
                         (cx_s + hw // 4, fin_base_y)])
    sk = pygame.Rect(0, 0, max(4, int(7 * s)), max(3, int(5 * s)))
    sk.center = (cx_s, pad + hh - 4)
    pygame.draw.ellipse(surf, (240, 235, 220), sk)
    pygame.draw.circle(surf, (15, 15, 18), (sk.centerx - 1, sk.centery), 1)
    pygame.draw.circle(surf, (15, 15, 18), (sk.centerx + 1, sk.centery), 1)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


def kit_1_skull_deck(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, bw, dh, pad, bsx, bsy, deck = _board_surface(s)
    pygame.draw.rect(surf, (200, 200, 210), deck, border_radius=3)
    pygame.draw.rect(surf, (10, 10, 18), deck.inflate(-2, -2), border_radius=2)
    pygame.draw.line(surf, (235, 235, 225),
                     (deck.left + 4, deck.top + 1),
                     (deck.right - 4, deck.bottom - 1), 1)
    pygame.draw.line(surf, (235, 235, 225),
                     (deck.left + 4, deck.bottom - 1),
                     (deck.right - 4, deck.top + 1), 1)
    sk = pygame.Rect(0, 0, max(5, int(7 * s)), max(3, int(5 * s)))
    sk.center = (bsx, deck.centery - 1)
    pygame.draw.ellipse(surf, (240, 240, 230), sk)
    pygame.draw.circle(surf, (10, 10, 18), (sk.centerx - 1, sk.centery - 1), 1)
    pygame.draw.circle(surf, (10, 10, 18), (sk.centerx + 1, sk.centery - 1), 1)
    _wheels_trucks(surf, bsx, deck, s, bird,
                   truck_col=(60, 60, 70),
                   wheel_outer=(50, 50, 60),
                   wheel_inner=(245, 240, 230),
                   wheel_dot=(200, 50, 50),
                   spoke_col=(180, 50, 50))
    bx, by, _s, tilt = _board_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── KIT 2 — Flame (black + red/orange flame + chrome) ─────────────────────

def _flame_band(surf, rect):
    """Horizontal flame gradient (yellow centre → orange → red edge)."""
    for x in range(rect.width):
        t = abs(x - rect.width / 2) / max(1, rect.width / 2)
        col = (
            int(255),
            int(240 + (60 - 240) * t),
            int(120 + (20 - 120) * t),
        )
        pygame.draw.line(surf, col,
                         (rect.left + x, rect.top),
                         (rect.left + x, rect.bottom))
    for fx in range(rect.left + 2, rect.right, 5):
        pygame.draw.polygon(surf, (255, 240, 100),
                            [(fx, rect.top),
                             (fx - 1, rect.top - 2),
                             (fx + 1, rect.top - 2)])


def kit_2_flame_helmet(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(15, 15, 20),
                      hi_col=(45, 45, 55),
                      rim_col=(70, 70, 80),         # chrome rim
                      strap_col=(35, 25, 20),
                      buckle_col=(255, 140, 30))    # orange buckle
    # Flame band across the dome upper-third.
    band = pygame.Rect(pad + 1, pad + 2, hw - 2, max(2, hh // 3))
    _flame_band(surf, band)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


def kit_2_flame_deck(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, bw, dh, pad, bsx, bsy, deck = _board_surface(s)
    pygame.draw.rect(surf, (5, 5, 10), deck, border_radius=3)
    pygame.draw.rect(surf, (25, 25, 35), deck.inflate(-2, -2),
                     border_radius=2)
    # Flame strip across the bottom half of the deck.
    flame_rect = pygame.Rect(deck.left + 1, deck.centery - 1,
                             deck.width - 2, deck.height // 2 + 1)
    _flame_band(surf, flame_rect)
    _wheels_trucks(surf, bsx, deck, s, bird,
                   truck_col=(70, 70, 80),
                   wheel_outer=(40, 40, 50),
                   wheel_inner=(210, 215, 225),
                   wheel_dot=(255, 130, 20),
                   spoke_col=(120, 120, 130))
    bx, by, _s, tilt = _board_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── KIT 3 — Neon Cyber (teal + cyan + magenta + glow) ─────────────────────

def _magenta_glow(surf, cx, cy, w, h):
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    for r in range(w // 2, 0, -2):
        a = int(70 * (r / (w // 2)))
        pygame.draw.ellipse(glow, (255, 60, 200, a),
                            (w // 2 - r, h // 2 - r // 2,
                             r * 2, max(1, r)))
    surf.blit(glow, (cx - w // 2, cy - h // 2),
              special_flags=pygame.BLEND_RGBA_ADD)


def kit_3_neon_helmet(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _magenta_glow(surf, pad + hw // 2, pad + hh, hw + 16, hh + 6)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(15, 60, 90),
                      hi_col=(60, 200, 230),
                      rim_col=(255, 100, 220),      # magenta rim
                      strap_col=(180, 60, 160),
                      buckle_col=(255, 100, 220))
    pygame.draw.line(surf, (255, 100, 220),
                     (pad + 2, pad + hh // 2 + 1),
                     (pad + hw - 2, pad + hh // 2 + 1), max(1, int(s)))
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


def kit_3_neon_deck(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, bw, dh, pad, bsx, bsy, deck = _board_surface(s, deck_h_min=3,
                                                       deck_h_mult=6)
    _magenta_glow(surf, bsx, deck.bottom, bw + 16, dh * 3 + 4)
    pygame.draw.rect(surf, (15, 60, 90), deck, border_radius=3)
    pygame.draw.rect(surf, (60, 200, 230),
                     pygame.Rect(deck.left + 1, deck.top + 1,
                                 deck.width - 2, max(1, deck.height // 2)),
                     border_radius=2)
    pygame.draw.line(surf, (255, 100, 220),
                     (deck.left + 2, deck.centery),
                     (deck.right - 2, deck.centery), max(1, int(s)))
    _wheels_trucks(surf, bsx, deck, s, bird,
                   truck_col=(180, 190, 200),
                   wheel_outer=(160, 30, 130),
                   wheel_inner=(255, 100, 220),
                   wheel_dot=(255, 240, 250),
                   spoke_col=(180, 60, 160))
    bx, by, _s, tilt = _board_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── KIT 4 — Royal Gold (deep purple + gold + crown) ───────────────────────

def _crown_emblem(surf, cx, cy, s, fg=(240, 200, 60), shade=(160, 110, 20)):
    """Small 3-point crown — base bar + three peaks + a centre gem."""
    w = max(6, int(9 * s))
    h = max(3, int(5 * s))
    base = pygame.Rect(cx - w // 2, cy + h // 2 - 1, w, max(1, int(2 * s)))
    pygame.draw.rect(surf, fg, base)
    for ix, sign in ((cx - w // 2, -1), (cx, 0), (cx + w // 2 - 1, 1)):
        pygame.draw.polygon(surf, fg,
                            [(ix - 1, cy + h // 2),
                             (ix + 1, cy + h // 2),
                             (ix,     cy - h // 2)])
    pygame.draw.circle(surf, (220, 60, 80), (cx, cy + h // 2 - 1), 1)
    pygame.draw.rect(surf, shade,
                     (base.left, base.top, base.width, 1))


def kit_4_royal_helmet(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    _draw_helmet_base(surf, hw, hh, pad, drop,
                      dome_col=(70, 30, 110),
                      hi_col=(140, 80, 180),
                      rim_col=(240, 200, 60),       # gold rim
                      strap_col=(60, 25, 80),
                      buckle_col=(240, 200, 60))
    # Gold crown emblem on the front of the dome.
    _crown_emblem(surf, pad + hw // 2, pad + hh - 4, s)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


def kit_4_royal_deck(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, bw, dh, pad, bsx, bsy, deck = _board_surface(s)
    pygame.draw.rect(surf, (240, 200, 60), deck, border_radius=3)
    pygame.draw.rect(surf, (70, 30, 110), deck.inflate(-2, -2),
                     border_radius=2)
    # Gold pinstripes along the top + bottom of the deck.
    pygame.draw.line(surf, (240, 200, 60),
                     (deck.left + 3, deck.top + 1),
                     (deck.right - 3, deck.top + 1), 1)
    pygame.draw.line(surf, (240, 200, 60),
                     (deck.left + 3, deck.bottom - 2),
                     (deck.right - 3, deck.bottom - 2), 1)
    # Crown emblem at deck centre.
    _crown_emblem(surf, bsx, deck.centery - 1, s)
    _wheels_trucks(surf, bsx, deck, s, bird,
                   truck_col=(60, 50, 30),
                   wheel_outer=(30, 25, 20),
                   wheel_inner=(20, 20, 25),
                   wheel_dot=(240, 200, 60),
                   spoke_col=(180, 140, 40))
    bx, by, _s, tilt = _board_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── KIT 5 — Sunset 80s (yellow → orange → magenta + pinstripe) ────────────

def _sunset_gradient(surf, rect):
    """Fill the rect with a vertical sunset gradient: yellow → orange →
    magenta top to bottom."""
    for y in range(rect.top, rect.bottom):
        t = (y - rect.top) / max(1, rect.height - 1)
        col = (
            255,
            int(220 + (90 - 220) * t),
            int(80 + (190 - 80) * t),
        )
        pygame.draw.line(surf, col,
                         (rect.left, y), (rect.right, y))


def kit_5_sunset_helmet(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, hw, hh, pad, drop = _helmet_surface(s)
    # Outline + gradient dome.
    pygame.draw.ellipse(surf, (80, 20, 60),
                        pygame.Rect(pad, pad, hw, hh * 2))
    grad = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    inner = pygame.Rect(pad + 1, pad + 1, hw - 2, hh - 1)
    _sunset_gradient(grad, inner)
    mask = pygame.Surface(grad.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), inner)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (0, 0))
    pygame.draw.ellipse(surf, (255, 240, 200),
                        pygame.Rect(pad + 3, pad + 1,
                                    max(2, hw - 8), max(2, hh - 5)))
    # Pinstripe + vents.
    pygame.draw.line(surf, (255, 250, 230),
                     (pad + 3, pad + hh // 2 + 1),
                     (pad + hw - 3, pad + hh // 2 + 1), max(1, int(s)))
    vent_y = pad + hh // 2 - 2
    for vx_frac in (0.30, 0.50, 0.70):
        vx = pad + int(hw * vx_frac)
        pygame.draw.line(surf, (80, 20, 60),
                         (vx - 1, vent_y), (vx + 1, vent_y), 1)
    # Rim + chinstrap + yellow buckle.
    pygame.draw.ellipse(surf, (90, 30, 60),
                        pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 3))
    left_shoulder  = (pad + 3,      pad + hh + 1)
    right_shoulder = (pad + hw - 3, pad + hh + 1)
    buckle = (pad + hw // 2, pad + hh + drop - 2)
    pygame.draw.line(surf, (250, 245, 235), left_shoulder,  buckle, 2)
    pygame.draw.line(surf, (250, 245, 235), right_shoulder, buckle, 2)
    pygame.draw.circle(surf, (255, 220, 60), buckle, 2)
    bx, by, _s, tilt = _helmet_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


def kit_5_sunset_deck(scene, bird):
    s = SHRINK_SCALE if bird.shrink_active else 1.0
    surf, bw, dh, pad, bsx, bsy, deck = _board_surface(s)
    pygame.draw.rect(surf, (80, 20, 60), deck, border_radius=3)
    grad = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    inner = deck.inflate(-2, -2)
    _sunset_gradient(grad, inner)
    mask = pygame.Surface(grad.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), inner, border_radius=2)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (0, 0))
    pygame.draw.line(surf, (255, 250, 230),
                     (deck.left + 3, deck.centery),
                     (deck.right - 3, deck.centery), max(1, int(s)))
    _wheels_trucks(surf, bsx, deck, s, bird,
                   truck_col=(30, 20, 25),
                   wheel_outer=(60, 30, 40),
                   wheel_inner=(250, 245, 235),
                   wheel_dot=(255, 220, 60),
                   spoke_col=(255, 180, 100))
    bx, by, _s, tilt = _board_anchor(bird)
    _blit_at(scene, surf, bx, by, tilt)


# ─── zoom inset (Pip + kit, scaled up) ─────────────────────────────────────

def _render_zoom(helmet_drawer, deck_drawer, zoom=4):
    """Render Pip wearing the kit on a clean canvas, then scale up so the
    helmet + deck details read clearly side-by-side."""
    from game.entities import Bird
    canvas_w, canvas_h = 110, 100
    canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    dummy = Bird()
    dummy.x = canvas_w // 2 - 8
    dummy.y = canvas_h // 2 - 2
    dummy.vy = 0
    dummy.frame_t = 0.6
    dummy.skateboard_active = True
    dummy._draw_helmet = lambda surf, cx, cy, flipped: helmet_drawer(surf, dummy)
    dummy._draw_skateboard = lambda surf, cx, cy, flipped: deck_drawer(surf, dummy)
    dummy.draw(canvas, 0, 0)
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

KITS = [
    ("kit_1_skull.png",       kit_1_skull_helmet,  kit_1_skull_deck),
    ("kit_2_flame.png",       kit_2_flame_helmet,  kit_2_flame_deck),
    ("kit_3_neon_cyber.png",  kit_3_neon_helmet,   kit_3_neon_deck),
    ("kit_4_royal_gold.png",  kit_4_royal_helmet,  kit_4_royal_deck),
    ("kit_5_sunset_80s.png",  kit_5_sunset_helmet, kit_5_sunset_deck),
]


def render_kit(helmet_drawer, deck_drawer):
    scene, bird = render_base()
    bird._draw_helmet = lambda surf, cx, cy, flipped: helmet_drawer(surf, bird)
    bird._draw_skateboard = lambda surf, cx, cy, flipped: deck_drawer(surf, bird)
    bird.draw(scene, 0, 0)
    zoomed = _render_zoom(helmet_drawer, deck_drawer)
    _blit_inset(scene, zoomed)
    return scene


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots",
                           "skateboard_variants", "matching_kits")
    os.makedirs(out_dir, exist_ok=True)
    for fname, helmet, deck in KITS:
        frame = render_kit(helmet, deck)
        out = os.path.join(out_dir, fname)
        pygame.image.save(frame, out)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
