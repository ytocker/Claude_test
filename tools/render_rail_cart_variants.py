"""Render 5 RAIL pickup-icon design candidates — cart-only family.

User picked R1's cart silhouette but wants the coins AND the
track removed. These 5 variants all show the empty minecart
floating on its wheels alone; each varies the cart shape OR
adds a single distinguishing prop (lantern / Pip / steam) so
the user can pick the silhouette they like best.

Painted at 6× supersample to a 64×48 footprint, smoothscale'd
down.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_rail_cart_variants.py
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
    _ss_paint, _v_gradient_rect, _sparkle,
)
from tools.render_rail_icon_variants import (
    _cart_body, _spoked_wheel, _pip_head,
    WOOD_DARK, WOOD_MID, WOOD_HI, IRON, IRON_HI,
    STROKE, SHADOW,
    NATIVE_W, NATIVE_H,
)
from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "rail_cart_variants")
os.makedirs(_OUT, exist_ok=True)


LANTERN_GLOW = (255, 215, 110)
LANTERN_HOT  = (255, 245, 200)


# ── extra helpers (cart shape variants) ─────────────────────────────────────

def _hopper_cart_body(big, SS, rect):
    """V-shaped coal-hopper cart — same plank+iron vocabulary as
    _cart_body but with trapezoidal sides (narrower bottom)."""
    inset = int(rect.width * 0.13)
    pts = [
        (rect.left + inset, rect.bottom),
        (rect.left,         rect.top),
        (rect.right,        rect.top),
        (rect.right - inset, rect.bottom),
    ]
    # Drop shadow.
    sh = pygame.Surface((rect.width + 4 * SS, rect.height + 4 * SS),
                        pygame.SRCALPHA)
    sh_pts = [(p[0] - rect.left + 2 * SS, p[1] - rect.top + 2 * SS)
              for p in pts]
    pygame.draw.polygon(sh, SHADOW, sh_pts)
    big.blit(sh, (rect.left - 2 * SS, rect.top - 2 * SS + SS + 1))
    # Wood fill (vertical gradient approximated by 2-pass fill).
    pygame.draw.polygon(big, WOOD_MID, pts)
    # Upper highlight band — narrower polygon on top.
    hi_pts = [
        (rect.left + int(inset * 0.3), rect.top + int(rect.height * 0.35)),
        (rect.left,                     rect.top),
        (rect.right,                    rect.top),
        (rect.right - int(inset * 0.3), rect.top + int(rect.height * 0.35)),
    ]
    pygame.draw.polygon(big, WOOD_HI, hi_pts)
    # Plank lines.
    for i in (1, 2, 3):
        t = i / 4
        top_x = rect.left + t * rect.width
        bot_x = rect.left + inset + t * (rect.width - 2 * inset)
        pygame.draw.line(big, WOOD_DARK,
                         (top_x, rect.top + SS),
                         (bot_x, rect.bottom - SS),
                         max(1, SS // 2))
    # Iron rim along the top edge.
    pygame.draw.rect(big, IRON,
                     (rect.left - SS, rect.top,
                      rect.width + 2 * SS, max(2, int(SS * 1.1))))
    pygame.draw.line(big, IRON_HI,
                     (rect.left - SS, rect.top),
                     (rect.right + SS, rect.top),
                     max(1, SS // 3))
    # Iron band 60% down (follows the trapezoid).
    bt = 0.62
    bx0 = rect.left + bt * inset
    bx1 = rect.right - bt * inset
    by  = rect.top + bt * rect.height
    pygame.draw.line(big, IRON, (bx0 - SS, by), (bx1 + SS, by),
                     max(2, int(SS * 0.9)))
    pygame.draw.line(big, IRON_HI, (bx0 - SS, by), (bx1 + SS, by),
                     max(1, SS // 3))
    # Dark stroke outline.
    pygame.draw.polygon(big, STROKE, pts, max(1, int(SS * 0.55)))


def _lantern(big, SS, hook_top, hook_bot):
    """Mining lantern hanging from a chain. hook_top and hook_bot
    are the chain anchor and lantern-top points."""
    # Chain — short black line.
    pygame.draw.line(big, STROKE, hook_top, hook_bot,
                     max(1, int(SS * 0.5)))
    # Lantern body — rounded warm rectangle.
    lx, ly = hook_bot
    lw, lh = int(SS * 4), int(SS * 4.5)
    body = pygame.Rect(0, 0, lw, lh)
    body.midtop = (lx, ly)
    # Glow halo behind the lantern.
    glow_r = int(SS * 5)
    glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
    for r, a in ((glow_r,     50),
                 (int(glow_r * 0.7), 90),
                 (int(glow_r * 0.45), 140)):
        pygame.draw.circle(glow, (*LANTERN_GLOW, a),
                           glow.get_rect().center, r)
    big.blit(glow, glow.get_rect(center=body.center))
    # Body.
    _v_gradient_rect(big, body, LANTERN_HOT, LANTERN_GLOW,
                     radius=int(SS * 0.8))
    pygame.draw.rect(big, STROKE, body, max(1, int(SS * 0.4)),
                     border_radius=int(SS * 0.8))
    # Iron cap on top.
    cap = pygame.Rect(0, 0, lw + int(SS * 0.6), int(SS * 0.8))
    cap.midbottom = (body.centerx, body.top + int(SS * 0.5))
    pygame.draw.rect(big, IRON, cap, border_radius=SS // 3)
    pygame.draw.line(big, IRON_HI, (cap.left, cap.top),
                     (cap.right, cap.top), max(1, SS // 3))
    # Bottom iron ring.
    bot_ring = pygame.Rect(0, 0, lw + int(SS * 0.6), int(SS * 0.7))
    bot_ring.midtop = (body.centerx, body.bottom - int(SS * 0.4))
    pygame.draw.rect(big, IRON, bot_ring, border_radius=SS // 3)
    # Vertical iron bars suggesting the lantern's frame.
    for tx_frac in (0.25, 0.50, 0.75):
        bx = body.left + body.width * tx_frac
        pygame.draw.line(big, STROKE,
                         (bx, body.top + int(SS * 0.6)),
                         (bx, body.bottom - int(SS * 0.6)),
                         max(1, SS // 4))


def _steam_plume(big, SS, cx, cy):
    """Steam plume curling upward — 3 alpha-stacked grey circles."""
    for dx, dy, r, alpha in (
        (0,             int(SS * -2), int(SS * 2.4), 220),
        (int(SS * -1),  int(SS * -7), int(SS * 3.0), 170),
        (int(SS * -3),  int(SS * -13), int(SS * 3.6), 110),
    ):
        puff = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
        pygame.draw.circle(puff, (245, 245, 245, alpha),
                           puff.get_rect().center, r)
        pygame.draw.circle(puff, (220, 220, 220, alpha * 3 // 4),
                           puff.get_rect().center, r,
                           max(1, SS // 3))
        big.blit(puff, puff.get_rect(center=(cx + dx, cy + dy)))


def _smokestack(big, SS, base_cx, base_cy):
    """Small iron smokestack at the back of the cart."""
    stack_w = int(SS * 2.0)
    stack_h = int(SS * 4.0)
    stack = pygame.Rect(0, 0, stack_w, stack_h)
    stack.midbottom = (base_cx, base_cy)
    pygame.draw.rect(big, IRON, stack, border_radius=SS // 3)
    pygame.draw.rect(big, STROKE, stack, max(1, SS // 3),
                     border_radius=SS // 3)
    # Top flare.
    flare = pygame.Rect(0, 0, int(stack_w * 1.6), int(SS * 0.8))
    flare.midbottom = (base_cx, stack.top + SS // 3)
    pygame.draw.rect(big, IRON, flare, border_radius=SS // 4)
    pygame.draw.rect(big, STROKE, flare, max(1, SS // 4),
                     border_radius=SS // 4)


# ── 5 cart-only variants ────────────────────────────────────────────────────

def _draw_wheels(big, SS, cart):
    """Common: 2 spoked wheels protruding from beneath a cart rect.
    No rail track — the cart is shown free-standing per user
    request."""
    wheel_r = int(SS * 4.5)
    wheel_cy = cart.bottom + int(SS * 0.5)
    for sign in (-1, 1):
        wcx = cart.centerx + sign * (cart.width // 2 - int(SS * 5))
        _spoked_wheel(big, SS, wcx, wheel_cy, wheel_r)


def draw_c1_plain(surf, cx, cy, pulse):
    """C1 — Plain wooden minecart on rails. No coins, no extras."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        cart_w = int(SS * 36)
        cart_h = int(SS * 16)
        cart = pygame.Rect(0, 0, cart_w, cart_h)
        cart.center = (w // 2, h // 2 + int(SS * 1))
        _cart_body(big, SS, cart)
        _draw_wheels(big, SS, cart)

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_c2_hopper(surf, cx, cy, pulse):
    """C2 — V-shaped coal-hopper cart on rails (different silhouette)."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        cart_w = int(SS * 38)
        cart_h = int(SS * 17)
        cart = pygame.Rect(0, 0, cart_w, cart_h)
        cart.center = (w // 2, h // 2 + int(SS * 1))
        _hopper_cart_body(big, SS, cart)
        _draw_wheels(big, SS, cart)

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_c3_lantern(surf, cx, cy, pulse):
    """C3 — Wooden minecart with a mining lantern hanging from a
    hook off the front edge."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        cart_w = int(SS * 34)
        cart_h = int(SS * 15)
        cart = pygame.Rect(0, 0, cart_w, cart_h)
        cart.center = (w // 2 + int(SS * 1), h // 2 + int(SS * 2))
        _cart_body(big, SS, cart)
        # Hook + lantern on the front-right corner.
        hook_top = (cart.right + int(SS * 1.2), cart.top + int(SS * 1))
        hook_bot = (cart.right + int(SS * 1.2), cart.top - int(SS * 2))
        # Iron hook arm reaching forward from the rim.
        pygame.draw.line(big, IRON,
                         (cart.right, cart.top + int(SS * 1.5)),
                         (hook_top[0], hook_top[1]),
                         max(1, int(SS * 0.7)))
        pygame.draw.line(big, IRON_HI,
                         (cart.right, cart.top + int(SS * 1.5)),
                         (hook_top[0], hook_top[1]),
                         max(1, SS // 3))
        # Lantern.
        _lantern(big, SS, hook_top, hook_bot)
        _draw_wheels(big, SS, cart)

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_c4_pip(surf, cx, cy, pulse):
    """C4 — Wooden minecart with Pip's head poking out the top
    (gameplay preview)."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        cart_w = int(SS * 36)
        cart_h = int(SS * 16)
        cart = pygame.Rect(0, 0, cart_w, cart_h)
        cart.center = (w // 2, h // 2 + int(SS * 3))
        _cart_body(big, SS, cart)
        # Pip head poking out — anchored slightly above the cart's
        # top edge.
        pip_r = int(SS * 4.5)
        _pip_head(big, SS, cart.centerx - int(SS * 1),
                  cart.top - int(SS * 1), pip_r)
        _draw_wheels(big, SS, cart)

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_c5_steam(surf, cx, cy, pulse):
    """C5 — Wooden minecart with a small iron smokestack at the
    back and a steam plume curling above (vintage-engine cart)."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        cart_w = int(SS * 36)
        cart_h = int(SS * 16)
        cart = pygame.Rect(0, 0, cart_w, cart_h)
        cart.center = (w // 2, h // 2 + int(SS * 3))
        _cart_body(big, SS, cart)
        # Smokestack at the back (left) of the cart.
        stack_cx = cart.left + int(SS * 5)
        _smokestack(big, SS, stack_cx, cart.top)
        # Steam plume above the smokestack.
        _steam_plume(big, SS, stack_cx, cart.top - int(SS * 5))
        _draw_wheels(big, SS, cart)

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


VARIANTS = [
    ("C1_plain",   draw_c1_plain,
     "C1: plain wooden minecart (no track)"),
    ("C2_hopper",  draw_c2_hopper,
     "C2: V-shaped coal-hopper cart"),
    ("C3_lantern", draw_c3_lantern,
     "C3: cart with mining lantern hanging off the front"),
    ("C4_pip",     draw_c4_pip,
     "C4: cart with Pip head poking out the top"),
    ("C5_steam",   draw_c5_steam,
     "C5: cart with smokestack + steam plume"),
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
            "v5_powerups/docs/screenshots/rail_cart_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
