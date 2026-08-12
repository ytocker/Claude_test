"""BUY accent ornaments run 3 — Figure H: the crown direction, made fancy.

G3's border-crown was approved but "needs more fancy". These five push it
to regalia grade: taller crown constructions, gem clusters, pearl strings,
cascading side curls, and compositions that pair the crown with the other
proven motifs (scrolls, vines, bezels). Same hard rules as run 2: layered
three-pass engraving, constructed curves only, micro-gem terminals, label
box untouched, CANCEL plain.

Usage: python _confirm_v8_premv1_hybrid2_buy_accents3.py <round>
round 1 → colorways/buy_accents3_r1.png
round 2 → colorways/buy_accents3_showcase_v1.png
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
from _confirm_v8_premv1_hybrid2_buy_accents2 import (engraved, spiral, s_curve,
                                                     _micro_gem,
                                                     acc_feather_scrolls,
                                                     acc_engraved_vine,
                                                     acc_gem_flank_bezels,
                                                     GLINT, BRIGHT, SHADOW,
                                                     GEM, GEM_DEEP)
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


def _pearl_string(ov, x0, x1, y, n=9):
    for k in range(n):
        t = k / (n - 1)
        px = x0 + (x1 - x0) * t
        pygame.draw.circle(ov, (*SHADOW, 200), (int(px + m(0.5)), int(y + m(0.5))), m(1.2))
        pygame.draw.circle(ov, (*BRIGHT, 220), (int(px), int(y)), m(0.9))


def _crown(ov, cx, ty, w_half, h, n_points=3, gems=True):
    """Graduated multi-point crown straddling a horizontal border line."""
    xs = [cx + w_half * (2 * k / (n_points - 1) - 1) for k in range(n_points)]
    heights = [h * (0.68 if k in (0, n_points - 1) else 1.0) for k in range(n_points)]
    # band base
    engraved(ov, [(cx - w_half - m(3), ty), (cx + w_half + m(3), ty)], w=1.7)
    # points as joined chevrons with concave sides (two-segment curves)
    prev = (cx - w_half - m(3), ty)
    for x, hh in zip(xs, heights):
        up = [(prev[0] + (x - prev[0]) * 0.5, ty - hh * 0.28), (x, ty - hh)]
        engraved(ov, [prev, *up], w=1.6)
        engraved(ov, [(x, ty - hh),
                      (x + (m(3) if x < cx + w_half else m(3)), ty - hh * 0.28),
                      (min(x + w_half, cx + w_half + m(3)), ty)], w=1.6)
        prev = (min(x + w_half, cx + w_half + m(3)), ty)
        if gems:
            _micro_gem(ov, x, ty - hh - m(0.8), r=1.9 if hh < h else 2.4)


# ── H1 · imperial crown ───────────────────────────────────────────────────────
def acc_imperial_crown(ov, r, half_tw):
    cx, ty = r.centerx, r.top + m(2)
    _crown(ov, cx, ty, m(13), m(9), n_points=3)
    # pearl string along the band beneath the crown
    _pearl_string(ov, cx - m(12), cx + m(12), ty + m(2.4), n=7)
    # cascading double side curls
    for sidex in (-1, 1):
        for k, (rad, dy) in enumerate(((m(5.4), m(1)), (m(3.6), m(4)))):
            curl = spiral(cx + sidex * (m(17) + k * m(7)), ty + dy, rad,
                          turns=1.4, mirror=sidex, phase=math.pi)
            engraved(ov, curl, w=1.4 - k * 0.2, body_a=225 - k * 20)
        _micro_gem(ov, cx + sidex * m(24), ty + m(3), r=1.4)
    # pendant drop with hanging gem on the bottom border
    by = r.bottom - m(2)
    engraved(ov, [(cx - m(7), by), (cx, by + m(4.6)), (cx + m(7), by)], w=1.5)
    engraved(ov, [(cx, by + m(4.6)), (cx, by + m(6.6))], w=1.2, body_a=210)
    _micro_gem(ov, cx, by + m(8), r=1.8)


# ── H2 · crown and scrolls ────────────────────────────────────────────────────
def acc_crown_and_scrolls(ov, r, half_tw):
    cx, ty = r.centerx, r.top + m(2)
    _crown(ov, cx, ty, m(11), m(8), n_points=3)
    acc_feather_scrolls(ov, r, half_tw)
    by = r.bottom - m(2)
    engraved(ov, [(cx - m(6), by), (cx, by + m(4)), (cx + m(6), by)], w=1.4)
    _micro_gem(ov, cx, by + m(1.4), r=1.5)


# ── H3 · tiara arc ────────────────────────────────────────────────────────────
def acc_tiara_arc(ov, r, half_tw):
    cx, ty = r.centerx, r.top + m(2)
    span = m(30)
    # graduated 5-point tiara: heights follow an arc
    xs = [cx + span * (2 * k / 4 - 1) for k in range(5)]
    hs = [m(4.2), m(6.6), m(9), m(6.6), m(4.2)]
    engraved(ov, [(cx - span - m(3), ty), (cx + span + m(3), ty)], w=1.7)
    prev = (cx - span - m(3), ty)
    for x, hh in zip(xs, hs):
        engraved(ov, [prev, (x - m(2.4), ty - hh * 0.3), (x, ty - hh)], w=1.5)
        nxt = (min(x + span / 2, cx + span + m(3)), ty)
        engraved(ov, [(x, ty - hh), (x + m(2.4), ty - hh * 0.3), nxt], w=1.5)
        prev = nxt
        _micro_gem(ov, x, ty - hh - m(0.6), r=1.7 if hh < m(9) else 2.6)
    # engraved arcs linking the tiara feet down the side borders
    for sidex in (-1, 1):
        arc = []
        for k in range(12):
            t = k / 11
            arc.append((cx + sidex * (span + m(3) + m(6) * math.sin(t * math.pi / 2)),
                        ty + m(12) * t))
        engraved(ov, arc, w=1.3, body_a=210, hi_a=120)
        _micro_gem(ov, arc[-1][0], arc[-1][1] + m(1.4), r=1.3)


# ── H4 · baroque cartouche ────────────────────────────────────────────────────
def acc_baroque_cartouche(ov, r, half_tw):
    cx, ty = r.centerx, r.top + m(2)
    _crown(ov, cx, ty, m(11), m(8.4), n_points=3)
    # inner rails along top/bottom with S-scroll segments
    for y, ph in ((r.top + m(8), 0.0), (r.bottom - m(8), math.pi)):
        pts = s_curve(r.left + m(13), r.right - m(13), y, m(1.9),
                      waves=2.0, phase=ph)
        engraved(ov, pts, w=1.2, body_a=205, hi_a=110)
    # corner acanthus curls
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        ax = r.left + m(9) if sx > 0 else r.right - m(9)
        ay = r.top + m(9) if sy > 0 else r.bottom - m(9)
        sp = spiral(ax, ay, m(5.6), turns=1.5,
                    phase=math.atan2(sy, sx) + math.pi, mirror=sx * sy)
        engraved(ov, sp, w=1.3, body_a=215, hi_a=125)
        _micro_gem(ov, *sp[-1], r=1.3)
    # bottom pendant
    by = r.bottom - m(2)
    engraved(ov, [(cx - m(6), by), (cx, by + m(4.4)), (cx + m(6), by)], w=1.4)
    _micro_gem(ov, cx, by + m(1.4), r=1.6)


# ── H5 · jewel regalia ────────────────────────────────────────────────────────
def acc_jewel_regalia(ov, r, half_tw):
    cx, ty = r.centerx, r.top + m(2)
    _crown(ov, cx, ty, m(12), m(8.6), n_points=3)
    _pearl_string(ov, cx - m(11), cx + m(11), ty + m(2.4), n=7)
    acc_gem_flank_bezels(ov, r, half_tw)
    # vine underline beneath the label
    y = r.bottom - m(7)
    pts = s_curve(cx - m(20), cx + m(20), y, m(1.8), waves=1.5)
    engraved(ov, pts, w=1.2, body_a=210, hi_a=120)
    _micro_gem(ov, cx, y, r=1.5)


ACCENTS3_R1 = [
    ("H1 · imperial-crown", acc_imperial_crown),
    ("H2 · crown-and-scrolls", acc_crown_and_scrolls),
    ("H3 · tiara-arc", acc_tiara_arc),
    ("H4 · baroque-cartouche", acc_baroque_cartouche),
    ("H5 · jewel-regalia", acc_jewel_regalia),
]
ACCENTS3_R2 = list(ACCENTS3_R1)


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    accents = ACCENTS3_R1 if round_no == 1 else ACCENTS3_R2
    out_name = ("buy_accents3_r1.png" if round_no == 1
                else "buy_accents3_showcase_v1.png")

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
                 f"FIGURE H · BUY crown regalia · round_{round_no} · gold · checkpoint-4",
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
