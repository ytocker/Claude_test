"""Render the LOTTERY scratch-card icon — D2 polished and richer.

User picked D2 (LUCKY arched red banner) as the direction. This
version adds:

  * a thick BLACK outer perimeter line outside the chrome ring
  * 2 cream sparkle stars flanking "LUCKY" on the banner
  * 4 thin gold sun-rays radiating downward from beneath the
    banner, painted across the upper gold body
  * a small red "WIN!" mini-stamp at the bottom-centre between
    the clover and the coin
  * 5 confetti dots scattered across the card in mixed colours

The clover, coin, foil "? ? ?" panel, and 3 corner sparkles
from the original D2 are preserved.

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


def _gold_card_base_black_rim(big, SS):
    """Variant of L1's _gold_card_base with an outer BLACK perimeter
    ring outside the chrome. Layers, outermost first:
        BLACK 2-SS ring  →  chrome 2-SS ring  →  dashed dark-gold
        inner stroke  →  gold body + top sheen.
    Returns (card_rect, inner_rect)."""
    w, h = big.get_width(), big.get_height()
    # Card body — slightly tighter so the black ring fits outside.
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
    # BLACK outer perimeter — sits 1 SS outside the chrome ring.
    black_rect = card.inflate(2 * SS, 2 * SS)
    pygame.draw.rect(big, BLACK, black_rect, width=2 * SS,
                     border_radius=5 * SS)
    # Dashed dark-gold inner stroke.
    inner = card.inflate(-4 * SS, -4 * SS)
    _dashed_rect(big, inner, STROKE, dash=4 * SS, gap=3 * SS,
                 width=max(1, SS // 2))
    return card, inner


def draw_d2_rich(surf, cx, cy, pulse):
    """D2 rich — LUCKY banner + clover + coin + WIN stamp +
    light rays + confetti + black outer perimeter."""

    def paint(big, SS):
        card, inner = _gold_card_base_black_rim(big, SS)

        # Red arched banner across the top, pinned over the chrome.
        banner = pygame.Rect(card.left + 6 * SS, card.top + SS,
                             card.width - 12 * SS, int(6 * SS))
        _v_gradient_rect(big, banner, RED_HI, RED, radius=2 * SS)
        pygame.draw.rect(big, STROKE, banner, max(1, SS // 2),
                         border_radius=2 * SS)
        # Ribbon-fold notches at the ends.
        notch_w = 2 * SS
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
        # across the upper gold body — gives the "burst of luck"
        # feel. Drawn before the foil panel so the panel hides their
        # bottoms cleanly.
        ray_origin = (banner.centerx, banner.bottom)
        for i, ang_deg in enumerate((-28, -10, 10, 28)):
            ang = math.radians(90 + ang_deg)
            x2 = ray_origin[0] + math.cos(ang) * int(banner.width * 0.6)
            y2 = ray_origin[1] + math.sin(ang) * int(banner.width * 0.6)
            ray = pygame.Surface(big.get_size(), pygame.SRCALPHA)
            pygame.draw.line(ray, (255, 245, 170, 120),
                              ray_origin, (x2, y2), max(1, SS))
            big.blit(ray, (0, 0))

        # LUCKY caption + 2 cream sparkles flanking the text inside
        # the banner.
        f = _font(int(banner.height * 0.88))
        bt = f.render("LUCKY", True, CREAM)
        big.blit(bt, bt.get_rect(center=banner.center))
        sp_y = banner.centery
        _sparkle(big, banner.left + 4 * SS, sp_y, int(SS * 1.4),
                 colour=CREAM)
        _sparkle(big, banner.right - 4 * SS, sp_y, int(SS * 1.4),
                 colour=CREAM)

        # Foil panel between banner and bottom-row stamps.
        bot_row_h = 7 * SS  # reserved for clover / coin / WIN stamp
        panel = pygame.Rect(inner.left + 2 * SS,
                            banner.bottom + 2 * SS,
                            inner.width - 4 * SS,
                            inner.bottom - banner.bottom - bot_row_h
                            - SS)
        _l1_panel_and_text(big, panel, SS)

        # Bottom-row decorations: clover left, WIN stamp centre,
        # coin right.
        bot_y = panel.bottom + int(3.5 * SS)
        _clover(big, card.left + 7 * SS, bot_y,
                int(SS * 1.6), SS)
        # Centre "WIN!" mini stamp on the gold body.
        win_rect = pygame.Rect(0, 0, int(13 * SS), int(4 * SS))
        win_rect.center = (card.centerx, bot_y)
        _v_gradient_rect(big, win_rect, RED_HI, RED,
                         radius=int(SS * 1.5))
        pygame.draw.rect(big, STROKE, win_rect, max(1, SS // 2),
                         border_radius=int(SS * 1.5))
        fw = _font(int(win_rect.height * 0.95))
        wt = fw.render("WIN!", True, CREAM)
        big.blit(wt, wt.get_rect(center=win_rect.center))
        # Coin lower-right.
        _coin_disc(big, card.right - 7 * SS, bot_y,
                   int(SS * 2.4), SS, label="$")

        # Confetti dots scattered around the card — mixed accent
        # colours to break up the gold. Skip positions that would
        # collide with the banner / panel / bottom row.
        confetti_specs = [
            (card.left  + 4 * SS,  card.top    + 11 * SS, TEAL),
            (card.right - 4 * SS,  card.top    + 12 * SS, RED_HI),
            (card.left  + 3 * SS,  card.bottom - 13 * SS, CREAM),
            (card.right - 3 * SS,  card.bottom - 12 * SS, TEAL),
            (card.centerx - 16 * SS, card.bottom - 9 * SS, CREAM),
        ]
        for x, y, col in confetti_specs:
            pygame.draw.circle(big, col, (x, y), max(1, int(SS * 1.1)))
            pygame.draw.circle(big, STROKE, (x, y),
                               max(1, int(SS * 1.1)),
                               max(1, SS // 3))

        # L1's 3 corner sparkles (kept).
        _sparkle(big, card.right - 6 * SS, card.top + 6 * SS, 3 * SS)
        _sparkle(big, card.left + 8 * SS, card.bottom - 8 * SS, 2 * SS)
        _sparkle(big, card.right - 10 * SS, card.bottom - 5 * SS,
                 2 * SS, colour=(255, 230, 120))

    icon = _ss_paint(paint)
    tilt = math.sin(pulse * 0.7) * 5
    rotated = pygame.transform.rotate(icon, tilt)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


# ── output ──────────────────────────────────────────────────────────────────

def main():
    # 56×42 zoom scaled 6× for review.
    base = pygame.Surface((56, 42), pygame.SRCALPHA)
    draw_d2_rich(base, 28, 21, pulse=1.6)
    zoom = pygame.transform.scale(base, (56 * 6, 42 * 6))
    pygame.draw.rect(zoom, (255, 215, 0), zoom.get_rect(), 2)
    zoom_path = os.path.join(_OUT, "D2_rich.png")
    pygame.image.save(zoom, zoom_path)
    print(f"saved {zoom_path}")

    # In-game composite.
    world = build_world()
    frame = render_play_scene(world)
    icon_cx = int(world.bird.x) + 110
    icon_cy = int(world.bird.y)
    base_ig = pygame.Surface((56, 42), pygame.SRCALPHA)
    draw_d2_rich(base_ig, 28, 21, pulse=1.6)
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
