"""hybrid-2 BUY/CANCEL size options — sovereign style at growing sizes.

The shelf runs y=335..426 with the rarity banner parked at cy=402, so the
button band can grow to ~46px tall (y 337..383) before it hits the banner.
The base draw's own buttons (and chip) are suppressed via exec-patch so every
variant paints on clean shelf. The price bar everywhere is the locked
S2-clean recipe: G2 bullion · 34px · linear sheen, no gloss ellipse.

  B1 · current 99×31 (reference)
  B2 · taller 99×42
  B3 · larger 106×46
  B4 · BUY-dominant 134×46 + CANCEL 78×46
  B5 · stacked full-width BUY 204×34 + slim CANCEL 204×18
"""
import os
import sys
import re
import inspect
import textwrap

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.store_cards import (m, font, vgrad_stops, bevel_rim, top_sheen,
                              drop_shadow, coin_glyph, plain_text,
                              chip_body_stops, _glyph_base, _stamp_bold,
                              CARD_RING_BRIGHT, CARD_RING_DEEP,
                              GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_NUM)
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
BAR_H = 34

G2 = [
    (0.00, (255, 232, 140)),
    (0.32, (244, 208, 92)),
    (0.66, (216, 172, 52)),
    (1.00, (166, 124, 30)),
]

# (label, [(cx, cy, w, h, is_cancel, font_px), ...])
VARIANTS = [
    ("B1 · current 99x31", [
        (76, 360, 99, 31, False, 14), (184, 360, 99, 31, True, 13)]),
    ("B2 · taller 99x42", [
        (76, 360, 99, 42, False, 16), (184, 360, 99, 42, True, 14)]),
    ("B3 · larger 106x46", [
        (73, 360, 106, 46, False, 16), (187, 360, 106, 46, True, 14)]),
    ("B4 · BUY-dominant", [
        (87, 360, 134, 46, False, 17), (201, 360, 78, 46, True, 13)]),
    ("B5 · stacked full-width", [
        (130, 354, 204, 34, False, 16), (130, 381, 204, 18, True, 11)]),
]


def _patched_draw():
    src = textwrap.dedent(inspect.getsource(StoreScene._draw_confirm))
    src, n1 = re.subn(r"_chip\(m\(CX\), m\(CHIP_CY\)\)", "pass", src)
    src, n2 = re.subn(r'_btn\(buy_r, "BUY", locked=not affordable\)', "pass", src)
    src, n3 = re.subn(r'_btn\(can_r, "CANCEL", is_cancel=True\)', "pass", src)
    assert (n1, n2, n3) == (1, 1, 1), f"patch failed: {n1},{n2},{n3}"
    ns = {}
    exec(compile(src, "<btn_options_draw>", "exec"), store_mod.__dict__, ns)
    return ns["_draw_confirm"]


def final_chip(ov, price, cy=h2.CHIP_CY):
    txt = f"{price:,}"
    r = pygame.Rect(0, 0, m(168), m(BAR_H))
    r.center = (m(h2.CX), m(cy))
    chip_body_stops(ov, r, m(11), G2, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT,
                    gloss=0)
    top_sheen(ov, r, m(11), m(12), peak=64)
    num_font = font(18)
    base = _stamp_bold(_glyph_base(txt, num_font, 0), m(0.7))
    bw = base.get_width()
    coin_d, gap = m(22), m(5)
    left = m(h2.CX) - (coin_d + gap + bw) // 2
    coin_glyph(ov, left + coin_d // 2, m(cy), m(11))
    plain_text(ov, txt, num_font,
               (left + coin_d + gap + bw // 2, m(cy)), GOLD_A_NUM,
               shadow_a=0, weight=m(0.7))
    for bx in (r.left + m(13), r.right - m(13)):
        h2._bolt_dot(ov, bx, m(cy))


def make_buttons_fn(layout):
    def buttons(ov):
        for cx, cy, w, h, is_cancel, fpx in layout:
            rad = m(min(12, h // 2 - 2)) if h < 26 else m(12)
            r = pygame.Rect(0, 0, m(w), m(h))
            r.center = (m(cx), m(cy))
            if is_cancel:
                stops = [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))]
                lab_c, pk, rw = (150, 155, 200), 14, m(2.2)
                rim_d, rim_b = CARD_RING_DEEP, CARD_RING_BRIGHT
                lbl = "CANCEL"
            else:
                stops = [(0.0, (120, 75, 18)), (1.0, (80, 45, 8))]
                lab_c, pk, rw = (255, 248, 220), 28, m(2.0)
                rim_d, rim_b = GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT
                lbl = "BUY"
            drop_shadow(ov, r, rad, blur=m(3), alpha=100, dy=m(2))
            ov.blit(vgrad_stops(r.w, r.h, rad, stops, 255), r.topleft)
            top_sheen(ov, r, rad, m(min(12, h // 2)), peak=pk)
            bevel_rim(ov, r, rad, rim_d, (*rim_b, 235), w=max(1, rw))
            plain_text(ov, lbl, font(fpx), r.center, lab_c,
                       shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))
    return buttons


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    h2._DRAW_FN[0] = _patched_draw()
    h2.overlay_bullion_chip = final_chip
    try:
        panels = []
        for label, layout in VARIANTS:
            h2.overlay_buttons = make_buttons_fn(layout)
            panels.append((label, h2.render_popup("EPIC")))

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 "hybrid-2 BUY/CANCEL size options · S2-clean bar · EPIC",
                 fill=(236, 214, 160))
        for i, (label, pop) in enumerate(panels):
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (POP_W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + POP_W // 2, HEAD + POP_H + 6), label,
                     fill=(206, 190, 150), anchor="mt")

        out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1",
                           "hybrid2_button_options.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
