"""Round-2 exploration for the lateral-split item-card concept (v2).

Left art zone (65%) / right metadata column (35%) split by a vertical
rarity rule. The right column now stacks THREE zones top-to-bottom: a
micro-caps tier wordmark, a lightened name plate, and a coin+price row.
Rendered headless and committed under docs/ for art-director review —
never wired into the game.

Round-2 addresses the art-director's iteration notes:
  1. A non-hue rarity cue — the "LEGENDARY" micro-caps wordmark — sits
     first in the column so the tier reads without relying on hue alone.
  2. Column vs plate values are pushed apart so the two rows register as
     distinct zones at 1x.
  3. The coin is a two-tone readable disc (dark rim / gold face / inner ring).
  4. The name plate's smoothscale-muddy inner gold border is gone; the
     lightened fill alone carries the structure.
  5. The name auto-shrinks to guarantee it never overflows the column.
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
GEM = (255, 202, 104)   # rule, tier wordmark, coin face, price text
GLOW = (255, 168, 58)   # unused warm mid — kept for provenance
DEEP = (150, 92, 22)    # coin rims

CARD_W_DEV, CARD_H_DEV = 324, 200
RULE_X, RULE_W = 210, 4
COL_X = 214
COL_W = CARD_W_DEV - COL_X          # 110 device px

# Right-column vertical zones (device px). Wordmark band on top, then the
# lightened name plate, then the coin+price row fills the rest.
WORD_CY = 15                          # tier wordmark baseline-center
PLATE_Y, PLATE_H = 30, 82             # name plate: y=30..112
PRICE_Y = PLATE_Y + PLATE_H          # price row: y=112..200
CARD_RAD = 16

# Distinct panel values so the rows read apart at 1x (AD note 2).
COL_BG = (22, 18, 32)                 # right column / price-row ground
PLATE_BG = (30, 24, 44)              # name plate — clearly lighter


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


def _tier_wordmark(surf, text, cx, cy, color):
    """Tier read that survives desaturation (AD note 1): very small micro-caps
    with wide manual tracking so it reads as a deliberate label, not body text.
    Authored at 10px device (~5px at 1x) — the smallest legible tier stamp."""
    f = sc._font(10, True)
    tracking = 3                                   # wide letter spacing
    widths = [f.size(ch)[0] for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    h = f.get_height()
    base = pygame.Surface((max(1, total), h), pygame.SRCALPHA)
    x = 0
    for ch, w in zip(text, widths):
        base.blit(f.render(ch, True, color), (x, 0))
        x += w + tracking
    surf.blit(base, base.get_rect(center=(cx, cy)))


def _name_fit(surf, text, cx, cy, max_w):
    """Auto-shrink the item name so it can never overflow the column (AD note
    5): start at the design size, step down until it fits, floor at 16px."""
    size = 18
    f = sc._font(size, True)
    while f.render(text, True, (255, 255, 255)).get_width() > max_w and size > 16:
        size -= 1
        f = sc._font(size, True)
    glyph = f.render(text, True, (255, 255, 255))
    surf.blit(glyph, glyph.get_rect(center=(cx, cy)))


def _coin_disc(surf, cx, cy, r):
    """Two-tone readable coin (AD note 3): a dark outer rim, a gold face, and a
    1px inner ring — legible as a coin even downscaled, unlike a flat disc."""
    pygame.draw.circle(surf, GEM, (cx, cy), r)             # gold face
    pygame.draw.circle(surf, DEEP, (cx, cy), r, 1)         # outer dark rim
    pygame.draw.circle(surf, DEEP, (cx, cy), max(2, r - 3), 1)  # inner ring


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

    # 4. Right column ground — pushed lighter so it reads apart from the body.
    pygame.draw.rect(canvas, COL_BG, (COL_X, 0, COL_W, CARD_H_DEV))

    cx = COL_X + COL_W // 2

    # 5. Tier wordmark — the FIRST thing in the column, above the name plate.
    _tier_wordmark(canvas, "LEGENDARY", cx, WORD_CY, GEM)

    # 6. Name plate — a clearly lighter zone; the fill alone carries structure
    #    (no inner gold border, which smoothscaled to mud).
    pygame.draw.rect(canvas, PLATE_BG, (COL_X, PLATE_Y, COL_W, PLATE_H))
    tint = pygame.Surface((COL_W, PLATE_H), pygame.SRCALPHA)
    tint.fill((*GEM, 14))                       # whisper-thin warm wash
    canvas.blit(tint, (COL_X, PLATE_Y))
    _name_fit(canvas, "KITSUNE", cx, PLATE_Y + PLATE_H // 2, COL_W - 16)

    # 7. Price row — coin disc + price, grouped and centered in the column.
    pygame.draw.line(canvas, (44, 38, 56),
                     (COL_X, PRICE_Y), (CARD_W_DEV, PRICE_Y), 1)
    row_cy = (PRICE_Y + CARD_H_DEV) // 2
    price_font = sc._font(17, True)
    price = price_font.render("3,500", True, GEM)
    coin_r, gap = 9, 7
    total_w = coin_r * 2 + gap + price.get_width()
    start_x = COL_X + (COL_W - total_w) // 2
    _coin_disc(canvas, start_x + coin_r, row_cy, coin_r)
    canvas.blit(price, (start_x + coin_r * 2 + gap,
                        row_cy - price.get_height() // 2))

    # 8. Rounded corners on the whole card.
    _round_corners(canvas, CARD_RAD)
    return canvas


def main():
    # The review PNG is the 324x200 device card itself, per the concept spec:
    # a single 2x card the validator downscales to 162x100 to sanity-check.
    card_dev = build_card()
    out = "docs/item_card_redesign_v2/lateral-split/round_2.png"
    os.makedirs(os.path.dirname(os.path.join("/home/user/skybit", out)),
                exist_ok=True)
    pygame.image.save(card_dev, os.path.join("/home/user/skybit", out))
    print("saved", out, card_dev.get_size())


if __name__ == "__main__":
    main()
