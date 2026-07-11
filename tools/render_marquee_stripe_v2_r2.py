"""marquee-stripe v2 — item-card redesign round 2 review render.

Round-2 folds in the art-director notes on the round-1 marquee card:
a second (non-hue) rarity channel via vertical LEGENDARY micro-caps down the
stripe, a stripe/price gold split so rarity never reads as currency, a top-of-
tray rule that completes the rarity "L", optical re-centring of the hero to
counter the stripe's left weight, and a slimmer tray so the art dominates more.
Authored at 2x supersample and smoothscaled once so edges resolve crisp,
matching store_cards' build path.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot, store_catalog, store_cards
from game.hud import _font

SS = 2
CARD_W, CARD_H = 162, 100


def m(v):
    return int(round(v * SS))


# ── legendary tier palette (matches store_cards.RARITY["legendary"]) ──────────
GEM = (255, 202, 104)
GLOW = (255, 168, 58)
DEEP = (150, 92, 22)
BG = (10, 8, 16)


def _coin_glyph(surf, cx, cy, r):
    """The in-game coin face at the requested radius so the tray price reads with
    the same coin the player collects."""
    from game.entities import _get_coin_face
    face = _get_coin_face()
    d = max(2, int(r * 2))
    img = pygame.transform.smoothscale(face, (d, d))
    surf.blit(img, img.get_rect(center=(cx, cy)))


def _bottom_scrim(w, h):
    """Vertical scrim, transparent at the top rising to near-opaque at the base,
    so tray type stays legible over whatever art bleeds down into the strip."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        a = int(210 * (y / max(1, h - 1)))
        pygame.draw.line(s, (4, 3, 9, a), (0, y), (w - 1, y))
    return s


def _stripe_rarity_word(text, color, size, spacing):
    """The rarity name rendered vertically down the stripe as a second, non-hue
    channel — colour-blind players still get a readable LEGENDARY signal. Deep
    gold on the brighter stripe gold keeps the micro-caps legible without a
    keyline that a 12px lane can't spare. Wide tracking so the letters breathe
    inside the narrow arm; rotated to run bottom-to-top per the vertical-label
    convention."""
    f = _font(size, True)
    glyphs = [f.render(ch, True, color) for ch in text]
    max_h = max(g.get_height() for g in glyphs)
    total_w = sum(g.get_width() for g in glyphs) + spacing * (len(glyphs) - 1)
    strip = pygame.Surface((total_w, max_h), pygame.SRCALPHA)
    x = 0
    for g in glyphs:
        strip.blit(g, (x, (max_h - g.get_height()) // 2))
        x += g.get_width() + spacing
    return pygame.transform.rotate(strip, 90)


def _label(text, color, size):
    """Bold project glyph with a tight dark keyline so type reads heavy against
    the art below it, faux-bolded via store_cards._stamp_bold at SS."""
    f = _font(size, True)
    base = f.render(text, True, (255, 255, 255))
    base = store_cards._stamp_bold(base, m(0.8))
    img = base.copy()
    img.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    key = base.copy()
    key.fill((6, 5, 12, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return img, key


def _blit_label(surf, text, color, size, *, left=None, right=None, cy=0):
    img, key = _label(text, color, size)
    r = img.get_rect()
    if left is not None:
        r.left = left
    if right is not None:
        r.right = right
    r.centery = cy
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        surf.blit(key, (r.x + dx, r.y + dy))
    surf.blit(img, r)
    return r


def build_marquee_card(scaled=True):
    """The marquee-stripe card authored at 2x (324x200). Returns the 162x100
    smoothscaled card by default, or the raw 324x200 surface when scaled=False
    (the review deliverable is saved at native 2x for pixel inspection)."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    W, H = big.get_size()               # 324 x 200
    STRIP_H = m(24)                     # slimmer bottom tray (48 device px)
    STRIPE_W = m(6)                     # left rarity stripe (12 device px)
    art_h = H - STRIP_H                 # 152: the art zone

    # 1) dark full-bleed body
    big.fill((*BG, 255))

    # 2) hero art — trimmed to its silhouette, scaled to dominate the art zone.
    #    Nudged a few px right of centre so the heavy left stripe doesn't pull
    #    the composition off-balance (optical, not geometric, centring).
    src = parrot.get_skin_icon("skin_kitsune") or parrot.get_skin_frame_hi("skin_kitsune")
    bb = src.get_bounding_rect()
    if bb.width and bb.height:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    fit_w, fit_h = W * 0.80, art_h * 0.92
    s = min(fit_w / sw, fit_h / sh)
    art = pygame.transform.smoothscale(src, (max(1, int(sw * s)), max(1, int(sh * s))))
    ar = art.get_rect(center=(W // 2 + m(3), art_h // 2))
    big.blit(art, ar)

    # 3) bottom scrim so the info tray stays legible over the art
    big.blit(_bottom_scrim(W, STRIP_H), (0, art_h))

    # 4) left rarity stripe in the deeper GLOW gold (distinct from the GEM price
    #    numerals so rarity never reads as currency). Full height, drawn OVER the
    #    scrim so the colour stays bright into the bottom corner.
    pygame.draw.rect(big, GLOW, (0, 0, STRIPE_W, H))

    # 5) top-of-tray rule in the same GLOW gold: with the vertical stripe it
    #    frames a visible rarity "L" corner without extra chrome.
    pygame.draw.rect(big, GLOW, (0, art_h, W, m(1)))

    # 6) second rarity channel — LEGENDARY micro-caps down the stripe, centred
    #    on its full height, so the tier is readable without relying on hue.
    word = _stripe_rarity_word("LEGENDARY", DEEP, 9, m(2))
    big.blit(word, word.get_rect(center=(STRIPE_W // 2, H // 2)))

    # 7/8) tray type: name left of the stripe lane, price accent to the right.
    tray_cy = art_h + STRIP_H // 2
    name_left = STRIPE_W + m(6)
    _blit_label(big, "KITSUNE", (255, 255, 255), m(10), left=name_left, cy=tray_cy)

    # price unit = coin glyph + gap + numerals, right-aligned as a whole so the
    # coin never collides with the number and the block hugs the tray's edge.
    # Numerals stay GEM so currency sits apart from the GLOW rarity gold.
    price = f"{store_catalog.cost('skin_kitsune'):,}"
    right_edge = W - m(6)
    pr = _blit_label(big, price, GEM, m(10), right=right_edge, cy=tray_cy)
    coin_r = int(STRIP_H * 0.30)
    coin_gap = m(4)
    _coin_glyph(big, pr.left - coin_gap - coin_r, tray_cy, coin_r)

    # 9) round all four corners via a rounded-rect alpha mask
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=m(8))
    big.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    if not scaled:
        return big
    return pygame.transform.smoothscale(big, (CARD_W, CARD_H))


def main():
    # The deliverable is the native 2x card (324x200) so pixel-level review and
    # PIL validation see the authored resolution, not a downscaled composite.
    card = build_marquee_card(scaled=False)
    out = "/home/user/skybit/docs/item_card_redesign_v2/marquee-stripe/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(card, out)
    print("saved", out, card.get_size())


if __name__ == "__main__":
    main()
