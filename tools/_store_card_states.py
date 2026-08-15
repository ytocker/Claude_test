"""Reference figure: the item card in every state the store can show.

One real item (MUMMY, epic) drawn through the live draw_card branches:
for-sale affordable, can't-afford, owned, equipped, and the secret/mystery
mask. Cards at 4x for close reading, labels beneath.

Output: docs/confirm_purchase_v8/premium-v1/colorways/card_states_v1.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc
import game.store_data as store_data
from game.store_cards import m
from PIL import Image, ImageDraw, ImageFont

SID = "skin_mummy"


def render(equipped, secret, owned, balance):
    store_data.balance = lambda: balance
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(sc._INSET), m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * m(sc._INSET),
                       sc.CARD_H * sc.SS - 2 * m(sc._INSET))
    sc.draw_card(big, SID, rect, equipped, secret, owned=owned)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# (label, equipped, secret, owned, balance)
STATES = [
    ("FOR SALE · affordable", False, False, False, 99999),
    ("FOR SALE · can't afford", False, False, False, 0),
    ("OWNED · not equipped", False, False, True, 99999),
    ("EQUIPPED", True, False, True, 99999),
    ("SECRET · not owned", False, True, False, 99999),
]


def main():
    _orig_bal = store_data.balance
    try:
        cards = [(label, render(e, s, o, b)) for label, e, s, o, b in STATES]

        f_head = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        f_role = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        K = 4
        cw_, ch_ = sc.CARD_W * K, sc.CARD_H * K
        MARGIN, HEAD, GAP = 24, 64, 24
        strip_w = MARGIN * 2 + len(cards) * (cw_ + GAP) - GAP
        strip_h = HEAD + ch_ + 56
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 16),
                 "item card states · live draw_card · MUMMY (epic) · 4x",
                 fill=(236, 214, 160), font=f_head)
        for i, (label, card) in enumerate(cards):
            cc = Image.frombytes("RGBA", (sc.CARD_W, sc.CARD_H),
                                 pygame.image.tostring(card, "RGBA"))
            bg = Image.new("RGBA", (cw_, ch_), (10, 9, 20, 255))
            bg.alpha_composite(cc.resize((cw_, ch_), Image.LANCZOS))
            x = MARGIN + i * (cw_ + GAP)
            strip.paste(bg.convert("RGB"), (x, HEAD))
            idr.text((x + cw_ // 2, HEAD + ch_ + 14), label,
                     fill=(206, 190, 150), anchor="mt", font=f_role)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "card_states_v1.png")
        strip.save(out)
        print("saved", out, strip.size)
    finally:
        store_data.balance = _orig_bal


if __name__ == "__main__":
    main()
