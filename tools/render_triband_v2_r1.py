"""Triband store-card concept (v2, round 1): three hard horizontal zones with a
shape+colour pip rarity header, dark art band, and a charcoal name/price footer.

Round-1 exploration render only — writes a 3-panel review sheet (current card /
triband at 1x / 3x zoom for pip legibility). Not wired into the live store.
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
from game import store_cards
from game.hud import _font

# ── legendary rarity palette (kitsune tier) ───────────────────────────────────
GEM = (255, 202, 104)   # header fill, hairline, pips-as-price, gold text
GLOW = (255, 168, 58)   # accent
DEEP = (150, 92, 22)    # dark rim under the pips

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


def render_triband():
    canvas = pygame.Surface((CW, CH), pygame.SRCALPHA)

    # 1. Header band — solid rarity fill.
    pygame.draw.rect(canvas, GEM, (0, 0, CW, HEADER_H))
    # A one-device-px darker seat under the header grounds the pips on the fill.
    pygame.draw.rect(canvas, DEEP, (0, HEADER_H - 2, CW, 2))

    # 2. Art band — dark near-black.
    pygame.draw.rect(canvas, (10, 10, 20), (0, ART_Y0, CW, ART_Y1 - ART_Y0))

    # 3. Item art — kitsune, fit within the art band with a small margin so it
    #    never touches the hard band edges.
    sprite = parrot.get_skin_icon("skin_kitsune") \
        or parrot.get_skin_frame_hi("skin_kitsune")
    art = _fit_within(sprite, CW - 40, (ART_Y1 - ART_Y0) - 24)
    ar = art.get_rect(center=(CW // 2, (ART_Y0 + ART_Y1) // 2))
    canvas.blit(art, ar.topleft)

    # 4. Rarity pips — 4 filled diamonds (legendary) centred in the header. A
    #    diamond reads as a countable shape at 1x better than a soft dot, and the
    #    dark seat under each gives it a crisp edge against the gold fill.
    pip_count = 4
    spacing = 24         # device px between pip centres
    pip_r = 6            # half-diagonal of the diamond
    total = spacing * (pip_count - 1)
    x0 = CW // 2 - total // 2
    cy = HEADER_H // 2 - 1
    for i in range(pip_count):
        cx = x0 + i * spacing
        # Dark under-shadow one px down for separation from the gold field.
        pygame.draw.polygon(canvas, DEEP, [
            (cx, cy - pip_r + 1), (cx + pip_r, cy + 1),
            (cx, cy + pip_r + 1), (cx - pip_r, cy + 1)])
        pygame.draw.polygon(canvas, (255, 255, 255), [
            (cx, cy - pip_r), (cx + pip_r, cy),
            (cx, cy + pip_r), (cx - pip_r, cy)])

    # 5. Hairline separator — rarity-coloured, at the top of the footer band.
    pygame.draw.line(canvas, GEM, (0, ART_Y1), (CW, ART_Y1), 2)

    # 6. Footer band — warm charcoal.
    pygame.draw.rect(canvas, (26, 22, 18), (0, ART_Y1 + 2, CW, FOOTER_H - 2))

    # 7. Name — white bold, left-aligned, vertically centred in the footer.
    name_f = _font(30, True)
    name = name_f.render("KITSUNE", True, (255, 255, 255))
    foot_cy = ART_Y1 + FOOTER_H // 2
    canvas.blit(name, (24, foot_cy - name.get_height() // 2))

    # 8. Price — gold, right-aligned, with a small coin glyph.
    price_f = _font(26, True)
    price = price_f.render("3,500", True, GEM)
    coin_r = 8
    coin_cx = CW - 24 - coin_r
    coin_cy = foot_cy
    px = coin_cx - coin_r - 8 - price.get_width()
    canvas.blit(price, (px, foot_cy - price.get_height() // 2))
    # Minimal coin token: gold disc + deep rim + a slim inner ring.
    pygame.draw.circle(canvas, DEEP, (coin_cx, coin_cy), coin_r)
    pygame.draw.circle(canvas, GEM, (coin_cx, coin_cy), coin_r - 2)
    pygame.draw.circle(canvas, GLOW, (coin_cx, coin_cy), coin_r - 2, 1)

    # 9. Rounded corners on the whole chip.
    return _round_corners(canvas, 16)


# ── 3-panel review sheet ──────────────────────────────────────────────────────
def build_sheet():
    before = store_cards.render_card("skin_kitsune", equipped=False, owned=True)
    tri_big = render_triband()                      # 324 x 200
    tri_1x = pygame.transform.smoothscale(tri_big, (CARD_W1, CARD_H1))

    disp_1x = pygame.transform.scale(tri_1x, (CARD_W1 * 2, CARD_H1 * 2))
    zoom_3x = pygame.transform.scale(tri_1x, (CARD_W1 * 3, CARD_H1 * 3))

    pad = 28
    label_h = 34
    panels = [
        ("BEFORE (current)", before),
        ("TRIBAND @1x (2x view)", disp_1x),
        ("3x ZOOM — pip detail", zoom_3x),
    ]
    inner_w = max(p[1].get_width() for p in panels)
    total_w = pad * (len(panels) + 1) + sum(p[1].get_width() for p in panels)
    max_card_h = max(p[1].get_height() for p in panels)
    total_h = pad * 2 + label_h + max_card_h + 40

    sheet = pygame.Surface((total_w, total_h))
    sheet.fill((22, 24, 30))
    title_f = _font(20, True)
    lab_f = _font(15, True)

    title = title_f.render(
        "TRIBAND item-card v2  —  round 1  (kitsune / legendary)",
        True, (235, 238, 245))
    sheet.blit(title, (pad, 10))

    x = pad
    top = 44
    for label, card in panels:
        lab = lab_f.render(label, True, (170, 200, 235))
        sheet.blit(lab, (x, top))
        cy = top + label_h
        # A neutral plate behind each card separates it from the sheet ground.
        plate = pygame.Rect(x - 6, cy - 6, card.get_width() + 12,
                            card.get_height() + 12)
        pygame.draw.rect(sheet, (14, 15, 19), plate, border_radius=8)
        sheet.blit(card, (x, cy))
        x += card.get_width() + pad

    return sheet


def main():
    out_dir = "/home/user/skybit/docs/item_card_redesign_v2/triband"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")
    sheet = build_sheet()
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
