"""Render 5 RAIL pickup-icon design candidates — train-ticket
family. Each ticket shows a small cart silhouette so the
pickup is unmistakably "RAIL", but the dominant shape is the
ticket itself. Five distinct ticket archetypes (Edmondson,
boarding pass, carnival, metro, gold express) drawn from
real-world train-ticket imagery.

All painted at 6× supersample to a 64×48 footprint,
smoothscale'd down.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_rail_ticket_variants.py
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
from tools.render_rail_icon_variants import (
    _spoked_wheel,
    WOOD_DARK, WOOD_MID, WOOD_HI, IRON, IRON_HI,
    NATIVE_W, NATIVE_H,
)
from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "rail_ticket_variants")
os.makedirs(_OUT, exist_ok=True)


# ── ticket palette extensions ───────────────────────────────────────────────
CREAM_PAPER  = (245, 235, 195)
CREAM_PAPER2 = (220, 205, 160)
MAROON       = (120,  40,  40)
MAROON_DK    = ( 80,  20,  30)
TEAL_HI      = ( 60, 130, 145)
TEAL_LO      = ( 40,  90, 110)
TEAL_DK      = ( 25,  60,  80)
RIDE_RED_HI  = (210,  65,  75)
RIDE_RED     = (180,  40,  50)
METRO_HI     = (220, 220, 225)
METRO_LO     = (170, 175, 185)
METRO_NAVY   = ( 40,  65, 105)
NAVY_HI      = ( 25,  30,  60)
NAVY_LO      = ( 15,  18,  40)
GOLD         = (220, 170,  50)
GOLD_HI      = (255, 220, 110)
GOLD_DK      = (140,  95,  25)
CREAM        = (255, 250, 220)
WHITE        = (255, 255, 255)
NEAR_BLACK   = ( 12,  12,  16)
CHROME_LO    = (190, 190, 200)


# ── shared mini cart silhouette ─────────────────────────────────────────────

def _mini_cart(big, SS, cx, cy_top, w, wood_top=WOOD_HI,
                wood_bot=WOOD_DARK, iron=IRON, iron_hi=IRON_HI,
                outline=NEAR_BLACK, with_wheels=True,
                wheel_scale=1.0):
    """Small C1-style cart silhouette anchored at top-centre.
    Designed to fit inside a ticket without dominating; controls
    are scale-tied to `w` (cart width in paint pixels)."""
    h = int(w * 0.45)
    cart = pygame.Rect(0, 0, w, h)
    cart.midtop = (cx, cy_top)
    _v_gradient_rect(big, cart, wood_top, wood_bot,
                     radius=max(1, int(SS * 0.35)))
    # 3 plank seams.
    for i in range(1, 4):
        px = cart.left + i * w // 4
        pygame.draw.line(big, wood_bot,
                         (px, cart.top + SS // 2),
                         (px, cart.bottom - SS // 2),
                         max(1, SS // 3))
    # 2 iron hoops.
    band_h = max(1, int(SS * 0.5))
    for band_y in (cart.top + int(cart.height * 0.22),
                   cart.bottom
                   - int(cart.height * 0.22) - band_h):
        pygame.draw.rect(big, iron,
                         (cart.left - SS // 2, band_y,
                          cart.width + SS, band_h))
        pygame.draw.line(big, iron_hi,
                         (cart.left - SS // 2, band_y),
                         (cart.right + SS // 2, band_y),
                         max(1, SS // 4))
    pygame.draw.rect(big, outline, cart, max(1, SS // 3),
                     border_radius=max(1, int(SS * 0.35)))
    # Wheels.
    if with_wheels:
        wheel_r = max(1, int(SS * 1.8 * wheel_scale))
        wheel_cy = cart.bottom + max(1, SS // 3)
        for sign in (-1, 1):
            wcx = cart.centerx + sign * (cart.width // 2
                                          - int(SS * 1.5))
            # Smaller wheel: skip spokes if r < 2 SS.
            if wheel_r < 2 * SS:
                pygame.draw.circle(big, (0, 0, 0, 60),
                                   (wcx, wheel_cy + 1),
                                   wheel_r + 1)
                pygame.draw.circle(big, iron, (wcx, wheel_cy),
                                   wheel_r)
                pygame.draw.circle(big, wood_bot, (wcx, wheel_cy),
                                   max(1, wheel_r - SS // 2))
                pygame.draw.circle(big, iron_hi, (wcx, wheel_cy),
                                   max(1, SS // 2))
                pygame.draw.circle(big, outline, (wcx, wheel_cy),
                                   wheel_r, max(1, SS // 3))
            else:
                _spoked_wheel(big, SS, wcx, wheel_cy, wheel_r,
                              spokes=4)


def _two_pass_text(big, font, text, centre, fill_col, sh_col, SS):
    """Render text with a dark shadow under a bright fill for
    crisp edges through smoothscale-down."""
    sh = font.render(text, True, sh_col)
    fl = font.render(text, True, fill_col)
    big.blit(sh, sh.get_rect(center=(centre[0] + SS // 2,
                                       centre[1] + SS // 2)))
    big.blit(fl, fl.get_rect(center=centre))


# ── 5 ticket variants ───────────────────────────────────────────────────────

def draw_t1_edmondson(surf, cx, cy, pulse):
    """T1 — Vintage Edmondson cardstock ticket."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        # Cream paper body.
        _v_gradient_rect(big, card, CREAM_PAPER, CREAM_PAPER2,
                         radius=int(SS * 0.8))
        # Outer maroon stroke + inner cream highlight (1 SS each).
        pygame.draw.rect(big, MAROON_DK, card,
                         max(1, int(SS * 0.6)),
                         border_radius=int(SS * 0.8))
        pygame.draw.rect(big, (255, 250, 230),
                         card.inflate(-2 * SS, -2 * SS),
                         max(1, SS // 3),
                         border_radius=int(SS * 0.5))
        # Engraving border (decorative): a dashed maroon rect
        # between the strokes.
        eng = card.inflate(-int(3.5 * SS), -int(3.5 * SS))
        pygame.draw.rect(big, MAROON, eng, max(1, SS // 3),
                         border_radius=int(SS * 0.4))
        # Header maroon strip.
        header = pygame.Rect(eng.left + SS, eng.top + SS,
                             eng.width - 2 * SS, int(5 * SS))
        pygame.draw.rect(big, MAROON, header,
                         border_radius=int(SS * 0.4))
        f_hdr = _font(int(header.height * 0.80))
        _two_pass_text(big, f_hdr, "RAIL PASS",
                        header.center, CREAM, MAROON_DK, SS)
        # Conductor's hole-punch dot in the upper-left corner of
        # the engraving area.
        pygame.draw.circle(big, NEAR_BLACK,
                            (card.left + int(SS * 4),
                             card.top + int(SS * 11)),
                            int(SS * 1.0))
        # Mini cart centred on the cream body, with 2 thin maroon
        # rails painted under it.
        cart_top_y = header.bottom + int(SS * 4)
        rail_y = cart_top_y + int(SS * 7.5)
        for dy in (-int(SS * 0.6), int(SS * 0.6)):
            pygame.draw.line(big, MAROON,
                             (eng.left + SS, rail_y + dy),
                             (eng.right - SS, rail_y + dy),
                             max(1, SS // 3))
        _mini_cart(big, SS, card.centerx + SS * 2, cart_top_y,
                   int(SS * 16))
        # Footer caption "★ ADMIT ONE ★".
        f_ft = _font(int(SS * 2.6))
        ft_y = eng.bottom - int(SS * 2.5)
        _two_pass_text(big, f_ft, "* ADMIT ONE *",
                        (card.centerx, ft_y),
                        MAROON, MAROON_DK, SS)

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_t2_boarding_pass(surf, cx, cy, pulse):
    """T2 — Modern boarding pass with tear-off stub."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        # 70/30 split.
        split_x = card.left + int(card.width * 0.66)
        main = pygame.Rect(card.left, card.top,
                            split_x - card.left, card.height)
        stub = pygame.Rect(split_x, card.top,
                            card.right - split_x, card.height)
        _v_gradient_rect(big, main, TEAL_HI, TEAL_LO,
                         radius=int(SS * 0.8))
        _v_gradient_rect(big, stub, TEAL_LO, TEAL_DK,
                         radius=int(SS * 0.8))
        # Re-paint corner overlaps so the radii line up between
        # the two cells.
        overlap = pygame.Rect(split_x - SS, card.top,
                               2 * SS, card.height)
        pygame.draw.rect(big, TEAL_LO, overlap)
        # Dashed cream perforation line between cells.
        dash_y = card.top + SS
        while dash_y < card.bottom - SS:
            pygame.draw.line(big, CREAM,
                             (split_x, dash_y),
                             (split_x, dash_y + 2 * SS),
                             max(1, SS // 3))
            dash_y += 4 * SS
        # 2 small semicircular notches on the top edge of the main
        # cell (where boarding passes get punched / clipped).
        for nx_frac in (0.30, 0.60):
            nx = main.left + int(main.width * nx_frac)
            pygame.draw.circle(big, (0, 0, 0, 0),
                                (nx, main.top - SS // 2),
                                int(SS * 1.2))
        # Chrome perimeter.
        pygame.draw.rect(big, CREAM, card, max(1, SS // 3),
                         border_radius=int(SS * 0.8))
        pygame.draw.rect(big, NEAR_BLACK, card, max(1, SS // 4),
                         border_radius=int(SS * 0.8))
        # Main caption.
        f_main = _font(int(SS * 6))
        _two_pass_text(big, f_main, "RAIL",
                        (main.centerx,
                         main.top + int(SS * 8)),
                        CREAM, NEAR_BLACK, SS)
        f_sub = _font(int(SS * 2.4))
        _two_pass_text(big, f_sub, "BOARDING",
                        (main.centerx,
                         main.top + int(SS * 14)),
                        CREAM, NEAR_BLACK, SS)
        # Stub: mini cart + star.
        _mini_cart(big, SS, stub.centerx,
                   stub.top + int(SS * 8),
                   int(SS * 11),
                   wood_top=GOLD_HI, wood_bot=GOLD_DK,
                   iron=IRON, iron_hi=IRON_HI,
                   outline=NEAR_BLACK)
        _sparkle(big, stub.centerx, stub.bottom - int(SS * 4),
                 int(SS * 1.8), colour=CREAM)
        # Corner sparkle upper-right.
        _sparkle(big, card.right - int(SS * 4),
                 card.top + int(SS * 4),
                 int(SS * 1.6), colour=CREAM)

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_t3_ride_pass(surf, cx, cy, pulse):
    """T3 — Carnival ride pass with serrated edges."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _v_gradient_rect(big, card, RIDE_RED_HI, RIDE_RED,
                         radius=int(SS * 0.8))
        # Serrated edges — 6 triangle notches along top and
        # bottom edges (paint background-coloured triangles
        # poking inward).
        notches = 7
        notch_w = card.width // notches
        notch_h = int(SS * 1.4)
        for i in range(notches):
            cxn = card.left + i * notch_w + notch_w // 2
            # Top.
            pygame.draw.polygon(big, (0, 0, 0, 0), [
                (cxn - notch_w // 3, card.top),
                (cxn + notch_w // 3, card.top),
                (cxn,                 card.top + notch_h),
            ])
            # Bottom.
            pygame.draw.polygon(big, (0, 0, 0, 0), [
                (cxn - notch_w // 3, card.bottom),
                (cxn + notch_w // 3, card.bottom),
                (cxn,                 card.bottom - notch_h),
            ])
        # Outer cream stroke + inner dark maroon stroke.
        pygame.draw.rect(big, CREAM, card,
                         max(1, int(SS * 0.55)),
                         border_radius=int(SS * 0.8))
        pygame.draw.rect(big, MAROON_DK,
                         card.inflate(-2 * SS, -2 * SS),
                         max(1, SS // 3),
                         border_radius=int(SS * 0.5))
        # Header caption.
        f_hdr = _font(int(SS * 4.6))
        _two_pass_text(big, f_hdr, "RIDE PASS",
                        (card.centerx,
                         card.top + int(SS * 7.5)),
                        CREAM, MAROON_DK, SS)
        # Mini cart flanked by 2 cream ★.
        cart_y = card.top + int(SS * 13)
        _mini_cart(big, SS, card.centerx, cart_y,
                   int(SS * 14),
                   wood_top=CREAM_PAPER, wood_bot=GOLD_DK,
                   iron=NEAR_BLACK, iron_hi=CREAM,
                   outline=NEAR_BLACK)
        # ★ flanking the cart.
        _sparkle(big, card.left + int(SS * 4),
                 cart_y + int(SS * 4), int(SS * 2.0),
                 colour=CREAM)
        _sparkle(big, card.right - int(SS * 4),
                 cart_y + int(SS * 4), int(SS * 2.0),
                 colour=CREAM)
        # Footer caption.
        f_ft = _font(int(SS * 2.5))
        _two_pass_text(big, f_ft, "* ALL ABOARD *",
                        (card.centerx, card.bottom - int(SS * 3.5)),
                        CREAM, MAROON_DK, SS)

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_t4_metro_card(surf, cx, cy, pulse):
    """T4 — Subway metro card with magnetic stripe + accent band."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _v_gradient_rect(big, card, METRO_HI, METRO_LO,
                         radius=int(SS * 0.8))
        # Top accent navy band.
        band = pygame.Rect(card.left + SS, card.top + SS,
                            card.width - 2 * SS, int(SS * 6.5))
        pygame.draw.rect(big, METRO_NAVY, band,
                         border_radius=int(SS * 0.4))
        pygame.draw.line(big, CREAM,
                         (band.left, band.top),
                         (band.right, band.top),
                         max(1, SS // 3))
        f_hdr = _font(int(SS * 3.6))
        _two_pass_text(big, f_hdr, "METRO RAIL",
                        band.center, CREAM, NEAR_BLACK, SS)
        # Mini cart on grey body.
        cart_y = band.bottom + int(SS * 3)
        _mini_cart(big, SS, card.centerx - int(SS * 3), cart_y,
                   int(SS * 14))
        # Route badge — small navy circle with cream "R1" lower-
        # right.
        badge_cx = card.right - int(SS * 5)
        badge_cy = card.bottom - int(SS * 7)
        badge_r = int(SS * 3.4)
        pygame.draw.circle(big, METRO_NAVY,
                           (badge_cx, badge_cy), badge_r)
        pygame.draw.circle(big, CREAM,
                           (badge_cx, badge_cy), badge_r,
                           max(1, SS // 3))
        f_badge = _font(int(SS * 2.6))
        _two_pass_text(big, f_badge, "R1",
                        (badge_cx, badge_cy),
                        CREAM, NEAR_BLACK, SS)
        # Magnetic stripe along the bottom — thin black band with
        # chrome highlight.
        mag = pygame.Rect(card.left + SS, card.bottom - int(SS * 3),
                           card.width - 2 * SS, int(SS * 1.8))
        pygame.draw.rect(big, NEAR_BLACK, mag,
                         border_radius=SS // 3)
        pygame.draw.line(big, CHROME_LO,
                         (mag.left, mag.top),
                         (mag.right, mag.top),
                         max(1, SS // 3))
        # Outer perimeter strokes.
        pygame.draw.rect(big, (130, 135, 145), card,
                         max(1, SS // 3),
                         border_radius=int(SS * 0.8))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


def draw_t5_gold_express(surf, cx, cy, pulse):
    """T5 — Gold first-class express ticket."""

    def paint(big, SS):
        w, h = big.get_width(), big.get_height()
        card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
        _v_gradient_rect(big, card, NAVY_HI, NAVY_LO,
                         radius=int(SS * 0.8))
        # Double border: outer gold + inner dark gold.
        pygame.draw.rect(big, GOLD, card,
                         max(2, int(SS * 0.8)),
                         border_radius=int(SS * 0.8))
        pygame.draw.rect(big, GOLD_DK,
                         card.inflate(-int(2.5 * SS),
                                       -int(2.5 * SS)),
                         max(1, SS // 3),
                         border_radius=int(SS * 0.5))
        # Ornate filigree dots in each corner (3-dot triangle pip).
        for corner_x, corner_y, dx_sgn, dy_sgn in (
            (card.left  + int(SS * 4), card.top    + int(SS * 4),  1,  1),
            (card.right - int(SS * 4), card.top    + int(SS * 4), -1,  1),
            (card.left  + int(SS * 4), card.bottom - int(SS * 4),  1, -1),
            (card.right - int(SS * 4), card.bottom - int(SS * 4), -1, -1),
        ):
            for dx, dy in ((0, 0), (int(SS * 1.6) * dx_sgn, 0),
                           (0, int(SS * 1.6) * dy_sgn)):
                pygame.draw.circle(big, GOLD_HI,
                                   (corner_x + dx, corner_y + dy),
                                   max(1, SS // 2))
        # Header "EXPRESS" engraved.
        f_hdr = _font(int(SS * 4.5))
        hdr_centre = (card.centerx, card.top + int(SS * 9))
        # Dark shadow below.
        sh = f_hdr.render("EXPRESS", True, GOLD_DK)
        big.blit(sh, sh.get_rect(
            center=(hdr_centre[0] + SS // 2,
                     hdr_centre[1] + SS // 2)))
        # Gold fill.
        fl = f_hdr.render("EXPRESS", True, GOLD)
        big.blit(fl, fl.get_rect(center=hdr_centre))
        # Cream highlight above.
        hl = f_hdr.render("EXPRESS", True, CREAM)
        big.blit(hl, hl.get_rect(
            center=(hdr_centre[0],
                     hdr_centre[1] - SS // 2)))
        # Mini gold-tinted cart centred below the header.
        cart_y = card.top + int(SS * 16)
        _mini_cart(big, SS, card.centerx, cart_y,
                   int(SS * 14),
                   wood_top=GOLD_HI, wood_bot=GOLD_DK,
                   iron=IRON, iron_hi=GOLD,
                   outline=NEAR_BLACK)
        # Faint gold rail underline beneath the cart.
        rail_y = cart_y + int(SS * 9)
        pygame.draw.line(big, GOLD,
                         (card.left + int(SS * 6), rail_y),
                         (card.right - int(SS * 6), rail_y),
                         max(1, SS // 3))
        # Footer caption.
        f_ft = _font(int(SS * 2.4))
        _two_pass_text(big, f_ft, "* FIRST CLASS *",
                        (card.centerx, card.bottom - int(SS * 3)),
                        GOLD, GOLD_DK, SS)

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    tilt = math.sin(pulse * 0.7) * 4
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


VARIANTS = [
    ("T1_edmondson",     draw_t1_edmondson,
     "T1: vintage Edmondson cardstock with RAIL PASS header"),
    ("T2_boarding_pass", draw_t2_boarding_pass,
     "T2: modern boarding pass with perforated tear-off stub"),
    ("T3_ride_pass",     draw_t3_ride_pass,
     "T3: carnival ride pass with serrated edges + stars"),
    ("T4_metro_card",    draw_t4_metro_card,
     "T4: subway metro card with magnetic stripe + R1 badge"),
    ("T5_gold_express",  draw_t5_gold_express,
     "T5: gold first-class express with ornate corners"),
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
            "v5_powerups/docs/screenshots/rail_ticket_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
