"""Matte-frame store-card concept (item-card redesign v2, round 1).

A museum-matte take: the item floats inside a flat rarity-coloured perimeter
frame — no bevels, gloss, or ornament — with name + price seated on a proper
inset background chip rather than floating over the art. Authored at 2x
(324x200) and smoothscaled to the live 162x100 so the flat frame edge stays
crisp. Review-only; not wired into the live store.
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

# ── legendary rarity palette (frame colour, hairline, price) ──────────────────
GEM = (255, 202, 104)
GLOW = (255, 168, 58)
ART_FIELD = (8, 8, 14)
CHIP_BG = (14, 12, 20)
WHITE = (245, 245, 248)

# Author at 2x: every device-px number below is the 2x figure so the flat frame
# edge survives the single smoothscale to the live 162x100 card.
CW, CH = 324, 200
FRAME = 10                       # 5 px logical border on every side
CORNER = 16


def _rounded(surf, radius):
    """Clip a rectangular surface to rounded corners without touching interior
    pixels — the frame corners soften along with the card."""
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), surf.get_rect(),
                     border_radius=radius)
    out = surf.copy()
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return out


def build_matte_frame(sid):
    canvas = pygame.Surface((CW, CH), pygame.SRCALPHA)

    # 1) flat rarity frame = the whole canvas painted GEM; the art field is
    #    then knocked out over it, leaving a clean uniform perimeter ring.
    canvas.fill((*GEM, 255))

    # 2) dark art field inset inside the frame
    art = pygame.Rect(FRAME, FRAME, CW - 2 * FRAME, CH - 2 * FRAME)  # 304x180
    pygame.draw.rect(canvas, ART_FIELD, art)

    # info chip lives at the bottom of the art field
    chip_h = 44
    chip_top = art.bottom - chip_h                                    # y=146
    art_zone = pygame.Rect(art.x, art.y, art.w, chip_top - art.y)     # 304x136

    # 3) item art scaled to fit the art zone above the chip, centred
    icon = parrot.get_skin_icon(sid) or parrot.get_skin_frame_hi(sid)
    bb = icon.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        icon = icon.subsurface(bb).copy()
    iw, ih = icon.get_size()
    pad = 8                                                           # breathing room
    s = min((art_zone.w - pad * 2) / iw, (art_zone.h - pad * 2) / ih)
    icon = pygame.transform.smoothscale(
        icon, (max(1, int(iw * s)), max(1, int(ih * s))))
    canvas.blit(icon, icon.get_rect(center=art_zone.center))

    # 4) hairline: a single rarity line separating art from the chip
    pygame.draw.rect(canvas, GEM, (art.x, chip_top, art.w, 2))

    # 5) chip background — slightly lifted off the art-field black
    pygame.draw.rect(canvas, CHIP_BG,
                     (art.x, chip_top + 2, art.w, chip_h - 2))

    chip_cy = chip_top + chip_h // 2

    # 6) name — white bold, left-aligned inside the chip
    fname = _font(20, True)
    nimg = fname.render("KITSUNE", True, WHITE)
    canvas.blit(nimg, nimg.get_rect(midleft=(art.x + 10, chip_cy)))

    # 7) price — rarity gold, right-aligned, led by a small filled coin
    fprice = _font(20, True)
    pimg = fprice.render("3,500", True, GEM)
    pr = pimg.get_rect(midright=(art.right - 2, chip_cy))
    canvas.blit(pimg, pr)
    coin_r = 6
    coin_cx = pr.left - 8 - coin_r
    pygame.draw.circle(canvas, GEM, (coin_cx, chip_cy), coin_r)
    pygame.draw.circle(canvas, CHIP_BG, (coin_cx, chip_cy), coin_r - 2)

    return _rounded(canvas, CORNER)


def _panel(label, card, font):
    """A labelled column: caption above a card surface."""
    cap = font.render(label, True, (210, 210, 220))
    return cap, card


def main():
    sid = "skin_kitsune"

    big = build_matte_frame(sid)                       # 324x200 (2x master)
    card_1x = pygame.transform.smoothscale(big, (162, 100))

    before = store_cards.render_card(sid, equipped=False, owned=True)

    # display scales so each column reads at a comfortable review size
    before_disp = pygame.transform.scale(before, (324, 200))
    matte_disp = pygame.transform.scale(card_1x, (324, 200))
    zoom_disp = pygame.transform.scale(card_1x, (486, 300))            # 3x

    cap_font = _font(20, True)
    panels = [
        ("BEFORE (live)", before_disp),
        ("MATTE-FRAME", matte_disp),
        ("3x ZOOM", zoom_disp),
    ]

    pad = 28
    cap_h = 34
    col_w = [p[1].get_width() for p in panels]
    col_h = [p[1].get_height() for p in panels]
    sheet_w = sum(col_w) + pad * (len(panels) + 1)
    sheet_h = pad * 2 + cap_h + max(col_h)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))

    x = pad
    for label, img in panels:
        cap = cap_font.render(label, True, (214, 214, 226))
        sheet.blit(cap, (x, pad))
        sheet.blit(img, (x, pad + cap_h))
        x += img.get_width() + pad

    out = "/home/user/skybit/docs/item_card_redesign_v2/matte-frame/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
