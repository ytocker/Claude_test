"""All-silver outlines — including the hero item's circular ring.

The earlier silver frame run left the hero disc's ring in its tier colour;
this version silvers every outline: the five D-frame constructions, the
constellation web glint, the platinum bar/BUY panels, and the cabochon ring
around the item itself (patched from tier gem alpha 50 to crisp silver
alpha 140).

Output: colorways/all_silver_showcase_v1.png — 5 frames, EPIC.
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
from _confirm_v8_premv1_hybrid2_panel_color_options import PLATINUM
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
HERO_RING = (206, 214, 226)


def _patched_draw_all_silver():
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
        # the item's circular outline goes silver too, crisp instead of a
        # faint tier tint
        (r'ring=pal\["gem"\], ring_a=50\)',
         f"ring={HERO_RING}, ring_a=140)"),
    ]
    for pat, rep in subs:
        src, n = re.subn(pat, rep, src)
        assert n == 1, f"patch failed: {pat}"
    ns = {}
    exec(compile(src, "<all_silver_draw>", "exec"), store_mod.__dict__, ns)
    return ns["_draw_confirm"]


FRAMES = [
    ("D1 · double-bevel", fr.frame_double_bevel),
    ("D2 · beaded", fr.frame_beaded),
    ("D3 · corner-plates", fr.frame_corner_plates),
    ("D4 · filigree-inlay", fr.frame_filigree_inlay),
    ("D5 · gemset", fr.frame_gemset),
]

SILVER = dict(deep=(60, 68, 88), mid=(178, 186, 202), bright=(240, 244, 252),
              gem=(168, 196, 232), gem_deep=(52, 72, 104))


def main():
    # frame constructions draw from the fr module palette — flip it to silver
    fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = (SILVER["deep"], SILVER["mid"],
                                              SILVER["bright"])
    fr.GEM_SIL, fr.GEM_SIL_DEEP = SILVER["gem"], SILVER["gem_deep"]

    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    h2._DRAW_FN[0] = _patched_draw_all_silver()
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    h2._chip_cy = _chip_cy_zone
    _, silver_pal = DESIGNS[0]
    store_mod._bg_hook = hook_constellation((190, 200, 215), BG_DEEP_A, BG_GLINT_A)
    bar, buy = PLATINUM
    h2.overlay_bullion_chip = cw.make_chip_fn(bar)
    h2.overlay_buttons = cw.make_buttons_fn(buy, silver_pal["can"])
    try:
        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(FRAMES) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 "ALL-SILVER outlines · incl. hero ring · platinum panels · EPIC",
                 fill=(236, 214, 160))
        for i, (label, frame_fn) in enumerate(FRAMES):
            store_mod._frame_hook = frame_fn
            pop = h2.render_popup("EPIC")
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (POP_W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + POP_W // 2, HEAD + POP_H + 6), label,
                     fill=(170, 170, 195), anchor="mt")

        out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "all_silver_showcase_v1.png")
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
