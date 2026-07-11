"""Round-2 review render for the `constellation-window` item-card concept.

Round-2 answers the art-director's round-1 notes: the nine tail-tip stars now
trace an actual RING that arcs through both side margins (not a top-only
garland), closed behind the fox so it wraps him like a star-window; the
constellation chain is thickened + double-stroked so it survives the 1x
downscale; the sky gains real depth (warm indigo bloom, milky-way haze, star
temperature/size variety, a wider base gradient); the aurora is now COOL in the
margins (teal S-curve left, violet S-curve right) leaving the warm centre to the
fox's own gold aura; the fox is scaled down + nudged low to open air above him;
and the price is a horizontal navy/gold pill in the lower-right corner.

Headless-only tooling — never shipped in the bundle.
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
from game.draw import lerp_color, WHITE
from game.store_cards import vgrad_stops, soft_glow, drop_shadow
from game.hud import _font


# ── card metrics (authored at 2x = 324x200, per brief) ──────────────────────
CARD_W, CARD_H = 324, 200
RAD = 34                                   # 17 @ 2x — matches the store card
CX, CY = CARD_W // 2, CARD_H // 2

# Wider base gradient so the sky reads as lit depth rather than flat black.
SKY_TOP = (4, 4, 30)
SKY_BOT = (2, 2, 12)
GOLD = (255, 202, 104)                     # legendary constellation gold
LINE_INNER = (255, 253, 224)               # #fffde0 — thin near-white core
BORDER = (60, 50, 100)

# The fox sits ~5px below centre and is scaled slightly down, opening air above
# him so the ring's top arc sweeps clean of the ears.
FOX_H = 185
FOX_CX, FOX_CY = CX, CY + 6

# Nine tail-tip stars traced as an OVAL that hugs the fox: one at the crown,
# four springing down each flank so the chain wraps through both side margins.
# Sequential around the ring (top -> down right -> across bottom -> up left) so
# pygame.draw.lines(closed=True) closes it into a continuous window frame.
RING = [
    (162, 24),     # 0  crown, sprung from the top tail tips
    (226, 34),     # 1  upper-right
    (280, 66),     # 2  right shoulder
    (289, 108),    # 3  right (3 o'clock)
    (258, 152),    # 4  lower-right
    (66, 152),     # 5  lower-left  (bottom span rides BEHIND the fox)
    (35, 108),     # 6  left (9 o'clock)
    (44, 66),      # 7  left shoulder
    (98, 34),      # 8  upper-left
]


def _round_mask(w, h, radius):
    m = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(m, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    return m


def _base_sky(w, h, radius):
    return vgrad_stops(w, h, radius, [(0.0, SKY_TOP), (1.0, SKY_BOT)],
                       alpha=255, gamma=1.0)


def _indigo_bloom(card):
    """Large low-alpha additive bloom behind the fox — a warm indigo/violet core
    that lifts the near-black flatness and makes the card feel lit from within
    without competing with the fox's own gold aura."""
    soft_glow(card, FOX_CX, FOX_CY, 82, (74, 58, 150), 32, layers=12)
    soft_glow(card, FOX_CX, FOX_CY - 6, 46, (96, 74, 168), 22, layers=10)


def _haze_bands(card):
    """Two faint milky-way ribbons at shallow, differing angles — additive and
    near-invisible on their own, but they give the sky depth behind the stars."""
    for (bcx, bcy), length, thick, ang, col, alpha in (
        ((150, 74),  360, 40, -9, (150, 140, 200), 13),
        ((176, 132), 340, 30,  6, (120, 150, 190), 10),
    ):
        band = pygame.Surface((length, thick), pygame.SRCALPHA)
        for y in range(thick):
            # soft-edged core: brightest along the band's spine, faded to nil.
            f = 1.0 - abs(y - thick / 2) / (thick / 2)
            a = int(alpha * (max(0.0, f)) ** 1.6)
            if a > 0:
                pygame.draw.line(band, (*col, a), (0, y), (length, y))
        rot = pygame.transform.rotate(band, ang)
        card.blit(rot, rot.get_rect(center=(bcx, bcy)),
                  special_flags=pygame.BLEND_ADD)


def _aurora(card):
    """Cool margin ribbons: teal on the LEFT, violet on the RIGHT, each a gentle
    S-curve (sigmoid) sweeping top-to-bottom in its own margin. Feathered soft
    blobs so light pools in the margins; the warm centre is left to the fox."""
    ribbons = [
        # (base_x, amplitude, phase, color, peak_alpha)
        (46,  20,  1.0, (70, 210, 200), 62),   # teal, left margin
        (278, 20, -1.0, (150, 92, 224), 60),   # violet, right margin
    ]
    for base_x, amp, sign, col, peak in ribbons:
        layer = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        for y in range(14, CARD_H - 14, 3):
            # tanh sigmoid gives a clean single S from top to bottom.
            s = math.tanh((y - CARD_H / 2) / 42.0)
            x = base_x + sign * amp * s
            # brightest mid-height, tapering at the ends so the ribbon floats.
            edge = 1.0 - abs(y - CARD_H / 2) / (CARD_H / 2 - 14)
            a = int(peak * (max(0.0, edge)) ** 0.7)
            for rr, af in ((16, 0.30), (11, 0.55), (6, 1.0)):
                pygame.draw.circle(layer, (*col, int(a * af)), (int(x), y), rr)
        card.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)


def _bg_stars(card):
    """A depth-graded starfield across the whole card: temperature variety (warm
    / cyan / white), size variety, and a thinned, dimmer core zone behind the
    fox so he still reads clean. Seeded for a repeatable field."""
    rng = random.Random(7411)
    layer = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    placed, tries = 0, 0
    while placed < 150 and tries < 8000:
        tries += 1
        x = rng.randint(4, CARD_W - 4)
        y = rng.randint(6, CARD_H - 8)
        d = math.hypot(x - FOX_CX, y - FOX_CY)
        # thin + dim the field inside the fox's core so he reads uncluttered.
        if d < 58 and rng.random() < 0.82:
            continue
        temp = rng.random()
        if temp < 0.20:
            col = (255, 248, 232)          # warm-white
        elif temp < 0.40:
            col = (232, 248, 255)          # cyan-white
        else:
            col = WHITE
        rr = rng.choice((1, 1, 1, 2, 2, 3))
        a = rng.randint(70, 210)
        if d < 58:
            a = int(a * 0.5)
        pygame.draw.circle(layer, (*col, a), (x, y), rr)
        if rr >= 3:                        # a faint bloom on the brightest stars
            pygame.draw.circle(layer, (*col, a // 4), (x, y), rr + 2)
        placed += 1
    card.blit(layer, (0, 0))


def _constellation_lines(card):
    """The star-chart chain: a closed ring through both side margins. Drawn
    thick + double-stroked so it survives the 1x downscale — a 3px gold body
    (alpha 120) with a 1px near-white core (alpha 80) threaded on top."""
    layer = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    pygame.draw.lines(layer, (*GOLD, 128), True, RING, 3)
    pygame.draw.lines(layer, (*LINE_INNER, 80), True, RING, 1)
    card.blit(layer, (0, 0))


def _constellation_stars(card):
    """The nine tail-tip stars, each with a soft gold halo, a gold body and a
    white core. Legendary lights all nine — the complete ring."""
    for (x, y) in RING:
        soft_glow(card, x, y, 9, GOLD, 70, layers=8)
    for (x, y) in RING:
        # a faint 4-point twinkle so each reads as a charted star, not a dot.
        for dx, dy in ((7, 0), (-7, 0), (0, 7), (0, -7)):
            pygame.draw.line(card, (*LINE_INNER, 120), (x, y), (x + dx, y + dy), 1)
        pygame.draw.circle(card, GOLD, (x, y), 4)
        pygame.draw.circle(card, WHITE, (x, y), 2)


def _fox(card):
    """Aura first, then the scaled sprite — the brightest element, low-centred so
    the ring's top arc clears the ears."""
    sprite = build_kitsune(20)               # 64x84
    aura = build_kitsune_aura()              # 64x84
    fw = int(round(64 / 84 * FOX_H))
    s_aura = pygame.transform.smoothscale(aura, (fw, FOX_H))
    s_fox = pygame.transform.smoothscale(sprite, (fw, FOX_H))
    rect = s_fox.get_rect(center=(FOX_CX, FOX_CY))
    card.blit(s_aura, rect.topleft)
    card.blit(s_fox, rect.topleft)


def _price_pill(card):
    """A horizontal navy/gold price plate in the lower-right corner. Its brass is
    deliberately dimmed so it never pulls focal weight off the fox."""
    w, h = 80, 22
    x = CARD_W - 18 - w
    y = CARD_H - 16 - h
    r = pygame.Rect(x, y, w, h)
    plate = pygame.Surface((w, h), pygame.SRCALPHA)
    pr = plate.get_rect()
    pygame.draw.rect(plate, (8, 8, 28, 232), pr, border_radius=h // 2)
    pygame.draw.rect(plate, (150, 120, 60, 235), pr, width=1, border_radius=h // 2)
    card.blit(plate, (x, y))
    f = _font(11, True)
    txt = f.render("3,500", True, (238, 214, 150))
    card.blit(txt, txt.get_rect(center=r.center))


def build_card():
    card = _base_sky(CARD_W, CARD_H, RAD)
    _indigo_bloom(card)
    _haze_bands(card)
    _aurora(card)
    _bg_stars(card)
    _constellation_lines(card)      # BEHIND the fox: the bottom span tucks away
    _fox(card)
    _constellation_stars(card)      # stars ride ON TOP, all in the margins
    _price_pill(card)
    # clip any additive/overflow spill back to the rounded body
    card.blit(_round_mask(CARD_W, CARD_H, RAD), (0, 0),
              special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(card, (*BORDER, 200), (0, 0, CARD_W, CARD_H),
                     width=2, border_radius=RAD)
    return card


# ── display sheet ───────────────────────────────────────────────────────────
def _grid_bg(w, h):
    bg = pygame.Surface((w, h))
    bg.fill((26, 26, 34))
    for x in range(0, w, 24):
        pygame.draw.line(bg, (34, 34, 44), (x, 0), (x, h))
    for y in range(0, h, 24):
        pygame.draw.line(bg, (34, 34, 44), (0, y), (w, y))
    return bg


def _before_card():
    from game import store_cards
    return store_cards.render_card("skin_kitsune", equipped=False, owned=True)


def _fit(surf, box_w):
    w, h = surf.get_size()
    s = box_w / w
    return pygame.transform.smoothscale(surf, (box_w, max(1, int(h * s))))


def main():
    card = build_card()                       # 324x200
    card_1x = pygame.transform.smoothscale(card, (CARD_W // 2, CARD_H // 2))

    W, H = 486, 300
    review = _grid_bg(W, H)
    title_f = _font(15, True)
    sub_f = _font(10, True)
    review.blit(title_f.render("constellation-window  ·  round 2", True,
                               (236, 232, 245)), (14, 10))

    before = _before_card()                   # 162x100
    round1 = pygame.image.load(
        "/home/user/skybit/docs/item_card_redesign/"
        "constellation-window/round_1.png").convert_alpha()

    panels = [
        ("BEFORE (live)", _fit(before, 146)),
        ("ROUND 1", _fit(round1, 146)),
        ("ROUND 2", _fit(card_1x, 146)),
    ]
    col_x = [8, 170, 332]
    for (label, img), cx0 in zip(panels, col_x):
        px = cx0 + (154 - img.get_width()) // 2
        py = 40 + (240 - img.get_height()) // 2
        sh = pygame.Surface((W, H), pygame.SRCALPHA)
        drop_shadow(sh, pygame.Rect(px, py, img.get_width(), img.get_height()),
                    10, 8, 140, 3)
        review.blit(sh, (0, 0))
        review.blit(img, (px, py))
        review.blit(sub_f.render(label, True, (176, 176, 196)), (cx0 + 6, 30))

    out = ("/home/user/skybit/docs/item_card_redesign/"
           "constellation-window/round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(review, out)
    print("saved:", out)
    print("card size:", card.get_size())
    print("review size:", review.get_size())


if __name__ == "__main__":
    main()
