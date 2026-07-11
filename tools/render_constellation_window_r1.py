"""Round-1 review render for the `constellation-window` item-card concept.

Celestial night-sky card: the kitsune's nine tail-tips are mapped as a live
gold constellation across the side margins, over a deep indigo sky dusted with
background stars, a faint zodiac arc, a legendary aurora ribbon, and a small
brass astrolabe price tag. Headless-only tooling — never shipped in the bundle.
"""
import os
import sys
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.animal_kitsune import build_kitsune, build_kitsune_aura
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.store_cards import vgrad, soft_glow, drop_shadow
from game.hud import _font


# ── card metrics (authored at 2x = 324x210) ─────────────────────────────────
CARD_W, CARD_H = 324, 210
RAD = 32                                  # radius 16 @ 2x
CX, CY = CARD_W // 2, CARD_H // 2

SKY_TOP = (4, 4, 18)
SKY_BOT = (10, 8, 30)
GOLD = (255, 202, 104)                    # legendary gem / constellation gold
BORDER = (60, 50, 100)

# Nine tail-tip constellation points — a symmetric fan arcing across the top
# in both side margins, matching the general direction of the fox's tails.
TIPS = [(20, 30), (44, 14), (80, 6), (120, 8), (162, 14),
        (204, 8), (248, 6), (288, 14), (308, 30)]


def _round_mask(w, h, radius):
    m = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(m, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    return m


def _aurora(card):
    """Legendary aurora ribbon — three wide low-alpha arc strokes blended
    additively so light pools in the margins without veiling the fox."""
    bands = [
        # (center, radius, a0, a1, color, peak_alpha)  arc angle span in degrees
        ((208, CY), 176, 128, 232, (80, 220, 160), 25),   # teal, left margin
        ((116, CY), 176, 308, 52, (120, 80, 200), 20),    # violet, right margin
        ((CX, 330), 258, 62, 118, (255, 202, 104), 15),   # gold, behind fox
    ]
    for (ccx, ccy), r, a0, a1, col, alpha in bands:
        layer = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        rect = pygame.Rect(ccx - r, ccy - r, r * 2, r * 2)
        # a few overlapping strokes so the ribbon has soft feathered width
        for k, wd in enumerate((7, 5, 3)):
            fa = int(alpha * (1.0 - k * 0.22))
            pygame.draw.arc(layer, (*col, fa), rect,
                            math.radians(a0), math.radians(a1), wd)
        card.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)


def _bg_stars(card):
    """Faint dust in the side margins only — sparse/absent behind the fox so he
    reads clean. Seeded for a repeatable star field."""
    rng = random.Random(7411)
    layer = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    placed = 0
    target = rng.randint(60, 80)
    tries = 0
    while placed < target and tries < 4000:
        tries += 1
        # left margin x=0..90 or right margin x=234..324
        if rng.random() < 0.5:
            x = rng.randint(4, 90)
        else:
            x = rng.randint(234, 320)
        y = rng.randint(6, CARD_H - 8)
        rr = rng.choice((1, 1, 2))
        col = rng.choice((WHITE, WHITE, (200, 210, 255)))
        a = rng.randint(90, 200)
        pygame.draw.circle(layer, (*col, a), (x, y), rr)
        placed += 1
    card.blit(layer, (0, 0))


def _zodiac_arc(card):
    """A faint gold zodiac ring threading through the nine tip points — a wide
    shallow arc capping the top of the card."""
    layer = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    # circle through (20,30)-(164,8)-(308,30): sagitta geometry -> R~482
    r = 482
    ccx, ccy = 164, 8 + r
    rect = pygame.Rect(ccx - r, ccy - r, r * 2, r * 2)
    pygame.draw.arc(layer, (*GOLD, 40), rect,
                    math.radians(72), math.radians(108), 1)
    card.blit(layer, (0, 0))


def _constellation_lines(card):
    """Thin gold star-chart lines linking adjacent tip stars."""
    layer = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    pygame.draw.lines(layer, (*GOLD, 70), False, TIPS, 1)
    card.blit(layer, (0, 0))


def _constellation_stars(card):
    """The nine glowing tip stars — legendary shows all nine lit (a complete
    ring); lower tiers would light fewer."""
    for (x, y) in TIPS:
        soft_glow(card, x, y, 8, GOLD, 60, layers=8)
    for (x, y) in TIPS:
        pygame.draw.circle(card, GOLD, (x, y), 4)
        pygame.draw.circle(card, WHITE, (x, y), 2)


def _fox(card):
    """Aura first, then the scaled sprite — the brightest element, centered."""
    sprite = build_kitsune(20)               # 64x84
    aura = build_kitsune_aura()              # 64x84
    fw, fh = 160, 210
    s_aura = pygame.transform.smoothscale(aura, (fw, fh))
    s_fox = pygame.transform.smoothscale(sprite, (fw, fh))
    rect = s_fox.get_rect(center=(CX, CY))
    card.blit(s_aura, rect.topleft)
    card.blit(s_fox, rect.topleft)


def _price_tag(card):
    """Small brass astrolabe circle in the lower-right margin."""
    x, y, r = 292, 178, 18
    pygame.draw.circle(card, (40, 32, 60), (x, y), r)
    pygame.draw.circle(card, (180, 140, 50), (x, y), r, 2)
    f = _font(13, True)
    txt = f.render("3,500", True, GOLD)
    if txt.get_width() > r * 2 - 4:
        s = (r * 2 - 4) / txt.get_width()
        txt = pygame.transform.smoothscale(
            txt, (int(txt.get_width() * s), int(txt.get_height() * s)))
    card.blit(txt, txt.get_rect(center=(x, y)))


def build_card():
    card = vgrad(CARD_W, CARD_H, RAD, SKY_TOP, SKY_BOT, alpha=255, gamma=1.0)
    _aurora(card)
    _bg_stars(card)
    _zodiac_arc(card)
    _constellation_lines(card)
    _fox(card)
    _constellation_stars(card)
    _price_tag(card)
    # clip any additive/overflow spill back to the rounded body
    card.blit(_round_mask(CARD_W, CARD_H, RAD), (0, 0),
              special_flags=pygame.BLEND_RGBA_MIN)
    # thin soft border defining the edge against the grid background
    pygame.draw.rect(card, (*BORDER, 200), (0, 0, CARD_W, CARD_H),
                     width=2, border_radius=RAD)
    return card


def _grid_bg(w, h):
    bg = pygame.Surface((w, h))
    bg.fill((26, 26, 34))
    for x in range(0, w, 24):
        pygame.draw.line(bg, (34, 34, 44), (x, 0), (x, h))
    for y in range(0, h, 24):
        pygame.draw.line(bg, (34, 34, 44), (0, y), (w, y))
    return bg


def main():
    card = build_card()

    pad = 40
    gap = 34
    small = pygame.transform.smoothscale(card, (CARD_W // 2, CARD_H // 2))
    W = pad * 2 + CARD_W
    H = pad + 30 + CARD_H + gap + small.get_height() + 30 + pad
    review = _grid_bg(W, H)

    title_f = _font(18, True)
    review.blit(title_f.render("constellation-window", True, (236, 232, 245)),
                (pad, pad - 8))
    sub_f = _font(11, True)
    review.blit(sub_f.render("round 1", True, (150, 150, 168)),
                (pad, pad + 12))

    # main card with a soft drop shadow so it lifts off the grid
    mx, my = pad, pad + 30
    sh = pygame.Surface((W, H), pygame.SRCALPHA)
    drop_shadow(sh, pygame.Rect(mx, my, CARD_W, CARD_H), RAD, 10, 150, 4)
    review.blit(sh, (0, 0))
    review.blit(card, (mx, my))

    # actual-size (1x) reference to check small-scale legibility
    sy = my + CARD_H + gap
    review.blit(small, (pad, sy + 18))
    review.blit(sub_f.render("actual size (1x)", True, (150, 150, 168)),
                (pad, sy))

    out = "/home/user/skybit/docs/item_card_redesign/constellation-window/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(review, out)
    print("saved:", out)
    print("card size:", card.get_size())
    print("review size:", review.get_size())


if __name__ == "__main__":
    main()
