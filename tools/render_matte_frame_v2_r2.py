"""Matte-frame store-card concept (item-card redesign v2, round 2).

A museum-matte take: the item floats inside a flat rarity-coloured perimeter
frame — no bevels, gloss, or ornament — with name + price seated on a proper
inset background chip rather than floating over the art. Authored at 2x
(324x200) and smoothscaled to the live 162x100 so the flat frame edge stays
crisp. Review-only; not wired into the live store.

Round-2 folds in art-director notes: a non-colour rarity cue (corner pips that
survive a colourblind filter), a coin token that reads as a coin at 1x, a
warmer separator so the three gold moments stop fusing, a shorter chip so the
art owns more of the card, and a larger name.
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

# ── legendary rarity palette (frame colour, hairline, price) ──────────────────
GEM = (255, 202, 104)
GLOW = (255, 168, 58)
DEEP = (150, 92, 22)             # shadow gold — pips + coin ring read as on-metal
COIN_RIM = (70, 44, 12)          # dark rim seats the coin against the gold price
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

    # info chip lives at the bottom of the art field. Shorter than round 1 so
    # the art owns the majority of the card height.
    chip_h = 36
    chip_top = art.bottom - chip_h                                    # y=154
    pygame.draw.rect(canvas, ART_FIELD, art)
    art_zone = pygame.Rect(art.x, art.y, art.w, chip_top - art.y)     # 304x144

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

    # 4) hairline: a single rarity line separating art from the chip. Warmer
    #    than the GEM frame + GEM price so the three gold moments don't fuse.
    pygame.draw.rect(canvas, GLOW, (art.x, chip_top, art.w, 2))

    # 5) chip background — slightly lifted off the art-field black
    pygame.draw.rect(canvas, CHIP_BG,
                     (art.x, chip_top + 2, art.w, chip_h - 2))

    chip_cy = chip_top + chip_h // 2

    # 6) name — white bold, left-aligned inside the chip. Larger than round 1;
    #    +8 from the frame edge so a long name can't clip into the price.
    fname = _font(22, True)
    nimg = fname.render("KITSUNE", True, WHITE)
    canvas.blit(nimg, nimg.get_rect(midleft=(art.x + 8, chip_cy)))

    # 7) price — rarity gold, right-aligned, led by a coin token. Bigger than
    #    round 1 with a DEEP inner ring so it reads as a coin at 1x.
    fprice = _font(20, True)
    pimg = fprice.render("3,500", True, GEM)
    pr = pimg.get_rect(midright=(art.right - 2, chip_cy))
    canvas.blit(pimg, pr)
    coin_r = 9
    coin_cx = pr.left - 8 - coin_r
    pygame.draw.circle(canvas, COIN_RIM, (coin_cx, chip_cy), coin_r)
    pygame.draw.circle(canvas, GEM, (coin_cx, chip_cy), coin_r - 1)
    pygame.draw.circle(canvas, DEEP, (coin_cx, chip_cy), coin_r - 1, 1)

    # 8) rarity pips — a non-colour tier cue seated ON the top gold band, top
    #    right, clear of the art field. Legendary = 4. DEEP so they survive a
    #    colourblind desaturation while staying on-metal.
    pip_r = 4
    pip_y = FRAME // 2
    pip_x = CW - 20                       # inset clear of the rounded corner
    for _ in range(4):
        pygame.draw.circle(canvas, DEEP, (pip_x, pip_y), pip_r)
        pip_x -= 11

    return _rounded(canvas, CORNER)


def main():
    sid = "skin_kitsune"

    # The review artifact is the 2x card master itself (324x200) so the frame,
    # pips, coin, and chip can be inspected at authoring resolution.
    big = build_matte_frame(sid)                       # 324x200 (2x master)

    out = "/home/user/skybit/docs/item_card_redesign_v2/matte-frame/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(big, out)
    print("saved", out, big.get_size())


if __name__ == "__main__":
    main()
