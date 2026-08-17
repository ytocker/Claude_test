"""State coverage figure for the active (gilded) store design.

Rendered entirely through the REAL game code with STORE_DESIGN="gilded":
top row — the confirm popup in its two states (affordable, can't-afford);
bottom row — the item card in every state (priced affordable, priced
can't-afford, owned EQUIP, EQUIPPED, secret ???). Proves the design
applies to the popup and the card across all their states.

Output: colorways/gilded_states_v1.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.config as config
config.STORE_DESIGN = "gilded"

import pygame
pygame.init()
pygame.display.set_mode((8, 8))

import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import m
from PIL import Image, ImageDraw, ImageFont

SID = "skin_mummy"
SECRET_SID = next((s for s in store_catalog.CATALOG
                   if store_catalog.is_secret(s)), SID)
store_catalog.cost = lambda sid: 1100


class _Stub:
    _confirm = SID
    _confirm_panel = None
    confirm_yes_rect = None
    confirm_no_rect = None

    @staticmethod
    def _disp_name(_sid):
        return "MUMMY"


def render_pop(balance):
    store_data.balance = lambda: balance
    surf = pygame.Surface((360, 640))
    surf.fill((8, 8, 20))
    store_mod.StoreScene._draw_confirm(_Stub(), surf)
    return surf.subsurface(pygame.Rect(50, 40, 260, 442)).copy()


def render_card(sid, equipped, secret, owned, balance):
    store_data.balance = lambda: balance
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS),
                         pygame.SRCALPHA)
    rect = pygame.Rect(m(sc._INSET), m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * m(sc._INSET),
                       sc.CARD_H * sc.SS - 2 * m(sc._INSET))
    sc.draw_card(big, sid, rect, equipped, secret, owned=owned)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def main():
    pops = [("AFFORDABLE", render_pop(99999)),
            ("CAN'T AFFORD", render_pop(50))]
    cards = [
        ("PRICED · AFFORDABLE", render_card(SID, False, False, False, 99999)),
        ("PRICED · CAN'T AFFORD", render_card(SID, False, False, False, 50)),
        ("OWNED · EQUIP", render_card(SID, False, False, True, 99999)),
        ("EQUIPPED", render_card(SID, True, False, False, 99999)),
        ("SECRET", render_card(SECRET_SID, False, True, False, 99999)),
    ]

    f_head = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    f_lab = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    MARGIN, HEAD, GAP = 24, 64, 24
    pop_w, pop_h = 260 * 2, 442 * 2
    card_w, card_h = sc.CARD_W * 2, sc.CARD_H * 2
    strip_w = max(MARGIN * 2 + 2 * pop_w + GAP,
                  MARGIN * 2 + len(cards) * (card_w + GAP) - GAP)
    strip_h = HEAD + pop_h + 46 + 40 + card_h + 46 + 20
    strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
    idr = ImageDraw.Draw(strip)
    idr.text((MARGIN, 16),
             "gilded design · popup and card states · real game render · 2x",
             fill=(236, 214, 160), font=f_head)
    px0 = (strip_w - (2 * pop_w + GAP)) // 2
    for i, (lab, pop) in enumerate(pops):
        x = px0 + i * (pop_w + GAP)
        pp = Image.frombytes("RGB", pop.get_size(),
                             pygame.image.tostring(pop, "RGB"))
        strip.paste(pp.resize((pop_w, pop_h), Image.LANCZOS), (x, HEAD))
        idr.text((x + pop_w // 2, HEAD + pop_h + 10), lab,
                 fill=(222, 208, 170), anchor="mt", font=f_lab)
    cy0 = HEAD + pop_h + 46 + 40
    cx0 = (strip_w - (len(cards) * (card_w + GAP) - GAP)) // 2
    for i, (lab, card) in enumerate(cards):
        x = cx0 + i * (card_w + GAP)
        cc = Image.frombytes("RGBA", card.get_size(),
                             pygame.image.tostring(card, "RGBA"))
        cbg = Image.new("RGBA", (card_w, card_h), (10, 9, 20, 255))
        cbg.alpha_composite(cc.resize((card_w, card_h), Image.LANCZOS))
        strip.paste(cbg.convert("RGB"), (x, cy0))
        idr.text((x + card_w // 2, cy0 + card_h + 10), lab,
                 fill=(222, 208, 170), anchor="mt", font=f_lab)
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "confirm_purchase_v8", "premium-v1",
                       "colorways", "gilded_states_v1.png")
    strip.save(out)
    print("saved", out, strip.size)


if __name__ == "__main__":
    main()
