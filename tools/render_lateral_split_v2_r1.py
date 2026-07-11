"""Round-1 exploration for the lateral-split item-card concept (v2).

Left art zone (65%) / right metadata column (35%) split by a vertical
rarity-colored rule. The right column carries exactly two rows: a
rarity-tinted name plate and a coin+price row. Rendered headless and
committed under docs/ for art-director review — never wired into the game.
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
from game import store_cards as sc

# Legendary-tier rarity palette (kitsune is legendary).
GEM = (255, 202, 104)   # rule, name-plate accent, price text
GLOW = (255, 168, 58)   # unused warm mid — kept for provenance
DEEP = (150, 92, 22)    # unused deep — kept for provenance

CARD_W_DEV, CARD_H_DEV = 324, 200
RULE_X, RULE_W = 210, 4
COL_X = 214
COL_W = CARD_W_DEV - COL_X          # 110 device px
PLATE_H = 110                        # top row height; price row fills the rest
CARD_RAD = 16


def _round_corners(surf, radius):
    """Clip a rectangular surface to rounded corners by intersecting its alpha
    with a rounded-rect mask (BLEND_RGBA_MIN keeps the smaller alpha)."""
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=radius)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


def _fit_sprite(box_w, box_h, pad):
    """The kitsune product shot, contrast-lifted and scaled to fit the art
    zone with a little breathing room, preserving aspect ratio."""
    src = parrot.get_skin_icon("skin_kitsune") or parrot.get_skin_frame_hi(
        "skin_kitsune")
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    s = min((box_w - pad) / sw, (box_h - pad) / sh)
    scaled = pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(sh * s))))
    return sc._punch_contrast(scaled)


def _draw_text_centered(surf, text, font, color, cx, cy):
    """Faux-bold centered label (the project ships only the Bold ttf, so
    store_cards.font already returns bold at supersample size)."""
    glyph = font.render(text, True, color)
    surf.blit(glyph, glyph.get_rect(center=(cx, cy)))


def build_card():
    canvas = pygame.Surface((CARD_W_DEV, CARD_H_DEV), pygame.SRCALPHA)

    # 1. Card background.
    canvas.fill((10, 8, 16))

    # 2. Art zone — center the hero within x=0..210.
    sprite = _fit_sprite(RULE_X, CARD_H_DEV, pad=22)
    r = sprite.get_rect(center=(RULE_X // 2, CARD_H_DEV // 2))
    # A soft warm rim reads the legendary hero as lit, not a flat sticker.
    canvas.blit(sc._rim_light(sprite), r.topleft, special_flags=pygame.BLEND_ADD)
    canvas.blit(sprite, r.topleft)

    # 3. Rarity rule — full-height vertical stripe dividing the two zones.
    pygame.draw.rect(canvas, GEM, (RULE_X, 0, RULE_W, CARD_H_DEV))

    # 4. Right column background (a touch lighter than the card body).
    pygame.draw.rect(canvas, (14, 12, 22), (COL_X, 0, COL_W, CARD_H_DEV))

    # 5. Name plate (top row) — rarity-tinted dark plate.
    pygame.draw.rect(canvas, (20, 16, 28), (COL_X, 0, COL_W, PLATE_H))
    tint = pygame.Surface((COL_W, PLATE_H), pygame.SRCALPHA)
    tint.fill((*GEM, 18))                       # faint warm wash over the plate
    canvas.blit(tint, (COL_X, 0))
    border = pygame.Surface((COL_W, PLATE_H), pygame.SRCALPHA)
    pygame.draw.rect(border, (*GEM, 80), border.get_rect(), width=2)
    canvas.blit(border, (COL_X, 0))
    name_font = sc.font(9)
    _draw_text_centered(canvas, "KITSUNE", name_font, (255, 255, 255),
                        COL_X + COL_W // 2, PLATE_H // 2)

    # 6. Price row (bottom) — coin glyph + price in rarity gold.
    pygame.draw.rect(canvas, (14, 12, 22),
                     (COL_X, PLATE_H, COL_W, CARD_H_DEV - PLATE_H))
    pygame.draw.line(canvas, (40, 36, 50),
                     (COL_X, PLATE_H), (CARD_W_DEV, PLATE_H), 1)
    coin_cx, coin_cy, coin_r = 222, 155, 7
    pygame.draw.circle(canvas, GEM, (coin_cx, coin_cy), coin_r)
    pygame.draw.circle(canvas, DEEP, (coin_cx, coin_cy), coin_r, 1)
    price_font = sc.font(9)
    price = price_font.render("3,500", True, GEM)
    canvas.blit(price, (232, coin_cy - price.get_height() // 2))

    # 7. Rounded corners on the whole card.
    _round_corners(canvas, CARD_RAD)
    return canvas


def label(surf, text, x, y):
    f = sc._font(14, True)
    surf.blit(f.render(text, True, (150, 156, 178)), (x, y))


def main():
    card_dev = build_card()                              # 324x200 device
    card_1x = pygame.transform.smoothscale(card_dev, (162, 100))
    card_3x = pygame.transform.smoothscale(card_dev, (162 * 3, 100 * 3))
    before = sc.render_card("skin_kitsune", equipped=False, owned=True)

    pad = 24
    gap = 30
    col_w = max(before.get_width(), card_1x.get_width(), card_3x.get_width())
    zoom_w = card_3x.get_width()
    sheet_w = pad * 2 + col_w + gap + zoom_w
    top = 44
    sheet_h = top + max(before.get_height(), card_1x.get_height(),
                        card_3x.get_height()) + card_3x.get_height() + gap + pad
    # Simpler: stack BEFORE + 1x in the left column, 3x zoom on the right.
    sheet_h = top + before.get_height() + gap + card_1x.get_height() + pad

    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill((8, 8, 20))

    lx = pad
    label(sheet, "BEFORE", lx, top - 22)
    sheet.blit(before, (lx, top))

    y2 = top + before.get_height() + gap
    label(sheet, "LATERAL-SPLIT", lx, y2 - 22)
    sheet.blit(card_1x, (lx, y2))

    rx = pad + col_w + gap
    label(sheet, "3x ZOOM", rx, top - 22)
    sheet.blit(card_3x, (rx, top))

    out = "docs/item_card_redesign_v2/lateral-split/round_1.png"
    os.makedirs(os.path.dirname(os.path.join("/home/user/skybit", out)),
                exist_ok=True)
    pygame.image.save(sheet, os.path.join("/home/user/skybit", out))
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
