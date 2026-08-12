"""BUY accent ornaments run 2 — Figure G: constructed, layered metalwork.

Run 1 (Figure F) read amateur because every element was a primitive shape.
Rule for this run: every visible stroke is LAYERED ENGRAVING — a dark
shadow pass, a gold body pass, and a bright highlight pass — and every
motif is a constructed curve (spirals, S-scroll vines, cartouches), never
a bare dot or tick. Terminals are finished with micro-gems. Ornament stays
inside the button face/border and clear of the measured label box.

Usage: python _confirm_v8_premv1_hybrid2_buy_accents2.py <round>
round 1 → colorways/buy_accents2_r1.png
round 2 → colorways/buy_accents2_showcase_v1.png
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
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import CHIP_CY, _chip_cy_zone
import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import m, facet_gem
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
BG_DEEP_A, BG_GLINT_A = 155, 138

GLINT = oc.GOLD["glint"]
BRIGHT = oc.GOLD["bright"]
SHADOW = (26, 17, 4)
GEM, GEM_DEEP = oc.GOLD["gem"], oc.GOLD["gem_deep"]


def engraved(ov, pts, w=1.7, body_a=235, hi_a=160):
    """Three-pass engraved stroke: shadow under, gold body, bright crest."""
    if len(pts) < 2:
        return
    sh = [(x + m(0.8), y + m(0.8)) for x, y in pts]
    hi = [(x - m(0.5), y - m(0.5)) for x, y in pts]
    pygame.draw.lines(ov, (*SHADOW, 210), False, sh, max(2, m(w)))
    pygame.draw.lines(ov, (*GLINT, body_a), False, pts, max(2, m(w)))
    pygame.draw.lines(ov, (*BRIGHT, hi_a), False, hi, max(1, m(w - 0.7)))


def spiral(cx, cy, r0, turns=1.9, phase=0.0, mirror=1, n=26, shrink=0.78):
    pts = []
    for k in range(n + 1):
        t = k / n
        th = phase + mirror * t * turns * 2 * math.pi
        rad = r0 * (1 - shrink * t)
        pts.append((cx + rad * math.cos(th), cy + rad * math.sin(th)))
    return pts


def s_curve(x0, x1, y, amp, waves=1.0, n=22, phase=0.0):
    pts = []
    for k in range(n + 1):
        t = k / n
        pts.append((x0 + (x1 - x0) * t,
                    y + amp * math.sin(phase + t * waves * 2 * math.pi)))
    return pts


def _micro_gem(ov, x, y, r=2.2):
    pygame.draw.circle(ov, (*SHADOW, 220), (int(x + m(0.6)), int(y + m(0.6))), m(r + 0.8))
    facet_gem(ov, int(x), int(y), m(r), GEM, GEM_DEEP)


# ── G1 · feather scrolls: curled spirals flanking the label ────────────────────
def acc_feather_scrolls(ov, r, half_tw):
    for side in (-1, 1):
        edge_x = r.centerx + side * (half_tw + m(20))
        # trailing swept line from near the text out to the curl
        tail = [(r.centerx + side * (half_tw + m(3)), r.centery + m(6)),
                (r.centerx + side * (half_tw + m(9)), r.centery + m(3)),
                (edge_x - side * m(5), r.centery - m(2))]
        engraved(ov, tail, w=1.6)
        # 2-turn curl at the end of the sweep
        curl = spiral(edge_x, r.centery - m(3), m(7), turns=1.6,
                      phase=math.pi / 2 if side > 0 else math.pi / 2,
                      mirror=side)
        engraved(ov, curl, w=1.6)
        _micro_gem(ov, *curl[-1], r=1.8)


# ── G2 · engraved vine: S-scroll bands top and bottom ─────────────────────────
def acc_engraved_vine(ov, r, half_tw):
    for y, ph in ((r.top + m(7), 0.0), (r.bottom - m(7), math.pi)):
        pts = s_curve(r.left + m(12), r.right - m(12), y, m(2.6),
                      waves=2.0, phase=ph)
        engraved(ov, pts, w=1.5, body_a=225)
        # leaf curls at the wave crests
        for t in (0.25, 0.75):
            lx = r.left + m(12) + (r.width - m(24)) * t
            ly = y + (m(2.6) if math.sin(ph + t * 4 * math.pi) < 0 else -m(2.6))
            leaf = spiral(lx, ly, m(3.4), turns=1.1, mirror=1 if t < 0.5 else -1)
            engraved(ov, leaf, w=1.2, body_a=210, hi_a=120)
    _micro_gem(ov, r.centerx, r.top + m(7), r=1.7)
    _micro_gem(ov, r.centerx, r.bottom - m(7), r=1.7)


# ── G3 · royal keystone: cartouche crown on the top border ────────────────────
def acc_royal_keystone(ov, r, half_tw):
    cx, ty = r.centerx, r.top + m(2)
    # pointed cartouche body straddling the border
    body = [(cx - m(9), ty), (cx - m(4), ty - m(5)), (cx, ty - m(6.5)),
            (cx + m(4), ty - m(5)), (cx + m(9), ty)]
    engraved(ov, body, w=1.8)
    engraved(ov, [(cx - m(9), ty), (cx + m(9), ty)], w=1.4, body_a=200)
    # side curls flowing from the cartouche into the border
    for sidex in (-1, 1):
        curl = spiral(cx + sidex * m(14), ty + m(1), m(4.6), turns=1.3,
                      mirror=sidex, phase=math.pi)
        engraved(ov, curl, w=1.3, body_a=215, hi_a=130)
    _micro_gem(ov, cx, ty - m(2.4), r=2.2)
    # mirrored small pendant on the bottom border
    by = r.bottom - m(2)
    pend = [(cx - m(6), by), (cx, by + m(4.4)), (cx + m(6), by)]
    engraved(ov, pend, w=1.5, body_a=215)
    _micro_gem(ov, cx, by + m(1.2), r=1.6)


# ── G4 · acanthus corners: 2-turn spiral scrolls in all four corners ──────────
def acc_acanthus_corners(ov, r, half_tw):
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        ax = r.left + m(11) if sx > 0 else r.right - m(11)
        ay = r.top + m(11) if sy > 0 else r.bottom - m(11)
        # spiral opens toward the button centre
        ph = math.atan2(sy, sx) + math.pi
        sp = spiral(ax, ay, m(7.4), turns=1.8, phase=ph, mirror=sx * sy)
        engraved(ov, sp, w=1.5)
        # short stem joining the scroll to the corner of the border
        stem = [(ax + sx * m(6), ay + sy * m(6)),
                (ax + sx * m(2.5), ay + sy * m(2.5))]
        engraved(ov, stem, w=1.4, body_a=210, hi_a=120)
        _micro_gem(ov, *sp[-1], r=1.5)


# ── G5 · gem flank bezels: jewelled stations set into the side borders ────────
def acc_gem_flank_bezels(ov, r, half_tw):
    for side in (-1, 1):
        bx = r.left + m(3) if side < 0 else r.right - m(3)
        by = r.centery
        # layered bezel rings
        pygame.draw.circle(ov, (*SHADOW, 220), (bx + m(0.7), by + m(0.7)), m(6.4))
        pygame.draw.circle(ov, (*GLINT, 240), (bx, by), m(6))
        pygame.draw.circle(ov, (*SHADOW, 235), (bx, by), m(4.6))
        pygame.draw.circle(ov, (*BRIGHT, 180), (bx, by), m(6), max(1, m(0.9)))
        facet_gem(ov, bx, by, m(3), GEM, GEM_DEEP)
        # rope-twist arcs merging the bezel into the border above and below
        for vy in (-1, 1):
            arc = []
            for k in range(14):
                t = k / 13
                arc.append((bx - side * m(2.2) * math.sin(t * math.pi),
                            by + vy * (m(6) + m(7) * t)))
            engraved(ov, arc, w=1.3, body_a=215, hi_a=125)
        _micro_gem(ov, bx - side * m(0.5), by - m(11.5), r=1.3)
        _micro_gem(ov, bx - side * m(0.5), by + m(11.5), r=1.3)


ACCENTS2_R1 = [
    ("G1 · feather-scrolls", acc_feather_scrolls),
    ("G2 · engraved-vine", acc_engraved_vine),
    ("G3 · royal-keystone", acc_royal_keystone),
    ("G4 · acanthus-corners", acc_acanthus_corners),
    ("G5 · gem-flank-bezels", acc_gem_flank_bezels),
]
ACCENTS2_R2 = list(ACCENTS2_R1)


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    accents = ACCENTS2_R1 if round_no == 1 else ACCENTS2_R2
    out_name = ("buy_accents2_r1.png" if round_no == 1
                else "buy_accents2_showcase_v1.png")

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
        ZX0, ZY0, ZX1, ZY1 = 14, 330, 246, 392
        zoom_w, zoom_h = (ZX1 - ZX0) * 2, (ZY1 - ZY0) * 2
        MARGIN, HEAD, GAP = 20, 50, 12
        cell_w = max(POP_W, zoom_w)
        strip_w = MARGIN * 2 + len(accents) * (cell_w + GAP) - GAP
        strip_h = HEAD + POP_H + 8 + zoom_h + 30
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 14),
                 f"FIGURE G · BUY accents run 2 · layered metalwork · round_{round_no}",
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
