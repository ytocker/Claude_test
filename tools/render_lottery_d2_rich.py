"""Render the LOTTERY scratch-card icon — D2 polished and richer.

User picked D2 (LUCKY arched red banner) as the direction. This
version (v3):

  * native footprint 64×48 — slightly smaller than v2's 76×56
    (closer to the original 40×30 live icon) but still ~38%
    bigger than v1 so the text reads sharply
  * black outer perimeter is 1 SS thin (kept from v2)
  * banner height 9 SS (kept from v2) — "LUCKY" reads crisply
  * "WIN!" stamp height 6 SS (kept from v2)
  * tilt animation restored to the original ±8° amplitude
    (was ±5° in v1/v2)
  * vertical bob from the original live icon is preserved by
    the final integration — see the comment in draw_d2_rich

Still keeps every richness element from v1:
  * 2 cream sparkle stars flanking "LUCKY" on the banner
  * 4 thin gold sun-rays radiating downward beneath the banner
  * small red "WIN!" mini-stamp at the bottom-centre
  * 5 confetti dots scattered around the card
  * clover stamp lower-left, gold "$" coin lower-right
  * 3 corner sparkle stars

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_lottery_d2_rich.py
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
    _dashed_rect, _silver_panel,
    GOLD_HI, GOLD_LO, GOLD_DEEP, STROKE,
    CHROME, SILVER_HI, SILVER_LO,
    CREAM, NAVY, WHITE, RED, RED_HI, SHADOW,
)
from tools.render_lottery_header_variants import (
    _coin_disc, _clover, _l1_panel_and_text,
)
from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene,
)

_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "lottery_d2_rich")
os.makedirs(_OUT, exist_ok=True)


BLACK = (8, 8, 14)
TEAL  = (90, 175, 175)

# Slightly smaller than v2 (was 76×56) — closer to the live
# icon's original footprint, but still significantly larger than
# the 40×30 live size so the new richness reads.
NATIVE_W = 64
NATIVE_H = 48


def _gold_card_base_black_rim(big, SS):
    """L1 chassis with a thin BLACK outer ring outside the chrome.
    Layers, outermost first:
        BLACK 1-SS ring  →  chrome 2-SS ring  →  dashed dark-gold
        inner stroke  →  gold body + top sheen.
    Returns (card_rect, inner_rect)."""
    w, h = big.get_width(), big.get_height()
    card = pygame.Rect(3 * SS, 3 * SS, w - 6 * SS, h - 6 * SS)
    # Drop shadow.
    sh = pygame.Surface((card.width + 4 * SS, card.height + 4 * SS),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, SHADOW, sh.get_rect(),
                     border_radius=4 * SS)
    big.blit(sh, sh.get_rect(center=(card.centerx,
                                      card.centery + SS + 1)))
    # Gold gradient body.
    _v_gradient_rect(big, card, GOLD_HI, GOLD_LO, radius=4 * SS)
    # Top sheen.
    hi_h = card.height // 3
    hi = pygame.Surface((card.width, hi_h), pygame.SRCALPHA)
    for y in range(hi_h):
        a = int(110 * (1.0 - y / hi_h))
        pygame.draw.line(hi, (255, 250, 220, a),
                         (0, y), (hi.get_width(), y))
    big.blit(hi, (card.x, card.y))
    # Chrome perimeter (2 SS).
    pygame.draw.rect(big, CHROME, card, width=2 * SS,
                     border_radius=4 * SS)
    # BLACK outer perimeter — slimmer (1 SS) than the v1's 2 SS so
    # it reads as a crisp outline.
    black_rect = card.inflate(2 * SS, 2 * SS)
    pygame.draw.rect(big, BLACK, black_rect, width=1 * SS,
                     border_radius=5 * SS)
    # Dashed dark-gold inner stroke.
    inner = card.inflate(-4 * SS, -4 * SS)
    _dashed_rect(big, inner, STROKE, dash=4 * SS, gap=3 * SS,
                 width=max(1, SS // 2))
    return card, inner


def draw_d2_rich(surf, cx, cy, pulse):
    """D2 rich v3 — LUCKY banner + clover + coin + WIN stamp +
    light rays + confetti + black outer perimeter on a 64×48
    canvas. Tilt amplitude restored to the original ±8°.

    Live integration note: the original _draw_lottery_icon also
    bobs vertically by sin(pulse * 0.8) * 2 px around its
    anchor — that should be added at the entities.py call site
    (not here, since the static renderer can't show motion)."""

    def paint(big, SS):
        card, inner = _gold_card_base_black_rim(big, SS)

        # Red arched banner across the top. Taller than v1 (9 SS vs
        # 6 SS) so "LUCKY" is ~7 native px instead of ~5 — crisp at
        # game scale.
        banner_h = int(9 * SS)
        banner = pygame.Rect(card.left + 6 * SS, card.top + SS,
                             card.width - 12 * SS, banner_h)
        _v_gradient_rect(big, banner, RED_HI, RED, radius=2 * SS)
        pygame.draw.rect(big, STROKE, banner, max(1, SS // 2),
                         border_radius=2 * SS)
        # Ribbon-fold notches at the ends.
        notch_w = int(2.5 * SS)
        pygame.draw.polygon(big, RED, [
            (banner.left, banner.top),
            (banner.left - notch_w, banner.centery),
            (banner.left, banner.bottom),
        ])
        pygame.draw.polygon(big, RED, [
            (banner.right, banner.top),
            (banner.right + notch_w, banner.centery),
            (banner.right, banner.bottom),
        ])

        # 4 gold sun-rays radiating downward from beneath the banner
        # across the upper gold body — "burst of luck" feel.
        ray_origin = (banner.centerx, banner.bottom)
        for ang_deg in (-32, -12, 12, 32):
            ang = math.radians(90 + ang_deg)
            x2 = ray_origin[0] + math.cos(ang) * int(banner.width * 0.55)
            y2 = ray_origin[1] + math.sin(ang) * int(banner.width * 0.55)
            ray = pygame.Surface(big.get_size(), pygame.SRCALPHA)
            pygame.draw.line(ray, (255, 245, 170, 130),
                              ray_origin, (x2, y2), max(1, SS))
            big.blit(ray, (0, 0))

        # LUCKY caption + 2 cream sparkles flanking the text inside
        # the banner. Two-pass render (dark shadow + cream fill)
        # gives crisper edges at game scale.
        f = _font(int(banner_h * 0.82))
        bt_sh = f.render("LUCKY", True, STROKE)
        bt    = f.render("LUCKY", True, CREAM)
        big.blit(bt_sh, bt_sh.get_rect(
            center=(banner.centerx + SS // 2,
                    banner.centery + SS // 2)))
        big.blit(bt, bt.get_rect(center=banner.center))
        sp_y = banner.centery
        _sparkle(big, banner.left + 5 * SS, sp_y, int(SS * 1.6),
                 colour=CREAM)
        _sparkle(big, banner.right - 5 * SS, sp_y, int(SS * 1.6),
                 colour=CREAM)

        # Foil panel between banner and bottom-row stamps.
        bot_row_h = 10 * SS  # reserved for clover / coin / WIN stamp
        panel = pygame.Rect(inner.left + 2 * SS,
                            banner.bottom + 2 * SS,
                            inner.width - 4 * SS,
                            inner.bottom - banner.bottom - bot_row_h)
        _silver_panel(big, panel, radius=2 * SS)
        # Two-pass "? ? ?" — STROKE shadow under CREAM highlight
        # under bold NAVY fill for the crispest possible read at
        # smoothscale-down time.
        f_q = _font(int(panel.height * 0.78))
        q_sh   = f_q.render("? ? ?", True, STROKE)
        q_hl   = f_q.render("? ? ?", True, CREAM)
        q_fill = f_q.render("? ? ?", True, NAVY)
        qr = q_fill.get_rect(center=panel.center)
        big.blit(q_sh, q_sh.get_rect(
            center=(qr.centerx + SS // 2, qr.centery + SS // 2)))
        big.blit(q_hl, q_hl.get_rect(
            center=(qr.centerx, qr.centery - SS // 2)))
        big.blit(q_fill, qr)

        # Bottom-row decorations: clover left, WIN stamp centre,
        # coin right.
        bot_y = panel.bottom + int(5 * SS)
        _clover(big, card.left + 8 * SS, bot_y,
                int(SS * 1.9), SS)
        # Centre "WIN!" mini stamp. Taller (6 SS vs v1's 4 SS) for
        # readable letters.
        win_h = 6 * SS
        win_rect = pygame.Rect(0, 0, int(16 * SS), win_h)
        win_rect.center = (card.centerx, bot_y)
        _v_gradient_rect(big, win_rect, RED_HI, RED,
                         radius=int(SS * 2))
        pygame.draw.rect(big, STROKE, win_rect, max(1, SS // 2),
                         border_radius=int(SS * 2))
        fw = _font(int(win_h * 0.82))
        wt_sh = fw.render("WIN!", True, STROKE)
        wt    = fw.render("WIN!", True, CREAM)
        big.blit(wt_sh, wt_sh.get_rect(center=(win_rect.centerx + SS // 2,
                                                 win_rect.centery + SS // 2)))
        big.blit(wt, wt.get_rect(center=win_rect.center))
        # Coin lower-right.
        _coin_disc(big, card.right - 8 * SS, bot_y,
                   int(SS * 2.8), SS, label="$")

        # Confetti dots scattered around the card — mixed accent
        # colours. Tuned positions for the larger 76×56 canvas.
        confetti_specs = [
            (card.left  + 5 * SS,  card.top    + 15 * SS, TEAL),
            (card.right - 5 * SS,  card.top    + 16 * SS, RED_HI),
            (card.left  + 4 * SS,  card.bottom - 17 * SS, CREAM),
            (card.right - 4 * SS,  card.bottom - 16 * SS, TEAL),
            (card.centerx - 22 * SS, card.bottom - 11 * SS, CREAM),
            (card.centerx + 22 * SS, card.bottom - 11 * SS, RED_HI),
        ]
        for x, y, col in confetti_specs:
            pygame.draw.circle(big, col, (x, y), max(1, int(SS * 1.2)))
            pygame.draw.circle(big, STROKE, (x, y),
                               max(1, int(SS * 1.2)),
                               max(1, SS // 3))

        # L1's 3 corner sparkles (kept), repositioned for the larger
        # canvas.
        _sparkle(big, card.right - 7 * SS, card.top + 13 * SS, 3 * SS)
        _sparkle(big, card.left + 10 * SS, card.bottom - 11 * SS, 2 * SS)
        _sparkle(big, card.right - 12 * SS, card.bottom - 8 * SS,
                 int(SS * 2.2), colour=(255, 230, 120))

    icon = _ss_paint(paint, native_w=NATIVE_W, native_h=NATIVE_H)
    # Tilt amplitude matches the original live _draw_lottery_icon
    # (±8°) so the new card has the same "alive" feel as the
    # previous one.
    tilt = math.sin(pulse * 0.7) * 8
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


# ── output ──────────────────────────────────────────────────────────────────

def main():
    # Native zoom scaled 6× for review.
    base = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    draw_d2_rich(base, NATIVE_W // 2, NATIVE_H // 2, pulse=1.6)
    zoom = pygame.transform.scale(base, (NATIVE_W * 6, NATIVE_H * 6))
    pygame.draw.rect(zoom, (255, 215, 0), zoom.get_rect(), 2)
    zoom_path = os.path.join(_OUT, "D2_rich.png")
    pygame.image.save(zoom, zoom_path)
    print(f"saved {zoom_path}")

    # In-game composite.
    world = build_world()
    frame = render_play_scene(world)
    icon_cx = int(world.bird.x) + 110
    icon_cy = int(world.bird.y)
    base_ig = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    draw_d2_rich(base_ig, NATIVE_W // 2, NATIVE_H // 2, pulse=1.6)
    frame.blit(base_ig, base_ig.get_rect(center=(icon_cx, icon_cy)))
    ingame_path = os.path.join(_OUT, "D2_rich_ingame.png")
    pygame.image.save(frame, ingame_path)
    print(f"saved {ingame_path}")

    base_url = ("https://raw.githubusercontent.com/ytocker/skybit/"
                "v5_powerups/docs/screenshots/lottery_d2_rich")
    print()
    print(f"{base_url}/D2_rich.png")
    print(f"{base_url}/D2_rich_ingame.png")


if __name__ == "__main__":
    main()
