"""marquee-stripe v2 — item-card redesign round 1 review render.

Headless-only exploration: a full-bleed store card where the item art dominates
the whole card, a full-height rarity stripe on the left, and a slim bottom info
tray (name + price) under a dark gradient scrim. Authored at 2x supersample and
smoothscaled once so edges resolve crisp, matching store_cards' build path.
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


def build_marquee_card():
    """The marquee-stripe card as a 162x100 surface (authored at 2x)."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    W, H = big.get_size()               # 324 x 200
    STRIP_H = m(28)                     # bottom tray height (56 device px)
    STRIPE_W = m(6)                     # left rarity stripe (12 device px)
    art_h = H - STRIP_H                 # 144: the art zone

    # 1) dark full-bleed body
    big.fill((*BG, 255))

    # 2) hero art — trimmed to its silhouette, scaled to dominate the art zone,
    #    centred in the zone (a touch of headroom above the tray).
    src = parrot.get_skin_icon("skin_kitsune") or parrot.get_skin_frame_hi("skin_kitsune")
    bb = src.get_bounding_rect()
    if bb.width and bb.height:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    fit_w, fit_h = W * 0.80, art_h * 0.92
    s = min(fit_w / sw, fit_h / sh)
    art = pygame.transform.smoothscale(src, (max(1, int(sw * s)), max(1, int(sh * s))))
    ar = art.get_rect(center=(W // 2, art_h // 2))
    big.blit(art, ar)

    # 3) bottom scrim so the info tray stays legible over the art
    big.blit(_bottom_scrim(W, STRIP_H), (0, art_h))

    # 4) left rarity stripe — full height, drawn OVER the scrim so its colour
    #    stays bright all the way into the bottom corner: the unbroken vertical
    #    arm plus the tray band read as one rarity L.
    pygame.draw.rect(big, GEM, (0, 0, STRIPE_W, H))

    # 5/6) tray type: name left of the stripe lane, price accent to the right.
    tray_cy = art_h + STRIP_H // 2
    name_left = STRIPE_W + m(6)
    _blit_label(big, "KITSUNE", (255, 255, 255), m(10), left=name_left, cy=tray_cy)

    # price unit = coin glyph + gap + numerals, right-aligned as a whole so the
    # coin never collides with the number and the block hugs the tray's edge.
    price = f"{store_catalog.cost('skin_kitsune'):,}"
    right_edge = W - m(6)
    pr = _blit_label(big, price, GEM, m(10), right=right_edge, cy=tray_cy)
    coin_r = int(STRIP_H * 0.30)
    coin_gap = m(4)
    _coin_glyph(big, pr.left - coin_gap - coin_r, tray_cy, coin_r)

    # 7) round all four corners via a rounded-rect alpha mask
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=m(8))
    big.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    return pygame.transform.smoothscale(big, (CARD_W, CARD_H))


def _panel_label(surf, text, x, y):
    f = _font(15, True)
    base = f.render(text, True, (238, 232, 250))
    sh = f.render(text, True, (4, 4, 12))
    surf.blit(sh, (x + 1, y + 1))
    surf.blit(base, (x, y))


def main():
    marquee = build_marquee_card()
    before = store_cards.render_card("skin_kitsune", equipped=False, owned=True)

    # 3-panel review sheet: BEFORE | MARQUEE (3x) | 3x ZOOM detail
    disp_w = CARD_W * 3
    disp_h = CARD_H * 3
    pad = 18
    label_h = 26
    panels = [
        ("BEFORE (live)", pygame.transform.smoothscale(before, (disp_w, disp_h))),
        ("MARQUEE-STRIPE", pygame.transform.smoothscale(marquee, (disp_w, disp_h))),
        ("3x ZOOM", pygame.transform.smoothscale(marquee, (disp_w, disp_h))),
    ]
    sheet_w = pad + (disp_w + pad) * 3
    sheet_h = pad + label_h + disp_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((8, 8, 20))
    x = pad
    for title, img in panels:
        _panel_label(sheet, title, x, pad // 2)
        sheet.blit(img, (x, pad // 2 + label_h))
        x += disp_w + pad

    out = "/home/user/skybit/docs/item_card_redesign_v2/marquee-stripe/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
