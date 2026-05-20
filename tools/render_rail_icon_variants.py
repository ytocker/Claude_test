"""Render 5 RAIL/CART powerup-icon design candidates. The current
live icon (`_draw_rail_icon`) is a tiny 2-line track with a gold
halo behind it; the halo is removed in all candidates here and
each variant proposes a richer, more "outstanding" silhouette
inspired by minecart / rollercoaster iconography.

All painted at 6× supersample to a 64×48 landscape footprint,
smoothscale'd down. Saved as zoom + ingame composites + 5-cell
contact sheet.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_rail_icon_variants.py
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

from tools.render_lottery_scratch_variants import (
    _ss_paint, _font, _v_gradient_rect, _star_polygon, _sparkle,
)
from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "rail_icon_variants")
os.makedirs(_OUT, exist_ok=True)


# ── shared rail palette ─────────────────────────────────────────────────────
WOOD_DARK  = ( 78,  50,  26)
WOOD_MID   = (135,  88,  44)
WOOD_HI    = (185, 130,  70)
IRON       = ( 70,  70,  80)
IRON_HI    = (150, 155, 170)
RAIL_GOLD  = (255, 215,  90)
RAIL_DEEP  = (170, 120,  30)
TIE_BROWN  = (100,  70,  40)
CREAM      = (255, 250, 220)
EMBER      = (240, 150,  60)
RED        = (190,  60,  60)
RED_HI     = (235,  90,  90)
STROKE     = ( 20,  16,  14)
SKY_BLUE   = (140, 200, 235)
SHADOW     = (  0,   0,   0,  90)

NATIVE_W = 64
NATIVE_H = 48


# ── shared shape helpers ────────────────────────────────────────────────────

def _track(big, SS, y, x0, x1, n_ties=6, gold=RAIL_GOLD,
            edge=RAIL_DEEP, tie=TIE_BROWN):
    """Horizontal rail segment at vertical y, between x0 and x1.
    Renders 2 stacked gold rails (top + bottom of the track) with
    dark-gold edges plus n_ties cross-ties peeking out at the
    bottom edge."""
    # Cross-ties below the rails.
    tie_w = max(2 * SS, (x1 - x0) // (n_ties * 2))
    tie_h = int(2.5 * SS)
    for i in range(n_ties):
        tx = x0 + i * (x1 - x0) // (n_ties - 1) - tie_w // 2
        ty = y - tie_h // 2 + int(SS * 0.6)
        pygame.draw.rect(big, tie, (tx, ty, tie_w, tie_h),
                         border_radius=SS // 2)
    # Top + bottom rails — thin dark stroke + gold fill.
    for sign in (-1, 1):
        y_rail = y + sign * int(2 * SS)
        pygame.draw.line(big, edge, (x0, y_rail), (x1, y_rail),
                         max(1, int(SS * 1.4)))
        pygame.draw.line(big, gold, (x0, y_rail), (x1, y_rail),
                         max(1, int(SS * 0.8)))


def _coin(big, SS, cx, cy, r, with_dollar=False):
    """Small gold coin with chrome rim, optional centred '$' glyph."""
    pygame.draw.circle(big, (0, 0, 0, 70), (cx, cy + SS // 2 + 1),
                       r + SS // 2)
    for shrink, col in ((1.00, RAIL_DEEP),
                        (0.86, RAIL_GOLD),
                        (0.68, (255, 235, 140))):
        pygame.draw.circle(big, col, (cx, cy),
                           max(1, int(r * shrink)))
    pygame.draw.circle(big, STROKE, (cx, cy), r, max(1, SS // 2))
    if with_dollar:
        f = _font(int(r * 1.6))
        glyph = f.render("$", True, STROKE)
        hl    = f.render("$", True, CREAM)
        gr = glyph.get_rect(center=(cx, cy))
        big.blit(hl, hl.get_rect(center=(gr.centerx,
                                          gr.centery - SS // 2)))
        big.blit(glyph, gr)


def _cart_body(big, SS, rect, with_planks=True):
    """Side-view minecart body — plank fill, 2 iron hoops, dark
    stroke. `rect` is the cart-body rectangle (no wheels)."""
    # Drop shadow.
    sh = pygame.Surface((rect.width + 2 * SS, rect.height + 2 * SS),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, SHADOW, sh.get_rect(),
                     border_radius=int(SS * 0.7))
    big.blit(sh, sh.get_rect(center=(rect.centerx,
                                      rect.centery + SS + 1)))
    # Wood gradient body.
    _v_gradient_rect(big, rect, WOOD_HI, WOOD_DARK,
                     radius=int(SS * 0.7))
    # Vertical plank lines.
    if with_planks:
        plank_n = 4
        for i in range(1, plank_n):
            px = rect.left + i * rect.width // plank_n
            pygame.draw.line(big, WOOD_DARK,
                             (px, rect.top + SS),
                             (px, rect.bottom - SS),
                             max(1, SS // 2))
    # 2 iron hoops band.
    band_h = max(2, int(SS * 0.9))
    for band_y in (rect.top + int(rect.height * 0.22),
                   rect.bottom - int(rect.height * 0.22) - band_h):
        pygame.draw.rect(big, IRON,
                         (rect.left - SS, band_y,
                          rect.width + 2 * SS, band_h))
        pygame.draw.line(big, IRON_HI,
                         (rect.left - SS, band_y),
                         (rect.right + SS, band_y),
                         max(1, SS // 3))
    # Outline.
    pygame.draw.rect(big, STROKE, rect, max(1, int(SS * 0.5)),
                     border_radius=int(SS * 0.7))


def _spoked_wheel(big, SS, cx, cy, r, spokes=4):
    """Spoked wheel with iron rim, mid-wood hub."""
    pygame.draw.circle(big, (0, 0, 0, 70),
                       (cx, cy + SS // 2 + 1), r + SS // 2)
    pygame.draw.circle(big, IRON, (cx, cy), r)
    pygame.draw.circle(big, WOOD_MID, (cx, cy), max(1, r - SS))
    # Spokes.
    for i in range(spokes):
        ang = math.radians(i * (360 / spokes))
        x2 = cx + math.cos(ang) * (r - SS)
        y2 = cy + math.sin(ang) * (r - SS)
        pygame.draw.line(big, IRON, (cx, cy),
                         (int(x2), int(y2)),
                         max(1, int(SS * 0.6)))
    # Hub centre.
    pygame.draw.circle(big, IRON_HI, (cx, cy), max(1, int(SS * 0.8)))
    # Outline.
    pygame.draw.circle(big, STROKE, (cx, cy), r, max(1, SS // 2))


def _pip_head(big, SS, cx, cy, r):
    """Tiny dark-red Pip head poking out of a cart — beak + goggle
    dot. Anchored at the head's centre."""
    head_rect = pygame.Rect(0, 0, int(r * 2.2), int(r * 2))
    head_rect.center = (cx, cy)
    pygame.draw.ellipse(big, (180, 40, 50), head_rect)
    pygame.draw.ellipse(big, STROKE, head_rect, max(1, SS // 2))
    # Beak.
    pygame.draw.polygon(big, (235, 170, 40), [
        (cx + r, cy - SS // 2),
        (cx + r + int(SS * 1.5), cy),
        (cx + r, cy + SS),
    ])
    pygame.draw.polygon(big, STROKE, [
        (cx + r, cy - SS // 2),
        (cx + r + int(SS * 1.5), cy),
        (cx + r, cy + SS),
    ], max(1, SS // 3))
    # Goggle dot.
    pygame.draw.circle(big, STROKE,
                       (cx + r // 2, cy - r // 3),
                       max(1, int(SS * 0.8)))
    pygame.draw.circle(big, CREAM,
                       (cx + r // 2 - SS // 3, cy - r // 3 - SS // 3),
                       max(1, SS // 3))


# ── 5 candidate variants ────────────────────────────────────────────────────

def draw_r1_treasure_cart(surf, cx, cy, pulse):
    """R1 — Treasure minecart overflowing with gold coins, on rails."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        # Track at the bottom.
        track_y = int(h * 0.78)
        _track(big, SS, track_y, int(SS * 4), w - int(SS * 4),
                n_ties=6)
        # Cart body sits on top of the wheels.
        cart_w = int(SS * 36)
        cart_h = int(SS * 14)
        cart = pygame.Rect(0, 0, cart_w, cart_h)
        cart.midbottom = (w // 2, track_y - int(SS * 2.3))
        _cart_body(big, SS, cart)
        # Wheels.
        wheel_r = int(SS * 4.5)
        wheel_cy = cart.bottom + int(SS * 0.5)
        for sign in (-1, 1):
            wcx = cart.centerx + sign * (cart.width // 2 - int(SS * 5))
            _spoked_wheel(big, SS, wcx, wheel_cy, wheel_r)
        # Coin pile inside the cart (overflowing top).
        coin_specs = [
            (cart.centerx - int(SS * 9), cart.top + int(SS * 2),
             int(SS * 3.0), False),
            (cart.centerx - int(SS * 3), cart.top - int(SS * 0.5),
             int(SS * 3.4), True),
            (cart.centerx + int(SS * 4), cart.top + int(SS * 1.5),
             int(SS * 3.0), False),
            (cart.centerx + int(SS * 10), cart.top + int(SS * 3),
             int(SS * 2.6), False),
            (cart.centerx - int(SS * 1), cart.top - int(SS * 5),
             int(SS * 2.4), False),
        ]
        for ccx, ccy, r, with_dollar in coin_specs:
            _coin(big, SS, ccx, ccy, r, with_dollar=with_dollar)
        # 3 cream sparkles above the pile.
        _sparkle(big, cart.centerx - int(SS * 9), cart.top - int(SS * 7),
                 int(SS * 1.4))
        _sparkle(big, cart.centerx + int(SS * 7), cart.top - int(SS * 6),
                 int(SS * 1.6))
        _sparkle(big, cart.centerx + int(SS * 1), cart.top - int(SS * 10),
                 int(SS * 1.2))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_r2_loop(surf, cx, cy, pulse):
    """R2 — Roller-coaster loop with a cart at the apex."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        loop_cx = w // 2
        loop_cy = int(h * 0.62)
        loop_r  = int(min(w, h) * 0.36)
        # Draw the 3/4 loop arc — paint a thick dark ring then a
        # thinner gold ring on top.
        ring_outer = loop_r + int(SS * 2)
        ring_inner = loop_r - int(SS * 1)
        # Mask: large dark disc then carve out the inner area + the
        # lower-quarter opening.
        loop_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(loop_surf, RAIL_DEEP,
                           (loop_cx, loop_cy), ring_outer)
        pygame.draw.circle(loop_surf, (0, 0, 0, 0),
                           (loop_cx, loop_cy), ring_inner)
        # Carve the lower-quarter opening so the loop reads as a
        # 3/4 ring (open at the bottom).
        gap = pygame.Rect(0, 0, ring_outer * 2, ring_outer)
        gap.midtop = (loop_cx, loop_cy + int(loop_r * 0.55))
        pygame.draw.rect(loop_surf, (0, 0, 0, 0), gap)
        big.blit(loop_surf, (0, 0))
        # Gold rail on top — a thinner ring inside the dark band.
        gold_outer = loop_r + int(SS * 1)
        gold_inner = loop_r - int(SS * 0.2)
        loop_gold = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(loop_gold, RAIL_GOLD,
                           (loop_cx, loop_cy), gold_outer)
        pygame.draw.circle(loop_gold, (0, 0, 0, 0),
                           (loop_cx, loop_cy), gold_inner)
        pygame.draw.rect(loop_gold, (0, 0, 0, 0), gap)
        big.blit(loop_gold, (0, 0))
        # Cross-ties along the inner edge.
        for ang_deg in range(-60, 241, 30):
            ang = math.radians(ang_deg)
            x1 = loop_cx + math.cos(ang) * (loop_r - int(SS * 1.5))
            y1 = loop_cy + math.sin(ang) * (loop_r - int(SS * 1.5))
            x2 = loop_cx + math.cos(ang) * (loop_r + int(SS * 1.0))
            y2 = loop_cy + math.sin(ang) * (loop_r + int(SS * 1.0))
            pygame.draw.line(big, TIE_BROWN,
                             (x1, y1), (x2, y2),
                             max(1, int(SS * 0.7)))
        # Cart at the top of the loop — small red cart, oriented
        # upside-down so it reads as "looping the loop".
        cart_w = int(SS * 14)
        cart_h = int(SS * 7)
        cart = pygame.Rect(0, 0, cart_w, cart_h)
        cart.center = (loop_cx, loop_cy - loop_r + int(SS * 1))
        # Cart fill — red gradient.
        _v_gradient_rect(big, cart, RED_HI, RED,
                         radius=int(SS * 0.6))
        # Iron band along the bottom (which is now the top from the
        # car's perspective — visible against the rail).
        pygame.draw.rect(big, IRON,
                         (cart.left, cart.top,
                          cart.width, int(SS * 0.8)))
        pygame.draw.line(big, IRON_HI,
                         (cart.left, cart.top),
                         (cart.right, cart.top),
                         max(1, SS // 3))
        pygame.draw.rect(big, STROKE, cart,
                         max(1, int(SS * 0.5)),
                         border_radius=int(SS * 0.6))
        # Clamps gripping the rail.
        for cl_x in (cart.left + int(SS * 2),
                     cart.right - int(SS * 2)):
            pygame.draw.rect(big, IRON,
                             (cl_x - int(SS * 0.5),
                              cart.top - int(SS * 2),
                              int(SS * 1.2),
                              int(SS * 2.5)))
        # Trailing sparks behind the cart along the rail.
        for i, off_deg in enumerate((22, 38, 55)):
            ang = math.radians(-90 + off_deg)
            sx = loop_cx + math.cos(ang) * loop_r
            sy = loop_cy + math.sin(ang) * loop_r
            pygame.draw.circle(big, EMBER, (int(sx), int(sy)),
                                max(1, int(SS * (1.0 - i * 0.2))))
            pygame.draw.circle(big, CREAM, (int(sx), int(sy)),
                                max(1, int(SS * (0.5 - i * 0.1))))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 5
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_r3_speed_cart(surf, cx, cy, pulse):
    """R3 — Speed cart tilted forward with motion streaks + wheel sparks."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        track_y = int(h * 0.78)
        # Track segment — short, with bleed-edges.
        _track(big, SS, track_y, int(SS * 2), w - int(SS * 2),
                n_ties=5)
        # Motion streaks — 3 cyan tapered lines behind the cart.
        streak_origin_x = int(w * 0.20)
        for i, dy in enumerate((-int(SS * 5), 0, int(SS * 5))):
            for px, alpha, length in ((streak_origin_x, 60, int(w * 0.45)),
                                       (streak_origin_x + int(SS * 4),
                                        120, int(w * 0.35)),
                                       (streak_origin_x + int(SS * 8),
                                        180, int(w * 0.22))):
                streak = pygame.Surface(big.get_size(), pygame.SRCALPHA)
                pygame.draw.line(streak,
                                  (200, 235, 255, alpha),
                                  (px, int(h * 0.45) + dy),
                                  (px + length, int(h * 0.45) + dy),
                                  max(1, int(SS * 0.7)))
                big.blit(streak, (0, 0))
        # Cart body, tilted ~6° forward via blit-rotate.
        cart_w = int(SS * 32)
        cart_h = int(SS * 13)
        sub = pygame.Surface((cart_w + 4 * SS,
                               cart_h + 4 * SS),
                              pygame.SRCALPHA)
        sub_cart = pygame.Rect(0, 0, cart_w, cart_h)
        sub_cart.center = (sub.get_width() // 2,
                            sub.get_height() // 2)
        _cart_body(sub, SS, sub_cart)
        # Wheels on the sub-surface, anchored to the cart.
        wheel_r = int(SS * 4.0)
        wheel_y = sub_cart.bottom + int(SS * 0.5)
        for sign in (-1, 1):
            wcx = sub_cart.centerx + sign * (sub_cart.width // 2
                                              - int(SS * 4))
            _spoked_wheel(sub, SS, wcx, wheel_y, wheel_r)
        rotated_cart = pygame.transform.rotate(sub, -6)
        rc_rect = rotated_cart.get_rect(
            center=(int(w * 0.58), track_y - int(SS * 4)))
        big.blit(rotated_cart, rc_rect)
        # Wheel sparks at the rear wheel — short ember/cream lines.
        rear_wheel_x = int(w * 0.58) - cart_w // 2 + int(SS * 2)
        rear_wheel_y = track_y - int(SS * 0.5)
        for ang_deg in (-160, -140, -120, -100):
            ang = math.radians(ang_deg)
            length = int(SS * 3.0)
            x2 = rear_wheel_x + math.cos(ang) * length
            y2 = rear_wheel_y + math.sin(ang) * length
            pygame.draw.line(big, EMBER,
                             (rear_wheel_x, rear_wheel_y),
                             (int(x2), int(y2)),
                             max(1, int(SS * 0.6)))
            pygame.draw.circle(big, CREAM, (int(x2), int(y2)),
                                max(1, int(SS * 0.5)))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 3
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_r4_diagonal(surf, cx, cy, pulse):
    """R4 — Cart on a diagonally-descending track from upper-left
    to lower-right."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        # Faint mountain background — 2 alpha-low triangles.
        bg_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(bg_surf, (140, 165, 180, 60), [
            (int(w * 0.05), int(h * 0.60)),
            (int(w * 0.45), int(h * 0.10)),
            (int(w * 0.65), int(h * 0.60)),
        ])
        pygame.draw.polygon(bg_surf, (110, 140, 160, 70), [
            (int(w * 0.40), int(h * 0.60)),
            (int(w * 0.75), int(h * 0.18)),
            (int(w * 0.95), int(h * 0.60)),
        ])
        big.blit(bg_surf, (0, 0))

        # Diagonal track from upper-left to lower-right.
        x0 = int(SS * 4)
        y0 = int(h * 0.30)
        x1 = w - int(SS * 4)
        y1 = h - int(SS * 6)
        # Cross-ties along the diagonal — perpendicular short rungs.
        n_ties = 9
        dxn = (x1 - x0) / max(1, n_ties - 1)
        dyn = (y1 - y0) / max(1, n_ties - 1)
        # Perpendicular unit vector.
        L = math.hypot(x1 - x0, y1 - y0)
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        tie_half = int(SS * 2.5)
        for i in range(n_ties):
            tx = x0 + i * dxn
            ty = y0 + i * dyn
            pygame.draw.line(big, TIE_BROWN,
                             (int(tx + nx * tie_half),
                              int(ty + ny * tie_half)),
                             (int(tx - nx * tie_half),
                              int(ty - ny * tie_half)),
                             max(1, int(SS * 0.9)))
        # 2 parallel rails — offset by ±1.5 SS perpendicular.
        rail_off = int(SS * 1.8)
        for sign in (-1, 1):
            r_x0 = x0 + nx * rail_off * sign
            r_y0 = y0 + ny * rail_off * sign
            r_x1 = x1 + nx * rail_off * sign
            r_y1 = y1 + ny * rail_off * sign
            pygame.draw.line(big, RAIL_DEEP,
                             (int(r_x0), int(r_y0)),
                             (int(r_x1), int(r_y1)),
                             max(1, int(SS * 1.4)))
            pygame.draw.line(big, RAIL_GOLD,
                             (int(r_x0), int(r_y0)),
                             (int(r_x1), int(r_y1)),
                             max(1, int(SS * 0.7)))

        # Cart sitting mid-descent (~50% along the track).
        t = 0.50
        cart_x = int(x0 + (x1 - x0) * t)
        cart_y = int(y0 + (y1 - y0) * t)
        cart_w = int(SS * 26)
        cart_h = int(SS * 11)
        sub = pygame.Surface((cart_w + 6 * SS, cart_h + 6 * SS),
                              pygame.SRCALPHA)
        sub_cart = pygame.Rect(0, 0, cart_w, cart_h)
        sub_cart.center = (sub.get_width() // 2,
                            sub.get_height() // 2)
        _cart_body(sub, SS, sub_cart)
        wheel_r = int(SS * 3.5)
        wheel_y = sub_cart.bottom + int(SS * 0.5)
        for sign in (-1, 1):
            wcx = sub_cart.centerx + sign * (sub_cart.width // 2
                                              - int(SS * 3))
            _spoked_wheel(sub, SS, wcx, wheel_y, wheel_r)
        # Rotate the cart to match the track angle.
        track_ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        rotated_cart = pygame.transform.rotate(sub, -track_ang)
        # Anchor the cart above the track (offset along normal).
        anchor_x = cart_x + int(nx * SS * 4)
        anchor_y = cart_y + int(ny * SS * 4)
        big.blit(rotated_cart,
                 rotated_cart.get_rect(center=(anchor_x, anchor_y)))
        # Trailing sparks back along the track.
        for i in range(4):
            sd = -int(SS * (3 + i * 2))
            sx = anchor_x + math.cos(math.radians(track_ang)) * sd
            sy = anchor_y + math.sin(math.radians(track_ang)) * sd
            pygame.draw.circle(big, EMBER, (int(sx), int(sy)),
                               max(1, int(SS * (1.2 - i * 0.25))))
            pygame.draw.circle(big, CREAM, (int(sx), int(sy)),
                               max(1, int(SS * (0.6 - i * 0.12))))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 3
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_r5_pip_cart(surf, cx, cy, pulse):
    """R5 — Iron-banded minecart with Pip's head poking out the top
    and a small steam plume curling above."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        track_y = int(h * 0.80)
        _track(big, SS, track_y, int(SS * 4), w - int(SS * 4),
                n_ties=5)
        # Cart body — chunky.
        cart_w = int(SS * 36)
        cart_h = int(SS * 16)
        cart = pygame.Rect(0, 0, cart_w, cart_h)
        cart.midbottom = (w // 2, track_y - int(SS * 2.3))
        _cart_body(big, SS, cart, with_planks=True)
        # Wheels.
        wheel_r = int(SS * 4.5)
        wheel_y = cart.bottom + int(SS * 0.5)
        for sign in (-1, 1):
            wcx = cart.centerx + sign * (cart.width // 2
                                          - int(SS * 5))
            _spoked_wheel(big, SS, wcx, wheel_y, wheel_r)
        # Pip head poking out the top.
        pip_r = int(SS * 4.5)
        _pip_head(big, SS, cart.centerx - int(SS * 1),
                  cart.top - int(SS * 1), pip_r)
        # Steam plume above the back of the cart — 3 stacked grey
        # circles, fading upward.
        plume_x = cart.left + int(SS * 6)
        for i, (dx, dy, r, alpha) in enumerate((
            (0,           int(SS * -2), int(SS * 2.6), 220),
            (int(SS * -1), int(SS * -7), int(SS * 3.2), 170),
            (int(SS * -3), int(SS * -13), int(SS * 3.8), 110),
        )):
            puff = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
            pygame.draw.circle(puff, (245, 245, 245, alpha),
                                puff.get_rect().center, r)
            pygame.draw.circle(puff, (220, 220, 220,
                                       alpha * 3 // 4),
                                puff.get_rect().center, r,
                                max(1, SS // 3))
            big.blit(puff, puff.get_rect(
                center=(plume_x + dx, cart.top + dy)))
        # 1 corner sparkle upper-right.
        _sparkle(big, w - int(SS * 5), int(SS * 6), int(SS * 1.8),
                 colour=CREAM)

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


VARIANTS = [
    ("R1_treasure_cart", draw_r1_treasure_cart,
     "R1: minecart overflowing with gold coins on rails"),
    ("R2_loop",          draw_r2_loop,
     "R2: roller-coaster loop with red cart at the apex"),
    ("R3_speed_cart",    draw_r3_speed_cart,
     "R3: cart tilted forward with motion streaks + wheel sparks"),
    ("R4_diagonal",      draw_r4_diagonal,
     "R4: cart on a diagonally-descending track (Donkey-Kong)"),
    ("R5_pip_cart",      draw_r5_pip_cart,
     "R5: iron-banded cart with Pip + steam plume"),
]


# ── output ──────────────────────────────────────────────────────────────────

def _icon_zoom_png(draw_fn, label):
    base = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    draw_fn(base, NATIVE_W // 2, NATIVE_H // 2, pulse=1.6)
    big = pygame.transform.scale(base, (NATIVE_W * 6, NATIVE_H * 6))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 2)
    return big


def _ingame_png(draw_fn, label):
    world = build_world()
    frame = render_play_scene(world)
    icon_cx = int(world.bird.x) + 110
    icon_cy = int(world.bird.y)
    base = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    draw_fn(base, NATIVE_W // 2, NATIVE_H // 2, pulse=1.6)
    frame.blit(base, base.get_rect(center=(icon_cx, icon_cy)))
    return frame


def main():
    saved = []
    for label, fn, caption in VARIANTS:
        icon_zoom = _icon_zoom_png(fn, label)
        ingame    = _ingame_png(fn, label)
        zoom_path   = os.path.join(_OUT, f"{label}.png")
        ingame_path = os.path.join(_OUT, f"{label}_ingame.png")
        pygame.image.save(icon_zoom, zoom_path)
        pygame.image.save(ingame, ingame_path)
        saved.append((label, caption, icon_zoom))
        print(f"saved {zoom_path}")
        print(f"saved {ingame_path}")

    cell_w = saved[0][2].get_width()
    cell_h = saved[0][2].get_height()
    band_h = 56
    gap    = 12
    sheet_w = len(saved) * cell_w + (len(saved) - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, icon) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        sheet.blit(icon, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/rail_icon_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
