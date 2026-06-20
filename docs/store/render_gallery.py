"""Render docs/store/all_items.png — a single figure of every Store item.

One contact sheet of the whole cosmetic roster (DEFAULT + all catalog skins),
grouped by store tab (COSTUMES / PARROTS / ANIMALS) with each item's name and
coin cost. Re-run after adding skins:

    SDL_VIDEODRIVER=dummy python docs/store/render_gallery.py
"""
import os
import sys
import pygame

# Allow running as a bare script: put the repo root (two levels up) on the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()

from game import parrot, store_catalog          # noqa: E402
from game.hud import _font, _coin_icon, _GOLD_BRIGHT, _GOLD_PALE  # noqa: E402

COLS = 5
CELL_W, CELL_H = 196, 170
HERO = 112
PAD = 16
HEADER_H = 40
BG = (14, 10, 34)
CARD = (26, 20, 52)
CARD_RIM = (90, 78, 130)

# Group → ordered ids (DEFAULT fronts the parrots, like the live store).
SECTIONS = []
for label, g in (("COSTUMES", "costume"), ("PARROTS", "parrot"),
                 ("ANIMALS", "animal")):
    ids = sorted(store_catalog.ids_of_group(g), key=store_catalog.cost)
    if g == "parrot":
        ids = [store_catalog.BASE_SKIN] + ids
    SECTIONS.append((label, ids))


def _hero(sid, box):
    src = parrot.get_skin_frame(sid, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    s = box / max(sw, sh)
    return pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(sh * s))))


def _disp_name(sid):
    return "DEFAULT" if sid == store_catalog.BASE_SKIN else store_catalog.name(sid)


# Lay out: a title, then per section a header bar + a grid of cards.
rows_total = sum((len(ids) + COLS - 1) // COLS for _, ids in SECTIONS)
W = PAD + COLS * CELL_W + PAD
H = 64 + len(SECTIONS) * HEADER_H + rows_total * CELL_H + PAD
sheet = pygame.Surface((W, H))
sheet.fill(BG)

title = _font(30, True).render("SKYBIT STORE — ALL ITEMS", True, _GOLD_BRIGHT)
sheet.blit(title, (PAD, 18))
sub = _font(14, True).render(
    f"{len(store_catalog.skin_ids())} skins across 3 tabs  ·  procedural, equippable",
    True, _GOLD_PALE)
sheet.blit(sub, (PAD, 48))

y = 70
for label, ids in SECTIONS:
    hdr = pygame.Rect(PAD, y, COLS * CELL_W, HEADER_H - 8)
    pygame.draw.rect(sheet, (40, 30, 64), hdr, border_radius=8)
    pygame.draw.rect(sheet, CARD_RIM, hdr, width=1, border_radius=8)
    h = _font(18, True).render(f"{label}   ({len(ids)})", True, _GOLD_BRIGHT)
    sheet.blit(h, h.get_rect(midleft=(PAD + 12, hdr.centery)))
    y += HEADER_H

    for i, sid in enumerate(ids):
        col, row = i % COLS, i // COLS
        cx = PAD + col * CELL_W
        cy = y + row * CELL_H
        card = pygame.Rect(cx + 6, cy + 6, CELL_W - 12, CELL_H - 12)
        pygame.draw.rect(sheet, CARD, card, border_radius=12)
        pygame.draw.rect(sheet, CARD_RIM, card, width=1, border_radius=12)

        hero = _hero(sid, HERO)
        sheet.blit(hero, hero.get_rect(center=(card.centerx, card.y + 60)))

        nimg = _font(15, True).render(_disp_name(sid), True, _GOLD_BRIGHT)
        sheet.blit(nimg, nimg.get_rect(center=(card.centerx, card.bottom - 34)))

        if sid == store_catalog.BASE_SKIN:
            cimg = _font(13, True).render("FREE", True, _GOLD_PALE)
            sheet.blit(cimg, cimg.get_rect(center=(card.centerx, card.bottom - 14)))
        else:
            cost = str(store_catalog.cost(sid))
            cimg = _font(14, True).render(cost, True, _GOLD_PALE)
            cw = 18 + 4 + cimg.get_width()
            x0 = card.centerx - cw // 2
            _coin_icon(sheet, x0 + 9, card.bottom - 14, 9)
            sheet.blit(cimg, cimg.get_rect(midleft=(x0 + 22, card.bottom - 14)))

    y += ((len(ids) + COLS - 1) // COLS) * CELL_H

out = os.path.join(os.path.dirname(__file__), "all_items.png")
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
