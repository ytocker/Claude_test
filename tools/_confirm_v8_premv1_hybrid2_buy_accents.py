"""BUY accent ornaments /design run — Figure F, 5 concepts.

The buttons stay twins; BUY alone gains a jewel-scale accent in the
constellation-web's language, placed only in the free zones (never under
the label). Each panel shows the full popup at 1× with a 2× close-up of
the button band beneath it.

Usage: python _confirm_v8_premv1_hybrid2_buy_accents.py <round>
round 1 → colorways/buy_accents_r1.png
round 2 → colorways/buy_accents_showcase_v1.png
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_colorway as cw
import _confirm_v8_premv1_hybrid2_frames as fr
import _confirm_v8_premv1_hybrid2_outline_compare as oc
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import CHIP_CY, _chip_cy_zone
import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import m
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
BG_DEEP_A, BG_GLINT_A = 155, 138   # V2.5 locked
FS, RIM_W = 15, 4.0                # locked button text/border

GLINT = oc.GOLD["glint"]
BRIGHT = oc.GOLD["bright"]


def _star4(ov, x, y, r, col):
    pts = [(x, y - r), (x + r * 0.32, y - r * 0.32), (x + r, y),
           (x + r * 0.32, y + r * 0.32), (x, y + r), (x - r * 0.32, y + r * 0.32),
           (x - r, y), (x - r * 0.32, y - r * 0.32)]
    pygame.draw.polygon(ov, col, pts)


def _sparkle(ov, x, y, r, col):
    pygame.draw.line(ov, col, (x - r, y), (x + r, y), max(1, m(1)))
    pygame.draw.line(ov, col, (x, y - r), (x, y + r), max(1, m(1)))


# accent fns receive the BUY rect (device px) and the label half-width
def acc_star_corners(ov, r, half_tw):
    inset = m(9)
    for cx, cy in ((r.left + inset, r.top + inset),
                   (r.right - inset, r.top + inset),
                   (r.left + inset, r.bottom - inset),
                   (r.right - inset, r.bottom - inset)):
        _star4(ov, cx, cy, m(3.2), (*BRIGHT, 215))


def acc_sparkle_flanks(ov, r, half_tw):
    gap = m(7)
    for x in (r.centerx - half_tw - gap, r.centerx + half_tw + gap):
        _sparkle(ov, x, r.centery, m(3.2), (*BRIGHT, 195))
        pygame.draw.circle(ov, (*GLINT, 170), (x, r.centery), m(1.1))


def acc_constellation_underline(ov, r, half_tw):
    y = r.bottom - m(8)
    xs = [r.centerx - m(16), r.centerx, r.centerx + m(16)]
    for a, b in zip(xs, xs[1:]):
        pygame.draw.line(ov, (*GLINT, 150), (a, y), (b, y), max(1, m(1)))
    for i, x in enumerate(xs):
        if i == 1:
            _star4(ov, x, y, m(2.6), (*BRIGHT, 200))
        else:
            pygame.draw.circle(ov, (*GLINT, 185), (x, y), m(1.4))


def acc_corner_filigree(ov, r, half_tw):
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        cx = r.left + m(7) if sx > 0 else r.right - m(7)
        cy = r.top + m(7) if sy > 0 else r.bottom - m(7)
        rect = pygame.Rect(0, 0, m(16), m(16))
        rect.center = (cx + sx * m(4), cy + sy * m(4))
        start = {(1, 1): 90, (-1, 1): 0, (1, -1): 180, (-1, -1): 270}[(sx, sy)]
        pygame.draw.arc(ov, (*GLINT, 175), rect,
                        math.radians(start), math.radians(start + 90),
                        max(1, m(1.2)))
        pygame.draw.circle(ov, (*BRIGHT, 190), (cx, cy), m(1.2))


def acc_orbit_ticks(ov, r, half_tw):
    tick = m(4)
    for x, y, dx, dy in ((r.centerx, r.top + m(6), 0, 1),
                         (r.centerx, r.bottom - m(6), 0, -1),
                         (r.left + m(6), r.centery, 1, 0),
                         (r.right - m(6), r.centery, -1, 0)):
        pygame.draw.line(ov, (*GLINT, 175), (x, y),
                         (x + dx * tick, y + dy * tick), max(1, m(1.2)))
    inset = m(8)
    for cx, cy in ((r.left + inset, r.top + inset),
                   (r.right - inset, r.top + inset),
                   (r.left + inset, r.bottom - inset),
                   (r.right - inset, r.bottom - inset)):
        pygame.draw.circle(ov, (*BRIGHT, 185), (cx, cy), m(1.2))


ACCENTS_R1 = [
    ("F1 · star-corners", acc_star_corners),
    ("F2 · sparkle-flanks", acc_sparkle_flanks),
    ("F3 · constellation-underline", acc_constellation_underline),
    ("F4 · corner-filigree", acc_corner_filigree),
    ("F5 · orbit-ticks", acc_orbit_ticks),
]
ACCENTS_R2 = list(ACCENTS_R1)


def make_buttons_accent(can_stops, buy_text, rim_d, rim_b, accent_fn):
    from game.store_cards import (vgrad_stops, bevel_rim, top_sheen,
                                  drop_shadow, plain_text, font)

    def buttons(ov):
        rad = m(12)
        for cx, lbl in ((76, "BUY"), (184, "CANCEL")):
            r = pygame.Rect(0, 0, m(99), m(42))
            r.center = (m(cx), m(360))
            drop_shadow(ov, r, rad, blur=m(3), alpha=100, dy=m(2))
            ov.blit(vgrad_stops(r.w, r.h, rad, can_stops, 255), r.topleft)
            top_sheen(ov, r, rad, m(12), peak=14)
            bevel_rim(ov, r, rad, rim_d, (*rim_b, 235), w=max(1, m(RIM_W)))
            if lbl == "BUY" and accent_fn is not None:
                half_tw = sc._glyph_base("BUY", font(FS), 0).get_width() // 2
                accent_fn(ov, r, half_tw + m(4))
            plain_text(ov, lbl, font(FS), r.center, buy_text,
                       shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))
    return buttons


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    accents = ACCENTS_R1 if round_no == 1 else ACCENTS_R2
    out_name = ("buy_accents_r1.png" if round_no == 1
                else "buy_accents_showcase_v1.png")

    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    h2._chip_cy = _chip_cy_zone
    _, silver_pal = DESIGNS[0]
    can_stops, _t, _, _ = silver_pal["can"]
    pal = oc.GOLD
    bar, buy = oc.PANEL_GOLD
    _bs, buy_text, _rd, _rb = buy
    fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = pal["deep"], pal["mid"], pal["bright"]
    fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
    h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])
    store_mod._bg_hook = hook_constellation(pal["glint"], BG_DEEP_A, BG_GLINT_A)
    store_mod._frame_hook = fr.frame_double_bevel
    h2.overlay_bullion_chip = cw.make_chip_fn(bar)
    try:
        # zoom band: button region at 2x under each popup
        ZX0, ZY0, ZX1, ZY1 = 14, 332, 246, 390
        zoom_w, zoom_h = (ZX1 - ZX0) * 2, (ZY1 - ZY0) * 2
        MARGIN, HEAD, GAP = 20, 50, 12
        cell_w = max(POP_W, zoom_w)
        strip_w = MARGIN * 2 + len(accents) * (cell_w + GAP) - GAP
        strip_h = HEAD + POP_H + 8 + zoom_h + 30
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 14),
                 f"FIGURE F · BUY accents · round_{round_no} · gold · checkpoint-4 base",
                 fill=(236, 214, 160))
        for i, (label, accent_fn) in enumerate(accents):
            h2.overlay_buttons = make_buttons_accent(
                can_stops, buy_text, pal["deep"], pal["bright"], accent_fn)
            pop = h2.render_popup("EPIC")
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (cell_w + GAP)
            strip.paste(pil, (x + (cell_w - POP_W) // 2, HEAD))
            zoom = pil.crop((ZX0, ZY0, ZX1, ZY1)).resize((zoom_w, zoom_h),
                                                         Image.LANCZOS)
            strip.paste(zoom, (x + (cell_w - zoom_w) // 2, HEAD + POP_H + 8))
            idr.text((x + cell_w // 2, HEAD + POP_H + 8 + zoom_h + 6), label,
                     fill=(170, 170, 195), anchor="mt")
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           out_name)
        strip.save(out)
        print("saved", out, strip.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        for attr in ("_bg_hook", "_frame_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


if __name__ == "__main__":
    main()
