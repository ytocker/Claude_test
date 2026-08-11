"""Outline comparison — gold vs silver, one figure, 2 rows × 5 frames.

Both rows share identical content: platinum bar/BUY panels (E2), charcoal
CANCEL fill, B5 web, zone-centred name, bar at cy=300. Only the OUTLINE
system differs per row — frame construction colours, web glint, hero bezel
(glass tint neutralized + crisp ring), and the CANCEL border.

Output: colorways/outline_compare_v5.png
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
import _confirm_v8_premv1_hybrid2_colorway as cw
import _confirm_v8_premv1_hybrid2_frames as fr
from _confirm_v8_premv1_hybrid2_panel_color_options import (PLATINUM,
                                                            GOLD as PANEL_GOLD)
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import (NAME_ZONE_C, CHIP_CY,
                                                    BG_DEEP_A, BG_GLINT_A,
                                                    _chip_cy_zone)
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.store_cards import m
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442

# Saturated gold — the CARD_RING values wash toward grey once 2-3px lines go
# through the LANCZOS downscale, so the row must overshoot to read as gold.
GOLD = dict(deep=(96, 66, 14), mid=(214, 156, 48), bright=(255, 210, 92),
            gem=(240, 178, 54), gem_deep=(120, 76, 12),
            glint=(240, 182, 62), ring=(250, 200, 80))
SILVER = dict(deep=(60, 68, 88), mid=(178, 186, 202), bright=(240, 244, 252),
              gem=(168, 196, 232), gem_deep=(52, 72, 104),
              glint=(190, 200, 215), ring=(206, 214, 226))

FRAMES = [
    ("D1 · double-bevel", fr.frame_double_bevel),
    ("D2 · beaded", fr.frame_beaded),
    ("D3 · corner-plates", fr.frame_corner_plates),
    ("D4 · filigree-inlay", fr.frame_filigree_inlay),
    ("D5 · gemset", fr.frame_gemset),
]


def _lift(c, f):
    return tuple(min(255, int(v * f)) for v in c)


def make_buttons_unified(buy_cfg, can_text):
    """CANCEL is drawn as a full clone of the BUY design — same panel fill,
    rims, sheen, shadow, and text treatment. The only elements kept from the
    old CANCEL are its label word and its muted label colour; the dark
    keyline keeps that colour legible on the bright panel."""
    from game.store_cards import (vgrad_stops, bevel_rim, top_sheen,
                                  drop_shadow, plain_text, font)
    buy_stops, buy_text, buy_rd, buy_rb = buy_cfg

    def buttons(ov):
        rad = m(12)
        for cx, text_col, lbl in ((76, buy_text, "BUY"),
                                  (184, can_text, "CANCEL")):
            r = pygame.Rect(0, 0, m(99), m(42))
            r.center = (m(cx), m(360))
            drop_shadow(ov, r, rad, blur=m(3), alpha=100, dy=m(2))
            ov.blit(vgrad_stops(r.w, r.h, rad, buy_stops, 255), r.topleft)
            top_sheen(ov, r, rad, m(12), peak=28)
            bevel_rim(ov, r, rad, buy_rd, (*buy_rb, 235), w=max(1, m(2.0)))
            plain_text(ov, lbl, font(14), r.center, text_col,
                       shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))
    return buttons


def _patched_draw(ring):
    src = textwrap.dedent(inspect.getsource(StoreScene._draw_confirm))
    subs = [
        (r"_chip\(m\(CX\), m\(CHIP_CY\)\)", "pass"),
        (r'_btn\(buy_r, "BUY", locked=not affordable\)', "pass"),
        (r'_btn\(can_r, "CANCEL", is_cancel=True\)', "pass"),
        (r"NAME_FS, Y_NAME = 45, 213", f"NAME_FS, Y_NAME = 45, {NAME_ZONE_C}"),
        (r"_cy1 = _disc_bot_ss \+ _nfnt\.get_height\(\) // 2",
         f"_cy1 = m({NAME_ZONE_C}) - int(_nfnt.get_height() * 1.15) // 2"),
        (r"store_cards\.bevel_rim\(big, rect, rad, store_cards\.CARD_RING_DEEP,"
         r"\s*\(\*store_cards\.CARD_RING_BRIGHT, 230\), w=max\(1, m\(1\.9\)\)\)",
         "pass"),
        (r"pygame\.draw\.rect\(big, \(\*store_cards\.CARD_RING_BRIGHT, 55\), tray,"
         r"\s*width=max\(1, m\(1\)\), border_radius=rad - m\(3\)\)",
         "pass"),
        (r"(\n\s*# ── corner gem pair)",
         r"\n    _bg_hook(big)\n    _frame_hook(big, rect, rad)\1"),
        (r'ring=pal\["gem"\], ring_a=50\)', f"ring={ring}, ring_a=140)"),
        (r'store_cards\.cabochon_glass\(big, cx_ss, cy_ss, r_ss, tint=pal\["gem"\]\)',
         f"store_cards.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint={ring})\n"
         f"    pygame.draw.circle(big, {ring}, (cx_ss, cy_ss), r_ss,"
         f" max(2, m(1.6)))"),
    ]
    for pat, rep in subs:
        src, n = re.subn(pat, rep, src)
        assert n == 1, f"patch failed: {pat}"
    ns = {}
    exec(compile(src, "<outline_compare_draw>", "exec"), store_mod.__dict__, ns)
    return ns["_draw_confirm"]


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    h2._chip_cy = _chip_cy_zone
    _, silver_pal = DESIGNS[0]
    can_stops, can_text, _, _ = silver_pal["can"]
    try:
        MARGIN, HEAD, GAP, ROW_FOOT = 20, 46, 12, 26
        strip_w = MARGIN * 2 + len(FRAMES) * (POP_W + GAP) - GAP
        strip_h = HEAD + 2 * (POP_H + ROW_FOOT + 24) + MARGIN
        grid = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(grid)
        idr.text((MARGIN, 14),
                 "outline systems · GOLD vs SILVER · platinum panels · EPIC",
                 fill=(236, 214, 160))

        y = HEAD
        # each row is its complete design system: gold outlines carry the gold
        # bar/BUY panels, silver outlines carry the platinum panels
        rows = (("GOLD outlines · gold panels", GOLD, PANEL_GOLD),
                ("SILVER outlines · platinum panels", SILVER, PLATINUM))
        for row_label, pal, (bar, buy) in rows:
            fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = (pal["deep"], pal["mid"],
                                                      pal["bright"])
            fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
            h2._DRAW_FN[0] = _patched_draw(pal["ring"])
            store_mod._bg_hook = hook_constellation(pal["glint"],
                                                    BG_DEEP_A, BG_GLINT_A)
            h2.overlay_bullion_chip = cw.make_chip_fn(bar)
            h2.overlay_buttons = make_buttons_unified(buy, can_text)
            idr.text((MARGIN, y + 2), row_label, fill=(206, 190, 150))
            y += 20
            for i, (label, frame_fn) in enumerate(FRAMES):
                store_mod._frame_hook = frame_fn
                pop = h2.render_popup("EPIC")
                pil = Image.frombytes("RGB", (POP_W, POP_H),
                                      pygame.image.tostring(pop, "RGB"))
                x = MARGIN + i * (POP_W + GAP)
                grid.paste(pil, (x, y))
                idr.text((x + POP_W // 2, y + POP_H + 5), label,
                         fill=(170, 170, 195), anchor="mt")
            y += POP_H + ROW_FOOT + 4

        out_img = grid.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "outline_compare_v5.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        for attr in ("_bg_hook", "_frame_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


if __name__ == "__main__":
    main()
