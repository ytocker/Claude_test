"""BUY accent ornaments run 4 — Figure I: one elegant gesture.

Run 3 (Figure H) read scattered because each concept stacked several
independent motifs around the button. Rule for this run, drawn from
luxury-ornament references: each concept is ONE unified, bilaterally
symmetric gesture, physically attached to the button's existing geometry
(border, label baseline, or corners) — a swash extends structure, it never
floats. Engraving craftsmanship from run 2 stays (three-pass strokes,
constructed curves); at most a single micro-gem, only on the axis of
symmetry. Presence aims subtle: ornament peaks well below the label's.

Usage: python _confirm_v8_premv1_hybrid2_buy_accents4.py <round>
round 1 → colorways/buy_accents4_r1.png
round 2 → colorways/buy_accents4_showcase_v1.png
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
from _confirm_v8_premv1_hybrid2_buy_accents import make_buttons_accent
from _confirm_v8_premv1_hybrid2_buy_accents2 import (engraved, spiral,
                                                     _micro_gem, GLINT,
                                                     BRIGHT, SHADOW)
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import CHIP_CY, _chip_cy_zone
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import m
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
BG_DEEP_A, BG_GLINT_A = 155, 138


def bezier(p0, p1, p2, p3, n=24):
    pts = []
    for k in range(n + 1):
        t = k / n
        u = 1 - t
        pts.append((u * u * u * p0[0] + 3 * u * u * t * p1[0]
                    + 3 * u * t * t * p2[0] + t * t * t * p3[0],
                    u * u * u * p0[1] + 3 * u * u * t * p1[1]
                    + 3 * u * t * t * p2[1] + t * t * t * p3[1]))
    return pts


def tapered(ov, pts, w0, w1, body_a=200, hi_a=115):
    """Engraved stroke whose weight thins from w0 to w1 along its length."""
    thirds = max(1, len(pts) // 3)
    for i in range(3):
        seg = pts[i * thirds:(i + 1) * thirds + 1]
        if len(seg) < 2:
            continue
        t = i / 2
        w = w0 + (w1 - w0) * t
        engraved(ov, seg, w=w, body_a=int(body_a * (1 - 0.18 * t)),
                 hi_a=int(hi_a * (1 - 0.25 * t)))


# ── I1 · swash underline: one calligraphic divider under the label ────────────
def acc_swash_underline(ov, r, half_tw):
    y0 = r.centery + m(13)
    for side in (-1, 1):
        run = [(r.centerx + side * m(1.5), y0),
               (r.centerx + side * m(10), y0 + m(0.5)),
               (r.centerx + side * m(20), y0 - m(0.5))]
        curl = spiral(r.centerx + side * m(26), y0 - m(2.2), m(2.8),
                      turns=1.15, phase=math.pi / 2, mirror=-side, n=20)
        tapered(ov, run + curl, 1.5, 0.9, body_a=205, hi_a=120)
    _micro_gem(ov, r.centerx, y0, r=1.4)


# ── I2 · deco fans: stepped chamfer lines in the top corners ──────────────────
def acc_deco_fans(ov, r, half_tw):
    for side in (-1, 1):
        cx = r.left if side < 0 else r.right
        for off, w, ba in ((m(7), 1.5, 205),
                           (m(11.5), 1.2, 175),
                           (m(16), 1.0, 145)):
            a = (cx - side * off, r.top + m(3))
            b = (cx - side * m(3), r.top + off)
            engraved(ov, [a, b], w=w, body_a=ba, hi_a=int(ba * 0.55))


# ── I3 · label swashes: mirrored strokes flowing out of the label flanks ──────
def acc_label_swashes(ov, r, half_tw):
    for side in (-1, 1):
        x0 = r.centerx + side * (half_tw + m(1))
        x1 = r.left + m(5) if side < 0 else r.right - m(5)
        pts = bezier((x0, r.centery + m(3)),
                     (x0 + side * m(7), r.centery + m(7)),
                     (x1 - side * m(9), r.centery - m(3)),
                     (x1, r.centery + m(1)), n=26)
        tapered(ov, pts, 1.7, 0.8, body_a=205, hi_a=125)


# ── I4 · centre finial: one small crest on the top border ─────────────────────
def acc_centre_finial(ov, r, half_tw):
    cx, ty = r.centerx, r.top + m(2)
    for side in (-1, 1):
        lead = [(cx + side * m(4), ty + m(0.4)),
                (cx + side * m(7), ty + m(0.2))]
        curl = spiral(cx + side * m(10.5), ty + m(0.6), m(3.2),
                      turns=1.1, phase=-math.pi / 2, mirror=side, n=20)
        tapered(ov, lead + curl, 1.4, 0.9, body_a=205, hi_a=120)
    engraved(ov, [(cx - m(4), ty), (cx, ty - m(5)), (cx + m(4), ty)],
             w=1.5, body_a=225, hi_a=140)
    engraved(ov, [(cx - m(2.1), ty), (cx, ty - m(2.6)), (cx + m(2.1), ty)],
             w=1.0, body_a=175, hi_a=95)
    _micro_gem(ov, cx, ty - m(0.8), r=1.4)


# ── I5 · inner keyline: hairline jeweller's mat inside the border ─────────────
def make_inner_keyline(glint, bright, shadow):
    def accent(ov, r, half_tw):
        kr = r.inflate(-m(13), -m(13))
        rad = m(7)
        pygame.draw.rect(ov, (*shadow, 175),
                         kr.move(m(0.7), m(0.7)), max(1, m(0.9)), border_radius=rad)
        pygame.draw.rect(ov, (*glint, 185), kr, max(1, m(0.9)), border_radius=rad)
        pygame.draw.rect(ov, (*bright, 85),
                         kr.move(-m(0.5), -m(0.5)), max(1, m(0.5)), border_radius=rad)
    return accent


acc_inner_keyline = make_inner_keyline(GLINT, BRIGHT, SHADOW)


ACCENTS4_R1 = [
    ("I1 · swash-underline", acc_swash_underline),
    ("I2 · deco-fans", acc_deco_fans),
    ("I3 · label-swashes", acc_label_swashes),
    ("I4 · centre-finial", acc_centre_finial),
    ("I5 · inner-keyline", acc_inner_keyline),
]
ACCENTS4_R2 = list(ACCENTS4_R1)


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    accents = ACCENTS4_R1 if round_no == 1 else ACCENTS4_R2
    out_name = ("buy_accents4_r1.png" if round_no == 1
                else "buy_accents4_showcase_v1.png")

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
        ZX0, ZY0, ZX1, ZY1 = 14, 322, 246, 396
        zoom_w, zoom_h = (ZX1 - ZX0) * 2, (ZY1 - ZY0) * 2
        MARGIN, HEAD, GAP = 20, 50, 12
        cell_w = max(POP_W, zoom_w)
        strip_w = MARGIN * 2 + len(accents) * (cell_w + GAP) - GAP
        strip_h = HEAD + POP_H + 8 + zoom_h + 30
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 14),
                 f"FIGURE I · BUY single-gesture accents · round_{round_no} · gold · checkpoint-4",
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
