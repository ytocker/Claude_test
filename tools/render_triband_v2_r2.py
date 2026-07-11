"""Triband store-card concept (v2, round 2): three hard horizontal zones with a
shape+colour pip rarity header, dark art band, and a charcoal name/price footer.

Round-2 render — writes the single 324x200 card at authored 2x so the pip
scale-track and plated header read at final size. Not wired into the live store.

Iterates on round 1 per art-director notes: DEEP pips on gold with a 5-slot
empty-pip track, a larger kitsune in the art band, a plated (inset + thick seat)
header, and a 2-tone coin token.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot
from game.hud import _font

# ── legendary rarity palette (kitsune tier) ───────────────────────────────────
GEM = (255, 202, 104)   # header fill, hairline, price/coin face, gold text
GLOW = (255, 168, 58)   # accent
DEEP = (150, 92, 22)    # header seat, filled pips, coin rim
EMPTY = (100, 62, 15)   # lighter outline for the unfilled fifth pip

# ── author at 2x, ship at 1x ──────────────────────────────────────────────────
SS = 2
CARD_W1, CARD_H1 = 162, 100
CW, CH = CARD_W1 * SS, CARD_H1 * SS   # 324 x 200 device px

# Band heights in device px (9 / 63 / 28 logical -> 18 / 126 / 56 device).
HEADER_H = 18
FOOTER_H = 56
ART_Y0, ART_Y1 = HEADER_H, CH - FOOTER_H   # 18 -> 144


def _fit_within(src, box_w, box_h):
    """Crop to the sprite's ink then scale to fit the box, aspect preserved."""
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    s = min(box_w / sw, box_h / sh)
    return pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(sh * s))))


def _round_corners(surf, radius):
    """Mask the square canvas down to a rounded-rect silhouette so the card reads
    as a physical chip rather than a raw tile."""
    w, h = surf.get_size()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=radius)
    out = surf.copy()
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return out


def _diamond(cx, cy, r):
    return [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]


def render_triband():
    canvas = pygame.Surface((CW, CH), pygame.SRCALPHA)

    # 1. Header plate — gold fill inset horizontally so it reads as a deliberate
    #    plate rather than a thin loading bar, seated on a thick DEEP baseline.
    plate_inset = 4
    pygame.draw.rect(canvas, GEM,
                     (plate_inset, 0, CW - plate_inset * 2, HEADER_H))
    # Thick (2 logical / 4 device px) DEEP seat anchors the plate to the art band.
    pygame.draw.rect(canvas, DEEP, (0, HEADER_H - 4, CW, 4))

    # 2. Art band — dark near-black.
    pygame.draw.rect(canvas, (10, 10, 20), (0, ART_Y0, CW, ART_Y1 - ART_Y0))

    # 3. Item art — kitsune, filling most of the art band. Tight margins let the
    #    silhouette dominate the middle zone rather than float in it.
    sprite = parrot.get_skin_icon("skin_kitsune") \
        or parrot.get_skin_frame_hi("skin_kitsune")
    art = _fit_within(sprite, CW - 16, (ART_Y1 - ART_Y0) - 10)
    ar = art.get_rect(center=(CW // 2, (ART_Y0 + ART_Y1) // 2))
    canvas.blit(art, ar.topleft)

    # 4. Rarity pips — a 5-slot track teaches the scale on one card; 4 filled DEEP
    #    diamonds (legendary) plus one empty outline. Dark-on-gold is legible
    #    without an under-shadow, so the pips sit flush on the fill.
    slots = 5
    filled = 4
    spacing = 26         # device px between pip centres
    pip_r = 6            # half-diagonal of the diamond, fills the 18px band
    total = spacing * (slots - 1)
    x0 = CW // 2 - total // 2
    cy = (HEADER_H - 4) // 2   # centre within the gold fill above the seat
    for i in range(slots):
        cx = x0 + i * spacing
        if i < filled:
            pygame.draw.polygon(canvas, DEEP, _diamond(cx, cy, pip_r))
        else:
            pygame.draw.polygon(canvas, EMPTY, _diamond(cx, cy, pip_r), 1)

    # 5. Hairline separator — rarity-coloured, at the top of the footer band.
    pygame.draw.line(canvas, GEM, (0, ART_Y1), (CW, ART_Y1), 2)

    # 6. Footer band — warm charcoal.
    pygame.draw.rect(canvas, (26, 22, 18), (0, ART_Y1 + 2, CW, FOOTER_H - 2))

    # 7. Name — white bold, left-aligned, vertically centred in the footer.
    name_f = _font(30, True)
    name = name_f.render("KITSUNE", True, (255, 255, 255))
    foot_cy = ART_Y1 + FOOTER_H // 2
    canvas.blit(name, (24, foot_cy - name.get_height() // 2))

    # 8. Price — gold, right-aligned, with a simple 2-tone coin token.
    price_f = _font(26, True)
    price = price_f.render("3,500", True, GEM)
    coin_r = 8
    coin_cx = CW - 24 - coin_r
    coin_cy = foot_cy
    px = coin_cx - coin_r - 8 - price.get_width()
    canvas.blit(price, (px, foot_cy - price.get_height() // 2))
    # 2-tone disc: DEEP rim + GEM face, legible at the final 162x100.
    pygame.draw.circle(canvas, DEEP, (coin_cx, coin_cy), coin_r)
    pygame.draw.circle(canvas, GEM, (coin_cx, coin_cy), coin_r - 2)

    # 9. Rounded corners on the whole chip.
    return _round_corners(canvas, 16)


def main():
    out_dir = "/home/user/skybit/docs/item_card_redesign_v2/triband"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")
    card = render_triband()
    pygame.image.save(card, out)
    print("wrote", out, card.get_size())


if __name__ == "__main__":
    main()
